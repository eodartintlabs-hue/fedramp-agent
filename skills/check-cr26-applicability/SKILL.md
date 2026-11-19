---
name: check-cr26-applicability
description: "Determine exact FedRAMP Consolidated Rules for 2026 (CR-26, version 2026.11.02.01) applicability, Minimum Assessment Scope (MAS) inclusion, RFC-2119 force elevations, and pending 20x Class D exclusions for AI agents across Class C (20x + Rev5), Class D (Rev5 + 20x-ready), runtime-cso, and internal-devsecops profiles."
---

# Check CR-26 Applicability

Use this skill to determine which FedRAMP Consolidated Rules for 2026 (`CR-26`, dataset version `2026.11.02.01`) requirements, Key Security Indicators (`KSI`), and `Rev5` Control Guidance (`CTL`) entries bind a specific AI agent, and at what normative force (`MUST`, `MUST NOT`, `SHOULD`, `SHOULD NOT`, `MAY`).

Defer full rule text and catalog lookups to `relevant-rulesets.md` and controlled definitions to `compliance/frd-glossary.md` rather than relying on memory.

## Step 1 — Establish the Five Scoping Dimensions

Record all five inputs before evaluating rules; flag any missing input that could change the verdict:

1. **Service Class (`fedramp.service_class`):** `C` (Moderate assurance) or `D` (High assurance).
2. **Certification Track(s) (`fedramp.certification_tracks`):** `20x`, `Rev5`, or both (`["Rev5", "20x"]`).
3. **Certification Path (`fedramp.certification_path`):** `Program`, `Agency`, or `Hybrid`.
4. **Agent Profile (`agent_profile`):** `runtime-cso` or `internal-devsecops` (or confirm whether the software is separately delivered client software installed on agency systems).
5. **Data & Privilege Footprint:** Whether the agent handles `Federal Customer Data` (`FRD-FCD`), handles sensitive metadata (`MAS-CSO-MDI`), or can affect the confidentiality, integrity, or availability (`CIA`) of the Cloud Service Offering (`FRD-CSO`).

## Step 2 — Evaluate Minimum Assessment Scope (`MAS`) Boundary

Apply CR-26 `MAS` rules in strict order:

1. **Separately Delivered Agency-Installed Client Exclusion (`MAS-CSO-IIR` Note 2):** Software delivered separately for installation on agency-operated systems and not operated as a provider-managed shared-responsibility cloud service is outside FedRAMP CSO scope.
2. **Mandatory In-Boundary Inclusion (`MAS-CSO-IIR`, `MAS-CSO-MDI`):** If the provider-operated agent handles `FRD-FCD`, processes or stores metadata likely to impact `FRD-FCD` `CIA`, mutates production CSO infrastructure/configuration, signs production artifacts, or publishes certification evidence, `in_minimum_assessment_scope` **MUST** be `true`.
3. **Unconnected Internal Workload Exclusion (`MAS-CSO-SUP`):** An `internal-devsecops` agent may set `in_minimum_assessment_scope: false` **only** when it touches zero `FRD-FCD`, zero production metadata, and holds zero privileges over production infrastructure, builds, signing, or compliance evidence.
4. **Application Layer (`20x`):** Under `FRC-CSX-MAS`, `20x` offerings **SHOULD** include user-facing agent interfaces inside `MAS`.

## Step 3 — Apply Class C vs. Class D Normative Elevations

Check every high-consequence class delta below:

- **Cryptographic Modules (`CMU-CSO-UVM`, `CMU-CSO-CMD`, `CTL.SC.SC-13`):**
  - Both classes **MUST** document all cryptographic modules (`CMU-CSO-CMD`).
  - **Class C:** **SHOULD** use active CMVP FIPS-validated modules (non-validated modules require senior-official risk acceptance in the `SDR` per `SDR-CSO-FRR`).
  - **Class D:** **MUST** use active CMVP FIPS-validated modules (`cryptography.fips_140_3_validated_modules: true` mandatory).
- **Digital Identity & Encrypted Assertions (`CTL.IA.IA-05`):**
  - Both classes **MUST** encrypt assertions across third parties (`OIDC` `JWE` or `SAML` XML-Encryption) and disable local password bypass (`KSI-IAM-APM`).
  - **Class C:** NIST Digital Identity Guidelines **`IAL2/AAL2/FAL2`** minimum.
  - **Class D:** NIST Digital Identity Guidelines **`IAL3/AAL3/FAL3`** mandatory.
- **Data, Processing & Service Residency (`CTL.SA.SA-09-05`):**
  - **Class C:** Document processing and storage locations for all `FRD-FCD`.
  - **Class D:** Restrict **all** information processing, `FRD-FCD`, and system services (including primary/fallback inference routes, caches, embeddings, and backups) to **U.S. / U.S. Territories / geographic locations under U.S. jurisdiction** (`model_serving.us_jurisdiction_only: true`).
- **Per-Service Certification Materials (`CDS-CSO-PSM`):**
  - **Class C:** **MAY** supply per-service certification materials.
  - **Class D:** **MUST** supply per-service certification materials (`lifecycle.per_service_certification_artifacts: true`).
- **Vulnerability Evaluation & Incident Escalation (`VER-TFR-EVU`, `VDR-TFR-PVR`, `VER-TFR-NRI`, `VDR-TFR-MVX`, `VDR-TFR-MVF`):**
  - **Evaluation SLA (`VER-TFR-EVU`):** Class C **SHOULD** evaluate within **`<= 5` days**; Class D **SHOULD** evaluate within **`<= 2` days**.
  - **PAIN=5 `IRV+LEV` Mitigation (`VDR-TFR-PVR`):** Class C **`2` days** vs. Class D **`12` hours**.
  - **Non-Internet-Reachable `PAIN=5` `LEV` Incident Escalation (`VER-TFR-NRI`):** Class C **`MAY`** vs. Class D **`SHOULD`** treat as a FedRAMP Reportable Incident until mitigated to `<= N4`.
  - **Persistent Machine Verification:** `Rev5` Class C and Class D **MUST** verify monthly (`VDR-TFR-MVF`); `20x` Class C **MUST** verify every **`3` days** (`VDR-TFR-MVX`).

## Step 4 — Enforce Zero-Invention on Pending `20x` Class D Entries

When `service_class == "D"` and `"20x"` is evaluated against CR-26 `2026.11.02.01`:

1. Explicitly report that five `20x` indicators — **`KSI-CNA-EIS`**, **`KSI-MLA-ALA`**, **`KSI-SVC-PRR`**, **`KSI-SVC-RUD`**, and **`KSI-SVC-VCM`** — plus **`VDR-TFR-MVX`** omit `varies_by_class.d` in `2026.11.02.01` (`20x` Class D specifics are scheduled for the `2027` Phase 4 Pilot per `SDR-CSX-KMT`).
2. **Never** copy Class C statements into Class D or invent normative force for `KSI` entries. Anchor Class D requirements in common `FRR` rules and `Rev5` High `CTL` entries (`CTL.SC.SC-07`, `CTL.SC.SC-13`, `CTL.AU.AU-06`, `CTL.CM.CM-14`, `CTL.SA.SA-09-05`, `CTL.IA.IA-05`).

## Output Format

1. **Scope Summary:** Class, track(s), path, profile, and `MAS` inclusion verdict (`in_minimum_assessment_scope: true | false` or `outside-fedramp-cso-scope`).
2. **Applicable Mandates & Class Deltas:** Bullet list citing exact `FRR`, `KSI`, and `CTL` IDs with their exact force (`MUST`/`SHOULD`/`MAY` for `FRR`; capability statement for `KSI`).
3. **Compliance Gaps / Warnings:** Specific manifest or architectural discrepancies and required fixes.
