# Canonical Vendor-Neutral Sub-Agents

`agents/` is the canonical, vendor-neutral surface for compliance and security sub-agent definitions in this repository, governed by [`../docs/adr/003-vendor-neutral-agent-and-eval-shipping.md`](../docs/adr/003-vendor-neutral-agent-and-eval-shipping.md) and aligned with the Coalition for Secure AI (`CoSAI`) Risk Map agent architecture pattern (`CoSAI ADR-006` and `ADR-033`).

Every file in this directory is the single authoritative specification for its agent's role, invocation modes, input contract, methodology, output contract, composition relationships, and strict operational boundaries. No runtime-specific wrapper files, model identifiers, tool-binding frontmatter, or vendor configuration directories are tracked in this tree.

---

## Canonical Shape

Each canonical agent definition follows the `CoSAI ADR-006` prose structure:

1. **Header Block:** Title (`# <Name> Sub-Agent Definition`), semantic version, scope, and governing ADR citation.
2. **`## Agent`:** Canonical kebab-case identifier, concise role summary, operating modes, and vendor-neutral invocation examples (`\<invoke <agent-name> agent\>`).
3. **`## Composition`:** How the agent composes with peer canonical agents in `agents/` and invokes domain knowledge skills in [`../skills/`](../skills/).
4. **Body Sections:** `## Identity & Purpose`, `## Invocation` (modes, caller format, input contract), `## Method`, `## Output Contract`, and `## Boundaries`.

---

## Agents in This Directory

| Agent File | Canonical Name | Primary Role & CR-26 / CoSAI Alignment | Composes With |
|---|---|---|---|
| [`fedramp-compliance-reviewer.md`](fedramp-compliance-reviewer.md) | `fedramp-compliance-reviewer` | Audits `agent-manifest.json`, architecture diffs, and repository artifacts against FedRAMP CR-26 (`2026.11.02.01`) Class C and Class D rules (`MAS`, `CMU`, `CTL.IA.IA-05`, `CTL.SA.SA-09-05`, `CDS-CSO-PSM`, `VER-TFR-EVU`). | Skills: `check-cr26-applicability`, `audit-tpir-boundary`, `map-cosai-controls` |
| [`threat-modeler.md`](threat-modeler.md) | `threat-modeler` | Performs structured agentic threat modeling across the `42` CoSAI components (`CoSAI ADR-030`), `36` risks, `37` controls, `STRIDE`, `MITRE ATLAS`, and `OWASP Top 10 for LLM`, verifying PEP placement and confinement boundaries. | Skills: `map-cosai-controls`, `audit-tpir-boundary` |
| [`change-impact-assessor.md`](change-impact-assessor.md) | `change-impact-assessor` | Evaluates proposed code, model, prompt, tool-allowlist, cryptography, or `TPIR` diffs under FedRAMP Significant Change Notification (`SCN-CSO-EVA`) rules and emits validated `scn-record.schema.json` records. | Skills: `classify-scn-change`, `check-cr26-applicability`; Peer: `fedramp-compliance-reviewer` |
| [`evidence-collector.md`](evidence-collector.md) | `evidence-collector` | Assembles deterministic, dual human-readable Markdown and machine-readable JSON compliance bundles (`SDR`, `SCG`, `CPO` addendum, `CCM` Ongoing Certification Report evidence) with SHA-256 artifact digests. | Peer agents: `fedramp-compliance-reviewer`, `threat-modeler`, `change-impact-assessor` |

---

## Standard End-to-End Composition Workflow

For feature pull requests or release candidates in a branched agent repository, invoke the canonical agents in sequence:

```text
threat-modeler -> change-impact-assessor -> fedramp-compliance-reviewer -> evidence-collector
```

1. **`threat-modeler`** maps new or modified data flows, `MCP` tools, and `PEPs` to `CoSAI` components, risks, and controls.
2. **`change-impact-assessor`** classifies the change under CR-26 `SCN` (`routine-non-significant`, `adaptive-change-notice`, `transformative-prior-notice`, `transformative-tpir-addition`, or `emergency-change`).
3. **`fedramp-compliance-reviewer`** performs the pre-merge gate check across Class C or Class D invariants (`READY`, `BLOCKING`, or `NEEDS_HUMAN_REVIEW`).
4. **`evidence-collector`** packages verified outputs and SHA-256 digests into an `evidence-bundle.schema.json` artifact for Trust Center publication (`CDS-CSO-UTC`, `CDS-CSO-PSM`).

---

## Neutrality Enforcement

All files in `agents/` are gated by `tools/check_neutrality.py` before commit and in continuous integration:

```bash
python3 tools/check_neutrality.py agents skills
```

Consumers adapting these canonical definitions to their local developer environment supply runtime-specific frontmatter or dispatch bindings outside this directory in untracked local adapters, keeping `agents/*.md` as the single source of truth.
