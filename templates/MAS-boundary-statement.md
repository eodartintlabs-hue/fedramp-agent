# Minimum Assessment Scope (MAS) Agent Boundary Statement

> **FedRAMP Consolidated Rules 2026 (CR-26) Alignment:** `MAS-CSO-IIR`, `MAS-CSO-FLO`, `MAS-CSO-TPR`, `MAS-CSO-MDI`, `MAS-CSO-SUP`, `CTL.SA.SA-09-05`
> **CoSAI Risk Map Alignment:** ADR-030 Agentic Component Model (`componentApplicationNetworkPolicyEnforcementPoint`, `componentAgentNetworkPolicyEnforcementPoint`, `componentModelServing`, `componentToolNetworkPolicyEnforcementPoint`, `componentAuthorizationPolicyEnforcementPoint`, `componentIsolationRuntime`, `componentAuditRecordRepository`)

## 1. Agent & Cloud Service Offering Identification

| Field | Value |
| :--- | :--- |
| **Agent Identifier (`agent_id`)** | `<e.g., procurement-research-agent-c / mission-incident-response-agent-d>` |
| **Agent Profile (`agent_profile`)** | `<runtime-cso \| internal-devsecops>` |
| **CSO Package ID (`cso_package_id`)** | `<e.g., FR2628650874 / F1603047866>` |
| **FedRAMP Service Class** | `<Class C (Moderate) \| Class D (High)>` |
| **Certification Tracks** | `<20x \| Rev5 \| 20x + Rev5>` |
| **Included in Minimum Assessment Scope** | `true` (Mandatory when handling Federal Customer Data or privileged metadata per `MAS-CSO-IIR` / `MAS-CSO-MDI`) |
| **Residency Boundary** | `<CONUS / U.S. Data Zone \| U.S. / U.S. Territories / U.S. Jurisdiction Only per CTL.SA.SA-09-05>` |

---

## 2. Minimum Assessment Scope Inclusion Analysis (`MAS-CSO-IIR`, `MAS-CSO-MDI`, `MAS-CSO-SUP`)

### 2.1 Information Resources Handling Federal Customer Data (`MAS-CSO-IIR`)
- **Handles Federal Customer Data (`FRD-FCD`):** `<Yes / No>`
- **Data Types Processed:** Prompts, uploaded customer documents, retrieval-augmented generation (`componentRAGContent`) chunks, intermediate reasoning states (`componentReasoningCore`), agent responses, and tool invocation parameters.
- **Boundary Determination:** Every container, memory store (`componentMemory`), vector index, model serving endpoint (`componentModelServing`), and tool server (`componentToolServer`) that stores, processes, or transmits Federal Customer Data is explicitly included within the Minimum Assessment Scope.

### 2.2 Metadata & Telemetry Isolation (`MAS-CSO-MDI`)
- **Handles Sensitive Metadata (`FRD-MTD`):** `<Yes / No>`
- **Prompt/Response Redaction Policy:** `observability.prompt_response_redacted_from_external_telemetry` is enforced as `true`. Raw user prompts, model completions, tool payloads, and agency identifiers are deterministically stripped before any metric or trace leaves the authorization boundary.

### 2.3 Supporting & Internal DevSecOps Resources (`MAS-CSO-SUP`)
- For `internal-devsecops` agents (CI/CD reviewers, compliance auditors, threat modelers, IaC scanners) that can affect the confidentiality, integrity, or availability of the certified CSO, the agent runtime, its credential store, and its execution runners are included as supporting information resources within the assessment boundary.

---

## 3. Policy Enforcement Point (PEP) & Data Flow Inventory (`MAS-CSO-FLO`)

All inbound and outbound data flows across the agent architecture are mediated by dedicated Policy Enforcement Points aligned with CoSAI ADR-030:

| Flow ID | Source Component | Enforcement Point (PEP) | Destination Component | Protocol & Crypto (`CMU-CSO-UVM`) | Residency & Scope Verification |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **FLO-01** | Agency User / Client Application | `componentApplicationNetworkPolicyEnforcementPoint` & `componentApplicationConsentSurface` | Agent Runtime (`componentRuntimeHosting`) | TLS 1.3 (FIPS 140-3 validated module) + OIDC JWE / SAML XML-Enc (`CTL.IA.IA-05`) | In-Boundary |
| **FLO-02** | Agent Orchestration (`componentReasoningCore`) | `componentModelServing` (Model Reachability PEP) | Authorized Model Artifact (`componentTheModel`) | mTLS 1.3 (FIPS 140-3 validated module) | Certified TPIR or In-Boundary U.S. Jurisdiction (`CTL.SA.SA-09-05`) |
| **FLO-03** | Agent Tool Transport (`componentAgentToolTransport`) | `componentAgentNetworkPolicyEnforcementPoint` -> `componentToolNetworkPolicyEnforcementPoint` -> `componentAuthorizationPolicyEnforcementPoint` | Isolated Tool Server (`componentToolServer` inside `componentIsolationRuntime`) | mTLS 1.3 + RFC 8693 audience-scoped token | Allowlisted in `componentToolRegistry` |
| **FLO-04** | Agent & PEPs | Separate Control-Plane Logging Sink | `componentAuditRecordRepository` | mTLS 1.3 + WORM digest-chained storage (`CTL.AU.AU-09`) | Isolated Control Plane |

---

## 4. Third-Party Information Resources (TPIR) Register (`MAS-CSO-TPR`)

Every external service, foundation model endpoint, or supporting SaaS dependency is inventoried below and synchronized with `agent-manifest.json` (`tpirs`) and [CPO-service-addendum.json](CPO-service-addendum.json):

| TPIR Name | Certified (`true`/`false`) | FedRAMP Package ID | Architectural Use Case | Mandatory Mitigations & Compensating Controls (`MAS-CSO-TPR`) |
| :--- | :--- | :--- | :--- | :--- |
| `<e.g., AWS GovCloud (US)>` | `true` | `<e.g., F1603047866>` | Cloud hosting, dedicated GPU inference, KMS/HSM, WORM audit storage | Private VPC endpoints; U.S. jurisdiction enforcement (`CTL.SA.SA-09-05`); active FIPS 140-3 modules (`CMU-CSO-UVM`). |
| `<e.g., CI/CD Build Pipeline>` | `false` | `null` | Out-of-band build and compliance verification | Zero Federal Customer Data/prompts (`MAS-CSO-MDI`); ephemeral in-boundary runners; cryptographic digest pinning. |

---

## 5. Attestation & Sign-Off

- **Responsible Official:** `<Name, Title>`
- **Last Verified Against `agent-manifest.json`:** `<YYYY-MM-DD>`
- **Automated Verification Command:** `python3 tools/audit_agent_repo.py --repo . --manifest agent-manifest.json`
