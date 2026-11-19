# ADR-002: Class C vs. Class D Compliance Profiles and Non-Invention Discipline

**Status:** Accepted  
**Date:** 2026-11-19  
**Authors:** Dual-Audience Documentation & Governance Lead, with Rules Analyst review

---

## Context

FedRAMP Consolidated Rules 2026 (CR-26, `info.version` `2026.11.02.01`, `last_updated` `2026-11-02`) spans both `20x` and `Rev5` frameworks and introduces sharp normative differences between **Class C** and **Class D** offerings. Engineering teams frequently confuse Class C (`SHOULD`/`MAY`, `IAL2`, `5-day` triage) with Class D (`MUST`, `IAL3`, U.S. residency, `2-day` triage), or worse, fabricate `20x` Class D KSI requirements where CR-26 `2026.11.02.01` intentionally omits them pending 2027 updates.

## Decision

We encode explicit, machine-enforced **Class C** and **Class D** compliance profiles into `fedramp-agent` schemas, templates, and validators, paired with a strict **non-invention discipline** for pending `20x` Class D indicators.

### D1. Enforced Class C vs. Class D Deltas

[../../tools/validate_manifest.py](../../tools/validate_manifest.py), [../../schemas/agent-manifest.schema.json](../../schemas/agent-manifest.schema.json), and reference manifests ([../../templates/agent-manifest.example.class-c.json](../../templates/agent-manifest.example.class-c.json), [../../templates/agent-manifest.example.class-d.json](../../templates/agent-manifest.example.class-d.json)) enforce the exact CR-26 deltas:

| Rule / Control | Class C | Class D |
| :--- | :--- | :--- |
| `CMU-CSO-UVM` | `SHOULD` use active FIPS-validated crypto modules | `MUST` use active FIPS-validated crypto modules |
| `CDS-CSO-PSM` | `MAY` supply per-service FedRAMP Certification materials | `MUST` supply per-service FedRAMP Certification materials |
| `CTL.IA.IA-05` | `IAL2` / `AAL2` / `FAL2` | `IAL3` / `AAL3` / `FAL3` + encrypted SAML XML-Enc / OIDC JWE |
| `CTL.SA.SA-09-05` | Standard external service controls | Explicit U.S. / U.S. Territories / U.S. jurisdiction residency |
| `VER-TFR-EVU` | `5-day` vulnerability triage SLA | `2-day` vulnerability triage SLA |
| `VER-TFR-NRI` | `MAY` treat non-internet likely exploitable findings as incidents | `SHOULD` treat non-internet likely exploitable findings as incidents |

### D2. Scope Across `20x` and `Rev5`

- **Class C:** Supported on both `20x` and `Rev5`.
- **Class D:** Supported on `Rev5` today and structured to be `20x`-ready for 2027.

### D3. Non-Invention of Pending `20x` Class D Variants

In CR-26 `2026.11.02.01`, five KSIs (`KSI-CNA-EIS`, `KSI-MLA-ALA`, `KSI-SVC-PRR`, `KSI-SVC-RUD`, `KSI-SVC-VCM`) and `VDR-TFR-MVX` omit `varies_by_class.d`. All documentation ([../../relevant-rulesets.md](../../relevant-rulesets.md)), canonical agents ([../../agents/fedramp-compliance-reviewer.md](../../agents/fedramp-compliance-reviewer.md)), and reports **MUST** mark these as *"Not defined in 2026.11.02.01 (20x Class D coming 2027)"* and **MUST NOT** copy Class C text or invent Class D requirements.

## Alternatives Considered

- **Single lowest-common-denominator profile (Class D for all agents)** — Rejected because Class C teams would be blocked by `IAL3`, mandatory per-service CDS, and `2-day` SLAs not required for Class C offerings.
- **Extrapolating missing `20x` Class D KSIs from Class C** — Rejected because it violates FedRAMP CR-26 source-of-truth rules and would create false compliance failures ahead of the 2027 `20x` Class D publication.

## Consequences

- **Positive:** Clear, auditable separation of Class C and Class D requirements with automated CI enforcement and zero hallucinated `20x` Class D rules.
- **Negative:** Requires maintaining two example manifests and updating profiles when FedRAMP publishes `20x` Class D KSI variants in 2027.
- **Follow-up:** Update [../../compliance/sources-manifest.json](../../compliance/sources-manifest.json) and [../../relevant-rulesets.md](../../relevant-rulesets.md) when the 2027 `20x` Class D dataset is released.
