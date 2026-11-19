# Significant Change Notification (SCN) — AI Agent Change Record

> **FedRAMP Consolidated Rules 2026 (CR-26) Alignment:** `SCN-CSO-EVA`, `SCN-CSO-MAR`, `SCN-CSO-INF`, `SCN-CSO-HIS`, `SCN-CSO-HRM`, `SCN-CSO-ARI`, `SCN-CSO-NOM`, `SCN-CSO-EMG`, `SCN-ADP-NTF`, `SCN-RTR-NNR`, `SCN-TRF-NIP`, `SCN-TRF-NFP`, `SCN-TRF-NAF`, `SCN-TRF-NAV`, `SCN-TRF-UPD`, `SCN-TRF-TPR`
> **Machine-Readable Companion Schema:** [schemas/scn-record.schema.json](../schemas/scn-record.schema.json)
> **Canonical Assessment Skill:** `skills/classify-scn-change/SKILL.md`

## 1. Change Identification & Classification (`SCN-CSO-EVA`, `SCN-CSO-MAR`)

| Field | Value |
| :--- | :--- |
| **SCN Record ID (`scn_id`)** | `SCN-2026-001` |
| **CSO Package ID (`cso_package_id`)** | `<e.g., FR2628650874 / F1603047866>` |
| **Agent Identifier (`agent_id`)** | `<e.g., procurement-research-agent-c / mission-incident-response-agent-d>` |
| **FedRAMP Service Class** | `<Class C \| Class D>` |
| **Change Title** | `<Brief descriptive title of the agent change>` |
| **SCN Classification** | `<routine-non-significant \| adaptive-change-notice \| transformative-prior-notice \| transformative-tpir-addition \| emergency-change>` |
| **CR-26 SCN Rules Triggered** | `<e.g., SCN-CSO-EVA, SCN-ADP-NTF or SCN-TRF-TPR>` |
| **Planned Effective Date** | `<YYYY-MM-DD>` |

---

## 2. Agent Change Classification Decision Matrix (`SCN-RTR`, `SCN-ADP`, `SCN-TRF`, `SCN-CSO-EMG`)

Use this matrix before merging any pull request affecting `agent-manifest.json`, model serving, tool registries, or Policy Enforcement Points:

| Agent Change Scenario | CR-26 SCN Tier | Applicable Rule IDs | Required Action Before Deployment |
| :--- | :--- | :--- | :--- |
| Prompt template refinement, UI copy update, or evaluation fixture expansion with no boundary, tool, model, or crypto change | **Routine / Non-Significant** | `SCN-CSO-EVA`, `SCN-RTR-NNR` | Log in version control history; no external SCN notice required. |
| Adding a new read-only tool within an existing isolated container, minor model version bump within the same certified TPIR & U.S. Data Zone, or updating internal guardrail thresholds | **Adaptive Change** | `SCN-CSO-EVA`, `SCN-ADP-NTF`, `SCN-CSO-HIS` | Record in SDR & publish Adaptive Change Notice via `lifecycle.scn_change_channel`. |
| Onboarding a new Third-Party Information Resource (TPIR) for inference, vector storage, or MCP tool execution | **Transformative Change (TPIR)** | `SCN-TRF-TPR`, `SCN-TRF-NIP`, `MAS-CSO-TPR` | Prior notification to FedRAMP and necessary parties; assessor verification (`SCN-TRF-NAV`); update CPO & TPIR Register before production cutover. |
| Replacing FIPS 140-3 cryptographic modules, altering SSO assertion encryption (`CTL.IA.IA-05`), changing data residency boundary (`CTL.SA.SA-09-05`), or removing a Policy Enforcement Point | **Transformative Change** | `SCN-TRF-NIP`, `SCN-TRF-NFP`, `SCN-TRF-NAF`, `SCN-TRF-NAV`, `SCN-TRF-UPD` | Full transformative notice, technical impact assessment, independent assessment verification, and package update prior to implementation. |
| Urgent security patch mitigating an actively exploited KEV / zero-day prompt injection or sandbox escape (`VDR-TFR-KEV`) | **Emergency Change** | `SCN-CSO-EMG`, `VER-TFR-EVU` | Deploy mitigation immediately to protect Federal Customer Data; submit emergency SCN notice and retrospective impact documentation immediately following containment. |

---

## 3. Technical & Security Impact Assessment (`SCN-CSO-INF`, `SCN-TRF-NIP`)

- **Affects Minimum Assessment Scope (`MAS-CSO-IIR` / `MAS-CSO-MDI`):** `<Yes / No — Explain>`
- **Introduces or Modifies a TPIR (`MAS-CSO-TPR` / `SCN-TRF-TPR`):** `<Yes / No — Specify FedRAMP Package ID and mitigations>`
- **Alters Cryptographic Modules (`CMU-CSO-CMD` / `CMU-CSO-UVM`):** `<Yes / No — Specify CMVP module IDs>`
- **Alters Tool / Network Egress Boundary (`componentAgentNetworkPolicyEnforcementPoint` / `componentToolNetworkPolicyEnforcementPoint`):** `<Yes / No — Explain>`
- **CoSAI Components & Controls Affected:** `<List component* and control* IDs>`

---

## 4. Verification, Rollback & Notification Delivery (`SCN-CSO-HIS`, `SCN-CSO-HRM`)

1. **Automated Pre-Deployment Verification Plan:**
   - `python3 tools/validate_manifest.py agent-manifest.json`
   - `python3 tools/check_neutrality.py agents skills`
   - `python3 tools/audit_agent_repo.py --repo . --manifest agent-manifest.json --strict`
2. **Rollback Procedure:**
   - Revert container digest and `agent-manifest.json` revision; flush model/tool routing cache at `componentModelServing` and `componentToolRegistry`; verify restoration via automated smoke and compliance evals.
3. **Controlled Channel Delivery Receipt:**
   - **Channel URI:** `<lifecycle.scn_change_channel from agent-manifest.json>`
   - **Notice Bundle SHA-256 Digest:** `<64-char hex SHA-256>`
   - **Timestamp Published:** `<YYYY-MM-DDTHH:MM:SSZ>`
