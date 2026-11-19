# Agent Instructions (`AGENTS.md`)

This file is the authoritative instruction set for any AI coding agent, compliance agent, or autonomous workflow operating on `fedramp-agent` or a cloned/branched team repository derived from it.

## 1. Mandatory Read Order

Before modifying code, manifests, schemas, or compliance artifacts, read in this exact order:

1. [llms.txt](llms.txt) — Machine-parsable index of all authoritative files, schemas, skills, canonical agents, templates, and CLI commands.
2. [relevant-rulesets.md](relevant-rulesets.md) — Exact FedRAMP Consolidated Rules 2026 (CR-26, version `2026.11.02.01`, last updated `2026-11-02`) applicability for `20x` and `Rev5`, Class C and Class D.
3. [specifications.md](specifications.md) — Polyglot architecture, agent profiles (`runtime-cso` and `internal-devsecops`), Policy Enforcement Points (PEPs), and CoSAI Risk Map alignment.
4. [compliance/cosai-crosswalk.json](compliance/cosai-crosswalk.json) — Machine-readable mapping between CR-26 rules/controls and CoSAI Risk Map controls/risks.
5. Your team's `agent-manifest.json` (or the reference examples [templates/agent-manifest.example.class-c.json](templates/agent-manifest.example.class-c.json) and [templates/agent-manifest.example.class-d.json](templates/agent-manifest.example.class-d.json)).

For terminology, consult [compliance/frd-glossary.md](compliance/frd-glossary.md). For dataset provenance, consult [compliance/sources-manifest.json](compliance/sources-manifest.json).

---

## 2. Non-Negotiable Compliance Invariants

You **MUST NOT** violate any of the following invariants under any circumstances:

1. **NEVER bypass Class D hard requirements:**
   - **`CMU-CSO-UVM`:** Class D `MUST` use active FIPS-validated cryptographic modules (Class C `SHOULD`).
   - **`CDS-CSO-PSM`:** Class D `MUST` supply per-service FedRAMP Certification materials (Class C `MAY`).
   - **`CTL.IA.IA-05`:** Class D `MUST` enforce `IAL3` / `AAL3` / `FAL3` with encrypted SAML XML-Enc or OIDC JWE assertions (Class C uses `IAL2` / `AAL2` / `FAL2`).
   - **`CTL.SA.SA-09-05`:** Class D `MUST` enforce explicit U.S. / U.S. Territories / U.S. jurisdiction residency for all Federal Customer Data, processing, and system services.
   - **`VER-TFR-EVU`:** Class D `MUST` enforce a `2-day` vulnerability triage SLA (Class C is `5-day`); **`VER-TFR-NRI`:** Class D `SHOULD` treat non-internet-reachable likely exploitable findings as incidents (Class C `MAY`).
2. **NEVER emit raw Federal prompts, responses, or Federal Customer Data to external telemetry:**
   - All observability, tracing, and logging for `runtime-cso` agents must scrub or redact Federal Customer Data and stay within the authorized `MAS` boundary.
3. **NEVER add unapproved Third-Party Information Resources (TPIRs):**
   - Every external model endpoint, MCP server, tool, or SaaS dependency must be registered with a `MAS-CSO-TPR` entry conforming to [schemas/tpir-register.schema.json](schemas/tpir-register.schema.json) before integration.
4. **NEVER introduce vendor or harness leakage into `agents/` or `skills/`:**
   - Canonical agents and skills must remain 100% vendor-neutral and harness-agnostic (per [docs/adr/003-vendor-neutral-agent-and-eval-shipping.md](docs/adr/003-vendor-neutral-agent-and-eval-shipping.md)). Do not reference proprietary vendor CLI flags, model brand names, or harness-specific directory paths inside [agents/](agents/README.md) or [skills/](skills/README.md).
5. **NEVER invent missing CR-26 Class D `20x` KSI or FRR variants:**
   - In CR-26 `2026.11.02.01`, five KSIs (`KSI-CNA-EIS`, `KSI-MLA-ALA`, `KSI-SVC-PRR`, `KSI-SVC-RUD`, `KSI-SVC-VCM`) and `VDR-TFR-MVX` intentionally omit `varies_by_class.d` (`20x` Class D guidance is pending for 2027). Mark them as not defined in `2026.11.02.01`; never fabricate or copy Class C statements into Class D.

---

## 3. Canonical Agents & Skills

Invoke the canonical agents and skills rather than improvising ad-hoc compliance checks:

- **Canonical Agents** ([agents/README.md](agents/README.md)):
  - [agents/fedramp-compliance-reviewer.md](agents/fedramp-compliance-reviewer.md) — Reviews manifests, architecture, and PRs against CR-26 Class C/D rules.
  - [agents/threat-modeler.md](agents/threat-modeler.md) — Performs CoSAI ADR-030 threat modeling across agentic components, MCP tools, and TPIRs.
  - [agents/change-impact-assessor.md](agents/change-impact-assessor.md) — Classifies changes under `SCN` and drafts [templates/SCN-change-notice.md](templates/SCN-change-notice.md).
  - [agents/evidence-collector.md](agents/evidence-collector.md) — Assembles [schemas/evidence-bundle.schema.json](schemas/evidence-bundle.schema.json) and `SDR` artifacts.
- **Canonical Skills** ([skills/README.md](skills/README.md)):
  - [skills/check-cr26-applicability/SKILL.md](skills/check-cr26-applicability/SKILL.md)
  - [skills/classify-scn-change/SKILL.md](skills/classify-scn-change/SKILL.md)
  - [skills/audit-tpir-boundary/SKILL.md](skills/audit-tpir-boundary/SKILL.md)
  - [skills/map-cosai-controls/SKILL.md](skills/map-cosai-controls/SKILL.md)

---

## 4. Mandatory Pre-PR Verification Commands

Run all of the following zero-dependency Python 3.11+ commands before opening or updating any PR:

```bash
python3 tools/validate_manifest.py templates/agent-manifest.example.class-c.json
python3 tools/validate_manifest.py templates/agent-manifest.example.class-d.json
python3 tools/check_neutrality.py agents skills
python3 tools/audit_agent_repo.py --repo . --manifest templates/agent-manifest.example.class-d.json
python3 tools/generate_compliance_report.py --manifest templates/agent-manifest.example.class-d.json --md-out compliance-report.md --json-out compliance-report.json
python3 -m unittest discover -s tests -v
```

When committing AI-assisted changes, include the vendor-neutral trailer defined in [CONTRIBUTING.md](CONTRIBUTING.md):

```text
Co-authored-by: AI Assistant <ai-assistant@coalitionforsecureai.org>
```
