---
name: audit-tpir-boundary
description: "Audit Third-Party Information Resources (TPIRs), external model-inference endpoints, vector databases, MCP tool servers, observability sinks, and CI/CD pipelines against FedRAMP CR-26 MAS-CSO-TPR, MAS-CSO-MDI, and Class D CTL.SA.SA-09-05 U.S.-jurisdiction rules."
---

# Audit TPIR Boundary

Use this skill to verify every Third-Party Information Resource (`FRD-TPR` — any information resource not entirely included inside the Cloud Service Offering's own Minimum Assessment Scope `FRD-MAS`) leveraged by an AI agent.

Consult `specifications.md` (Section 3.1, 3.4, 3.6), `schemas/tpir-register.schema.json`, and `compliance/marketplace-class-cd-analysis.md` when reviewing real or proposed `TPIR` inventories.

## Audit Checklist (`MAS-CSO-TPR`, `MAS-CSO-MDI`, `CTL.SA.SA-09-05`)

Apply all six checks to `model_serving`, `observability`, and every item in `tpirs[]` (or `thirdPartyInformationResources` in `schemas/tpir-register.schema.json`):

1. **Completeness of `MAS-CSO-TPR` Documentation (`MUST`):**
   - When `MAS-CSO-IIR` applies (`in_minimum_assessment_scope: true`), every external cloud platform, managed inference API, hosted vector index, remote `MCP` server, external telemetry collector, or out-of-boundary CI/CD runner **MUST** document:
     - General usage and configuration
     - Explanation or justification for use
     - Mitigation measures reducing potential impact to `Federal Customer Data` (`FRD-FCD`)
     - Compensating controls reducing potential impact to `FRD-FCD`

2. **Certified vs. Non-Certified Structural Integrity:**
   - If `certified == true`, a valid non-empty FedRAMP Marketplace Package ID (`fedramp_package_id` / `fedRampCertifiedThirdPartyInformationResource`) **MUST** be supplied, and the inherited service/feature/region **MUST** actually fall inside that package's authorized scope (never claim parent cloud authorization for a separate uncertified SaaS offering).
   - If `certified == false`, `fedramp_package_id` **MUST** be `null` and `mitigations` / `compensatingControls` **MUST** be non-empty.

3. **Inference Destination Gate (`componentModelServing` / `ADR-030 D11/D12`):**
   - `model_serving.model_reachability_pep` **MUST** be `true`.
   - External inference endpoints processing unredacted `FRD-FCD` **MUST** be FedRAMP Certified (`certified: true`) at an assurance level commensurate with the CSO's class (Class C Moderate or Class D High), configured with **zero data retention** and **zero model training** on customer prompts/completions.
   - Self-hosted inference running entirely inside the CSO's own `MAS` sets `fedramp_certified_tpir_id: null` (or cites the inherited certified IaaS/PaaS package ID hosting the compute).

4. **Class D U.S.-Jurisdiction Sovereignty Gate (`CTL.SA.SA-09-05`):**
   - For `service_class == "D"` handling `FRD-FCD`, **every** `TPIR` that stores, processes, caches, embeds, or routes `FRD-FCD` or provides system services **MUST** operate exclusively within **U.S. / U.S. Territories / geographic locations under U.S. jurisdiction** (`model_serving.us_jurisdiction_only: true`).
   - Flag any global load-balanced inference endpoint, cross-border failover route, or offshore support plane on Class D as a **blocking violation**.

5. **External Telemetry & Observability Redaction Gate (`MAS-CSO-MDI`):**
   - Whenever any external observability/APM `TPIR` is used or `FRD-FCD` is handled, `observability.prompt_response_redacted_from_external_telemetry` **MUST** be `true`.
   - Non-certified observability `TPIRs` may receive only scrubbed operational metrics (`FRD-DTM`—latency, token counts, status codes), never raw prompts, completions, RAG documents, secrets, or unmitigated vulnerability details (`VER-RPT-NID`).

6. **Out-of-Band CI/CD & Supporting Pipeline Gate (`MAS-CSO-IIR`, `KSI-SCR-MIT`):**
   - Non-certified build/CI `TPIRs` **MUST NOT** ingest production `FRD-FCD`, **SHOULD** execute builds on ephemeral runners inside the boundary with federated short-lived credentials (`KSI-IAM-SNU`), and **MUST** enforce cryptographic artifact signing and digest pinning (`CTL.CM.CM-14`, `CTL.SR.SR-03`).

## Output Format

- **Per-TPIR Verdict:** `PASS`, `BLOCKING`, or `NEEDS_REMEDIATION` with exact `FRR`/`KSI`/`CTL` rule citations.
- **Boundary Summary:** Overall `TPIR` posture and required manifest/register updates.
