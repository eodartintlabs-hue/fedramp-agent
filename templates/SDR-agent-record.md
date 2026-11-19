# Security Decision Record (SDR) — AI Agent Addendum

> **FedRAMP Consolidated Rules 2026 (CR-26) Alignment:** `SDR-CSO-FRR`, `SDR-CSO-MTD`, `SDR-CSX-KSI`, `SDR-CSX-KMT`, `SDR-CSF-CTF`, `CMU-CSO-CMD`, `CMU-CSO-UVM`, `CDS-CSO-PSM`
> **Machine-Readable Companion Schema:** [schemas/sdr-agent-addendum.schema.json](../schemas/sdr-agent-addendum.schema.json)

## 1. Record Metadata (`SDR-CSO-MTD`)

| Metadata Attribute | Value |
| :--- | :--- |
| **SDR Identifier (`sdr_id`)** | `SDR-AGENT-2026-001` |
| **CSO Package ID (`cso_package_id`)** | `<e.g., FR2628650874 / F1603047866>` |
| **Agent Identifier (`agent_id`)** | `<e.g., procurement-research-agent-c / mission-incident-response-agent-d>` |
| **FedRAMP Service Class** | `<Class C \| Class D>` |
| **Certification Tracks** | `<20x \| Rev5 \| 20x + Rev5>` |
| **Approving Official** | `<Name, Title, Email>` |
| **Recorded Timestamp** | `<YYYY-MM-DDTHH:MM:SSZ>` |

---

## 2. Summary of Key Class C vs. Class D Architectural Decisions (`SDR-CSO-FRR`)

### Decision SDR-01: Cryptographic Module Selection & Validation (`CMU-CSO-CMD`, `CMU-CSO-UVM`)
- **Rule Requirement:**
  - **Class C:** `CMU-CSO-UVM` has RFC-2119 force `SHOULD` (use active FIPS-validated cryptographic modules; if an unvalidated module is used, the provider MUST document the rationale and compensating controls in the SDR).
  - **Class D:** `CMU-CSO-UVM` has RFC-2119 force `MUST` (strictly mandatory active FIPS-validated cryptographic modules across all transport, storage, token encryption, and inference paths).
- **Agent Implementation Decision:**
  - `cryptography.fips_140_3_validated_modules`: `<true / false>`
  - Inventoried CMVP Modules: `<List module names and CMVP certificate IDs from agent-manifest.json>`
  - **Rationale & Compensating Controls (Required if Class C uses any non-validated module):** `<Document rationale here; N/A when fips_140_3_validated_modules is true>`

### Decision SDR-02: Digital Identity Assurance & Encrypted Assertions (`CTL.IA.IA-05`, `KSI-IAM-MFA`)
- **Rule Requirement:**
  - **Class C:** Minimum `IAL2/AAL2/FAL2` with encrypted SAML (`XML-Enc`) or OIDC (`JWE`) assertions and local password bypass disabled.
  - **Class D:** Mandatory `IAL3/AAL3/FAL3` with hardware-backed phishing-resistant authentication, encrypted assertions, and short-lived delegated capability tokens.
- **Agent Implementation Decision:**
  - Enforced Level: `<IAL2/AAL2/FAL2 \| IAL3/AAL3/FAL3>` via `<OIDC \| SAML>` with `encrypted_assertions: true` and `local_password_bypass_disabled: true`.
  - Confused-Deputy Prevention (`controlAgentCredentialIsolation`): Agent never forwards caller root bearer tokens to downstream tools; `componentAuthorizationPolicyDecisionPoint` issues RFC 8693 audience-restricted tokens per tool call.

### Decision SDR-03: Inference & Data Residency Boundary (`CTL.SA.SA-09-05`, `MAS-CSO-TPR`)
- **Rule Requirement:**
  - **Class D (`CTL.SA.SA-09-05`):** All Federal Customer Data, inference processing, model weights, prompt caches, and system services MUST remain exclusively within the United States, U.S. Territories, or under U.S. jurisdiction.
- **Agent Implementation Decision:**
  - `model_serving.us_jurisdiction_only`: `true`
  - `data_classification.residency_boundary`: `<Specify sovereign region / U.S. Data Zone>`
  - Enforced by `componentModelServing` (Model Reachability PEP) preventing routing to global or multi-jurisdiction inference endpoints.

### Decision SDR-04: Tool & MCP Execution Isolation (`KSI-CNA-EIS`, `KSI-SVC-PRR`, CoSAI ADR-030)
- **Rule Requirement:** Isolate untrusted or third-party tool execution and prevent unauthorized lateral movement or arbitrary egress.
- **Agent Implementation Decision:**
  - All tools execute inside `componentIsolationRuntime` (`third_party_tool_isolation: true`).
  - Dual Policy Enforcement Points (`componentToolNetworkPolicyEnforcementPoint` and `componentAuthorizationPolicyEnforcementPoint`) enforce default-deny egress and per-tool capability checks against `componentToolRegistry` (`tool_registry_allowlist: true`).
  - Dual consent surfaces (`componentApplicationConsentSurface` and `componentAgentConsentSurface`) require explicit user authorization before state-mutating tool actions.

### Decision SDR-05: Per-Service Certification Package Materials (`CDS-CSO-PSM`)
- **Rule Requirement:**
  - **Class C:** `MAY` provide per-service certification materials.
  - **Class D:** `MUST` maintain and supply per-service FedRAMP Certification materials (`lifecycle.per_service_certification_artifacts: true`).
- **Agent Implementation Decision:** Maintained via automated generation of per-agent SDR addenda, manifest validation artifacts, and evidence bundles (`tools/generate_compliance_report.py`).

---

## 3. 20x Key Security Indicator (KSI) & Rev5 Control Mitigation Ledger (`SDR-CSX-KSI`, `SDR-CSX-KMT`, `SDR-CSF-CTF`)

> **Regulatory Non-Invention Note (CR-26 `2026.11.02.01`):** In dataset version `2026.11.02.01`, five 20x KSIs (`KSI-CNA-EIS`, `KSI-MLA-ALA`, `KSI-SVC-PRR`, `KSI-SVC-RUD`, `KSI-SVC-VCM`) and `VDR-TFR-MVX` do not define `varies_by_class.d` statements because FedRAMP 20x Class D is scheduled for 2027. For Class D agents tracking 20x readiness alongside Rev5, those five indicators are tracked against their Rev5 NIST SP 800-53 High Baseline control mappings without inventing unauthorized 20x Class D rule text.

| Decision ID | CR-26 Rule / KSI / CTL IDs | CoSAI Control IDs | Implementation & Evidence Reference | Residual Risk | Review Date |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `SDR-DEC-001` | `MAS-CSO-IIR`, `MAS-CSO-TPR`, `CTL.SA.SA-09-05` | `controlOrchestratorAndRouteIntegrity`, `controlAgentInventoryManagement` | `agent-manifest.json` (`fedramp`, `model_serving`, `tpirs`) | Low | `2027-06-01` |
| `SDR-DEC-002` | `CMU-CSO-CMD`, `CMU-CSO-UVM`, `KSI-SVC-PRR` | `controlInterComponentTransportSecurity` | `agent-manifest.json` (`cryptography.modules`) | Low | `2027-06-01` |
| `SDR-DEC-003` | `CTL.IA.IA-05`, `KSI-IAM-MFA`, `KSI-IAM-SFA` | `controlAgentCredentialIsolation`, `controlComponentIdentityProvenance` | `agent-manifest.json` (`identity_access`) | Low | `2027-06-01` |
| `SDR-DEC-004` | `KSI-MLA-ALA`, `MAS-CSO-MDI`, `CTL.AU.AU-09` | `controlAgentObservability`, `controlRuntimePrivacyEnhancingTechnologies` | `agent-manifest.json` (`observability`) | Low | `2027-06-01` |
| `SDR-DEC-005` | `VER-TFR-EVU`, `VDR-CSO-DET`, `IEC-CSO-IIR` | `controlVulnerabilityManagement`, `controlIncidentResponseManagement` | `agent-manifest.json` (`lifecycle.vdr_triage_sla_days`) | Low | `2027-06-01` |
