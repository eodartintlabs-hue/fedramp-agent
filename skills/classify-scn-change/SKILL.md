---
name: classify-scn-change
description: "Classify proposed AI agent code, model, prompt, tool-allowlist, cryptographic, identity, or Third-Party Information Resource (TPIR) changes under FedRAMP CR-26 Significant Change Notification (SCN) rules and calculate mandatory pre- and post-change notification timelines."
---

# Classify SCN Change

Use this skill to execute `SCN-CSO-EVA` (*Evaluate Changes*) for any proposed modification to an in-scope FedRAMP Class C or Class D AI agent, map the change to the canonical `schemas/scn-record.schema.json` taxonomy, and determine exact notification obligations.

Consult `relevant-rulesets.md`, `schemas/scn-record.schema.json`, and `templates/SCN-change-notice.md` when assembling notices.

## Decision Tree (`SCN-CSO-EVA`)

Evaluate the proposed change against the five canonical classifications in priority order:

### 1. `emergency-change` (`SCN-CSO-EMG`)
- **Trigger:** Urgent action executed during an active security incident, `PAIN=5` / Known Exploited Vulnerability (`FRD-KEV`) emergency, or live containment/kill-switch event where delaying for standard `SCN` timelines would jeopardize `Federal Customer Data` (`FRD-FCD`).
- **Obligations:** `MAY` execute immediately (including transformative actions) without advance notice (`SCN-CSO-EMG`); **MUST** record audit evidence (`SCN-CSO-MAR`), complete post-change vulnerability detection (`VDR-CSO-DAC`), and issue post-change `SCN` / `IEC` notifications promptly.

### 2. `transformative-tpir-addition` (`FRD-TRF`, `MAS-CSO-TPR`, `SCN-TRF-*`)
- **Trigger:** Onboarding a net-new Third-Party Information Resource (`tpirs[]` addition or switching `model_serving.fedramp_certified_tpir_id` to a new external provider, external `MCP` server, hosted vector database, or external observability sink) that handles or can impact `FRD-FCD`.
- **Pre-Check:** Verify the new `TPIR` does not violate Class D U.S.-jurisdiction residency (`CTL.SA.SA-09-05`) or route unredacted `FRD-FCD` to an uncertified service (`MAS-CSO-TPR`); if it does, flag **illegal/non-compliant change** before scheduling notices.
- **Obligations:**
  - **`>= 30` business days prior:** Notify all necessary parties (`FRD-ANP`) of initial plans (`SCN-TRF-NIP`).
  - **Assessor Review:** **SHOULD** engage a FedRAMP-recognized assessor prior to starting if human validation is needed (`SCN-TRF-TPR`).
  - **`>= 10` business days prior:** Notify all necessary parties of final plans (`SCN-TRF-NFP`).
  - **`<= 5` business days after finishing:** Send completion notice (`SCN-TRF-NAF`).
  - **`<= 5` business days after verification/validation:** Send verification notice (`SCN-TRF-NAV`).
  - **`<= 30` business days after finishing:** Publish updated certification/service documentation (`SCN-TRF-UPD`).

### 3. `transformative-prior-notice` (`FRD-TRF`, `SCN-TRF-*`)
- **Trigger:** Any non-emergency change (without adding a new `TPIR`) that introduces substantive potential security risks likely to alter existing risk determinations (`FRD-TRF`), including:
  - Removing, bypassing, or re-architecting any `ADR-030` Policy Enforcement Point (`model_reachability_pep`, `network_egress_pep`, `authorization_pep`) or `componentIsolationRuntime`.
  - Replacing cryptographic modules or altering `fips_140_3_validated_modules` (`alters_cryptographic_modules: true`).
  - Changing `digital_identity_level`, `sso_protocol`, or `delegation_model` token-scoping rules.
  - Expanding `allowed_tools` from read-only retrieval to autonomous external write/mutation capabilities (`alters_tool_egress_boundary: true`), or expanding Minimum Assessment Scope (`affects_minimum_assessment_scope: true`).
  - Upgrading or downgrading the offering's FedRAMP Certification Class (`FRD-CCC`, `FRC-CCL-UCC`, `FRC-CCL-DCC`).
- **Obligations:** Identical `TRF` timeline (`30` business days initial `SCN-TRF-NIP`, `10` business days final `SCN-TRF-NFP`, `SCN-TRF-TPR`, `5` business days finish `SCN-TRF-NAF`, `5` business days verification `SCN-TRF-NAV`, `30` business days doc update `SCN-TRF-UPD`).

### 4. `adaptive-change-notice` (`FRD-ADP`, `SCN-ADP-NTF`)
- **Trigger:** A non-recurring significant change that does **not** introduce substantive new security risks requiring deep re-assessment (`FRD-ADP`), such as:
  - Adding an in-boundary, read-only tool already governed by existing `Authorization PEP`, `Tool Registry` allowlisting, and `Isolation Runtime`.
  - Upgrading to a newer minor model checkpoint from the **same** already-authorized `TPIR` within the same residency boundary after passing portable evals and re-binding workload identity (`controlAgentIntegrityManagement`).
  - Refining system instructions or RAG chunking parameters that alter functional scope without weakening security boundaries.
- **Obligations:**
  - **Within `10` business days after finishing:** Notify all necessary parties (`SCN-ADP-NTF`) with required `SCN-CSO-INF` content in both human-readable and JSON formats (`SCN-CSO-HRM`).
  - Maintain evaluation audit record (`SCN-CSO-MAR`) and `12` months of historical notices (`SCN-CSO-HIS`), and run post-change vulnerability detection (`VDR-CSO-DAC`).

### 5. `routine-non-significant` (`FRD-RTR`, `SCN-RTR-NNR`)
- **Trigger:** Regularly recurring operational maintenance, vulnerability patching/remediation, container base-image rebuilds, routine key/certificate rotation within the already-documented CMVP module, or adding test/evaluation cases (`portable_eval_paths`).
- **Obligations:**
  - Providers **SHOULD NOT** issue formal Significant Change Notifications (`SCN-RTR-NNR` — exempted from notification).
  - Providers **MUST** still record the `SCN-CSO-EVA` evaluation in internal audit records (`SCN-CSO-MAR`) and run post-change detection (`VDR-CSO-DAC`).

## Universal Format Rules (`SCN-CSO-INF`, `SCN-CSO-HRM`, `SCN-CSO-HIS`)

- Every formal notice and audit record **MUST** exist in synchronized human-readable and JSON (`schemas/scn-record.schema.json`) formats (`SCN-CSO-HRM`).
- Retain **`12` months** of historical notifications with FedRAMP Certification Data (`SCN-CSO-HIS`).

## Output Format

1. **`change_classification`:** Exact enum string from `schemas/scn-record.schema.json`.
2. **`cr26_scn_rules_triggered`:** Exact list of `SCN-XXX-XXX` rule IDs.
3. **`impact_assessment` flags:** Boolean values for `affects_minimum_assessment_scope`, `introduces_new_tpir`, `alters_cryptographic_modules`, and `alters_tool_egress_boundary`.
4. **Notification Schedule & Compliance Blockers:** Concrete business-day milestones (or exemption note) plus any Class C/D compliance blockers detected.
