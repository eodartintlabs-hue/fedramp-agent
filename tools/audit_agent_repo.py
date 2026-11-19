#!/usr/bin/env python3
"""
Audit a FedRAMP AI Agent repository end-to-end against FedRAMP Consolidated Rules 2026
(CR-26, version 2026.11.02.01) and CoSAI Risk Map repository standards.

Performs:
1. Manifest structural & semantic validation (`validate_manifest.py`).
2. Required repository artifact verification (`schemas/`, `templates/`, `compliance/`,
   governance docs, and valid JSON syntax on schemas/templates).
3. Vendor-neutrality & Agent Skills structural check (`check_neutrality.py`) when
   `agents/` or `skills/` exist in the target repository.
4. Verification that all `lifecycle.portable_eval_paths` declared in the manifest exist
   and contain valid JSON evaluation suites inside the target repository.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

_TOOLS_DIR = Path(__file__).resolve().parent
if str(_TOOLS_DIR.parent) not in sys.path:
    sys.path.insert(0, str(_TOOLS_DIR.parent))

from tools.check_neutrality import check_paths  # noqa: E402
from tools.validate_manifest import (  # noqa: E402
    CR26_DATASET_VERSION,
    Finding,
    validate_manifest_file,
)

REQUIRED_SCHEMAS: tuple[str, ...] = (
    "schemas/agent-manifest.schema.json",
    "schemas/sdr-agent-addendum.schema.json",
    "schemas/scn-record.schema.json",
    "schemas/tpir-register.schema.json",
    "schemas/evidence-bundle.schema.json",
)

REQUIRED_TEMPLATES: tuple[str, ...] = (
    "templates/agent-manifest.example.class-c.json",
    "templates/agent-manifest.example.class-d.json",
    "templates/MAS-boundary-statement.md",
    "templates/SDR-agent-record.md",
    "templates/SCG-agent-secure-config.md",
    "templates/SCN-change-notice.md",
    "templates/VDR-vulnerability-profile.md",
    "templates/IEC-incident-runbook.md",
    "templates/CPO-service-addendum.json",
    "templates/PR-compliance-checklist.md",
)

RECOMMENDED_GOVERNANCE_ARTIFACTS: tuple[tuple[str, str], ...] = (
    ("relevant-rulesets.md", "SDR-CSO-FRR"),
    ("specifications.md", "SCG-CSO-RSC"),
    ("compliance/frd-glossary.md", "SDR-CSO-FRR"),
    ("compliance/cosai-crosswalk.md", "SDR-CSX-KSI"),
    ("compliance/cosai-crosswalk.json", "SDR-CSX-KSI"),
    ("compliance/sources-manifest.json", "CDS-CSO-FRC"),
)


@dataclass
class RepoAuditReport:
    """Structured result of auditing a repository and its agent manifest."""

    repo_path: str
    manifest_path: str
    cr26_dataset_version: str
    agent_id: str | None
    service_class: str | None
    certification_tracks: list[str]
    strict_mode: bool
    passed: bool
    errors: list[Finding]
    warnings: list[Finding]

    def to_dict(self) -> dict[str, Any]:
        return {
            "repo_path": self.repo_path,
            "manifest_path": self.manifest_path,
            "cr26_dataset_version": self.cr26_dataset_version,
            "agent_id": self.agent_id,
            "service_class": self.service_class,
            "certification_tracks": self.certification_tracks,
            "strict_mode": self.strict_mode,
            "passed": self.passed,
            "error_count": len(self.errors),
            "warning_count": len(self.warnings),
            "errors": [asdict(e) for e in self.errors],
            "warnings": [asdict(w) for w in self.warnings],
        }


def audit_repository(
    repo_dir: Path,
    manifest_path: Path,
    strict: bool = False,
) -> RepoAuditReport:
    """Run full manifest, artifact, neutrality, and portable-eval audit on `repo_dir`."""
    errors: list[Finding] = []
    warnings: list[Finding] = []

    resolved_manifest = manifest_path if manifest_path.is_file() else (repo_dir / manifest_path)
    schema_path = repo_dir / "schemas" / "agent-manifest.schema.json"
    if not schema_path.is_file():
        schema_path = _TOOLS_DIR.parent / "schemas" / "agent-manifest.schema.json"

    manifest_result = validate_manifest_file(resolved_manifest, schema_path=schema_path)
    errors.extend(manifest_result.errors)
    warnings.extend(manifest_result.warnings)

    # 1. Check required schemas and templates
    for rel_schema in REQUIRED_SCHEMAS:
        spath = repo_dir / rel_schema
        if not spath.is_file():
            errors.append(
                Finding(
                    severity="ERROR",
                    rule_id="CDS-CSO-FRC",
                    field=rel_schema,
                    message=f"Required compliance schema '{rel_schema}' is missing from repository.",
                )
            )
        else:
            try:
                json.loads(spath.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:
                errors.append(
                    Finding(
                        severity="ERROR",
                        rule_id="SCHEMA-JSON-INVALID",
                        field=rel_schema,
                        message=f"Schema file '{rel_schema}' contains invalid JSON: {exc}",
                    )
                )

    for rel_tmpl in REQUIRED_TEMPLATES:
        tpath = repo_dir / rel_tmpl
        if not tpath.is_file():
            errors.append(
                Finding(
                    severity="ERROR",
                    rule_id="CDS-CSO-PSM",
                    field=rel_tmpl,
                    message=f"Required compliance template '{rel_tmpl}' is missing from repository.",
                )
            )
        elif tpath.suffix == ".json":
            try:
                json.loads(tpath.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:
                errors.append(
                    Finding(
                        severity="ERROR",
                        rule_id="TEMPLATE-JSON-INVALID",
                        field=rel_tmpl,
                        message=f"JSON template '{rel_tmpl}' contains invalid JSON: {exc}",
                    )
                )

    # 2. Check governance / compliance docs (warn if absent during staging, or error if --strict and present/expected)
    for rel_doc, rule_id in RECOMMENDED_GOVERNANCE_ARTIFACTS:
        dpath = repo_dir / rel_doc
        if not dpath.is_file():
            warnings.append(
                Finding(
                    severity="WARNING",
                    rule_id=rule_id,
                    field=rel_doc,
                    message=f"Recommended compliance reference artifact '{rel_doc}' not found in '{repo_dir}'.",
                )
            )
        elif dpath.suffix == ".json":
            try:
                json.loads(dpath.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:
                errors.append(
                    Finding(
                        severity="ERROR",
                        rule_id=rule_id,
                        field=rel_doc,
                        message=f"Compliance JSON artifact '{rel_doc}' contains invalid JSON: {exc}",
                    )
                )

    # 3. Verify portable_eval_paths declared in the manifest exist when present in repo
    if resolved_manifest.is_file():
        try:
            raw_manifest = json.loads(resolved_manifest.read_text(encoding="utf-8"))
        except Exception:
            raw_manifest = {}
        if isinstance(raw_manifest, dict):
            lc = raw_manifest.get("lifecycle")
            if isinstance(lc, dict):
                eval_paths = lc.get("portable_eval_paths")
                if isinstance(eval_paths, list):
                    skills_dir_exists = (repo_dir / "skills").is_dir()
                    for idx, rel_eval in enumerate(eval_paths):
                        if not isinstance(rel_eval, str) or not rel_eval.strip():
                            continue
                        epath = repo_dir / rel_eval
                        if not epath.is_file():
                            # If skills/ exists (or path isn't under skills/), missing eval path is a hard error
                            if skills_dir_exists or not rel_eval.startswith("skills/"):
                                errors.append(
                                    Finding(
                                        severity="ERROR",
                                        rule_id="COSAI-ADR-033-D6",
                                        field=f"lifecycle.portable_eval_paths[{idx}]",
                                        message=f"Declared portable evaluation suite '{rel_eval}' does not exist at '{epath}'.",
                                    )
                                )
                            else:
                                warnings.append(
                                    Finding(
                                        severity="WARNING",
                                        rule_id="COSAI-ADR-033-D6",
                                        field=f"lifecycle.portable_eval_paths[{idx}]",
                                        message=f"Declared portable evaluation suite '{rel_eval}' not yet staged (skills/ directory absent).",
                                    )
                                )
                        else:
                            try:
                                json.loads(epath.read_text(encoding="utf-8"))
                            except json.JSONDecodeError as exc:
                                errors.append(
                                    Finding(
                                        severity="ERROR",
                                        rule_id="COSAI-ADR-033-D6",
                                        field=f"lifecycle.portable_eval_paths[{idx}]",
                                        message=f"Portable evaluation suite '{rel_eval}' is not valid JSON: {exc}",
                                    )
                                )

    # 4. Run neutrality check if agents/ or skills/ exist
    neutrality_targets: list[Path] = []
    for sub in ("agents", "skills"):
        candidate = repo_dir / sub
        if candidate.exists():
            neutrality_targets.append(candidate)

    if neutrality_targets:
        n_violations = check_paths(neutrality_targets)
        for nv in n_violations:
            errors.append(
                Finding(
                    severity="ERROR",
                    rule_id=nv.rule_id,
                    field=f"{nv.path}:{nv.line}",
                    message=nv.message,
                )
            )

    if strict:
        # In strict mode, promote any warnings other than the informational 20x Class D 2027 notice to errors
        promoted: list[Finding] = []
        remaining_warnings: list[Finding] = []
        for w in warnings:
            if w.rule_id == "CR26-20X-CLASS-D-2027":
                remaining_warnings.append(w)
            else:
                promoted.append(
                    Finding(
                        severity="ERROR",
                        rule_id=w.rule_id,
                        field=w.field,
                        message=f"[strict] {w.message}",
                    )
                )
        errors.extend(promoted)
        warnings = remaining_warnings

    passed = len(errors) == 0
    return RepoAuditReport(
        repo_path=str(repo_dir),
        manifest_path=str(resolved_manifest),
        cr26_dataset_version=CR26_DATASET_VERSION,
        agent_id=manifest_result.agent_id,
        service_class=manifest_result.service_class,
        certification_tracks=manifest_result.certification_tracks,
        strict_mode=strict,
        passed=passed,
        errors=errors,
        warnings=warnings,
    )


def _format_audit_report(report: RepoAuditReport) -> str:
    status = "PASS" if report.passed else "FAIL"
    tracks = ",".join(report.certification_tracks) if report.certification_tracks else "none"
    lines = [
        f"[{status}] FedRAMP CR-26 ({report.cr26_dataset_version}) Repository Compliance Audit",
        f"  Repository: {report.repo_path}",
        f"  Manifest:   {report.manifest_path}",
        f"  Agent ID:   {report.agent_id or '<unknown>'} | Class: {report.service_class or '<invalid>'} | Tracks: {tracks} | Strict: {report.strict_mode}",
    ]
    for w in report.warnings:
        lines.append(f"  [WARNING] [{w.rule_id}] {w.field}: {w.message}")
    for e in report.errors:
        lines.append(f"  [ERROR]   [{e.rule_id}] {e.field}: {e.message}")
    lines.append(
        f"  Audit Summary: {len(report.errors)} error(s), {len(report.warnings)} warning(s)."
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Audit an AI agent repository against FedRAMP CR-26 and CoSAI Risk Map compliance gates."
    )
    parser.add_argument(
        "--repo",
        required=True,
        help="Path to the repository root directory.",
    )
    parser.add_argument(
        "--manifest",
        required=True,
        help="Path to the agent-manifest.json file.",
    )
    parser.add_argument(
        "--json-out",
        default=None,
        help="Optional file path to write structured JSON audit report.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat warnings (such as non-FIPS Class C or missing optional artifacts) as hard errors.",
    )
    args = parser.parse_args(argv)

    repo_dir = Path(args.repo)
    manifest_path = Path(args.manifest)
    report = audit_repository(repo_dir=repo_dir, manifest_path=manifest_path, strict=args.strict)

    if args.json_out:
        out_path = Path(args.json_out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(report.to_dict(), indent=2) + "\n", encoding="utf-8")

    formatted = _format_audit_report(report)
    stream = sys.stdout if report.passed else sys.stderr
    print(formatted, file=stream)
    return 0 if report.passed else 1


if __name__ == "__main__":
    sys.exit(main())
