# Incident Communications & Containment Runbook (IEC) — AI Agent Service

> **FedRAMP Consolidated Rules 2026 (CR-26) Alignment:** `IEC-CSO-EFR`, `IEC-CSO-DPR`, `IEC-CSO-IIR`, `IEC-CSO-OIR`, `IEC-CSO-FIR`, `IEC-CSO-EFI`, `IEC-CSO-AIR`, `VER-TFR-IRI`, `VER-TFR-NRI`
> **CoSAI Risk Map Alignment:** `controlIncidentResponseManagement`, `controlThreatDetection`, `controlAgentObservability`, `controlAgentExecutionBounds`

## 1. Purpose & Activation Triggers (`IEC-CSO-EFR`, `IEC-CSO-DPR`)

This runbook governs incident detection, deterministic containment (kill-switch execution), forensic preservation, and formal notification to FedRAMP and affected agency customers whenever a security incident or reportable vulnerability escalation occurs within an in-scope AI agent service.

### Mandatory Activation Triggers
1. **Direct Security Breach or Unauthorized Disclosure (`IEC-CSO-IIR`):** Confirmed or suspected unauthorized access to Federal Customer Data (`FRD-FCD`), sensitive metadata (`FRD-MTD`), model weights, or tenant credentials.
2. **Agentic Control-Plane or Boundary Compromise:**
   - Bypass of `componentApplicationNetworkPolicyEnforcementPoint`, `componentAgentNetworkPolicyEnforcementPoint`, `componentModelServing`, `componentToolNetworkPolicyEnforcementPoint`, or `componentAuthorizationPolicyEnforcementPoint`.
   - Unauthorized tool execution outside `tool_boundaries.allowed_tools` or sandbox escape from `componentIsolationRuntime`.
   - Cross-tenant data leakage via shared memory (`componentMemory`), vector store poisoning (`componentRAGContent`), or unredacted external telemetry emission (`MAS-CSO-MDI` violation).
3. **Vulnerability Escalation Triggers (`VER-TFR-IRI`, `VER-TFR-NRI`):**
   - **Class C & Class D (`VER-TFR-IRI` — `MUST`):** Discovery of any Likely Exploitable (`FRD-LEX`), internet-reachable vulnerability affecting the agent or its Minimum Assessment Scope components.
   - **Class D (`VER-TFR-NRI` — `SHOULD`) & Class C (`MAY`):** Discovery of a Likely Exploitable non-internet-reachable vulnerability inside the agent boundary.

---

## 2. Immediate Containment & Agent Kill-Switch Procedures (0–15 Minutes)

When an activation trigger fires, the On-Call Incident Commander executes the following deterministic containment sequence:

1. **Engage Agent Egress & Tool Kill-Switch (`controlAgentExecutionBounds`):**
   - Set `tool_boundaries.allowed_tools` to `[]` (empty allowlist) at `componentAuthorizationPolicyEnforcementPoint` to halt all tool invocations immediately.
   - Block outbound network egress at `componentAgentNetworkPolicyEnforcementPoint` and `componentToolNetworkPolicyEnforcementPoint`.
2. **Revoke Active Delegated Tokens (`controlAgentCredentialIsolation`):**
   - Revoke all active RFC 8693 on-behalf-of tokens and rotate signing keys at `componentAuthorizationPolicyDecisionPoint`.
3. **Isolate Model Serving & Memory Stores (`componentModelServing`, `componentMemory`):**
   - Quarantine affected tenant conversation states and vector indices (`componentRAGContent`) to prevent secondary prompt-injection propagation.
4. **Preserve Tamper-Evident Forensics (`componentAuditRecordRepository`, `CTL.AU.AU-09`):**
   - Snapshot the immutable control-plane audit logs, container memory state, and Policy Enforcement Point decision traces. Verify WORM retention locks.

---

## 3. FedRAMP & Agency Notification Workflow (`IEC-CSO-IIR`, `IEC-CSO-OIR`, `IEC-CSO-FIR`)

All notifications are transmitted via `lifecycle.iec_incident_channel` (as declared in `agent-manifest.json` and [CPO-service-addendum.json](CPO-service-addendum.json)):

| Report Stage | CR-26 Rule ID | Recipient Population | Required Contents |
| :--- | :--- | :--- | :--- |
| **Initial Incident Report (IIR)** | `IEC-CSO-IIR` | `fedramp_security@fedramp.gov`, affected agency security contacts, and controlled Trust Center feed | Incident ID, CSO Package ID, affected `agent_id`, service class (`C` or `D`), activation trigger (`IEC` or `VER-TFR-IRI`/`NRI`), initial PAIN rating, affected data categories, and active containment status. |
| **Ongoing Incident Report (OIR)** | `IEC-CSO-OIR` | All necessary parties via controlled distribution channel | Updated forensic findings, blast-radius verification across CoSAI components, remediation progress, and updated indicator-of-compromise (IoC) feeds. |
| **Final Incident Report (FIR)** | `IEC-CSO-FIR` | All necessary parties via controlled distribution channel | Root-cause analysis, complete timeline, verification of eradication, new regression tests added to `lifecycle.portable_eval_paths`, and resulting `SDR` / `SCN` updates. |

---

## 4. Post-Incident Compliance Verification Gate

Before re-enabling the agent or restoring `tool_boundaries.allowed_tools` in production:

1. Add a regression evaluation fixture reproducing the incident vector under `lifecycle.portable_eval_paths` (CoSAI ADR-033 D6/D7).
2. Re-run the full repository compliance gate:
   ```bash
   python3 tools/validate_manifest.py agent-manifest.json
   python3 tools/check_neutrality.py agents skills
   python3 tools/audit_agent_repo.py --repo . --manifest agent-manifest.json --strict
   ```
3. Record any architectural or cryptographic changes in [SDR-agent-record.md](SDR-agent-record.md) and classify under [SCN-change-notice.md](SCN-change-notice.md).
