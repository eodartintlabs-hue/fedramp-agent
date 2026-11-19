# Model Routing Playbook

This playbook defines the operational multi-model routing standard for engineering, compliance, and platform teams using the organization's available subscription models across `fedramp-agent` workflows.

> [!WARNING]
> **Runtime CSO Inference Boundary (`MAS-CSO-TPR` & `CTL.SA.SA-09-05`)**
> The subscription models listed below are for **internal engineering, compliance analysis, CI/CD triage, and governance orchestration** (`internal-devsecops` workflows). **Production `runtime-cso` inference** inside a FedRAMP CSO boundary handling Federal Customer Data **MUST** route exclusively through FedRAMP-certified, boundary-approved inference destinations registered in your TPIR register ([../schemas/tpir-register.schema.json](../schemas/tpir-register.schema.json)) and compliant with `CTL.SA.SA-09-05` U.S. residency rules (for Class D).

---

## 1. Model Portfolio & Routing Matrix

| Model / Orchestrator | Tier / Strength | Primary `fedramp-agent` Responsibilities | Typical Triggers |
| :--- | :--- | :--- | :--- |
| **`Gemini 4 Neon (Extra)`** | Deep reasoning & regulatory precision | Deep CR-26 regulatory interpretation, rule-by-rule applicability (`relevant-rulesets.md`), Class D compliance reviews (`agents/fedramp-compliance-reviewer.md`), independent compliance verification | New CR-26 dataset release, Class D authorization review, disputed `SCN` classification |
| **`Gemini 4 Carbon (Medium)`** | Architecture & structured synthesis | Architecture design (`specifications.md`), CoSAI ADR-030 threat modeling (`agents/threat-modeler.md`), multi-framework crosswalks (`compliance/cosai-crosswalk.md`), canonical agent & skill authoring (`agents/`, `skills/`) | New agent profile design, TPIR boundary architecture, CoSAI control mapping |
| **`Gemini 4 Argon (Medium)`** | Deterministic engineering & automation | JSON Schema engineering (`schemas/`), deterministic Python 3.11+ validators & unit tests (`tools/`, `tests/`), CI/CD & pre-commit automation (`.github/workflows/`, `.pre-commit-config.yaml`), functional QA verification | Schema updates, validator rule additions, CI failures, unit test expansion |
| **`Gemini 4 Hydrogen (Medium)`** | Fast prose & lightweight checks | Dual-audience documentation (`README.md`, `CONTRIBUTING.md`), onboarding guides (`docs/getting-started.md`), ADRs (`docs/adr/`), lightweight linting and status monitoring | Doc updates, ADR drafting, checklist formatting, routine repo hygiene |
| **`Orchestrator (Neon)`** | Enterprise-wide high-stakes orchestration | Quarterly `CCM` / CR-26 version upgrades across 100+ cloned team agent repositories | CR-26 dataset bump, CISA BOD 26-04 (`2026-12-07`), CR-26 Mandatory Adoption (`2027-01-01`), End of New Rev5 (`2027-06-11`) |
| **`Orchestrator (Carbon)`** | Team-level delivery orchestration | End-to-end feature-to-compliance delivery pipelines: architecture design → threat model → `SCN` classification → `SDR` evidence bundle | Major agent feature PR, new MCP server onboarding, `MAS` boundary change |
| **`Orchestrator (Argon)`** | High-volume automated triage | High-volume automated PR compliance triage, `VDR`/`VER` vulnerability triage support (`5-day` Class C / `2-day` Class D SLAs) | Every PR open/sync, daily `VDR`/`VER` scanner feed triage |

---

## 2. Routing Decision Flow

1. **Is it a deterministic check?**
   - Run the zero-dependency Python CLI first (`validate_manifest.py`, `check_neutrality.py`, `audit_agent_repo.py`, `unittest`) — zero model tokens required.
2. **Is it high-volume PR or `VDR`/`VER` triage?**
   - Route to **`Orchestrator (Argon)`** / **`Gemini 4 Argon (Medium)`**. Respect the `2-day` Class D vs. `5-day` Class C `VER-TFR-EVU` triage SLA.
3. **Does it change architecture, TPIRs, or threat boundaries?**
   - Route to **`Orchestrator (Carbon)`** / **`Gemini 4 Carbon (Medium)`**.
4. **Does it interpret CR-26 regulatory force, Class D hard gates, or sign off on compliance?**
   - Route to **`Gemini 4 Neon (Extra)`** (or **`Orchestrator (Neon)`** for fleet-wide rollouts).
5. **Is it documentation, ADR drafting, or onboarding prose?**
   - Route to **`Gemini 4 Hydrogen (Medium)`**.

---

## 3. Cost & Quota Stewardship

- **Deterministic before generative:** Always run [../tools/validate_manifest.py](../tools/validate_manifest.py), [../tools/check_neutrality.py](../tools/check_neutrality.py), and [../tools/audit_agent_repo.py](../tools/audit_agent_repo.py) before invoking an LLM reviewer.
- **Reserve `Neon` for high-leverage gates:** Do not spend `Gemini 4 Neon (Extra)` quota on formatting, boilerplate tests, or doc typos; reserve it for CR-26 regulatory interpretation and final Class D verification.
- **Keep canonical prompts portable:** Author all reusable instructions in [../agents/](../agents/README.md) and [../skills/](../skills/README.md) without model-specific quirks so routing remains flexible across tiers.
