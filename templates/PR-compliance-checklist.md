# Pull Request Compliance Checklist — FedRAMP Class C & Class D AI Agents

> **Usage:** Copy or auto-populate this checklist into every Pull Request in this repository or any downstream cloned/branched agent repository. All automated gates MUST exit `0` before merge.

## 1. Scope & Change Classification

- [ ] **Agent Manifest Identified:** Target `agent-manifest.json` path(s) declared: `<path>`
- [ ] **FedRAMP Service Class:** `[ ] Class C (Moderate)` | `[ ] Class D (High)`
- [ ] **Certification Track(s):** `[ ] 20x` | `[ ] Rev5`
- [ ] **Agent Profile:** `[ ] runtime-cso` | `[ ] internal-devsecops`
- [ ] **Significant Change Notification (`SCN-CSO-EVA`):** Change classified using `skills/classify-scn-change/SKILL.md` and [templates/SCN-change-notice.md](SCN-change-notice.md):
  - `[ ] Routine / Non-Significant (SCN-RTR-NNR)`
  - `[ ] Adaptive Change Notice Required (SCN-ADP-NTF)`
  - `[ ] Transformative Change — Prior Notice & Verification Required (SCN-TRF-NIP / SCN-TRF-TPR)`
  - `[ ] Emergency Security Change (SCN-CSO-EMG)`

---

## 2. Mandatory Non-Negotiable Invariants (Class C & Class D)

- [ ] **Minimum Assessment Scope (`MAS-CSO-IIR`, `MAS-CSO-MDI`):** If `handles_federal_customer_data` or `handles_sensitive_metadata` is `true`, `fedramp.in_minimum_assessment_scope` is `true`.
- [ ] **Policy Enforcement Points (CoSAI ADR-030):** `model_reachability_pep`, `network_egress_pep`, `authorization_pep`, and `tool_registry_allowlist` are all `true`.
- [ ] **Third-Party Information Resources (`MAS-CSO-TPR`):** Every external service or inference endpoint is declared in `tpirs`. Certified TPIRs include a valid `fedramp_package_id`; non-certified TPIRs include non-empty `mitigations`.
- [ ] **Telemetry Redaction & Audit Separation (`MAS-CSO-MDI`, `KSI-MLA-ALA`, `CTL.AU.AU-09`):** `tamper_evident_audit_repo`, `prompt_response_redacted_from_external_telemetry`, and `audit_control_plane_separated` are `true`.
- [ ] **SSO & Credential Isolation (`CTL.IA.IA-05`, `KSI-IAM-MFA`):** `encrypted_assertions` (`JWE`/`XML-Enc`) and `local_password_bypass_disabled` are `true`; downstream tools use scoped delegated tokens (`controlAgentCredentialIsolation`).
- [ ] **Vendor Neutrality (`CoSAI ADR-033 D2a/D5`):** Zero vendor, product, harness, CLI, or model family identifiers appear anywhere in `agents/**` or `skills/**`; every `skills/*/SKILL.md` frontmatter contains ONLY `name` and `description`; every skill includes `evals/evals.json`.

---

## 3. Class D (High Baseline) Strict Escalation Gates (If `service_class == "D"`)

- [ ] **Mandatory FIPS 140-3 Validated Modules (`CMU-CSO-UVM` Class D `MUST`):** `cryptography.fips_140_3_validated_modules` is `true` and all CMVP certificate IDs are listed in `cryptography.modules`.
- [ ] **High-Assurance Digital Identity (`CTL.IA.IA-05` Class D):** `identity_access.digital_identity_level` is `"IAL3/AAL3/FAL3"`.
- [ ] **Strict U.S. Jurisdiction Residency (`CTL.SA.SA-09-05` Class D):** `model_serving.us_jurisdiction_only` is `true` and `data_classification.residency_boundary` explicitly enforces U.S. / U.S. Territories / U.S. jurisdiction.
- [ ] **Per-Service Certification Artifacts (`CDS-CSO-PSM` Class D `MUST`):** `lifecycle.per_service_certification_artifacts` is `true` and SDR/CPO artifacts are updated.
- [ ] **2-Day Vulnerability Evaluation SLA (`VER-TFR-EVU` Class D):** `lifecycle.vdr_triage_sla_days` is `<= 2` (vs `<= 5` for Class C).
- [ ] **Non-Invention Discipline (`CR-26 2026.11.02.01`):** No fabricated 20x Class D statements for `KSI-CNA-EIS`, `KSI-MLA-ALA`, `KSI-SVC-PRR`, `KSI-SVC-RUD`, `KSI-SVC-VCM`, or `VDR-TFR-MVX`.

---

## 4. Automated Verification Commands (Paste Output / Confirm Exit Code `0`)

```bash
python3 -m unittest discover -s tests -v
python3 tools/validate_manifest.py <path-to-agent-manifest.json>
python3 tools/check_neutrality.py agents skills
python3 tools/audit_agent_repo.py --repo . --manifest <path-to-agent-manifest.json>
```
