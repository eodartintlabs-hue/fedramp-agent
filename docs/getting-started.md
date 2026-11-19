# Getting Started: Day-0 to Day-N Onboarding

This guide walks engineering teams through creating a FedRAMP CR-26 compliant AI agent repository from `fedramp-agent` for **Class C** (`20x` & `Rev5`) or **Class D** (`Rev5` + `20x`-ready for 2027).

---

## Day 0: Clone, Branch & Select Your Profile

1. **Clone the enterprise standard and create a working branch:**
   ```bash
   git clone <your-org>/fedramp-agent.git my-team-agent
   cd my-team-agent
   git checkout -b feat/onboard-agent
   ```
2. **Choose your Agent Profile** (see [../specifications.md](../specifications.md)):
   - **`runtime-cso`**: Agent runs inside the FedRAMP CSO authorization boundary and handles Federal Customer Data or in-scope metadata.
   - **`internal-devsecops`**: Internal engineering, platform, CI/CD, or compliance agent operating on CSO repositories/configs without ingesting raw Federal Customer Data.
3. **Copy the matching example manifest to `agent-manifest.json`:**
   - Class C: copy [../templates/agent-manifest.example.class-c.json](../templates/agent-manifest.example.class-c.json)
   - Class D: copy [../templates/agent-manifest.example.class-d.json](../templates/agent-manifest.example.class-d.json)
   - Schema reference: [../schemas/agent-manifest.schema.json](../schemas/agent-manifest.schema.json)

---

## Day 1: Define MAS Boundary & TPIRs

1. **Document your Minimum Assessment Scope (`MAS`):**
   - Fill out [../templates/MAS-boundary-statement.md](../templates/MAS-boundary-statement.md) defining what is inside vs. outside the CSO boundary.
2. **Register every Third-Party Information Resource (`TPIR`):**
   - Any external LLM inference endpoint, MCP server, vector store, or SaaS API must be declared under `MAS-CSO-TPR` in your TPIR register conforming to [../schemas/tpir-register.schema.json](../schemas/tpir-register.schema.json).
   - Run [../skills/audit-tpir-boundary/SKILL.md](../skills/audit-tpir-boundary/SKILL.md) to verify no unapproved TPIRs exist.
   - For `runtime-cso` agents, all inference destinations handling Federal Customer Data must be FedRAMP-certified and boundary-approved.

---

## Day 2: Configure FIPS, Identity/SSO, Residency & PEPs

Apply the exact Class C vs. Class D controls from [../relevant-rulesets.md](../relevant-rulesets.md) and [../templates/SCG-agent-secure-config.md](../templates/SCG-agent-secure-config.md):

| Control Area | Class C Requirement | Class D Requirement |
| :--- | :--- | :--- |
| **Cryptography (`CMU-CSO-UVM`)** | `SHOULD` use active FIPS-validated cryptographic modules | `MUST` use active FIPS-validated cryptographic modules |
| **Certification Docs (`CDS-CSO-PSM`)** | `MAY` supply per-service FedRAMP Certification materials | `MUST` supply per-service FedRAMP Certification materials |
| **Identity / SSO (`CTL.IA.IA-05`)** | `IAL2` / `AAL2` / `FAL2` | `IAL3` / `AAL3` / `FAL3` + encrypted SAML XML-Enc / OIDC JWE assertions |
| **Data Residency (`CTL.SA.SA-09-05`)** | Standard external service controls | Explicit U.S. / U.S. Territories / U.S. jurisdiction residency for all Federal data, processing, and services |
| **Vulnerability Triage (`VER-TFR-EVU` / `NRI`)** | `5-day` triage SLA; `MAY` treat non-internet likely exploitable findings as incidents | `2-day` triage SLA; `SHOULD` treat non-internet likely exploitable findings as incidents |

Configure Policy Enforcement Points (PEPs) per [../specifications.md](../specifications.md) and [../compliance/cosai-crosswalk.json](../compliance/cosai-crosswalk.json):
- Scrub Federal Customer Data from all external telemetry and logs.
- Enforce tool-call allowlists and least-privilege MCP scopes.
- Align vulnerability tracking with [../templates/VDR-vulnerability-profile.md](../templates/VDR-vulnerability-profile.md) (CISA BOD 26-04 effective `2026-12-07`) and incident escalation with [../templates/IEC-incident-runbook.md](../templates/IEC-incident-runbook.md).

---

## Day 3: Add Portable Evals & Validate Locally

1. **Keep evals and canonical specs vendor-neutral:**
   - Follow [adr/003-vendor-neutral-agent-and-eval-shipping.md](adr/003-vendor-neutral-agent-and-eval-shipping.md) so behavioral evals run portably across models and harnesses.
2. **Run all zero-dependency Python 3.11+ compliance gates:**
   ```bash
   python3 tools/validate_manifest.py templates/agent-manifest.example.class-c.json
   python3 tools/validate_manifest.py templates/agent-manifest.example.class-d.json
   python3 tools/check_neutrality.py agents skills
   python3 tools/audit_agent_repo.py --repo . --manifest templates/agent-manifest.example.class-d.json
   python3 -m unittest discover -s tests -v
   ```
   *(Replace `templates/agent-manifest.example.class-d.json` with your team's `agent-manifest.json` once customized.)*

---

## Day-N: Generate Dual SDR/Compliance Reports & Ship

1. **Generate human + machine-readable compliance reports:**
   ```bash
   python3 tools/generate_compliance_report.py --manifest templates/agent-manifest.example.class-d.json --md-out compliance-report.md --json-out compliance-report.json
   ```
2. **Update SDR & CPO artifacts:**
   - Populate [../templates/SDR-agent-record.md](../templates/SDR-agent-record.md) (schema: [../schemas/sdr-agent-addendum.schema.json](../schemas/sdr-agent-addendum.schema.json)) and [../templates/CPO-service-addendum.json](../templates/CPO-service-addendum.json).
3. **Open a PR with SCN classification:**
   - Complete [../templates/PR-compliance-checklist.md](../templates/PR-compliance-checklist.md), classify changes with [../skills/classify-scn-change/SKILL.md](../skills/classify-scn-change/SKILL.md), and include the neutral `Co-authored-by: AI Assistant <ai-assistant@coalitionforsecureai.org>` trailer per [../CONTRIBUTING.md](../CONTRIBUTING.md).
