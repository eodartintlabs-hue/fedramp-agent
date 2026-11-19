---
name: map-cosai-controls
description: "Map AI agent architectural components, threat scenarios, and external framework identifiers (MITRE ATLAS, NIST AI RMF, OWASP Top 10 for LLM, STRIDE, ISO 22989, EU AI Act) to verbatim Coalition for Secure AI (CoSAI) Risk Map IDs and FedRAMP CR-26 Class C and Class D rules."
---

# Map CoSAI Controls

Use this skill to resolve any AI agent component, security risk, defensive control, operational persona, or external framework pin to **100% verbatim identifiers** in `compliance/cosai-crosswalk.json` and `compliance/cosai-crosswalk.md`, together with their mapped FedRAMP CR-26 (`2026.11.02.01`) `FRR`, `KSI`, and `CTL` rules.

## Non-Negotiable Grounding Rule

**Never invent or paraphrase an identifier.** Every CoSAI ID (`component*`, `risk*`, `control*`, `persona*`), external framework pin (`AML.T*` / `AML.M*`, `GOVERN-*` / `MAP-*` / `MEASURE-*` / `MANAGE-*`, `LLM01:2025`..`LLM10:2025`, `STRIDE`, `ISO 22989`, `EU AI Act`), and FedRAMP ID (`FRR`, `KSI`, `CTL`) **MUST** exist verbatim in `compliance/cosai-crosswalk.json` (or the specified eval fixture when evaluating a fixture-grounded test case).

## Lookup Procedure

1. **Component-to-Boundary Mapping (`42` Components, `CoSAI ADR-030`):**
   - Locate the architectural role in `components[]` of `compliance/cosai-crosswalk.json`.
   - Verify `ADR-030` placement rules:
     - Model artifact (`componentTheModel`) is reached at runtime solely via `componentModelServing` (`D11`, `D12`).
     - Outbound agent traffic transits `componentAgentNetworkPolicyEnforcementPoint` (`D4`), which consults `componentToolRegistry` (`D14`) before crossing `componentAgentToolTransport` into `componentToolNetworkPolicyEnforcementPoint` -> `componentToolInputHandling` -> `componentAuthorizationPolicyEnforcementPoint` -> `componentToolServer` / `componentTools`.
     - First-party workloads run on `componentRuntimeHosting` and third-party tool servers run on `componentToolHosting`, both confined inside `componentIsolationRuntime` (`D6`, `D13`).
     - Human approvals distinguish `componentApplicationConsentSurface` vs. `componentAgentConsentSurface` (`D5`).
     - Durable telemetry lands in `componentAuditRecordRepository` (`D15`).

2. **Risk-to-Control & External Framework Resolution (`36` Risks, `37` Controls):**
   - Look up the threat mechanism in `risks[]` of `compliance/cosai-crosswalk.json` to retrieve:
     - Exact `cosai_controls` (`control*` IDs) that mitigate the risk.
     - Exact `external_mappings` (preserving version pins such as `@5.0.1` on individual `mitre-atlas` entries where the upstream CoSAI corpus pins `@5.0.1` alongside the `mitre-atlas@2026.09` registry entry, `@1.0` on `nist-ai-rmf`, and `:2025` on `owasp-top10-llm`).
     - Mapped `fedramp_frr_ids`, `fedramp_ksi_ids`, and `fedramp_ctl_ids`.

3. **Class C vs. Class D Enforcement & Verification Method:**
   - Extract `class_c_enforcement`, `class_d_enforcement`, `agent_manifest_paths`, and `verification_method` (`automated-cli`, `hybrid-cli-and-ivv`, or `procedural-ivv`).
   - Check `ksi_20x_class_d_omitted_in_2026_11_02_01`: whenever `KSI-CNA-EIS`, `KSI-MLA-ALA`, `KSI-SVC-PRR`, `KSI-SVC-RUD`, or `KSI-SVC-VCM` appears on a Class D mapping, note that CR-26 `2026.11.02.01` omits `varies_by_class.d` pending `2027` and rely on the mapped `FRR` and `Rev5` `CTL` controls.

4. **Persona Resolution (`10` Personas):**
   - Map organizational roles to the `8` active personas (`personaModelProvider`, `personaDataProvider`, `personaPlatformProvider`, `personaModelServing`, `personaAgenticProvider`, `personaApplicationDeveloper`, `personaGovernance`, `personaEndUser`) and flag `personaModelCreator` or `personaModelConsumer` if encountered in legacy manifests as **deprecated** (`deprecated: true`).

## Output Format

- **Verbatim CoSAI IDs:** `components`, `risks`, `controls`, `personas`, and exact `external_mappings`.
- **FedRAMP CR-26 Alignment:** `FRR`, `KSI` (with pending Class D flags where applicable), and `CTL` IDs.
- **Manifest Gate & Class C/D Delta:** Exact `agent-manifest.json` field(s) and verification method.
