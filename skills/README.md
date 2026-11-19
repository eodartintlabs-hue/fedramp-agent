# Canonical Vendor-Neutral Agent Skills

`skills/` is the canonical, vendor-neutral directory for domain compliance skills in this repository, governed by [`../docs/adr/003-vendor-neutral-agent-and-eval-shipping.md`](../docs/adr/003-vendor-neutral-agent-and-eval-shipping.md) and aligned with the **Agent Skills** open standard (`agentskills.io`, pinned to specification commit `6868401b64f791e9ff565f29beb6338826b73a2b` per CoSAI `ADR-031 D6` and `ADR-033 D1/D4`).

Skills package discrete, checkable compliance knowledge and decision procedures that both humans and canonical sub-agents ([`../agents/`](../agents/)) invoke inline. No runtime-specific wrapper files, vendor identifiers, or extended frontmatter keys are tracked in this tree.

---

## Format & Frontmatter Allowlist

Each skill directory under `skills/<skill-name>/` contains:

- **`SKILL.md`** — Opens with a YAML frontmatter block declaring **only** `name` and `description`, followed by vendor-neutral Markdown instructions. Additional frontmatter keys (such as runtime tool or model bindings) are prohibited by `tools/check_neutrality.py`.
- **`evals/evals.json`** — Required portable behavior specification (`{skill_name, evals: [{id, prompt, expected_output, expectations[]}]}`) that travels with the skill (`CoSAI ADR-033 D6`).
- **`evals/fixtures/`** — Self-contained synthetic test inputs referenced by fixture-grounded evaluation cases (`CoSAI ADR-033 D7a/D7b`). Per `CoSAI ADR-033 D7d`, fixtures and prompts carry **zero** grading notes, planted-defect labels, or expected verdicts; all grading rationale resides exclusively in `expected_output`. Each evaluation suite also retains live-repository lookup cases (`CoSAI ADR-033 D7c`).

---

## Skills in This Directory

| Skill Directory | Purpose | Authoritative Sources Consulted | Invoked By |
|---|---|---|---|
| [`check-cr26-applicability/`](check-cr26-applicability/SKILL.md) | Resolves Minimum Assessment Scope (`MAS`), certification track (`20x` / `Rev5`), Class C vs. Class D enforcement elevations, and pending `20x` Class D exclusions for `runtime-cso` and `internal-devsecops` agents. | `relevant-rulesets.md`, `specifications.md`, `compliance/frd-glossary.md` | `fedramp-compliance-reviewer`, `change-impact-assessor`, engineers |
| [`classify-scn-change/`](classify-scn-change/SKILL.md) | Applies the CR-26 Significant Change Notification (`SCN-CSO-EVA`) decision tree (`routine-non-significant`, `adaptive-change-notice`, `transformative-prior-notice`, `transformative-tpir-addition`, `emergency-change`) and calculates mandatory lead/post-notice timelines. | `relevant-rulesets.md`, `schemas/scn-record.schema.json`, `templates/SCN-change-notice.md` | `change-impact-assessor`, release engineers |
| [`audit-tpir-boundary/`](audit-tpir-boundary/SKILL.md) | Audits Third-Party Information Resources (`MAS-CSO-TPR`), inference destination certification, Class D U.S.-jurisdiction residency (`CTL.SA.SA-09-05`), and external telemetry prompt/response redaction (`MAS-CSO-MDI`). | `specifications.md`, `schemas/tpir-register.schema.json`, `compliance/marketplace-class-cd-analysis.md` | `fedramp-compliance-reviewer`, `threat-modeler` |
| [`map-cosai-controls/`](map-cosai-controls/SKILL.md) | Resolves verbatim Coalition for Secure AI (`CoSAI`) component, risk, control, persona, and external framework identifiers (`MITRE ATLAS`, `NIST AI RMF`, `OWASP Top 10 for LLM`, `STRIDE`, `ISO 22989`, `EU AI Act`) to FedRAMP CR-26 rules and Class C/D manifest gates. | `compliance/cosai-crosswalk.json`, `compliance/cosai-crosswalk.md` | `threat-modeler`, `fedramp-compliance-reviewer` |

---

## Verification Gate

Run the repository neutrality and structural validator across all skills and fixtures before committing:

```bash
python3 tools/check_neutrality.py agents skills
```
