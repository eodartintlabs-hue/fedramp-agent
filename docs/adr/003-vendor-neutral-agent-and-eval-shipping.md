# ADR-003: Vendor-Neutral Canonical Agents, Skills, and Portable Eval Shipping

**Status:** Accepted  
**Date:** 2026-11-19  
**Authors:** Dual-Audience Documentation & Governance Lead, with Architecture & Tooling review

---

## Context

Enterprise teams use heterogeneous AI coding harnesses, CI runners, and model providers. If canonical compliance agents (`agents/`), skills (`skills/`), or behavioral evals embed vendor-specific CLI flags, proprietary model identifiers, or harness-specific directory conventions, they break portability and lock compliance governance to a single vendor. This mirrors the Coalition for Secure AI (CoSAI) Risk Map patterns established in CoSAI ADR-006 (agent architecture pattern), ADR-030 (agentic component model), and ADR-033 (vendor-neutral agent and skill shipping), as well as CoSAI ADR-004 (vendor-neutral `Co-authored-by` commit trailers).

## Decision

All canonical compliance agents, skills, commit attribution, and behavioral evals in `fedramp-agent` **MUST** remain 100% vendor-neutral and harness-agnostic.

### D1. Vendor-Neutral Canonical `agents/` and `skills/`

- Canonical agents ([../../agents/README.md](../../agents/README.md)) and skills ([../../skills/README.md](../../skills/README.md)) use plain Markdown contracts and standard relative repo paths.
- They **MUST NOT** reference proprietary model names, vendor-specific tool/harness names, or vendor-owned CLI flags.
- Enforcement is automated by [../../tools/check_neutrality.py](../../tools/check_neutrality.py) in pre-commit ([../../.pre-commit-config.yaml](../../.pre-commit-config.yaml)) and CI ([../../.github/workflows/fedramp-agent-compliance.yml](../../.github/workflows/fedramp-agent-compliance.yml)).

### D2. Portable Behavioral Evals

- Agent behavioral evaluations and compliance checks ship as deterministic Python 3.11+ assertions ([../../tests/test_validate_manifest.py](../../tests/test_validate_manifest.py), [../../tests/test_check_neutrality.py](../../tests/test_check_neutrality.py), [../../tests/test_audit_agent_repo.py](../../tests/test_audit_agent_repo.py)) and structured schemas ([../../schemas/evidence-bundle.schema.json](../../schemas/evidence-bundle.schema.json)) rather than vendor-locked eval harnesses.

### D3. Vendor-Neutral AI Commit Trailers

- Following CoSAI ADR-004, AI-assisted commits use the single neutral trailer:
  ```text
  Co-authored-by: AI Assistant <ai-assistant@coalitionforsecureai.org>
  ```
- Contributors suppress vendor-default trailers that expose specific model or vendor domains.

### D4. Separation of Dev Routing from Runtime CSO Inference

- Multi-model routing for internal development and compliance workflows is documented separately in [../model-routing-playbook.md](../model-routing-playbook.md), keeping `agents/` and `skills/` model-agnostic while enforcing that `runtime-cso` production inference routes only to FedRAMP-certified `MAS-CSO-TPR` destinations.

## Alternatives Considered

- **Shipping harness-specific plugin bundles (one directory per AI coding tool)** — Rejected because maintaining N parallel copies of compliance agents and skills causes drift and creates vendor lock-in.
- **Allowing model brand names in `agents/` and `skills/`** — Rejected because it couples compliance governance to transient model releases and violates CoSAI ADR-033 neutrality.

## Consequences

- **Positive:** Any team can execute canonical compliance agents and skills in any harness, and `check_neutrality.py` prevents accidental vendor leakage at PR time.
- **Negative:** Contributors must occasionally strip vendor-default commit trailers or harness-specific syntax caught by `check_neutrality.py`.
- **Follow-up:** Maintain the forbidden-pattern ruleset in [../../tools/check_neutrality.py](../../tools/check_neutrality.py) and its unit tests in [../../tests/test_check_neutrality.py](../../tests/test_check_neutrality.py).
