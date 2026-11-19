# Secure Configuration Guide (SCG) — AI Agent Service

> **FedRAMP Consolidated Rules 2026 (CR-26) Alignment:** `SCG-CSO-RSC`, `SCG-CSO-AUP`, `SCG-CSO-PUB`, `SCG-CSO-SDF`, `SCG-ENH-CMP`, `SCG-ENH-EXP`, `SCG-ENH-API`, `SCG-ENH-MRG`, `SCG-ENH-VRH`
> **CoSAI Risk Map Alignment:** `controlSecureByDefaultMLTooling`, `controlAgentPluginUserControl`, `controlAgentPluginPermissions`, `controlAgentExecutionBounds`

## 1. Purpose & Audience (`SCG-CSO-RSC`, `SCG-CSO-PUB`)

This Secure Configuration Guide provides federal agency administrators, Authorizing Officials (AOs), and platform engineering teams with the mandatory secure-by-default baseline settings, customer-configurable policy dials, and privileged access guardrails for operating the AI agent service within a FedRAMP Class C or Class D Cloud Service Offering.

---

## 2. Secure-by-Default Baseline Configuration (`SCG-CSO-SDF`, `SCG-ENH-CMP`)

Upon tenant provisioning, the following settings are enforced by default and verified by `tools/validate_manifest.py`:

| Configuration Control | Default Value | CR-26 Rule / KSI / CTL ID | CoSAI Component / Control | Security Guarantee |
| :--- | :--- | :--- | :--- | :--- |
| **Federated SSO Enforcement** | Enabled (`OIDC` / `SAML`) | `CTL.IA.IA-05`, `KSI-IAM-SFA` | `componentIdentityProvider` | Disables local password authentication (`local_password_bypass_disabled: true`). |
| **Digital Identity Assurance** | Class C: `IAL2/AAL2/FAL2`<br>Class D: `IAL3/AAL3/FAL3` | `CTL.IA.IA-05`, `KSI-IAM-MFA` | `controlComponentIdentityProvenance` | Rejects authentication assertions below the service class assurance threshold. |
| **Encrypted Identity Assertions** | `true` (`JWE` / `XML-Enc`) | `CTL.IA.IA-05` | `controlInterComponentTransportSecurity` | Prevents token inspection or tampering at federation proxies. |
| **Model Reachability PEP** | `true` (Default-Deny Egress) | `MAS-CSO-TPR`, `CTL.SA.SA-09-05` | `componentModelServing`, `controlOrchestratorAndRouteIntegrity` | Restricts inference calls exclusively to allowlisted FedRAMP-authorized U.S. endpoints. |
| **Tool Registry Allowlist** | `true` (Strict Pinning) | `SCG-CSO-SDF`, `KSI-CNA-EIS` | `componentToolRegistry`, `controlToolRegistryAndDiscoveryIntegrity` | Blocks unapproved MCP servers, dynamic plugins, or unverified tool binaries. |
| **Dual Consent Surfaces** | `true` (Mandatory Approval) | `SCG-CSO-AUP` | `componentApplicationConsentSurface`, `componentAgentConsentSurface` | Requires explicit human confirmation before high-impact or external write actions. |
| **External Telemetry Redaction** | `true` (Deterministic Scrub) | `MAS-CSO-MDI` | `controlRuntimePrivacyEnhancingTechnologies` | Strips prompts, completions, and Federal Customer Data from external telemetry sinks. |
| **Control-Plane Audit Separation** | `true` (WORM Retention) | `KSI-MLA-ALA`, `CTL.AU.AU-09` | `componentAuditRecordRepository`, `controlAgentObservability` | Stores signed audit records in a control plane isolated from the agent runtime. |

---

## 3. Agency Customer Responsibilities & Configurable Policy Controls (`SCG-CSO-AUP`, `SCG-ENH-API`)

Agency administrators MUST configure and review the following tenant controls during onboarding and quarterly access reviews:

1. **Identity Provider (IdP) Binding (`CTL.IA.IA-05`):**
   - Configure agency OIDC or SAML federation with encrypted assertions enabled.
   - Map agency role claims to least-privilege agent execution scopes (`read-only-research`, `operator-with-consent`, `tenant-security-auditor`).
2. **Allowed Tool Inventory (`tool_boundaries.allowed_tools`):**
   - Review and restrict the tenant's active tool allowlist to only those tools required for the agency mission.
   - Verify that any agency-connected data source tool operates through `componentToolNetworkPolicyEnforcementPoint` over FIPS 140-3 validated TLS 1.3 (`CMU-CSO-UVM`).
3. **Agent Execution Bounds (`controlAgentExecutionBounds`):**
   - Set per-session token budgets, maximum tool recursion depth (recommended `<= 10` steps), and per-tool execution timeout (`<= 30s`).
4. **Export & Data Loss Prevention Policies (`SCG-ENH-EXP`):**
   - Enable tenant boundary watermarks and restrict cross-workspace share links to authenticated agency principals.

---

## 4. Machine-Readable Configuration Verification (`SCG-ENH-MRG`, `SCG-ENH-VRH`)

Every configuration change is version-controlled in `agent-manifest.json` and continuously validated against [schemas/agent-manifest.schema.json](../schemas/agent-manifest.schema.json):

```bash
python3 tools/validate_manifest.py agent-manifest.json
python3 tools/audit_agent_repo.py --repo . --manifest agent-manifest.json --strict
```
