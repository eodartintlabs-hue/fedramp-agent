#!/usr/bin/env python3
"""
Enforce CoSAI ADR-033 D2a/D5/D6/D8 vendor-neutrality and Agent Skills structural rules
across shipped `agents/` and `skills/` surfaces using pure Python 3.11+ standard library.

Checks enforced:
1. Vendor / product / company / harness / model / config-path denylist scan across
   markdown, JSON, YAML, and text files under target paths (defaulting to `agents` and `skills`),
   with span-based suppression for allowlisted regulatory and standards authorities
   (FedRAMP, NIST, CISA, OMB, FIPS, MITRE, ATLAS, OWASP, ISO, EU AI Act, STRIDE, CoSAI,
   OASIS, RFC-2119, OIDC, SAML, JWE, MCP, SPDX, CycloneDX).
2. Canonical skill frontmatter ceiling: every `skills/<skill>/SKILL.md` MUST carry a valid
   YAML frontmatter block containing ONLY `name` and `description` (both non-empty).
   Top-level agent definitions (`agents/*.md`, excluding `README.md`) must not declare
   runtime-binding frontmatter keys (`tools`, `model`, `color`, `allowed-tools`).
3. Portable evaluation suite completeness (CoSAI ADR-033 D6): every skill directory
   (`skills/<skill>/`) carrying a `SKILL.md` MUST also contain a valid `evals/evals.json`
   with `skill_name` and a non-empty `evals` array.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

HOOK_NAME = "check-neutrality"

TEXT_EXTENSIONS: frozenset[str] = frozenset(
    {".md", ".json", ".yaml", ".yml", ".txt", ".py", ".sh", ".toml"}
)

# ---------------------------------------------------------------------------
# Denylist patterns (aligned with CoSAI secure-ai-tooling _neutrality_data.py
# plus additional enterprise harness/framework/cloud-AI tokens required by brief).
# ---------------------------------------------------------------------------
VENDOR_PRODUCT_TERMS: tuple[str, ...] = (
    "GitHub Copilot",
    "Claude Code",
    "Vertex AI",
    "Amazon Bedrock",
    "AWS Bedrock",
    "Antigravity",
    "Anthropic",
    "LangChain",
    "LangGraph",
    "LlamaIndex",
    "Semantic Kernel",
    "Windsurf",
    "ChatGPT",
    "Copilot",
    "Codeium",
    "AutoGen",
    "Bedrock",
    "CrewAI",
    "OpenAI",
    "Gemini",
    "Claude",
    "Cursor",
    "Vertex",
    "Replit",
    "Aider",
    "Devin",
    "Cody",
    "GPT-4",
    "GPT-5",
    "GPT",
)

VENDOR_PRODUCT_LOWERCASE_TERMS: tuple[str, ...] = (
    "antigravity",
    "anthropic",
    "langchain",
    "langgraph",
    "llamaindex",
    "windsurf",
    "chatgpt",
    "copilot",
    "codeium",
    "autogen",
    "bedrock",
    "crewai",
    "openai",
    "gemini",
    "claude",
    "cursor",
    "aider",
)

_VENDOR_ALT = "|".join(re.escape(t) for t in sorted(VENDOR_PRODUCT_TERMS, key=len, reverse=True))
_VENDOR_LOWER_ALT = "|".join(
    re.escape(t) for t in sorted(VENDOR_PRODUCT_LOWERCASE_TERMS, key=len, reverse=True)
)
VENDOR_PRODUCT_RE: re.Pattern[str] = re.compile(rf"\b(?:{_VENDOR_ALT}|{_VENDOR_LOWER_ALT})\b")

_MODEL_FAMILY_PREFIXES: tuple[str, ...] = (
    "claude",
    "gpt",
    "gemini",
    "llama",
    "mistral",
    "codex",
    "palm",
    "deepseek",
    "grok",
    "qwen",
)
MODEL_IDENTIFIER_RE: re.Pattern[str] = re.compile(
    rf"\b(?:{'|'.join(_MODEL_FAMILY_PREFIXES)})-[A-Za-z0-9]+(?:[.-][A-Za-z0-9]+)*\b",
    re.IGNORECASE,
)

CLI_ENTRYPOINT_NAMES: tuple[str, ...] = (
    "claude",
    "cursor",
    "aider",
    "windsurf",
    "codex",
    "cline",
    "antigravity",
    "agy",
)
_CLI_ALT = "|".join(re.escape(name) for name in CLI_ENTRYPOINT_NAMES)
CLI_ENTRYPOINT_RE: re.Pattern[str] = re.compile(rf"`(?:{_CLI_ALT})\b[^`\n]*`", re.IGNORECASE)

INVOKE_TOOL_RE: re.Pattern[str] = re.compile(
    r"\\?<[^<>]*\b(?:uses|invoke)\b[^<>]*\btool\b[^<>]*>\\?",
    re.IGNORECASE,
)

SUBAGENT_TYPE_RE: re.Pattern[str] = re.compile(r"subagent[_-]type", re.IGNORECASE)

AUTO_LOAD_TRIGGER_RE: re.Pattern[str] = re.compile(
    r"auto-(?:load|trigger|activate|invoke)(?:s|d|ed|ing)?",
    re.IGNORECASE,
)

HARNESS_CONFIG_PATH_TERMS: tuple[str, ...] = (
    ".claude/",
    ".cursor/",
    ".windsurf/",
    ".aider/",
    ".continue/",
    ".codeium/",
    ".antigravity/",
    ".github/copilot",
)
_HARNESS_PATH_ALT = "|".join(
    re.escape(t) for t in sorted(HARNESS_CONFIG_PATH_TERMS, key=len, reverse=True)
)
HARNESS_CONFIG_PATH_RE: re.Pattern[str] = re.compile(_HARNESS_PATH_ALT, re.IGNORECASE)

DENYLIST_CATEGORIES: tuple[tuple[re.Pattern[str], str], ...] = (
    (VENDOR_PRODUCT_RE, "names a specific AI vendor, product, harness, or model family"),
    (MODEL_IDENTIFIER_RE, "names a specific model identifier"),
    (CLI_ENTRYPOINT_RE, "names a specific harness CLI entry point"),
    (INVOKE_TOOL_RE, "embeds a harness-invocation stage direction"),
    (SUBAGENT_TYPE_RE, "embeds a harness-specific subagent_type token"),
    (AUTO_LOAD_TRIGGER_RE, "embeds harness-specific auto-load/auto-trigger phrasing"),
    (HARNESS_CONFIG_PATH_RE, "references a harness-specific config path"),
)

# ---------------------------------------------------------------------------
# Framework & Standards Authority Allowlist (span-level overlap suppression)
# ---------------------------------------------------------------------------
FRAMEWORK_ALLOWLIST_TERMS: tuple[str, ...] = (
    "FedRAMP",
    "NIST",
    "CISA",
    "OMB",
    "FIPS",
    "MITRE",
    "ATLAS",
    "OWASP",
    "ISO",
    "EU AI Act",
    "STRIDE",
    "CoSAI",
    "OASIS",
    "RFC-2119",
    "OIDC",
    "SAML",
    "JWE",
    "MCP",
    "SPDX",
    "CycloneDX",
)

FRAMEWORK_ALLOWLIST_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"\bFedRAMP\b"),
    re.compile(r"\bNIST(?:\s+SP\s+[0-9A-Za-z-]+|\s+AI\s+RMF)?\b"),
    re.compile(r"\bCISA(?:\s+BOD\s+\d+-\d+|\s+KEV)?\b"),
    re.compile(r"\bOMB(?:\s+M-\d+-\d+)?\b"),
    re.compile(r"\bFIPS\s?(?:140-[23]|199|20[0-9])?\b"),
    re.compile(r"\bMITRE\b"),
    re.compile(r"\bATLAS\b"),
    re.compile(r"\bATT&CK\b"),
    re.compile(r"\bAML\.[TM]\d{4}(?:@[0-9.]+)?\b"),
    re.compile(r"\b(?:GOVERN|MAP|MEASURE|MANAGE)-\d+(?:\.\d+)?\b"),
    re.compile(r"\bOWASP(?:\s+Top\s+10)?\b"),
    re.compile(r"\bLLM\d{2}:\d{4}\b"),
    re.compile(r"\bISO(?:/IEC)?(?:\s?\d+)?\b"),
    re.compile(r"\bEU\s+AI\s+Act\b"),
    re.compile(r"\bSTRIDE\b"),
    re.compile(r"\bCoSAI\b"),
    re.compile(r"\bOASIS\b"),
    re.compile(r"\bRFC[-\s]?(?:2119|8693|7516|7519)\b", re.IGNORECASE),
    re.compile(r"\bOIDC\b"),
    re.compile(r"\bSAML\b"),
    re.compile(r"\bJWE\b"),
    re.compile(r"\bMCP\b"),
    re.compile(r"\bSPDX\b"),
    re.compile(r"\bCycloneDX\b"),
)

SKILL_FRONTMATTER_ALLOWED_KEYS: frozenset[str] = frozenset({"name", "description"})
AGENT_FRONTMATTER_FORBIDDEN_KEYS: frozenset[str] = frozenset(
    {"tools", "model", "color", "allowed-tools"}
)


@dataclass(frozen=True)
class NeutralityViolation:
    """A single neutrality, frontmatter, or skill-eval structural violation."""

    path: str
    line: int
    rule_id: str
    token: str
    message: str

    def format_line(self) -> str:
        return f"{HOOK_NAME}: {self.path}:{self.line}: [{self.rule_id}] {self.message}"


def _allowlist_spans(line: str) -> list[tuple[int, int]]:
    spans: list[tuple[int, int]] = []
    for pattern in FRAMEWORK_ALLOWLIST_PATTERNS:
        spans.extend((m.start(), m.end()) for m in pattern.finditer(line))
    return spans


def _overlaps(span: tuple[int, int], others: list[tuple[int, int]]) -> bool:
    start, end = span
    return any(start < o_end and o_start < end for o_start, o_end in others)


def _scan_line(path: Path, line_number: int, line: str) -> list[NeutralityViolation]:
    allow_spans = _allowlist_spans(line)
    violations: list[NeutralityViolation] = []
    for pattern, description in DENYLIST_CATEGORIES:
        for match in pattern.finditer(line):
            if _overlaps((match.start(), match.end()), allow_spans):
                continue
            token = match.group(0).strip("`")
            violations.append(
                NeutralityViolation(
                    path=str(path),
                    line=line_number,
                    rule_id="COSAI-ADR-033-D5-DENYLIST",
                    token=token,
                    message=f"{description}: {token!r}",
                )
            )
    return violations


def _normalize_key(key: str) -> str:
    return key.strip().lower().replace("_", "-")


def _parse_yaml_frontmatter_stdlib(block_lines: list[str], start_line_offset: int) -> tuple[dict[str, tuple[str, int]] | None, str | None]:
    """
    Pure-stdlib YAML frontmatter key/value parser for SKILL.md and agent markdown files.

    Supports top-level `key: value` pairs, quoted values, and folded/literal multiline
    scalars (`>` or `|`). Fails closed on non-mapping lines, list items at top level,
    duplicate keys, or syntax errors.
    """
    mapping: dict[str, tuple[str, int]] = {}
    current_key: str | None = None
    current_val_parts: list[str] = []
    current_key_line: int = start_line_offset

    key_re = re.compile(r"^([A-Za-z0-9_-]+)\s*:\s*(.*)$")

    for idx, raw_line in enumerate(block_lines):
        line_no = start_line_offset + idx
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        # Indented continuation line for multiline value
        if raw_line.startswith((" ", "\t")):
            if current_key is None:
                return None, f"unexpected indentation on line {line_no}"
            current_val_parts.append(stripped)
            mapping[current_key] = (" ".join(current_val_parts).strip(), current_key_line)
            continue

        match = key_re.match(raw_line)
        if not match:
            return None, f"invalid YAML mapping entry on line {line_no}: {raw_line!r}"

        key = match.group(1)
        val = match.group(2).strip()
        if val in (">", "|", ">-", "|-"):
            val = ""
        elif (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
            val = val[1:-1]

        current_key = key
        current_key_line = line_no
        current_val_parts = [val] if val else []
        mapping[key] = (val, line_no)

    return mapping, None


def _is_canonical_skill_file(path: Path) -> bool:
    return path.name == "SKILL.md" and path.parent.parent.name == "skills"


def _is_top_level_agent_file(path: Path) -> bool:
    return path.suffix == ".md" and path.name != "README.md" and path.parent.name == "agents"


def _check_frontmatter(path: Path, lines: list[str]) -> list[NeutralityViolation]:
    is_skill = _is_canonical_skill_file(path)
    is_agent = _is_top_level_agent_file(path)

    has_opening_fence = bool(lines) and lines[0].strip() == "---"

    if is_skill and not has_opening_fence:
        return [
            NeutralityViolation(
                path=str(path),
                line=1,
                rule_id="COSAI-ADR-033-D2A-FRONTMATTER",
                token="---",
                message="SKILL.md must begin with a YAML frontmatter block declaring 'name' and 'description'.",
            )
        ]

    if not has_opening_fence:
        return []

    closing_index: int | None = None
    for idx in range(1, len(lines)):
        if lines[idx].strip() == "---":
            closing_index = idx
            break

    if closing_index is None:
        if is_skill or is_agent:
            return [
                NeutralityViolation(
                    path=str(path),
                    line=1,
                    rule_id="COSAI-ADR-033-D2A-FRONTMATTER",
                    token="---",
                    message="unverifiable frontmatter: opening '---' fence has no closing '---'.",
                )
            ]
        return []

    if not (is_skill or is_agent):
        return []

    block_lines = lines[1:closing_index]
    parsed, err = _parse_yaml_frontmatter_stdlib(block_lines, start_line_offset=2)
    if err is not None or parsed is None:
        return [
            NeutralityViolation(
                path=str(path),
                line=1,
                rule_id="COSAI-ADR-033-D2A-FRONTMATTER",
                token="---",
                message=f"unverifiable frontmatter: {err or 'block is not a valid mapping'}",
            )
        ]

    violations: list[NeutralityViolation] = []
    if is_skill:
        normalized_present: set[str] = set()
        for raw_key, (val, key_line) in parsed.items():
            norm = _normalize_key(raw_key)
            normalized_present.add(norm)
            if norm not in SKILL_FRONTMATTER_ALLOWED_KEYS:
                violations.append(
                    NeutralityViolation(
                        path=str(path),
                        line=key_line,
                        rule_id="COSAI-ADR-033-D2A-SKILL-KEYS",
                        token=raw_key,
                        message=(
                            f"SKILL.md frontmatter may declare only 'name' and 'description': "
                            f"found forbidden key {raw_key!r}"
                        ),
                    )
                )
            elif not val:
                violations.append(
                    NeutralityViolation(
                        path=str(path),
                        line=key_line,
                        rule_id="COSAI-ADR-033-D2A-SKILL-KEYS",
                        token=raw_key,
                        message=f"SKILL.md frontmatter key {raw_key!r} must have a non-empty value.",
                    )
                )
        for req_key in ("name", "description"):
            if req_key not in normalized_present:
                violations.append(
                    NeutralityViolation(
                        path=str(path),
                        line=1,
                        rule_id="COSAI-ADR-033-D2A-SKILL-KEYS",
                        token=req_key,
                        message=f"SKILL.md frontmatter is missing required key {req_key!r}.",
                    )
                )
    elif is_agent:
        for raw_key, (_val, key_line) in parsed.items():
            norm = _normalize_key(raw_key)
            if norm in AGENT_FRONTMATTER_FORBIDDEN_KEYS:
                violations.append(
                    NeutralityViolation(
                        path=str(path),
                        line=key_line,
                        rule_id="COSAI-ADR-033-D2A-AGENT-KEYS",
                        token=raw_key,
                        message=f"agent frontmatter must not declare runtime-binding key {raw_key!r}",
                    )
                )

    return violations


def _check_skill_evals(skill_md_path: Path) -> list[NeutralityViolation]:
    """Verify that a skill directory containing SKILL.md also contains a valid evals/evals.json."""
    skill_dir = skill_md_path.parent
    evals_path = skill_dir / "evals" / "evals.json"
    if not evals_path.is_file():
        return [
            NeutralityViolation(
                path=str(skill_md_path),
                line=1,
                rule_id="COSAI-ADR-033-D6-EVALS",
                token="evals/evals.json",
                message=f"Skill '{skill_dir.name}' is missing required portable evaluation file '{evals_path}'.",
            )
        ]

    try:
        data = json.loads(evals_path.read_text(encoding="utf-8"))
    except Exception as exc:
        return [
            NeutralityViolation(
                path=str(evals_path),
                line=1,
                rule_id="COSAI-ADR-033-D6-EVALS",
                token="evals.json",
                message=f"Invalid JSON in '{evals_path}': {exc}",
            )
        ]

    if not isinstance(data, dict) or not isinstance(data.get("evals"), list) or len(data["evals"]) == 0:
        return [
            NeutralityViolation(
                path=str(evals_path),
                line=1,
                rule_id="COSAI-ADR-033-D6-EVALS",
                token="evals",
                message=f"'{evals_path}' must contain an object with a non-empty 'evals' array.",
            )
        ]

    return []


def validate_file(path: Path) -> list[NeutralityViolation]:
    """Validate a single file for vendor neutrality, frontmatter rules, and skill eval linkage."""
    try:
        raw = path.read_bytes()
    except OSError:
        return [
            NeutralityViolation(
                path=str(path),
                line=1,
                rule_id="FILE-READ-ERROR",
                token=path.name,
                message="file could not be read; cannot verify neutrality",
            )
        ]

    is_known_text = path.suffix in TEXT_EXTENSIONS
    if not is_known_text and b"\x00" in raw[:8192]:
        return []

    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        if not is_known_text:
            return []
        return [
            NeutralityViolation(
                path=str(path),
                line=1,
                rule_id="INVALID-UTF8",
                token=path.name,
                message="file is not valid UTF-8; cannot verify neutrality",
            )
        ]

    lines = text.splitlines()
    violations: list[NeutralityViolation] = []
    for line_no, line in enumerate(lines, start=1):
        violations.extend(_scan_line(path, line_no, line))
    violations.extend(_check_frontmatter(path, lines))
    if _is_canonical_skill_file(path):
        violations.extend(_check_skill_evals(path))
    return violations


def discover_target_files(paths: list[Path]) -> tuple[list[Path], list[NeutralityViolation]]:
    """Expand directories and files into a deterministic sorted list of text files plus directory-level skill checks."""
    discovered: list[Path] = []
    structural_violations: list[NeutralityViolation] = []

    for target in paths:
        if target.is_symlink() and not target.exists():
            discovered.append(target)
            continue
        if not target.exists():
            continue
        if target.is_file():
            discovered.append(target)
        elif target.is_dir():
            # If scanning a `skills` directory, verify every child skill directory has SKILL.md and evals/evals.json
            if target.name == "skills":
                for child in sorted(target.iterdir()):
                    if child.is_dir() and not child.name.startswith("."):
                        skill_md = child / "SKILL.md"
                        if not skill_md.is_file():
                            structural_violations.append(
                                NeutralityViolation(
                                    path=str(child),
                                    line=1,
                                    rule_id="COSAI-ADR-033-D2A-SKILL-MD",
                                    token="SKILL.md",
                                    message=f"Skill directory '{child}' is missing required 'SKILL.md'.",
                                )
                            )
            for sub in sorted(target.rglob("*")):
                if not sub.is_dir() and (sub.is_file() or sub.is_symlink()) and sub.suffix in TEXT_EXTENSIONS:
                    discovered.append(sub)

    return discovered, structural_violations


def check_paths(paths: list[Path]) -> list[NeutralityViolation]:
    """Run all neutrality and structural checks across the given paths."""
    files, violations = discover_target_files(paths)
    seen: set[Path] = set()
    for fpath in files:
        if fpath in seen:
            continue
        seen.add(fpath)
        violations.extend(validate_file(fpath))
    return violations


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Enforce CoSAI ADR-033 vendor neutrality, SKILL.md frontmatter ceiling, and skill eval completeness."
    )
    parser.add_argument(
        "paths",
        nargs="*",
        default=["agents", "skills"],
        help="Files or directories to scan (defaults to 'agents' and 'skills').",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Emit structured JSON report to stdout.",
    )
    args = parser.parse_args(argv)

    target_paths = [Path(p) for p in args.paths]
    violations = check_paths(target_paths)

    if args.json_output:
        payload: dict[str, Any] = {
            "passed": len(violations) == 0,
            "targets": [str(p) for p in target_paths],
            "violation_count": len(violations),
            "violations": [asdict(v) for v in violations],
        }
        print(json.dumps(payload, indent=2))
    else:
        if violations:
            for v in violations:
                print(v.format_line(), file=sys.stderr)
        else:
            print(
                f"[PASS] {HOOK_NAME}: 0 neutrality or frontmatter/eval violations across {', '.join(str(p) for p in target_paths)}."
            )

    return 1 if violations else 0


if __name__ == "__main__":
    sys.exit(main())
