# FedRAMP CR-26 Controlled Definitions Glossary (FRD)

> **Authoritative Source:** `fedramp-consolidated-rules.json` (`info.version`: `2026.11.02.01`, `info.last_updated`: `2026-11-02`, path: `FRD.data.all`, git SHA `64fa769510416fa75fd00a4689466094265b8083`)  
> **FRD Document Status:** `stable` | **Effective:** Required (`obtain`: `2026-07-04`, `maintain`: `2026-07-04`, `grace.default`: `2026-05-04`)  
> **Analysis Date:** `2026-11-19` | **Coverage:** **81 / 81** controlled definitions (`FRD-AAP` through `FRD-VUL`)  
> **Companion References:** [relevant-rulesets.md](../relevant-rulesets.md) | [marketplace-class-cd-analysis.md](marketplace-class-cd-analysis.md) | [sources-manifest.json](sources-manifest.json) | [specifications.md](../specifications.md)

## How to Use Controlled Definitions (Normative Rule)

Per `FRD.info.purpose` and `fedramp-cr6-markdown/rules.md`, FedRAMP Definitions act as **normative subroutines** embedded inside every FRR rule and KSI statement:

> *"When a defined term appears in a rule, the definition is a critical part of that rule and must be followed precisely, even if the term is commonly used differently elsewhere; when no definition exists, the plain-language meaning is expected."* (`FRD.info.purpose`)

### Critical Callout: Terms Without Dedicated `FRD-<KEY>` Entries

Per `fedramp-cr26-mrf/AGENTS.md`, agents and engineers MUST NOT invent `FRD-<KEY>` IDs for terms absent from `FRD.data.all`. Two high-impact agent concepts do **not** have dedicated `FRD-<KEY>` definitions in CR-26 v`2026.11.02.01` and are instead governed by plain-language meaning plus specific process rules:

- **Metadata:** No standalone `FRD-<KEY>` entry. Distinguished from `FRD-FCD` (*Federal Customer Data*, which excludes provider-generated service metadata/analytics/telemetry by default unless altered by contract) and explicitly scoped by `MAS-CSO-MDI` (`FRR.MAS.data.all.CSO.MAS-CSO-MDI`), which mandates including metadata (including metadata about Federal Customer Data) in the Minimum Assessment Scope whenever `MAS-CSO-IIR` applies.
- **Cryptographic Module:** No standalone `FRD-<KEY>` entry. Governed by plain-language + NIST Cryptographic Module Validation Program (CMVP) terminology under `CMU-CSO-CMD`, `CMU-CSO-UVM` (Class C `SHOULD` vs Class D `MUST`), and `CMU-CSO-CAT`, plus `CTL.SC.SC-13`.

---

## High-Impact Definitions for Enterprise AI Agent Teams

The table below highlights the highest-impact CR-26 definitions for **`runtime-cso`** (in-boundary) and **`internal-devsecops`** (engineering/compliance) agents:

| Tag | FRD ID | JSON Path | Official Term | Key Agent Engineering Implication |
| :--- | :--- | :--- | :--- | :--- |
| `[CRITICAL-AGENT]` | `FRD-DTM` | `FRD.data.all.FRD-DTM` | **Deterministic Telemetry** | Explicitly prohibits using generative AI / probabilistic LLM outputs to generate deterministic telemetry. Both `runtime-cso` and `internal-devsecops` agents MUST never fabricate compliance evidence, KSI metrics, or system-state facts; agents may only orchestrate/query authoritative deterministic telemetry tools and cite factual observations. |
| `[CRITICAL-AGENT]` | `FRD-FCD` | `FRD.data.all.FRD-FCD` | **Federal Customer Data** | Prompts, uploaded documents, RAG corpora, tool payloads, conversation histories, and fine-tuning/context records supplied by agency users constitute Federal Customer Data. Provider-generated operational telemetry/metadata is excluded by default UNLESS prompt/response content leaks into logs or agency contracts expand ownership (see `MAS-CSO-MDI`). |
| `[CRITICAL-AGENT]` | `FRD-MAS` | `FRD.data.all.FRD-MAS` | **Minimum Assessment Scope** | Defines the exact boundary of the CSO. Every `runtime-cso` agent, its LLM serving endpoint, vector database, MCP server, and orchestration runtime handling `FRD-FCD` or impacting its CIA sits inside MAS—or else becomes a `FRD-TPR` requiring `MAS-CSO-TPR` justification and mitigations. |
| `[CRITICAL-AGENT]` | `FRD-TPR` | `FRD.data.all.FRD-TPR` | **Third-Party Information Resource** | External LLM APIs, third-party MCP servers, observability/eval SaaS (e.g., trace collectors), and `internal-devsecops` coding agents operating outside MAS are TPIRs. If `MAS-CSO-IIR` applies, every TPIR must be documented under `MAS-CSO-TPR` (usage, justification, mitigations, compensating controls). |
| `[CRITICAL-AGENT]` | `FRD-TRF` | `FRD.data.all.FRD-TRF` | **Transformative Change** | Introducing a new customer-facing AI/agentic feature, changing a model inference TPIR handling `FRD-FCD`, or switching deployment/residency posture is typically Transformative—requiring 30 business days advance notice (`SCN-TRF-NIP`), 10-day final notice (`SCN-TRF-NFP`), 5-day post-deploy/verification notices (`SCN-TRF-NAF`/`SCN-TRF-NAV`), and 30-day doc updates (`SCN-TRF-UPD`). |
| `[CRITICAL-AGENT]` | `FRD-PAI` | `FRD.data.all.FRD-PAI` | **Potential Agency Impact** | Potential Agency Impact N-rating (`N0`..`N5` defined in `VER-EVA-EPA`) drives both vulnerability remediation SLAs (`VDR-TFR-PVR`), incident escalation (`VER-TFR-IRI`/`VER-TFR-NRI`), and default `PAIN-5` incident treatment (`IEC-CSO-DPR`) when unrated. |
| `[CRITICAL-AGENT]` | `FRD-FRI` | `FRD.data.all.FRD-FRI` | **FedRAMP Reportable Incident** | Triggered whenever an incident affects or is likely to affect confidentiality or integrity of `FRD-FCD`—including cross-tenant RAG leakage, unauthorized prompt/data exfiltration to an unapproved TPIR, or agent tool-abuse corrupting federal records (`IEC-CSO-EFR`). |
| `[HIGH-AGENT]` | `FRD-IRS` | `FRD.data.all.FRD-IRS` | **Information Resource** | Encompasses both machine-based resources (agent runtimes, models, prompts-as-code, MCP tools, CI runners) and non-machine-based resources (AI governance policies, human-in-the-loop reviewers, incident playbooks). Rules referencing 'information resources' without qualification apply to BOTH. |
| `[HIGH-AGENT]` | `FRD-MBI` | `FRD.data.all.FRD-MBI` | **Machine-Based (Information Resources)** | All software components of `runtime-cso` and `internal-devsecops` agents (containers, model weights/artifacts, MCP servers, orchestration pipelines, sandboxed execution pods) are machine-based information resources subject to `VDR-TFR-MVX`/`VDR-TFR-MVF`, `KSI-CNA-*`, `KSI-CMT-RMV`, and `KSI-SVC-VRI`. |
| `[HIGH-AGENT]` | `FRD-HAN` | `FRD.data.all.FRD-HAN` | **Handle** | Extremely broad: even transient in-memory inspection, RAG retrieval, embedding generation, prompt routing, or tool-call relaying counts as 'handling' `FRD-FCD` and pulls the component (or TPIR) into `MAS-CSO-IIR` scope. |
| `[HIGH-AGENT]` | `FRD-DFT` | `FRD.data.all.FRD-DFT` | **Drift** | For AI agents, drift includes unapproved prompt/system-instruction edits, silent upstream model-version updates, MCP tool-schema mutations, guardrail policy changes, and runtime privilege creep—triggering `VDR-TFR-PDD` (Class C 14d / Class D 7d) and `KSI-SVC-ACM`. |
| `[HIGH-AGENT]` | `FRD-PER` | `FRD.data.all.FRD-PER` | **Persistently** | Allows intentional, documented, automated recurring cycles (not strictly zero-gap continuous), but the cycle cadence and current status MUST always be known—critical for `internal-devsecops` compliance agents producing KSI validation evidence (`KSI-SVC-ACM`, `CPO-CSX-CPM`, `VER-RPT-PER`). |
| `[HIGH-AGENT]` | `FRD-SGC` | `FRD.data.all.FRD-SGC` | **Significant Change** | Adding a new `runtime-cso` agent, swapping foundation model providers, enabling autonomous tool execution, or changing egress boundaries is a Significant Change that MUST be evaluated and audited under `SCN-CSO-EVA` and `SCN-CSO-MAR`. |
| `[HIGH-AGENT]` | `FRD-ADP` | `FRD.data.all.FRD-ADP` | **Adaptive Change** | Iterative non-recurring engineering refinements (e.g., guardrail tuning, deterministic prompt template fixes, non-breaking tool-policy tightening without new risk surface) require post-change notification within 10 business days (`SCN-ADP-NTF`). |
| `[HIGH-AGENT]` | `FRD-VUL` | `FRD.data.all.FRD-VUL` | **Vulnerability** | Broader than CVEs: explicitly includes gaps in 20x KSIs or Rev5 controls, misconfigurations, prompt-injection / tool-abuse exposures, over-privileged agent tokens, weak credentials, and broken VDR pipelines (`VDR-CSO-FAV`). |
| `[HIGH-AGENT]` | `FRD-LEV` | `FRD.data.all.FRD-LEV` | **Likely Exploitable Vulnerability (LEV)** | Determines VDR SLA tier (`VDR-TFR-PVR`) and incident escalation (`VER-TFR-IRI`/`VER-TFR-NRI`). Unauthenticated internet-exploitable agent endpoints or publicly reachable indirect prompt-injection paths that trigger privileged tool actions meet LEV. |
| `[HIGH-AGENT]` | `FRD-IRV` | `FRD.data.all.FRD-IRV` | **Internet-Reachable Vulnerability (IRV)** | CRITICAL FOR AGENTS: Explicitly includes non-internet-routable internal resources that process payloads originating from the public internet (e.g., an internal RAG/MCP worker ingesting web-scraped pages, external emails, or customer-uploaded files containing indirect prompt injection). |
| `[HIGH-AGENT]` | `FRD-KEV` | `FRD.data.all.FRD-KEV` | **Known Exploited Vulnerability (KEV)** | Bound to CISA BOD 26-04 (effective 2026-12-07). Agent container images, LLM serving frameworks, and MCP runtime dependencies with CISA KEVs SHOULD NOT be deployed (`VDR-CSO-AKE`) and SHOULD be remediated by CISA KEV due dates even if fully mitigated (`VDR-TFR-KEV`). |
| `[HIGH-AGENT]` | `FRD-VLD` | `FRD.data.all.FRD-VLD` | **Vulnerability Detection** | Covers static/dynamic scanning, threat intel, bug bounties, pentesting, supply chain monitoring, AND persistent automated verification/validation of agent guardrails and configurations (`VDR-CSO-DET`). |
| `[HIGH-AGENT]` | `FRD-VLR` | `FRD.data.all.FRD-VLR` | **Vulnerability Response** | End-to-end triage, PAIN/LEV/IRV evaluation, mitigation, remediation, exploitation assessment, and machine-readable reporting (`VDR-CSO-RES`, `VER`). |
| `[HIGH-AGENT]` | `FRD-INT` | `FRD.data.all.FRD-INT` | **Incident** | Statutory FISMA definition (44 USC § 3552(b)(2)); includes imminent policy/AUP violations (e.g., runaway autonomous agent attempting unauthorized exfiltration). |
| `[HIGH-AGENT]` | `FRD-DCE` | `FRD.data.all.FRD-DCE` | **Debilitating Customer Effect** | Anchors `PAIN-4`/`PAIN-5`. Crucial fail-safe: unknown adverse customer effect MUST be treated as debilitating until proven otherwise. |
| `[HIGH-AGENT]` | `FRD-PAC` | `FRD.data.all.FRD-PAC` | **Privileged Account** | Covers BOTH human admin accounts AND privileged non-human service/agent identities/roles that can modify CSO state, access cross-tenant data, or invoke state-changing tools (`KSI-IAM-JIT`, `KSI-IAM-SUS`, `SCG-CSO-SDF`). |
| `[HIGH-AGENT]` | `FRD-TLA` | `FRD.data.all.FRD-TLA` | **Top-Level Administrative Account** | Highest customer-org admin account/role; agents MUST NOT operate with persistent TLA privileges and MUST respect SCG secure defaults (`SCG-CSO-RSC`/`SCG-CSO-SDF`). |
| `[HIGH-AGENT]` | `FRD-SDR` | `FRD.data.all.FRD-SDR` | **Security Decision Record (SDR)** | Replaces legacy SSP with a persistently maintained, machine-readable JSON + human-readable record of security decisions, verification, validation, and assessment findings (`SDR-CSO-FRR`, `SDR-CSX-KSI`, `SDR-CSF-CTF`). `internal-devsecops` agents help assemble/check SDRs but cannot fabricate `FRD-DTM`. |
| `[HIGH-AGENT]` | `FRD-MGN` | `FRD.data.all.FRD-MGN` | **Machine-Generated** | Produced automatically by deterministic software without human manipulation during generation; underpins automated KSI/VDR evidence pipelines (`FRC-CSX-VVK`). |
| `[HIGH-AGENT]` | `FRD-MRD` | `FRD.data.all.FRD-MRD` | **Machine-Readable** | Statutory 44 USC § 3502(18) requirement; drives JSON schema compliance (`FRC-CSO-JSN`), dual-format consistency (`CDS-CSO-CBF`), and API-accessible compliance artifacts (`CDS-TRC-PAC`, `SCN-CSO-HRM`, `VER-TFR-MRH`). |
| `[HIGH-AGENT]` | `FRD-VRF` | `FRD.data.all.FRD-VRF` | **Verification** | Objective evidence that specified FedRAMP Practices are implemented as documented (`IVV-CSO-SEI`, `SDR-CSO-FRR`). |
| `[HIGH-AGENT]` | `FRD-VLN` | `FRD.data.all.FRD-VLN` | **Validation** | Objective evidence that implemented controls/guardrails actually work as intended in operation (`IVV-CSO-SEE`, `FRC-CSX-VVK`). |
| `[HIGH-AGENT]` | `FRD-RSP` | `FRD.data.all.FRD-RSP` | **Responsibly** | Prohibits leaking exploit-enabling technical specifics (e.g., unpatched prompt-injection payloads or internal network topologies) in public/shared reports (`CDS-CSO-RIS`, `VER-RPT-NID`). |

---

## Complete Controlled Glossary (All 81 Definitions, Grouped by Official FRD Tag)

| Official Tag Group | Count | Included FRD IDs |
| :--- | ---: | :--- |
| Information Resource | 3 | `FRD-IRS`, `FRD-MBI`, `FRD-TPR` |
| Core & General Concepts | 24 | `FRD-CSO`, `FRD-DFT`, `FRD-DTM`, `FRD-FCD`, `FRD-FIN`, `FRD-FPR`, `FRD-FRA`, `FRD-FSI`, `FRD-HAN`, `FRD-LKY`, `FRD-MAS`, `FRD-MGN`, `FRD-MRD`, `FRD-OCR`, `FRD-PAI`, `FRD-PER`, `FRD-PRO`, `FRD-RGL`, `FRD-RSP`, `FRD-SCT`, `FRD-SDR`, `FRD-TRC`, `FRD-VLN`, `FRD-VRF` |
| Significant Changes | 5 | `FRD-ADP`, `FRD-CCC`, `FRD-RTR`, `FRD-SGC`, `FRD-TRF` |
| Vulnerability | 12 | `FRD-ACV`, `FRD-FMV`, `FRD-FPV`, `FRD-IRV`, `FRD-KEV`, `FRD-LEV`, `FRD-ODV`, `FRD-PMV`, `FRD-RMV`, `FRD-VLD`, `FRD-VLR`, `FRD-VUL` |
| Incident | 5 | `FRD-FIR`, `FRD-FRI`, `FRD-IIR`, `FRD-INT`, `FRD-OIR` |
| Customer Effect | 4 | `FRD-DCE`, `FRD-DCF`, `FRD-MCE`, `FRD-NCE` |
| Accounts | 2 | `FRD-PAC`, `FRD-TLA` |
| Certification | 12 | `FRD-ART`, `FRD-CCL`, `FRD-CPF`, `FRD-CPH`, `FRD-CRD`, `FRD-CRP`, `FRD-CTY`, `FRD-FCR`, `FRD-FCT`, `FRD-INC`, `FRD-ONC`, `FRD-QTR` |
| Assessment | 2 | `FRD-IFA`, `FRD-PFA` |
| Force of the Rule | 5 | `FRD-MAY`, `FRD-MNT`, `FRD-MST`, `FRD-SHD`, `FRD-SNT` |
| Stakeholder | 7 | `FRD-AAP`, `FRD-ADV`, `FRD-AGY`, `FRD-ANA`, `FRD-ANP`, `FRD-ASR`, `FRD-PRV` |
| **Total** | **81** | **All 81 definitions in `FRD.data.all`** |

### Information Resource (3)

#### `FRD-IRS` — Information Resource `[HIGH-AGENT]`
- **JSON Path:** `FRD.data.all.FRD-IRS`
- **Alternate Forms (`alts`):** `information resource`, `information resources`
- **Official Definition:** Has the meaning from 44 USC § 3502 (6): "information and related resources, such as personnel, equipment, funds, and information technology." This includes any aspect of the cloud service offering, both technical and managerial, including everything that makes up the business of the offering from non-machine-based information resources like organizational policies, procedures, employees, etc. to machine-based information resources like hardware, software, cloud services, code, etc.
- **Official Note:** Information resources are either machine-based or non-machine-based; any requirement or recommendation that references information resources without specifying a type is inclusive of all information resources.
- **Reference:** [44 USC § 3502 (6)](https://www.govinfo.gov/app/details/USCODE-2023-title44/USCODE-2023-title44-chap35-subchapI-sec3502)
- **Agent Engineering Implication:** Encompasses both machine-based resources (agent runtimes, models, prompts-as-code, MCP tools, CI runners) and non-machine-based resources (AI governance policies, human-in-the-loop reviewers, incident playbooks). Rules referencing 'information resources' without qualification apply to BOTH.

#### `FRD-MBI` — Machine-Based (Information Resources) `[HIGH-AGENT]`
- **JSON Path:** `FRD.data.all.FRD-MBI`
- **Alternate Forms (`alts`):** `machine-based`, `machine based`
- **Official Definition:** Any information technology information resource—including systems, processes, software, hardware, services, cloud-native capabilities, and any other such capability, component, or resource—that relies primarily on mechanical or electronic devices (i.e. computers) for operation.
- **Official Note:** All other information resources that do not rely on computers are non-machine-based information resources.
- **Agent Engineering Implication:** All software components of `runtime-cso` and `internal-devsecops` agents (containers, model weights/artifacts, MCP servers, orchestration pipelines, sandboxed execution pods) are machine-based information resources subject to `VDR-TFR-MVX`/`VDR-TFR-MVF`, `KSI-CNA-*`, `KSI-CMT-RMV`, and `KSI-SVC-VRI`.

#### `FRD-TPR` — Third-Party Information Resource `[CRITICAL-AGENT]`
- **JSON Path:** `FRD.data.all.FRD-TPR`
- **Alternate Forms (`alts`):** `third-party information resource`, `third-party information resources`
- **Official Definition:** Any information resource that is not entirely included in the Minimum Assessment Scope for the cloud service offering obtaining FedRAMP Certification.
- **Agent Engineering Implication:** External LLM APIs, third-party MCP servers, observability/eval SaaS (e.g., trace collectors), and `internal-devsecops` coding agents operating outside MAS are TPIRs. If `MAS-CSO-IIR` applies, every TPIR must be documented under `MAS-CSO-TPR` (usage, justification, mitigations, compensating controls).

### Core & General Concepts (24)

#### `FRD-CSO` — Cloud Service Offering `[MEDIUM-AGENT]`
- **JSON Path:** `FRD.data.all.FRD-CSO`
- **Alternate Forms (`alts`):** `cloud service offering`, `cloud service offerings`
- **Official Definition:** A specific, packaged cloud computing product or service supplied by a cloud service provider for use by customers, that is the subject of a FedRAMP Certification.
- **Official Note:** The FedRAMP Minimum Assessment Scope defines the full scope of the cloud service offering from the perspective of a FedRAMP Certification.
- **Agent Engineering Implication:** The packaged cloud service boundary defined by `FRD-MAS`; determines whether an agent is a `runtime-cso` service component or an `internal-devsecops` operational tool.

#### `FRD-DFT` — Drift `[HIGH-AGENT]`
- **JSON Path:** `FRD.data.all.FRD-DFT`
- **Alternate Forms (`alts`):** `drift`, `drifts`, `drifting`
- **Official Definition:** Changes to information resources that cause deviations from the intended and assessed state; common forms of drift include changes to configurations, deployed software, privileges, running processes, and availability.
- **Agent Engineering Implication:** For AI agents, drift includes unapproved prompt/system-instruction edits, silent upstream model-version updates, MCP tool-schema mutations, guardrail policy changes, and runtime privilege creep—triggering `VDR-TFR-PDD` (Class C 14d / Class D 7d) and `KSI-SVC-ACM`.

#### `FRD-DTM` — Deterministic Telemetry `[CRITICAL-AGENT]`
- **JSON Path:** `FRD.data.all.FRD-DTM`
- **Alternate Forms (`alts`):** `deterministic telemetry`
- **Official Definition:** Verifiable data collected directly from an authoritative source that represents a factual and reproducible observation of the attributes of a system such as the system's state, configuration, or behavior.
- **Official Note:** Probabilistic inferences, generative outputs, or predictive assessments such as those produced using generative transformer models (commonly referred to as “Generative AI”) do not constitute a factual record of the system state and must not be used to generate deterministic telemetry.
- **Agent Engineering Implication:** Explicitly prohibits using generative AI / probabilistic LLM outputs to generate deterministic telemetry. Both `runtime-cso` and `internal-devsecops` agents MUST never fabricate compliance evidence, KSI metrics, or system-state facts; agents may only orchestrate/query authoritative deterministic telemetry tools and cite factual observations.

#### `FRD-FCD` — Federal Customer Data `[CRITICAL-AGENT]`
- **JSON Path:** `FRD.data.all.FRD-FCD`
- **Alternate Forms (`alts`):** `federal customer data`
- **Official Definition:** All electronic information, content, and materials that an agency or its authorized users upload, store, or otherwise supply to a cloud service for processing or storage. This does NOT include account information, service metadata, analytics, telemetry, or other similar metadata generated by the cloud service provider.
- **Official Note:** In the context of FedRAMP Certification, "federal customer data" ONLY ever refers to data owned by federal agency customers. Agreements and contracts with specific agencies may require providers to protect additional data or even transfer ownership of telemetry or usage data to the agency; always consult a lawyer that is familiar with company agreements and contracts when determining the scope of federal customer data.
- **Agent Engineering Implication:** Prompts, uploaded documents, RAG corpora, tool payloads, conversation histories, and fine-tuning/context records supplied by agency users constitute Federal Customer Data. Provider-generated operational telemetry/metadata is excluded by default UNLESS prompt/response content leaks into logs or agency contracts expand ownership (see `MAS-CSO-MDI`).

#### `FRD-FIN` — FedRAMP Independent Assessment
- **JSON Path:** `FRD.data.all.FRD-FIN`
- **Alternate Forms (`alts`):** `FedRAMP independent assessment`, `FedRAMP independent assessments`
- **Official Definition:** An independent verification and validation assessment, performed by a FedRAMP Recognized independent assessment service or FedRAMP following FedRAMP rules. These assessments are typically first performed to obtain an initial FedRAMP Certification then repeated on an annual basis to maintain FedRAMP Certification.

#### `FRD-FPR` — FedRAMP Practices `[MEDIUM-AGENT]`
- **JSON Path:** `FRD.data.all.FRD-FPR`
- **Alternate Forms (`alts`):** `FedRAMP Practice`, `FedRAMP Practices`
- **Official Definition:** The security measures, safeguards, precautions, procedures, activities, policies, capabilities, mechanisms, etc. that are expected to be in place by FedRAMP to demonstrate that information resources are properly protected, expressed in FedRAMP 20x Key Security Indicators or FedRAMP Rev5 Controls and supplemented by FedRAMP rules.
- **Agent Engineering Implication:** Umbrella term for 20x KSIs OR Rev5 Controls supplemented by FRR rules—both tracks share the FRR rulesets.

#### `FRD-FRA` — FedRAMP Recognized
- **JSON Path:** `FRD.data.all.FRD-FRA`
- **Alternate Forms (`alts`):** `FedRAMP Recognized`, `FedRAMP Recognition`
- **Official Definition:** The status of independent assessment services that are recognized by FedRAMP to perform assessment activities on behalf of FedRAMP for cloud service offerings seeking to obtain or maintain FedRAMP Certification.

#### `FRD-FSI` — FedRAMP Security Inbox `[MEDIUM-AGENT]`
- **JSON Path:** `FRD.data.all.FRD-FSI`
- **Alternate Forms (`alts`):** `security inbox`, `security inboxes`, `FSI`
- **Official Definition:** An email address that follows the FedRAMP Security Inbox rules.
- **Agent Engineering Implication:** Dedicated email inbox (`AFC-CSO-INB`) monitored without CAPTCHA/portal friction (`AFC-CSO-RCV`) for `@fedramp.gov`/`@gsa.gov` Emergency and Important messages.

#### `FRD-HAN` — Handle `[HIGH-AGENT]`
- **JSON Path:** `FRD.data.all.FRD-HAN`
- **Alternate Forms (`alts`):** `handle`, `handles`, `handled`, `handling`
- **Official Definition:** Has the plain language meaning inclusive of any possible action taken with information, such as access, collect, control, create, display, disclose, disseminate, dispose, maintain, manipulate, process, receive, review, store, transmit, use... etc.
- **Agent Engineering Implication:** Extremely broad: even transient in-memory inspection, RAG retrieval, embedding generation, prompt routing, or tool-call relaying counts as 'handling' `FRD-FCD` and pulls the component (or TPIR) into `MAS-CSO-IIR` scope.

#### `FRD-LKY` — Likely
- **JSON Path:** `FRD.data.all.FRD-LKY`
- **Alternate Forms (`alts`):** `likely`, `likelihood`
- **Official Definition:** A reasonable degree of probability based on context.

#### `FRD-MAS` — Minimum Assessment Scope `[CRITICAL-AGENT]`
- **JSON Path:** `FRD.data.all.FRD-MAS`
- **Alternate Forms (`alts`):** `minimum assessment scope`, `MAS`
- **Official Definition:** The boundary of the assessment and FedRAMP Certification for the cloud service offering, which effectively defines the cloud service offering itself for the purposes of a FedRAMP Certification Package; anything that is not entirely included in the Minimum Assessment Scope is a third-party information resource.
- **Official Note:** The Minimum Assessment Scope ruleset explains how to determine the Minimum Assessment Scope for a cloud service offering.
- **Agent Engineering Implication:** Defines the exact boundary of the CSO. Every `runtime-cso` agent, its LLM serving endpoint, vector database, MCP server, and orchestration runtime handling `FRD-FCD` or impacting its CIA sits inside MAS—or else becomes a `FRD-TPR` requiring `MAS-CSO-TPR` justification and mitigations.

#### `FRD-MGN` — Machine-Generated `[HIGH-AGENT]`
- **JSON Path:** `FRD.data.all.FRD-MGN`
- **Alternate Forms (`alts`):** `machine-generated`
- **Official Definition:** Automatically produced by a computer process, application, or other mechanism without the intervention or manipulation of a human during production.
- **Agent Engineering Implication:** Produced automatically by deterministic software without human manipulation during generation; underpins automated KSI/VDR evidence pipelines (`FRC-CSX-VVK`).

#### `FRD-MRD` — Machine-Readable `[HIGH-AGENT]`
- **JSON Path:** `FRD.data.all.FRD-MRD`
- **Alternate Forms (`alts`):** `machine-readable`
- **Official Definition:** Has the meaning from 44 U.S. Code § 3502 (18) which is "the term "machine-readable", when used with respect to data, means data in a format that can be easily processed by a computer without human intervention while ensuring no semantic meaning is lost"
- **Reference:** [44 U.S. Code § 3502 (18)](https://www.govinfo.gov/app/details/USCODE-2023-title44/USCODE-2023-title44-chap35-subchapI-sec3502)
- **Agent Engineering Implication:** Statutory 44 USC § 3502(18) requirement; drives JSON schema compliance (`FRC-CSO-JSN`), dual-format consistency (`CDS-CSO-CBF`), and API-accessible compliance artifacts (`CDS-TRC-PAC`, `SCN-CSO-HRM`, `VER-TFR-MRH`).

#### `FRD-OCR` — Ongoing Certification Report (OCR)
- **JSON Path:** `FRD.data.all.FRD-OCR`
- **Alternate Forms (`alts`):** `ongoing certification report`, `OCR`, `OCRs`
- **Official Definition:** A regular report that is supplied by FedRAMP Certified cloud service providers to agency customers, following FedRAMP Collaborative Continuous Monitoring rules.

#### `FRD-PAI` — Potential Agency Impact `[CRITICAL-AGENT]`
- **JSON Path:** `FRD.data.all.FRD-PAI`
- **Alternate Forms (`alts`):** `potential agency impact`, `potential agency impacts`, `PAIN`, `Potential Agency Impact N-rating`
- **Official Definition:** The estimated cumulative effect of unauthorized access, disruption, harm, or other adverse impacts to all agencies using the cloud service that are likely to result from security incidents or the exploitation of vulnerabilities in the cloud service offering; as estimated following appropriate FedRAMP rules to calculate the Potential Agency Impact N-rating (PAIN).
- **Official Note:** Potential Agency Impact N-rating (PAIN) levels are defined in VER-EVA-EPA (Estimate Potential Agency Impact)
- **Agent Engineering Implication:** Potential Agency Impact N-rating (`N0`..`N5` defined in `VER-EVA-EPA`) drives both vulnerability remediation SLAs (`VDR-TFR-PVR`), incident escalation (`VER-TFR-IRI`/`VER-TFR-NRI`), and default `PAIN-5` incident treatment (`IEC-CSO-DPR`) when unrated.

#### `FRD-PER` — Persistently `[HIGH-AGENT]`
- **JSON Path:** `FRD.data.all.FRD-PER`
- **Alternate Forms (`alts`):** `persistently`, `persistent`
- **Official Definition:** Occurring in a firm, steady way that is repeated over a long period of time in spite of obstacles or difficulties. Persistent activities may vary between actors, may occur irregularly, and may include interruptions or waiting periods between cycles. These attributes of persistent activities should be intentional, understood, and documented; the status of persistent activities will always be known.
- **Official Note:** The use of persistently indicates a process that may not always occur continuously (without interruption or gaps) or regularly (on a consistent, predictable basis) but will repeat frequently in cycles. It aligns generally with historical misuse of "continuous" in federal information security policies.
- **Agent Engineering Implication:** Allows intentional, documented, automated recurring cycles (not strictly zero-gap continuous), but the cycle cadence and current status MUST always be known—critical for `internal-devsecops` compliance agents producing KSI validation evidence (`KSI-SVC-ACM`, `CPO-CSX-CPM`, `VER-RPT-PER`).

#### `FRD-PRO` — Promptly `[MEDIUM-AGENT]`
- **JSON Path:** `FRD.data.all.FRD-PRO`
- **Alternate Forms (`alts`):** `promptly`, `prompt`
- **Official Definition:** Without unnecessary delay.
- **Official Note:** The use of promptly in FedRAMP materials frames conveys a need for urgent action where the expected time frame will vary by circumstance but earlier action is more likely to improve security outcomes and increase the security posture of a cloud service offering.
- **Agent Engineering Implication:** Without unnecessary delay; governs incident reportability triage (`IEC-CSO-EFR`), PAIN estimation (`IEC-CSO-EFI`), vulnerability response (`VDR-CSO-RES`), and unwanted Federal Customer Data removal (`KSI-SVC-RUD`, including clearing vector indices/caches).

#### `FRD-RGL` — Regularly `[MEDIUM-AGENT]`
- **JSON Path:** `FRD.data.all.FRD-RGL`
- **Alternate Forms (`alts`):** `regularly`, `regular`
- **Official Definition:** Performing the activity on a consistent, predictable, and repeated basis, at set intervals, automatically if possible, following a documented plan. These intervals may vary as appropriate between different activities.
- **Agent Engineering Implication:** Predictable, interval-based, preferably automated execution following a documented plan (e.g., automated secret rotation under `KSI-SVC-ASM`, quarterly OCR/QTR generation under `CCM`).

#### `FRD-RSP` — Responsibly `[HIGH-AGENT]`
- **JSON Path:** `FRD.data.all.FRD-RSP`
- **Alternate Forms (`alts`):** `responsibly`
- **Official Definition:** In a way that shows that you have good judgment and the ability to act correctly and make decisions on your own.
- **Official Note:** Refrain from broadcasting any details that might assist adversaries in their endeavors, disclosing vulnerabilities prior to full remediation, or providing overly specific technical information that could potentially facilitate further compromise.
- **Agent Engineering Implication:** Prohibits leaking exploit-enabling technical specifics (e.g., unpatched prompt-injection payloads or internal network topologies) in public/shared reports (`CDS-CSO-RIS`, `VER-RPT-NID`).

#### `FRD-SCT` — Security Category `[MEDIUM-AGENT]`
- **JSON Path:** `FRD.data.all.FRD-SCT`
- **Alternate Forms (`alts`):** `security category`, `security categories`, `impact level`, `impact levels`
- **Official Definition:** Has the meaning from NIST FIPS 199, which is "The characterization of information or an information system based on an assessment of the potential impact that a loss of confidentiality, integrity, or availability of such information or information system would have on organizational operations, organizational assets, or individuals." Security categories are often referred to as "impact levels" and include Low, Moderate, and High.
- **Reference:** [NIST FIPS 199 Standards for Security Categorization of Federal Information and Information Systems](https://csrc.nist.gov/pubs/fips/199/final)
- **Agent Engineering Implication:** NIST FIPS 199 Low/Moderate/High impact levels; individual services/TPIRs inside a CSO may carry distinct security categories (`MAS-CSO-FLO`, `CDS-CSO-SVC`).

#### `FRD-SDR` — Security Decision Record (SDR) `[HIGH-AGENT]`
- **JSON Path:** `FRD.data.all.FRD-SDR`
- **Alternate Forms (`alts`):** `security decision record`, `security decision records`, `SDR`
- **Official Definition:** A persistently maintained, verified, and validated record of the security decisions made by a provider over the lifecycle of a cloud service offering. The Security Decision Record replaces the traditional System Security Plan and documents how applicable FedRAMP Practices are addressed, including implementation rationale, resulting customer risk, assessment findings, and supporting artifacts.
- **Agent Engineering Implication:** Replaces legacy SSP with a persistently maintained, machine-readable JSON + human-readable record of security decisions, verification, validation, and assessment findings (`SDR-CSO-FRR`, `SDR-CSX-KSI`, `SDR-CSF-CTF`). `internal-devsecops` agents help assemble/check SDRs but cannot fabricate `FRD-DTM`.

#### `FRD-TRC` — Trust Center `[MEDIUM-AGENT]`
- **JSON Path:** `FRD.data.all.FRD-TRC`
- **Alternate Forms (`alts`):** `trust center`, `trust centers`
- **Official Definition:** A secure repository or service used by cloud service providers to store and share FedRAMP Certification Data. Trust centers are the complete and definitive source for FedRAMP Certification Data and must follow the FedRAMP Certification Data Sharing rules to be FedRAMP-compatible.
- **Official Note:** In FedRAMP documentation, all references to trust centers indicate FedRAMP-compatible trust centers unless otherwise specified.
- **Agent Engineering Implication:** Authoritative FedRAMP-compatible repository (`CDS-TRC-*`) for storing and sharing certification data programmatically and via browser.

#### `FRD-VLN` — Validation `[HIGH-AGENT]`
- **JSON Path:** `FRD.data.all.FRD-VLN`
- **Alternate Forms (`alts`):** `validation`, `validate`, `validated`
- **Official Definition:** Confirmation through objective evidence that implemented security capabilities and related certification data are suitable for their intended FedRAMP Certification use and support the expected security outcomes for a cloud service offering.
- **Official Note:** This adapts the ISO conformity assessment concept of validation to the FedRAMP Certification context.
- **Agent Engineering Implication:** Objective evidence that implemented controls/guardrails actually work as intended in operation (`IVV-CSO-SEE`, `FRC-CSX-VVK`).

#### `FRD-VRF` — Verification `[HIGH-AGENT]`
- **JSON Path:** `FRD.data.all.FRD-VRF`
- **Alternate Forms (`alts`):** `verification`, `verify`, `verified`
- **Official Definition:** Confirmation through objective evidence that specified FedRAMP Practices have been fulfilled for a cloud service offering.
- **Official Note:** This adapts the ISO conformity assessment concept of verification to the FedRAMP Certification context.
- **Agent Engineering Implication:** Objective evidence that specified FedRAMP Practices are implemented as documented (`IVV-CSO-SEI`, `SDR-CSO-FRR`).

### Significant Changes (5)

#### `FRD-ADP` — Adaptive Change `[HIGH-AGENT]`
- **JSON Path:** `FRD.data.all.FRD-ADP`
- **Alternate Forms (`alts`):** `adaptive`, `adaptive change`, `adaptive changes`
- **Official Definition:** A type of significant change that does not routinely recur and does not introduce substantive potential security risks that need to be assessed in depth.
- **Official Note:** Adaptive changes typically require careful planning that focuses on engineering execution instead of customer adoption, can be verified with minor changes to existing automated validation procedures, and do not require large changes to operational procedures, deployment plans, or documentation.
- **Agent Engineering Implication:** Iterative non-recurring engineering refinements (e.g., guardrail tuning, deterministic prompt template fixes, non-breaking tool-policy tightening without new risk surface) require post-change notification within 10 business days (`SCN-ADP-NTF`).

#### `FRD-CCC` — Certification Class Change `[MEDIUM-AGENT]`
- **JSON Path:** `FRD.data.all.FRD-CCC`
- **Alternate Forms (`alts`):** `certification class change`, `certification class changes`
- **Official Definition:** A type of significant change that is likely to change the FedRAMP Certification class for the entire cloud service offering (e.g. from Class B to Class C or from Class D to Class C).
- **Agent Engineering Implication:** Upgrading a CSO from Class C to Class D (or downgrading) triggers `FRC-CCL-UCC`/`FRC-CCL-DCC`/`FRC-CCL-DNP` and requires Class D agent controls (FIPS-validated crypto `CMU-CSO-UVM`, IAL3/AAL3/FAL3 `CTL.IA.IA-05`, U.S. residency `CTL.SA.SA-09-05`, 2-day VDR triage `VER-TFR-EVU`).

#### `FRD-RTR` — Routine Recurring Change `[MEDIUM-AGENT]`
- **JSON Path:** `FRD.data.all.FRD-RTR`
- **Alternate Forms (`alts`):** `routine recurring`, `routine recurring change`, `routine recurring changes`
- **Official Definition:** The type of significant change that regularly and routinely recurs as part of ongoing operations, vulnerability mitigation, or vulnerability remediation.
- **Agent Engineering Implication:** Routine automated patching, base image rebuilds, and scheduled dependency updates following mature CI/CD processes are exempt from formal SCN (`SCN-RTR-NNR`), provided they truly recur regularly and follow audited pipelines.

#### `FRD-SGC` — Significant Change `[HIGH-AGENT]`
- **JSON Path:** `FRD.data.all.FRD-SGC`
- **Alternate Forms (`alts`):** `significant change`, `significant changes`
- **Official Definition:** Has the meaning given in NIST SP 800-37 Rev. 2 which is "a change that is likely to substantively affect the security or privacy posture of a system."
- **Reference:** [NIST SP 800-37 Rev. 2](https://csrc.nist.gov/pubs/sp/800/37/r2/final)
- **Agent Engineering Implication:** Adding a new `runtime-cso` agent, swapping foundation model providers, enabling autonomous tool execution, or changing egress boundaries is a Significant Change that MUST be evaluated and audited under `SCN-CSO-EVA` and `SCN-CSO-MAR`.

#### `FRD-TRF` — Transformative Change `[CRITICAL-AGENT]`
- **JSON Path:** `FRD.data.all.FRD-TRF`
- **Alternate Forms (`alts`):** `transformative`, `transformative change`, `transformative changes`
- **Official Definition:** The type of significant change that introduces substantive potential security risks that are likely to affect existing risk determinations and must be assessed in depth.
- **Official Note:** Transformative changes typically introduce major features or capabilities that may change how a customer uses the service (in whole or in part) and require extensive updates to security assessments, operational procedures, deployment plans, and documentation.
- **Agent Engineering Implication:** Introducing a new customer-facing AI/agentic feature, changing a model inference TPIR handling `FRD-FCD`, or switching deployment/residency posture is typically Transformative—requiring 30 business days advance notice (`SCN-TRF-NIP`), 10-day final notice (`SCN-TRF-NFP`), 5-day post-deploy/verification notices (`SCN-TRF-NAF`/`SCN-TRF-NAV`), and 30-day doc updates (`SCN-TRF-UPD`).

### Vulnerability (12)

#### `FRD-ACV` — Accepted Vulnerability `[MEDIUM-AGENT]`
- **JSON Path:** `FRD.data.all.FRD-ACV`
- **Alternate Forms (`alts`):** `accepted vulnerability`, `accepted vulnerabilities`
- **Official Definition:** A vulnerability that the provider does not intend to fully mitigate or remediate, OR that has not or will not be fully mitigated or remediated within the maximum overdue period in FedRAMP Vulnerability Detection and Response rules.
- **Agent Engineering Implication:** Any vulnerability not fully mitigated or remediated within 192 days of evaluation MUST be marked as an Accepted Vulnerability (`VER-TFR-MAV`) and reported via `VER-RPT-AVI` and `CCM-OCR-AVL`.

#### `FRD-FMV` — Fully Mitigated Vulnerability `[MEDIUM-AGENT]`
- **JSON Path:** `FRD.data.all.FRD-FMV`
- **Alternate Forms (`alts`):** `fully mitigated vulnerability`, `fully mitigated vulnerabilities`, `fully mitigate vulnerabilities`
- **Official Definition:** A vulnerability where the likelihood of exploitation or Potential Agency Impact N-rating has been reduced from the original evaluation until either are negligible, but the vulnerability is still detected.
- **Agent Engineering Implication:** Risk reduced to negligible via compensating controls (e.g., egress proxy blocking exploit vector) while underlying flaw remains detected; distinct from `FRD-RMV` (eliminated). KEVs still require full remediation (`VDR-TFR-KEV`).

#### `FRD-FPV` — False Positive Vulnerability `[MEDIUM-AGENT]`
- **JSON Path:** `FRD.data.all.FRD-FPV`
- **Alternate Forms (`alts`):** `false positive vulnerability`, `false positive vulnerabilities`
- **Official Definition:** A detected vulnerability that is not actually present in an exploitable state in the information resource
- **Official Note:** This includes situations where vulnerable software or code exist on a machine-based information resource but are not loaded, running, or otherwise in an operating state required for exploitation.
- **Official Note:** This only applies if the vulnerability is not and was not present; a remediated vulnerability or a fully mitigated vulnerability cannot also be a false positive vulnerability.
- **Agent Engineering Implication:** Applies ONLY when vulnerable code is not loaded/running/exploitable and was never present; cannot reclassify an already-present remediated/mitigated flaw.

#### `FRD-IRV` — Internet-Reachable Vulnerability (IRV) `[HIGH-AGENT]`
- **JSON Path:** `FRD.data.all.FRD-IRV`
- **Alternate Forms (`alts`):** `internet-reachable vulnerability`, `internet-reachable vulnerabilities`, `IRV`, `IRVs`, `NIRV`, `NIRVs`
- **Official Definition:** A vulnerability in a machine-based information resource that might be exploited or otherwise triggered by a payload originating from a source on the public internet.
- **Official Note:** This includes machine-based information resources that have no direct route to/from the internet but receive payloads or otherwise take action triggered by internet activity.
- **Official Note:** Internet-reachability applies only to the specific vulnerable machine-based information resources processing the payload.
- **Official Note:** The opposite of this is a Not Internet-reachable Vulnerability (NIRV).
- **Agent Engineering Implication:** CRITICAL FOR AGENTS: Explicitly includes non-internet-routable internal resources that process payloads originating from the public internet (e.g., an internal RAG/MCP worker ingesting web-scraped pages, external emails, or customer-uploaded files containing indirect prompt injection).

#### `FRD-KEV` — Known Exploited Vulnerability (KEV) `[HIGH-AGENT]`
- **JSON Path:** `FRD.data.all.FRD-KEV`
- **Alternate Forms (`alts`):** `known exploited vulnerability`, `known exploited vulnerabilities`, `KEV`, `KEVs`
- **Official Definition:** Has the meaning given in CISA Binding Operational Directive 26-04, which is any vulnerability identified in CISA's Known Exploited Vulnerabilities catalog.
- **Reference:** [CISA BOD 26-04](https://www.cisa.gov/news-events/directives/bod-26-04-prioritizing-security-updates-based-risk)
- **Agent Engineering Implication:** Bound to CISA BOD 26-04 (effective 2026-12-07). Agent container images, LLM serving frameworks, and MCP runtime dependencies with CISA KEVs SHOULD NOT be deployed (`VDR-CSO-AKE`) and SHOULD be remediated by CISA KEV due dates even if fully mitigated (`VDR-TFR-KEV`).

#### `FRD-LEV` — Likely Exploitable Vulnerability (LEV) `[HIGH-AGENT]`
- **JSON Path:** `FRD.data.all.FRD-LEV`
- **Alternate Forms (`alts`):** `likely exploitable vulnerability`, `likely exploitable vulnerabilities`, `LEV`, `LEVs`, `NLEV`, `NLEVs`
- **Official Definition:** A vulnerability that is not fully mitigated AND is reachable by a likely threat actor; AND a likely threat actor with knowledge of the vulnerability would likely gain unauthorized access, cause harm, disrupt operations, or otherwise have an undesired adverse impact within the cloud service offering by exploiting the vulnerability.
- **Official Note:** At the absolute minimum, any vulnerability that an automated unauthenticated system can exploit over the internet is a likely exploitable vulnerability.
- **Official Note:** The opposite of this is a Not Likely Exploitable Vulnerability (NLEV).
- **Agent Engineering Implication:** Determines VDR SLA tier (`VDR-TFR-PVR`) and incident escalation (`VER-TFR-IRI`/`VER-TFR-NRI`). Unauthenticated internet-exploitable agent endpoints or publicly reachable indirect prompt-injection paths that trigger privileged tool actions meet LEV.

#### `FRD-ODV` — Overdue Vulnerability `[MEDIUM-AGENT]`
- **JSON Path:** `FRD.data.all.FRD-ODV`
- **Alternate Forms (`alts`):** `overdue vulnerability`, `overdue vulnerabilities`
- **Official Definition:** A vulnerability that the provider intends to fully mitigate or remediate but has not or will not do so within the time frames recommended or required by FedRAMP.
- **Agent Engineering Implication:** Detected vulnerability exceeding `VDR-TFR-PVR` timeframes; tracked in `VER-RPT-VDT` until remediated, fully mitigated, or converted to `FRD-ACV` at 192 days.

#### `FRD-PMV` — Partially Mitigated Vulnerability `[MEDIUM-AGENT]`
- **JSON Path:** `FRD.data.all.FRD-PMV`
- **Alternate Forms (`alts`):** `partially mitigated vulnerability`, `partially mitigated vulnerabilities`, `partially mitigate vulnerabilities`
- **Official Definition:** A vulnerability where the likelihood or Potential Agency Impact N-rating has been reduced from the original evaluation but the risk of exploitation still exists and the vulnerability is still detected.
- **Agent Engineering Implication:** Reduces PAIN or likelihood (e.g., downgrading an N4 agent tool-injection exposure to N3 via read-only scoping) while exploit risk persists.

#### `FRD-RMV` — Remediated Vulnerability `[MEDIUM-AGENT]`
- **JSON Path:** `FRD.data.all.FRD-RMV`
- **Alternate Forms (`alts`):** `remediated vulnerability`, `remediated vulnerabilities`, `remediate vulnerabilities`
- **Official Definition:** A vulnerability that has been neutralized or eliminated and is no longer detected.
- **Agent Engineering Implication:** Vulnerability completely eliminated and no longer detected by persistent scanning/validation.

#### `FRD-VLD` — Vulnerability Detection `[HIGH-AGENT]`
- **JSON Path:** `FRD.data.all.FRD-VLD`
- **Alternate Forms (`alts`):** `vulnerability detection`, `detect vulnerabilities`, `detect`, `detection`, `detected`
- **Official Definition:** The systematic process of discovering and identifying security vulnerabilities in information resources through assessment, scanning, threat intelligence, vulnerability disclosure mechanisms, bug bounties, supply chain monitoring, and other capabilities. This process includes the initial discovery of a vulnerability's existence and the determination of affected information resources within a cloud service offering.
- **Official Note:** This definition applies to other forms such as "detect vulnerabilities" or simply "detection" / "detected" used in FedRAMP materials.
- **Agent Engineering Implication:** Covers static/dynamic scanning, threat intel, bug bounties, pentesting, supply chain monitoring, AND persistent automated verification/validation of agent guardrails and configurations (`VDR-CSO-DET`).

#### `FRD-VLR` — Vulnerability Response `[HIGH-AGENT]`
- **JSON Path:** `FRD.data.all.FRD-VLR`
- **Alternate Forms (`alts`):** `vulnerability response`, `respond to vulnerabilities`, `respond`, `response`, `responded`
- **Official Definition:** The systematic process of tracking, evaluating, mitigating, monitoring, remediating, assessing exploitation, reporting, and otherwise managing detected vulnerabilities.
- **Official Note:** This definition applies to other forms such as "respond to vulnerabilities" or simply "response" / "responded" used in FedRAMP materials.
- **Agent Engineering Implication:** End-to-end triage, PAIN/LEV/IRV evaluation, mitigation, remediation, exploitation assessment, and machine-readable reporting (`VDR-CSO-RES`, `VER`).

#### `FRD-VUL` — Vulnerability `[HIGH-AGENT]`
- **JSON Path:** `FRD.data.all.FRD-VUL`
- **Alternate Forms (`alts`):** `vulnerability`, `vulnerabilities`
- **Official Definition:** Has the meaning given to "security vulnerability" in 6 USC § 650 (25), which is "any attribute of hardware, software, process, or procedure that could enable or facilitate the defeat of [...] management, operational, and technical controls used to protect against an unauthorized effort to adversely affect the confidentiality, integrity, and availability of an information system or its information." This includes gaps in Rev5 Controls and 20x Key Security Indicators, software vulnerabilities, misconfigurations, exposures, weak credentials, insecure services, and all other such potential weaknesses in protection (intentional or unintentional).
- **Reference:** [6 USC § 650 (25)](https://www.govinfo.gov/app/details/USCODE-2024-title6/USCODE-2024-title6-chap1-subchapXVIII-sec650)
- **Agent Engineering Implication:** Broader than CVEs: explicitly includes gaps in 20x KSIs or Rev5 controls, misconfigurations, prompt-injection / tool-abuse exposures, over-privileged agent tokens, weak credentials, and broken VDR pipelines (`VDR-CSO-FAV`).

### Incident (5)

#### `FRD-FIR` — Final Incident Report (FIR)
- **JSON Path:** `FRD.data.all.FRD-FIR`
- **Alternate Forms (`alts`):** `final incident report`, `final incident reports`, `FIR`, `FIRs`
- **Official Definition:** A final report after recovery from an incident that is supplied by FedRAMP Certified cloud service providers to FedRAMP and agency customers, following FedRAMP Incident Evaluation and Communication rules.

#### `FRD-FRI` — FedRAMP Reportable Incident `[CRITICAL-AGENT]`
- **JSON Path:** `FRD.data.all.FRD-FRI`
- **Alternate Forms (`alts`):** `FedRAMP Reportable Incident`, `FedRAMP Reportable Incidents`
- **Official Definition:** An incident that affects the confidentiality or integrity of federal customer data or is likely to affect the confidentiality or integrity of federal customer data.
- **Agent Engineering Implication:** Triggered whenever an incident affects or is likely to affect confidentiality or integrity of `FRD-FCD`—including cross-tenant RAG leakage, unauthorized prompt/data exfiltration to an unapproved TPIR, or agent tool-abuse corrupting federal records (`IEC-CSO-EFR`).

#### `FRD-IIR` — Initial Incident Report (IIR)
- **JSON Path:** `FRD.data.all.FRD-IIR`
- **Alternate Forms (`alts`):** `initial incident report`, `initial incident reports`, `IIR`, `IIRs`
- **Official Definition:** An initial report about an incident that is supplied by FedRAMP Certified cloud service providers to FedRAMP and agency customers, following FedRAMP FedRAMP Incident Evaluation and Communication rules.

#### `FRD-INT` — Incident `[HIGH-AGENT]`
- **JSON Path:** `FRD.data.all.FRD-INT`
- **Alternate Forms (`alts`):** `incident`, `incidents`
- **Official Definition:** Has the meaning given in 44 USC § 3552 (b)(2) which is "an occurrence that (A) actually or imminently jeopardizes, without lawful authority, the integrity, confidentiality, or availability of information or an information system; or (B) constitutes a violation or imminent threat of violation of law, security policies, security procedures, or acceptable use policies."
- **Reference:** [44 USC § 3552 (b)(2)](https://www.govinfo.gov/app/details/USCODE-2024-title44/USCODE-2024-title44-chap35-subchapII-sec3552)
- **Agent Engineering Implication:** Statutory FISMA definition (44 USC § 3552(b)(2)); includes imminent policy/AUP violations (e.g., runaway autonomous agent attempting unauthorized exfiltration).

#### `FRD-OIR` — Ongoing Incident Report (OIR)
- **JSON Path:** `FRD.data.all.FRD-OIR`
- **Alternate Forms (`alts`):** `ongoing incident report`, `ongoing incident reports`, `OIR`, `OIRs`
- **Official Definition:** A recurring report about an ongoing incident that is supplied by FedRAMP Certified cloud service providers to FedRAMP and agency customers, following the FedRAMP Incident Evaluation and Communication rules.

### Customer Effect (4)

#### `FRD-DCE` — Debilitating Customer Effect `[HIGH-AGENT]`
- **JSON Path:** `FRD.data.all.FRD-DCE`
- **Alternate Forms (`alts`):** `debilitating customer effect`, `debilitating customer effects`
- **Official Definition:** An unwanted customer effect that interrupts use of the cloud service for most users or compromises the integrity or confidentiality of most federal customer data. If the adverse customer effect is unknown then it should be treated as if it is debilitating until proven otherwise.
- **Agent Engineering Implication:** Anchors `PAIN-4`/`PAIN-5`. Crucial fail-safe: unknown adverse customer effect MUST be treated as debilitating until proven otherwise.

#### `FRD-DCF` — Disruptive Customer Effect `[MEDIUM-AGENT]`
- **JSON Path:** `FRD.data.all.FRD-DCF`
- **Alternate Forms (`alts`):** `disruptive customer effect`, `disruptive customer effects`
- **Official Definition:** An unwanted customer effect that interrupts use of the cloud service for many users for less than 24 hours, or that compromises the integrity or confidentiality of large amounts or many types of federal customer data.
- **Agent Engineering Implication:** Anchors `PAIN-3` (single agency) and `PAIN-4` (multi-agency); interrupts many users <24h or compromises large amounts/many types of `FRD-FCD`.

#### `FRD-MCE` — Minimal Customer Effect `[MEDIUM-AGENT]`
- **JSON Path:** `FRD.data.all.FRD-MCE`
- **Alternate Forms (`alts`):** `minimal customer effect`, `minimal customer effects`
- **Official Definition:** An unwanted customer effect that is only noticeable by some users. This includes minor inconveniences such as reduced performance.
- **Agent Engineering Implication:** Anchors `PAIN-1`; minor noticeable inconveniences (e.g., elevated LLM latency) without data compromise.

#### `FRD-NCE` — Narrow Customer Effect `[MEDIUM-AGENT]`
- **JSON Path:** `FRD.data.all.FRD-NCE`
- **Alternate Forms (`alts`):** `narrow customer effect`, `narrow customer effects`
- **Official Definition:** An unwanted customer effect that interrupts use of the cloud service for some users for less than 12 hours, or that compromises the integrity or confidentiality of an extremely limited amount and type of federal customer data.
- **Agent Engineering Implication:** Anchors `PAIN-2`; interrupts some users <12h or compromises an extremely limited amount/type of `FRD-FCD`.

### Accounts (2)

#### `FRD-PAC` — Privileged Account `[HIGH-AGENT]`
- **JSON Path:** `FRD.data.all.FRD-PAC`
- **Alternate Forms (`alts`):** `privileged account`, `privileged accounts`
- **Official Definition:** An account with elevated privileges that enables administrative functions over some aspect of the cloud service offering that may affect the confidentiality, integrity, or availability of information beyond those given to normal users; levels of privilege may vary wildly.
- **Official Note:** Any references to privileged accounts in FedRAMP materials should be presumed to apply to privileged roles or other similar capabilities that are used to assign privileges to privileged accounts.
- **Agent Engineering Implication:** Covers BOTH human admin accounts AND privileged non-human service/agent identities/roles that can modify CSO state, access cross-tenant data, or invoke state-changing tools (`KSI-IAM-JIT`, `KSI-IAM-SUS`, `SCG-CSO-SDF`).

#### `FRD-TLA` — Top-Level Administrative Account `[HIGH-AGENT]`
- **JSON Path:** `FRD.data.all.FRD-TLA`
- **Alternate Forms (`alts`):** `top-level administrative account`, `top-level administrative accounts`
- **Official Definition:** The most privileged account with the highest level of access within a cloud service offering for a customer organization, typically with complete control over all aspects of the cloud service offering, including managing resources, users, access, privileges, and the account itself.
- **Official Note:** Any references to top-level administrative accounts in FedRAMP materials should be presumed to apply to top-level administrative roles or other similar capabilities that are used to assign top-level administrative account privileges.
- **Agent Engineering Implication:** Highest customer-org admin account/role; agents MUST NOT operate with persistent TLA privileges and MUST respect SCG secure defaults (`SCG-CSO-RSC`/`SCG-CSO-SDF`).

### Certification (12)

#### `FRD-ART` — Artifacts `[MEDIUM-AGENT]`
- **JSON Path:** `FRD.data.all.FRD-ART`
- **Alternate Forms (`alts`):** `artifact`, `artifacts`
- **Official Definition:** Security-related materials that supply information regarding or evidence of functions, policies, decisions, procedures, operations, or other such activities, for the purposes of obtaining and maintaining a FedRAMP Certification. All such artifacts are considered FedRAMP Certification Data and are included in the FedRAMP Certification Package.
- **Agent Engineering Implication:** Objective evidence materials included in the Certification Package; default FRR/KSI artifact expectations are defined in `info.default_artifacts`.

#### `FRD-CCL` — Certification Class
- **JSON Path:** `FRD.data.all.FRD-CCL`
- **Alternate Forms (`alts`):** `Certification Class`, `Certification Classes`
- **Official Definition:** The category of assurance that a cloud service offering supplies to federal government customers following FedRAMP Practices, increasing from minimal assurance at Class A to significant assurance at Class D; currently available categories are Class A, B, C, or D.

#### `FRD-CPF` — Certification Profile
- **JSON Path:** `FRD.data.all.FRD-CPF`
- **Alternate Forms (`alts`):** `Certification Profile`, `Certification Profiles`
- **Official Definition:** The combination of a FedRAMP Certification Type (Rev5 or 20x), FedRAMP Certification Path (Program or Agency), and FedRAMP Certification Class (A, B, C, or D) for a cloud service offering.

#### `FRD-CPH` — Certification Path
- **JSON Path:** `FRD.data.all.FRD-CPH`
- **Alternate Forms (`alts`):** `Certification Path`, `Certification Paths`
- **Official Definition:** The underlying source of the FedRAMP Certification, either from a federal agency sponsored authorization to operate or directly from FedRAMP itself. The agency path is a legacy path that is only available for FedRAMP Rev5 and still requires review and approval from FedRAMP.

#### `FRD-CRD` — Certification Data `[MEDIUM-AGENT]`
- **JSON Path:** `FRD.data.all.FRD-CRD`
- **Alternate Forms (`alts`):** `certification data`
- **Official Definition:** The collective information required by FedRAMP for initial and ongoing FedRAMP Certification of a cloud service offering, including the FedRAMP Certification Package.
- **Official Note:** In FedRAMP documentation, certification data always refers to FedRAMP Certification Data unless otherwise specified.
- **Agent Engineering Implication:** All required initial and ongoing certification information; governed by `CDS`, must carry the CSO's FedRAMP ID (`CDS-CSO-FID`), and must avoid leaking secrets/exploit specifics (`CDS-CSO-RIS`).

#### `FRD-CRP` — Certification Package `[MEDIUM-AGENT]`
- **JSON Path:** `FRD.data.all.FRD-CRP`
- **Alternate Forms (`alts`):** `certification package`, `certification packages`
- **Official Definition:** Has meaning from 44 USC § 3607 (b)(8) given to "authorization package", which is "the essential information that can be used by an agency to determine whether to authorize the operation of an information system or the use of a designated set of common controls for all cloud computing products and services [certified] by FedRAMP."
- **Official Note:** In FedRAMP documentation, certification package always refers to a FedRAMP Certification Package unless otherwise specified.
- **Reference:** [44 USC § 3607 (b)(8)](https://fedramp.gov/2026/authority/law/#b-additional-definitions)
- **Agent Engineering Implication:** Statutory authorization package (`44 USC § 3607(b)(8)`): CPO + SDR + OCR + IVV findings (`FRC-CSO-PKG`), maintained every 2w/1w (20x C/D) or 1y/6m (Rev5 C/D).

#### `FRD-CTY` — Certification Type
- **JSON Path:** `FRD.data.all.FRD-CTY`
- **Alternate Forms (`alts`):** `Certification Type`, `Certification Types`
- **Official Definition:** The form of assurance that a cloud service offering supplies to federal government customers following FedRAMP Practices, either Rev5 or 20x. Rev5 follows a legacy approach based primarily on documented plans while 20x follows a modern approach based primarily on measured outcomes.

#### `FRD-FCR` — FedRAMP Certification Report
- **JSON Path:** `FRD.data.all.FRD-FCR`
- **Alternate Forms (`alts`):** `FedRAMP Certification Report`, `FedRAMP certification report`, `certification report`
- **Official Definition:** A report that is produced by FedRAMP documenting the results of a FedRAMP Certification assessment. This report is typically produced after the initial FedRAMP Certification assessment on the Program Certification Path and updated as necessary during ongoing FedRAMP Certification, but may be produced at any time by FedRAMP as part of ongoing FedRAMP Certification activities for any cloud service offering (such as corrective action). Cloud service offerings must include these reports in their FedRAMP Certification Package.

#### `FRD-FCT` — FedRAMP Certified
- **JSON Path:** `FRD.data.all.FRD-FCT`
- **Alternate Forms (`alts`):** `FedRAMP Certified`, `FedRAMP certified`, `certified`, `FedRAMP authorized`, `FedRAMP Authorized`, `authorized`
- **Official Definition:** The status of a cloud service offering that has received FedRAMP Certification and meets the legal requirement to be FedRAMP authorized.
- **Official Note:** FedRAMP uses "FedRAMP Certified" as the current program term for cloud service offerings that satisfy the statutory concept of FedRAMP authorization.

#### `FRD-INC` — Initial Certification
- **JSON Path:** `FRD.data.all.FRD-INC`
- **Alternate Forms (`alts`):** `initial certification`, `initial certifications`
- **Official Definition:** The first FedRAMP Certification of a cloud service offering based on the applicable FedRAMP Practices.

#### `FRD-ONC` — Ongoing Certification
- **JSON Path:** `FRD.data.all.FRD-ONC`
- **Alternate Forms (`alts`):** `ongoing certification`, `ongoing certifications`
- **Official Definition:** The continued FedRAMP Certification of a cloud service offering based on the applicable FedRAMP Practices.

#### `FRD-QTR` — Quarterly Review
- **JSON Path:** `FRD.data.all.FRD-QTR`
- **Alternate Forms (`alts`):** `quarterly review`, `quarterly reviews`
- **Official Definition:** A regular synchronous meeting hosted by a FedRAMP Certified cloud service provider for agency customers, following FedRAMP Collaborative Continuous Monitoring rules.

### Assessment (2)

#### `FRD-IFA` — Initial FedRAMP Assessment
- **JSON Path:** `FRD.data.all.FRD-IFA`
- **Alternate Forms (`alts`):** `initial FedRAMP assessment`, `IFRA`
- **Official Definition:** The first full assessment of a cloud service offering obtaining FedRAMP Certification, coordinated by the provider with all necessary assessors, that results in a FedRAMP Certification.

#### `FRD-PFA` — Persistent FedRAMP Assessment
- **JSON Path:** `FRD.data.all.FRD-PFA`
- **Alternate Forms (`alts`):** `persistent FedRAMP assessment`, `PFRA`
- **Official Definition:** Follow-on assessments of a cloud service offering focused on Key Security Indicators, coordinated by the provider with all necessary assessors, to maintain FedRAMP Certification or change its FedRAMP Certification class.

### Force of the Rule (5)

#### `FRD-MAY` — MAY `[NORM-FORCE]`
- **JSON Path:** `FRD.data.all.FRD-MAY`
- **Official Definition:** The rule is truly optional. Parties SHOULD address such rules in their security documentation by explaining their decisions about how they handle such rules.
- **Official Note:** This definition only applies when the term is used in all capital letters in FedRAMP materials, otherwise the plain language meaning applies.
- **Agent Engineering Implication:** Truly optional in FRR rules; providers SHOULD still document their decision in security documentation (e.g., `CDS-CSO-PSM` is `MAY` at Class C, `MUST` at Class D).

#### `FRD-MNT` — MUST NOT `[NORM-FORCE]`
- **JSON Path:** `FRD.data.all.FRD-MNT`
- **Official Definition:** The rule is an absolute prohibition. Parties MUST meet such rules and address them in their security documentation. Failure to follow the rule is a vulnerability likely requiring corrective action and/or the denial of initial or ongoing FedRAMP Certification.
- **Official Note:** This definition only applies when the term is used in all capital letters in FedRAMP materials, otherwise the plain language meaning applies.
- **Agent Engineering Implication:** Absolute prohibition in FRR rules; violation is a `FRD-VUL`.

#### `FRD-MST` — MUST `[NORM-FORCE]`
- **JSON Path:** `FRD.data.all.FRD-MST`
- **Official Definition:** The rule is an absolute requirement. Parties MUST meet such rules and address them in their security documentation. Failure to follow the rule is a vulnerability likely requiring corrective action and/or the denial of initial or ongoing FedRAMP Certification.
- **Official Note:** This definition only applies when the term is used in all capital letters in FedRAMP materials, otherwise the plain language meaning applies.
- **Agent Engineering Implication:** Absolute requirement in FRR rules; noncompliance is a `FRD-VUL` risking Corrective Action Plan or denial/revocation of certification. (Note: KSIs never carry RFC-2119 force.)

#### `FRD-SHD` — SHOULD `[NORM-FORCE]`
- **JSON Path:** `FRD.data.all.FRD-SHD`
- **Official Definition:** There may exist valid reasons in particular circumstances to ignore this rule, but the full implications must be understood and carefully weighed. Parties MUST address such rules in their security documentation by explaining their decisions about how they handle such rules.
- **Official Note:** This definition only applies when the term is used in all capital letters in FedRAMP materials, otherwise the plain language meaning applies.
- **Agent Engineering Implication:** Expected practice in FRR rules; exceptions require documented risk justification in the `FRD-SDR` (e.g., `CMU-CSO-UVM` at Class C is `SHOULD`, rising to `MUST` at Class D).

#### `FRD-SNT` — SHOULD NOT `[NORM-FORCE]`
- **JSON Path:** `FRD.data.all.FRD-SNT`
- **Official Definition:** There may exist valid reasons in particular circumstances when the particular action is acceptable or even useful, but the full implications must be understood and carefully weighed. Parties MUST address such rules in their security documentation by explaining their decisions about how they handle such rules.
- **Official Note:** This definition only applies when the term is used in all capital letters in FedRAMP materials, otherwise the plain language meaning applies.
- **Agent Engineering Implication:** Expected avoidance in FRR rules; exceptions require documented justification in the `FRD-SDR`.

### Stakeholder (7)

#### `FRD-AAP` — All Affected Parties
- **JSON Path:** `FRD.data.all.FRD-AAP`
- **Alternate Forms (`alts`):** `all affected parties`
- **Official Definition:** All federal entities whose interests are affected directly or are likely to be affected directly in the event of a vulnerability or incident related to federal customer data. This always includes FedRAMP and directly impacted federal customer agencies.

#### `FRD-ADV` — Advisor
- **JSON Path:** `FRD.data.all.FRD-ADV`
- **Alternate Forms (`alts`):** `advisor`, `advisors`
- **Official Definition:** An entity that helps a provider understand, prepare for, or maintain FedRAMP Certification without replacing the provider's responsibility or the assessor's independence.

#### `FRD-AGY` — Agency
- **JSON Path:** `FRD.data.all.FRD-AGY`
- **Alternate Forms (`alts`):** `agency`, `agencies`
- **Official Definition:** Has the meaning given in 44 U.S. Code § 3502 (1), which is "any executive department, military department, Government corporation, Government controlled corporation, or other establishment in the executive branch of the Government (including the Executive Office of the President), or any independent regulatory agency, but does not include—(A) the Government Accountability Office; (B) Federal Election Commission; (C) the governments of the District of Columbia and of the territories and possessions of the United States, and their various subdivisions; or (D) Government-owned contractor-operated facilities, including laboratories engaged in national defense research and production activities."
- **Reference:** [44 U.S. Code § 3502 (1)](https://www.govinfo.gov/app/details/USCODE-2023-title44/USCODE-2023-title44-chap35-subchapI-sec3502)

#### `FRD-ANA` — All Necessary Assessors
- **JSON Path:** `FRD.data.all.FRD-ANA`
- **Alternate Forms (`alts`):** `all necessary assessors`
- **Official Definition:** All entities who participate in the FedRAMP assessment of a cloud service offering in the context of a FedRAMP Certification. This always includes FedRAMP and any FedRAMP Recognized independent assessor contracted by a provider to perform a FedRAMP assessment.

#### `FRD-ANP` — All Necessary Parties
- **JSON Path:** `FRD.data.all.FRD-ANP`
- **Alternate Forms (`alts`):** `all necessary parties`
- **Official Definition:** All entities whose interests are affected directly by activity related to a specific cloud service offering in the context of FedRAMP Certifications. This always includes FedRAMP and any agency customer who is using the cloud service offering, but may include additional parties depending on agreements made by the cloud service provider (such as consultants or independent assessors). Potential agency customers or third-party cloud service providers should also be included in most cases but this is not a mandatory requirement under FedRAMP because the cloud service provider may choose who they wish to do business with.

#### `FRD-ASR` — Assessor
- **JSON Path:** `FRD.data.all.FRD-ASR`
- **Alternate Forms (`alts`):** `assessor`, `assessors`
- **Official Definition:** An assessor that performs assessment, verification, or validation activities for a cloud service offering seeking to obtain or maintain FedRAMP Certification; FedRAMP is the final assessor for FedRAMP Certification, but FedRAMP Recognized independent assessment services are typically also utilized.
- **Official Note:** FedRAMP has transitioned from using the historical term "Third-Party Assessment Organization (3PAO)" to align with the explicit terminology used in the FedRAMP Authorization Act and to avoid the confusion caused when the same organizations provide both assessment and advisory services to different customers while being referred to as a 3PAO.

#### `FRD-PRV` — Provider
- **JSON Path:** `FRD.data.all.FRD-PRV`
- **Alternate Forms (`alts`):** `provider`, `providers`, `cloud service provider`, `cloud service providers`
- **Official Definition:** The cloud service provider responsible for a cloud service offering in the context of FedRAMP Certification.
- **Official Note:** FedRAMP Consolidated Rules frequently refer to providers without using the full term "cloud service provider" or acronym "CSP".

---

## Alphabetical Quick Index (All 81 `FRD-<KEY>` IDs)

| FRD ID | Term | Official Tag | Agent Priority |
| :--- | :--- | :--- | :--- |
| `FRD-AAP` | All Affected Parties | Stakeholder | Standard |
| `FRD-ACV` | Accepted Vulnerability | Vulnerability | `[MEDIUM-AGENT]` |
| `FRD-ADP` | Adaptive Change | Significant Changes | `[HIGH-AGENT]` |
| `FRD-ADV` | Advisor | Stakeholder | Standard |
| `FRD-AGY` | Agency | Stakeholder | Standard |
| `FRD-ANA` | All Necessary Assessors | Stakeholder | Standard |
| `FRD-ANP` | All Necessary Parties | Stakeholder | Standard |
| `FRD-ART` | Artifacts | Certification | `[MEDIUM-AGENT]` |
| `FRD-ASR` | Assessor | Stakeholder | Standard |
| `FRD-CCC` | Certification Class Change | Significant Changes | `[MEDIUM-AGENT]` |
| `FRD-CCL` | Certification Class | Certification | Standard |
| `FRD-CPF` | Certification Profile | Certification | Standard |
| `FRD-CPH` | Certification Path | Certification | Standard |
| `FRD-CRD` | Certification Data | Certification | `[MEDIUM-AGENT]` |
| `FRD-CRP` | Certification Package | Certification | `[MEDIUM-AGENT]` |
| `FRD-CSO` | Cloud Service Offering | Core & General Concepts | `[MEDIUM-AGENT]` |
| `FRD-CTY` | Certification Type | Certification | Standard |
| `FRD-DCE` | Debilitating Customer Effect | Customer Effect | `[HIGH-AGENT]` |
| `FRD-DCF` | Disruptive Customer Effect | Customer Effect | `[MEDIUM-AGENT]` |
| `FRD-DFT` | Drift | Core & General Concepts | `[HIGH-AGENT]` |
| `FRD-DTM` | Deterministic Telemetry | Core & General Concepts | `[CRITICAL-AGENT]` |
| `FRD-FCD` | Federal Customer Data | Core & General Concepts | `[CRITICAL-AGENT]` |
| `FRD-FCR` | FedRAMP Certification Report | Certification | Standard |
| `FRD-FCT` | FedRAMP Certified | Certification | Standard |
| `FRD-FIN` | FedRAMP Independent Assessment | Core & General Concepts | Standard |
| `FRD-FIR` | Final Incident Report (FIR) | Incident | Standard |
| `FRD-FMV` | Fully Mitigated Vulnerability | Vulnerability | `[MEDIUM-AGENT]` |
| `FRD-FPR` | FedRAMP Practices | Core & General Concepts | `[MEDIUM-AGENT]` |
| `FRD-FPV` | False Positive Vulnerability | Vulnerability | `[MEDIUM-AGENT]` |
| `FRD-FRA` | FedRAMP Recognized | Core & General Concepts | Standard |
| `FRD-FRI` | FedRAMP Reportable Incident | Incident | `[CRITICAL-AGENT]` |
| `FRD-FSI` | FedRAMP Security Inbox | Core & General Concepts | `[MEDIUM-AGENT]` |
| `FRD-HAN` | Handle | Core & General Concepts | `[HIGH-AGENT]` |
| `FRD-IFA` | Initial FedRAMP Assessment | Assessment | Standard |
| `FRD-IIR` | Initial Incident Report (IIR) | Incident | Standard |
| `FRD-INC` | Initial Certification | Certification | Standard |
| `FRD-INT` | Incident | Incident | `[HIGH-AGENT]` |
| `FRD-IRS` | Information Resource | Information Resource | `[HIGH-AGENT]` |
| `FRD-IRV` | Internet-Reachable Vulnerability (IRV) | Vulnerability | `[HIGH-AGENT]` |
| `FRD-KEV` | Known Exploited Vulnerability (KEV) | Vulnerability | `[HIGH-AGENT]` |
| `FRD-LEV` | Likely Exploitable Vulnerability (LEV) | Vulnerability | `[HIGH-AGENT]` |
| `FRD-LKY` | Likely | Core & General Concepts | Standard |
| `FRD-MAS` | Minimum Assessment Scope | Core & General Concepts | `[CRITICAL-AGENT]` |
| `FRD-MAY` | MAY | Force of the Rule | `[NORM-FORCE]` |
| `FRD-MBI` | Machine-Based (Information Resources) | Information Resource | `[HIGH-AGENT]` |
| `FRD-MCE` | Minimal Customer Effect | Customer Effect | `[MEDIUM-AGENT]` |
| `FRD-MGN` | Machine-Generated | Core & General Concepts | `[HIGH-AGENT]` |
| `FRD-MNT` | MUST NOT | Force of the Rule | `[NORM-FORCE]` |
| `FRD-MRD` | Machine-Readable | Core & General Concepts | `[HIGH-AGENT]` |
| `FRD-MST` | MUST | Force of the Rule | `[NORM-FORCE]` |
| `FRD-NCE` | Narrow Customer Effect | Customer Effect | `[MEDIUM-AGENT]` |
| `FRD-OCR` | Ongoing Certification Report (OCR) | Core & General Concepts | Standard |
| `FRD-ODV` | Overdue Vulnerability | Vulnerability | `[MEDIUM-AGENT]` |
| `FRD-OIR` | Ongoing Incident Report (OIR) | Incident | Standard |
| `FRD-ONC` | Ongoing Certification | Certification | Standard |
| `FRD-PAC` | Privileged Account | Accounts | `[HIGH-AGENT]` |
| `FRD-PAI` | Potential Agency Impact | Core & General Concepts | `[CRITICAL-AGENT]` |
| `FRD-PER` | Persistently | Core & General Concepts | `[HIGH-AGENT]` |
| `FRD-PFA` | Persistent FedRAMP Assessment | Assessment | Standard |
| `FRD-PMV` | Partially Mitigated Vulnerability | Vulnerability | `[MEDIUM-AGENT]` |
| `FRD-PRO` | Promptly | Core & General Concepts | `[MEDIUM-AGENT]` |
| `FRD-PRV` | Provider | Stakeholder | Standard |
| `FRD-QTR` | Quarterly Review | Certification | Standard |
| `FRD-RGL` | Regularly | Core & General Concepts | `[MEDIUM-AGENT]` |
| `FRD-RMV` | Remediated Vulnerability | Vulnerability | `[MEDIUM-AGENT]` |
| `FRD-RSP` | Responsibly | Core & General Concepts | `[HIGH-AGENT]` |
| `FRD-RTR` | Routine Recurring Change | Significant Changes | `[MEDIUM-AGENT]` |
| `FRD-SCT` | Security Category | Core & General Concepts | `[MEDIUM-AGENT]` |
| `FRD-SDR` | Security Decision Record (SDR) | Core & General Concepts | `[HIGH-AGENT]` |
| `FRD-SGC` | Significant Change | Significant Changes | `[HIGH-AGENT]` |
| `FRD-SHD` | SHOULD | Force of the Rule | `[NORM-FORCE]` |
| `FRD-SNT` | SHOULD NOT | Force of the Rule | `[NORM-FORCE]` |
| `FRD-TLA` | Top-Level Administrative Account | Accounts | `[HIGH-AGENT]` |
| `FRD-TPR` | Third-Party Information Resource | Information Resource | `[CRITICAL-AGENT]` |
| `FRD-TRC` | Trust Center | Core & General Concepts | `[MEDIUM-AGENT]` |
| `FRD-TRF` | Transformative Change | Significant Changes | `[CRITICAL-AGENT]` |
| `FRD-VLD` | Vulnerability Detection | Vulnerability | `[HIGH-AGENT]` |
| `FRD-VLN` | Validation | Core & General Concepts | `[HIGH-AGENT]` |
| `FRD-VLR` | Vulnerability Response | Vulnerability | `[HIGH-AGENT]` |
| `FRD-VRF` | Verification | Core & General Concepts | `[HIGH-AGENT]` |
| `FRD-VUL` | Vulnerability | Vulnerability | `[HIGH-AGENT]` |
