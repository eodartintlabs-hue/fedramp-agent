# ADR-001: Polyglot Dual-Audience `fedramp-agent` Repository Standard

**Status:** Accepted  
**Date:** 2026-11-19  
**Authors:** Dual-Audience Documentation & Governance Lead, with Architecture & Tooling review

---

## Context

Hundreds of engineering teams across the organization are building AI agents for FedRAMP Class C and Class D Cloud Service Offerings (CSOs). Without a shared repository standard, teams duplicate compliance research, invent incompatible manifest formats, and miss critical FedRAMP Consolidated Rules 2026 (CR-26, version `2026.11.02.01`) deadlines—including CISA BOD 26-04 (`2026-12-07`), CR-26 Mandatory Adoption (`2027-01-01`), and the End of New Rev5 Certifications (`2027-06-11`).

At the same time, the repository must serve **two distinct audiences**:
1. **Humans** (engineers, security architects, compliance leads, and assessors) who need readable guides, Architecture Decision Records, and templates.
2. **AI agents** (coding assistants, compliance reviewers, and CI orchestrators) that need deterministic entrypoints (`llms.txt`, `AGENTS.md`), machine-readable schemas (`schemas/`), and zero-dependency validation CLIs (`tools/`).

## Decision

We establish `fedramp-agent` as a **polyglot, dual-audience enterprise standard repository** structured around four pillars:

### D1. Dual-Audience Entrypoints

The repository root provides explicit entrypoints for both audiences:
- **Humans:** [../../README.md](../../README.md), [../getting-started.md](../getting-started.md), [../../CONTRIBUTING.md](../../CONTRIBUTING.md), and [../../specifications.md](../../specifications.md).
- **AI Agents:** [../../llms.txt](../../llms.txt) (machine-parsable index) and [../../AGENTS.md](../../AGENTS.md) (mandatory read order and non-negotiable compliance invariants).

### D2. Polyglot Canonical Specifications

Core architecture ([../../specifications.md](../../specifications.md)), ruleset applicability ([../../relevant-rulesets.md](../../relevant-rulesets.md)), CoSAI crosswalks ([../../compliance/cosai-crosswalk.json](../../compliance/cosai-crosswalk.json)), canonical agents ([../../agents/README.md](../../agents/README.md)), and skills ([../../skills/README.md](../../skills/README.md)) are framework- and language-agnostic so teams building in Python, Go, TypeScript, or Java can adopt the same compliance contract.

### D3. Zero-Dependency Python 3.11+ Compliance Tooling

All automated validation, neutrality checking, repository auditing, and report generation in [../../tools/validate_manifest.py](../../tools/validate_manifest.py), [../../tools/check_neutrality.py](../../tools/check_neutrality.py), [../../tools/audit_agent_repo.py](../../tools/audit_agent_repo.py), and [../../tools/generate_compliance_report.py](../../tools/generate_compliance_report.py) use **Python 3.11+ standard library only** (`pyproject.toml` declares zero external runtime dependencies). This guarantees the compliance gates run identically in air-gapped, restricted, or minimal CI environments.

### D4. Dual Agent Profiles

The standard explicitly distinguishes two operational profiles:
- `runtime-cso`: In-boundary agents handling Federal Customer Data or in-scope metadata.
- `internal-devsecops`: Internal engineering, platform, and compliance agents operating on CSO repositories without ingesting raw Federal Customer Data.

## Alternatives Considered

- **Language-specific SDK (e.g., Python-only or TypeScript-only framework)** — Rejected because teams build agents across multiple languages and runtimes; coupling compliance to one SDK would force rewrites or non-adoption.
- **Human-only Markdown wiki without machine-readable schemas or CLIs** — Rejected because manual checklists do not scale to hundreds of teams and cannot enforce hard gates in CI (`.github/workflows/fedramp-agent-compliance.yml`) or pre-commit (`.pre-commit-config.yaml`).
- **Third-party Python dependencies (`jsonschema`, `pydantic`, `pyyaml`) in `tools/`** — Rejected because restricted enterprise/FedRAMP build sandboxes frequently lack external PyPI access; stdlib-only Python 3.11+ runs everywhere with zero supply-chain surface.

## Consequences

- **Positive:** Any team can clone or branch `fedramp-agent` and immediately run deterministic compliance gates locally and in CI with Python 3.11+. Both humans and AI agents share a single source of truth.
- **Negative:** Implementing structural Draft 2020-12 schema checks in stdlib Python requires maintaining explicit validation logic in `tools/validate_manifest.py` rather than delegating to a third-party `jsonschema` library.
- **Follow-up:** Teams must sync quarterly `upstream` updates to `relevant-rulesets.md`, `compliance/sources-manifest.json`, and `tools/` as CR-26 evolves toward 2027.
