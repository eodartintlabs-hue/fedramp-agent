#!/usr/bin/env python3
"""
Generate dual human-readable Markdown (`--md-out`) and machine-readable JSON (`--json-out`)
FedRAMP CR-26 Compliance & Security Decision Record (SDR) Evidence Reports grounded in
an agent manifest (`--manifest`).

Aligned with `schemas/evidence-bundle.schema.json` and CR-26 `SDR-CSO-FRR`, `CDS-CSO-PSM`,
and `CCM-OCR-AVL`. Runs with Python 3.11+ standard library only.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_TOOLS_DIR = Path(__file__).resolve().parent
if str(_TOOLS_DIR.parent) not in sys.path:
    sys.path.insert(0, str(_TOOLS_DIR.parent))

from tools.validate_manifest import (  # noqa: E402
    CR26_DATASET_VERSION,
    PENDING_20X_CLASS_D_KSIS,
    ValidationResult,
    validate_manifest_file,
)

KSI_THEMES: tuple[str, ...] = (
    "CED",
    "CMT",
    "CNA",
    "IAM",
    "INR",
    "MLA",
    "PIY",
    "RPL",
    "SCR",
    "SVC",
)


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def build_evidence_bundle(
    manifest_path: Path,
    manifest_data: dict[str, Any],
    validation: ValidationResult,
) -> dict[str, Any]:
    """Construct a JSON evidence bundle conforming to schemas/evidence-bundle.schema.json."""
    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    fedramp = manifest_data.get("fedramp", {}) if isinstance(manifest_data.get("fedramp"), dict) else {}
    lifecycle = manifest_data.get("lifecycle", {}) if isinstance(manifest_data.get("lifecycle"), dict) else {}

    service_class = fedramp.get("service_class", "C")
    tracks = fedramp.get("certification_tracks", [])
    agent_id = str(manifest_data.get("agent_id", "unknown-agent"))

    class_d_notice: str | None = None
    if service_class == "D" and "20x" in tracks:
        class_d_notice = (
            f"CR-26 {CR26_DATASET_VERSION} omits varies_by_class.d for 5 KSIs "
            f"({', '.join(PENDING_20X_CLASS_D_KSIS)}) and VDR-TFR-MVX pending FedRAMP 20x Class D in 2027. "
            "Rev5 High Baseline controls govern Class D enforcement without fabricating 20x Class D statements."
        )

    findings = [asdict(e) for e in validation.errors] + [asdict(w) for w in validation.warnings]

    digests: list[dict[str, str]] = []
    if manifest_path.is_file():
        digests.append({"path": str(manifest_path), "sha256": _sha256_file(manifest_path)})

    return {
        "schema_version": "1.0.0",
        "bundle_id": f"EVB-{agent_id}-{service_class}",
        "generated_at": now_iso,
        "cr26_dataset_version": CR26_DATASET_VERSION,
        "agent_manifest_summary": {
            "agent_id": agent_id,
            "name": str(manifest_data.get("name", "")),
            "version": str(manifest_data.get("version", "")),
            "agent_profile": str(manifest_data.get("agent_profile", "runtime-cso")),
            "service_class": str(service_class),
            "certification_tracks": list(tracks) if isinstance(tracks, list) else [],
            "cso_package_id": str(fedramp.get("cso_package_id", "")),
            "in_minimum_assessment_scope": bool(fedramp.get("in_minimum_assessment_scope", False)),
        },
        "validation_status": {
            "passed": validation.passed,
            "error_count": len(validation.errors),
            "warning_count": len(validation.warnings),
        },
        "findings": findings,
        "ksi_coverage": {
            "applicable_themes": list(KSI_THEMES),
            "class_d_20x_notice": class_d_notice,
        },
        "cosai_alignment": {
            "component_ids": list(lifecycle.get("cosai_component_ids", [])),
            "control_ids": list(lifecycle.get("cosai_control_ids", [])),
            "portable_eval_paths": list(lifecycle.get("portable_eval_paths", [])),
        },
        "artifact_digests": digests,
    }


def render_markdown_report(
    bundle: dict[str, Any],
    manifest_data: dict[str, Any],
) -> str:
    """Render a human-readable Markdown compliance and SDR summary report."""
    summary = bundle["agent_manifest_summary"]
    vstatus = bundle["validation_status"]
    status_badge = "PASS" if vstatus["passed"] else "FAIL"

    owner = manifest_data.get("owner", {}) if isinstance(manifest_data.get("owner"), dict) else {}
    data_class = (
        manifest_data.get("data_classification", {})
        if isinstance(manifest_data.get("data_classification"), dict)
        else {}
    )
    model_srv = (
        manifest_data.get("model_serving", {})
        if isinstance(manifest_data.get("model_serving"), dict)
        else {}
    )
    crypto = (
        manifest_data.get("cryptography", {})
        if isinstance(manifest_data.get("cryptography"), dict)
        else {}
    )
    iam = (
        manifest_data.get("identity_access", {})
        if isinstance(manifest_data.get("identity_access"), dict)
        else {}
    )
    tools_cfg = (
        manifest_data.get("tool_boundaries", {})
        if isinstance(manifest_data.get("tool_boundaries"), dict)
        else {}
    )
    obs = (
        manifest_data.get("observability", {})
        if isinstance(manifest_data.get("observability"), dict)
        else {}
    )
    lifecycle = (
        manifest_data.get("lifecycle", {})
        if isinstance(manifest_data.get("lifecycle"), dict)
        else {}
    )
    tpirs = manifest_data.get("tpirs", []) if isinstance(manifest_data.get("tpirs"), list) else []

    tracks_str = ", ".join(summary["certification_tracks"])
    lines: list[str] = [
        f"# FedRAMP CR-26 AI Agent Compliance & SDR Report — `{summary['agent_id']}`",
        "",
        f"- **Validation Status:** `{status_badge}` ({vstatus['error_count']} error(s), {vstatus['warning_count']} warning(s))",
        f"- **CR-26 Dataset Version:** `{bundle['cr26_dataset_version']}`",
        f"- **Evidence Bundle ID:** `{bundle['bundle_id']}`",
        f"- **Generated At:** `{bundle['generated_at']}`",
        "",
        "## 1. Agent & CSO Authorization Scope",
        "",
        "| Attribute | Value |",
        "| :--- | :--- |",
        f"| **Agent Name** | {summary['name']} (`{summary['agent_id']}` v{summary['version']}) |",
        f"| **Agent Profile** | `{summary['agent_profile']}` |",
        f"| **FedRAMP Service Class** | **Class {summary['service_class']}** (FIPS 199 `{data_class.get('fips199_level', 'N/A')}`) |",
        f"| **Certification Tracks** | `{tracks_str}` |",
        f"| **CSO Package ID** | `{summary['cso_package_id']}` |",
        f"| **In Minimum Assessment Scope (`MAS-CSO-IIR`)** | `{summary['in_minimum_assessment_scope']}` |",
        f"| **Responsible Official (`CPO-CSO-OVR`)** | {owner.get('responsible_official', 'N/A')} ({owner.get('team', 'N/A')} — `{owner.get('contact_email', 'N/A')}`) |",
        f"| **Data Residency Boundary (`CTL.SA.SA-09-05`)** | {data_class.get('residency_boundary', 'N/A')} (`us_jurisdiction_only={model_srv.get('us_jurisdiction_only')}`) |",
        "",
        "## 2. CR-26 Control Posture Summary",
        "",
        "| Domain | CR-26 Rule / KSI / CTL IDs | Enforced Manifest Setting |",
        "| :--- | :--- | :--- |",
        f"| **Cryptography & FIPS 140-3** | `CMU-CSO-CMD`, `CMU-CSO-UVM` | `fips_140_3_validated_modules={crypto.get('fips_140_3_validated_modules')}` ({len(crypto.get('modules', []))} module(s) inventoried) |",
        f"| **Digital Identity & SSO** | `CTL.IA.IA-05`, `KSI-IAM-MFA` | `{iam.get('digital_identity_level')}` over `{iam.get('sso_protocol')}` (`encrypted_assertions={iam.get('encrypted_assertions')}`, `local_password_bypass_disabled={iam.get('local_password_bypass_disabled')}`) |",
        f"| **Model Serving PEP** | `MAS-CSO-TPR`, `KSI-CNA-EIS` | `{model_srv.get('inference_provider')}` (`model_reachability_pep={model_srv.get('model_reachability_pep')}`, TPIR: `{model_srv.get('fedramp_certified_tpir_id')}`) |",
        f"| **Tool & MCP Boundaries** | `SCG-CSO-SDF`, `KSI-IAM-ATP` | `network_egress_pep={tools_cfg.get('network_egress_pep')}`, `authorization_pep={tools_cfg.get('authorization_pep')}`, `tool_registry_allowlist={tools_cfg.get('tool_registry_allowlist')}` ({len(tools_cfg.get('allowed_tools', []))} allowed tool(s)) |",
        f"| **Audit & Telemetry Redaction** | `CTL.AU.AU-09`, `MAS-CSO-MDI` | `tamper_evident_audit_repo={obs.get('tamper_evident_audit_repo')}`, `prompt_response_redacted_from_external_telemetry={obs.get('prompt_response_redacted_from_external_telemetry')}` |",
        f"| **Vulnerability Triage & CDS** | `VER-TFR-EVU`, `CDS-CSO-PSM` | `vdr_triage_sla_days={lifecycle.get('vdr_triage_sla_days')}`, `per_service_certification_artifacts={lifecycle.get('per_service_certification_artifacts')}` |",
        "",
        "## 3. Third-Party Information Resources (`MAS-CSO-TPR`)",
        "",
        "| TPIR Name | Certified | FedRAMP Package ID | Use Case | Mitigations |",
        "| :--- | :--- | :--- | :--- | :--- |",
    ]

    for tpir in tpirs:
        if isinstance(tpir, dict):
            lines.append(
                f"| {tpir.get('name')} | `{tpir.get('certified')}` | `{tpir.get('fedramp_package_id')}` | "
                f"{tpir.get('use_case')} | {tpir.get('mitigations')} |"
            )

    lines.extend(
        [
            "",
            "## 4. CoSAI Risk Map Alignment",
            "",
            f"- **CoSAI Components ({len(bundle['cosai_alignment']['component_ids'])}):** "
            + ", ".join(f"`{c}`" for c in bundle["cosai_alignment"]["component_ids"]),
            f"- **CoSAI Controls ({len(bundle['cosai_alignment']['control_ids'])}):** "
            + ", ".join(f"`{c}`" for c in bundle["cosai_alignment"]["control_ids"]),
            f"- **Portable Evaluation Suites ({len(bundle['cosai_alignment']['portable_eval_paths'])}):** "
            + ", ".join(f"`{p}`" for p in bundle["cosai_alignment"]["portable_eval_paths"]),
        ]
    )

    if bundle["ksi_coverage"]["class_d_20x_notice"]:
        lines.extend(
            [
                "",
                "## 5. Regulatory Non-Invention Notice (`CR-26 2026.11.02.01`)",
                "",
                f"> {bundle['ksi_coverage']['class_d_20x_notice']}",
            ]
        )

    lines.extend(["", "## 6. Validation Findings", ""])
    if not bundle["findings"]:
        lines.append("No errors or warnings detected.")
    else:
        for f in bundle["findings"]:
            lines.append(f"- **[{f['severity']}] `{f['rule_id']}`** (`{f['field']}`): {f['message']}")

    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate dual Markdown and JSON FedRAMP CR-26 compliance and SDR reports from an agent manifest."
    )
    parser.add_argument("--manifest", required=True, help="Path to the agent-manifest.json file.")
    parser.add_argument("--md-out", required=True, help="Output file path for the Markdown report.")
    parser.add_argument("--json-out", required=True, help="Output file path for the JSON evidence bundle.")
    args = parser.parse_args(argv)

    manifest_path = Path(args.manifest)
    validation = validate_manifest_file(manifest_path)

    try:
        manifest_data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"[ERROR] Failed to parse manifest '{manifest_path}': {exc}", file=sys.stderr)
        return 1

    if not isinstance(manifest_data, dict):
        print(f"[ERROR] Manifest '{manifest_path}' root must be a JSON object.", file=sys.stderr)
        return 1

    bundle = build_evidence_bundle(manifest_path, manifest_data, validation)
    md_report = render_markdown_report(bundle, manifest_data)

    md_out = Path(args.md_out)
    json_out = Path(args.json_out)
    md_out.parent.mkdir(parents=True, exist_ok=True)
    json_out.parent.mkdir(parents=True, exist_ok=True)

    md_out.write_text(md_report, encoding="utf-8")
    json_out.write_text(json.dumps(bundle, indent=2) + "\n", encoding="utf-8")

    status = "PASS" if validation.passed else "FAIL"
    print(
        f"[{status}] Generated compliance report Markdown at '{md_out}' and JSON evidence bundle at '{json_out}'."
    )
    return 0 if validation.passed else 1


if __name__ == "__main__":
    sys.exit(main())
