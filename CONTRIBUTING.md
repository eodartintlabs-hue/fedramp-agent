# Contributing to `fedramp-agent`

This guide defines the standard workflow for engineering teams cloning, branching from, or contributing upstream to `fedramp-agent`.

---

## 1. Team Repo Workflow: Clone, Branch, and Sync Upstream

1. **Create your team repository** by cloning or forking `fedramp-agent` and adding `upstream` so you can pull quarterly CR-26 and `CCM` updates:
   ```bash
   git clone <your-org>/fedramp-agent.git my-service-agent
   cd my-service-agent
   git remote add upstream <your-org>/fedramp-agent.git
   git checkout -b feat/initial-agent-setup
   ```
2. **Keep compliance baselines synchronized:**
   - Periodically fetch `upstream` and merge/rebase updates to [relevant-rulesets.md](relevant-rulesets.md), [compliance/sources-manifest.json](compliance/sources-manifest.json), [schemas/](schemas/agent-manifest.schema.json), and [tools/](tools/validate_manifest.py).
   - Never locally weaken [tools/validate_manifest.py](tools/validate_manifest.py) or [tools/check_neutrality.py](tools/check_neutrality.py) to bypass a failing gate.

---

## 2. Local Pre-Commit & CI Gates

Install and run pre-commit hooks defined in [.pre-commit-config.yaml](.pre-commit-config.yaml), or run the exact CI gates from [.github/workflows/fedramp-agent-compliance.yml](.github/workflows/fedramp-agent-compliance.yml) locally before pushing:

```bash
python3 tools/validate_manifest.py templates/agent-manifest.example.class-c.json
python3 tools/validate_manifest.py templates/agent-manifest.example.class-d.json
python3 tools/check_neutrality.py agents skills
python3 tools/audit_agent_repo.py --repo . --manifest templates/agent-manifest.example.class-d.json
python3 tools/generate_compliance_report.py --manifest templates/agent-manifest.example.class-d.json --md-out compliance-report.md --json-out compliance-report.json
python3 -m unittest discover -s tests -v
```

---

## 3. Change Classification (`SCN`) & Pull Requests

Every PR that modifies agent capabilities, model endpoints, MCP tools, TPIRs, cryptographic posture, identity/SSO (`CTL.IA.IA-05`), data residency (`CTL.SA.SA-09-05`), or `MAS` boundaries **MUST**:

1. Complete [templates/PR-compliance-checklist.md](templates/PR-compliance-checklist.md) in the PR description.
2. Classify the change under FedRAMP Significant Change Notification (`SCN`) rules using [skills/classify-scn-change/SKILL.md](skills/classify-scn-change/SKILL.md) and [agents/change-impact-assessor.md](agents/change-impact-assessor.md).
3. When an `SCN` is triggered, create or update a record conforming to [schemas/scn-record.schema.json](schemas/scn-record.schema.json) using [templates/SCN-change-notice.md](templates/SCN-change-notice.md).
4. Update [templates/SDR-agent-record.md](templates/SDR-agent-record.md) (conforming to [schemas/sdr-agent-addendum.schema.json](schemas/sdr-agent-addendum.schema.json)) if the system design or boundary changed.

---

## 4. Vendor-Neutral AI-Assisted Commit Trailers

Following the CoSAI Risk Map convention (ADR-004), any commit where an AI coding assistant materially shaped the output **MUST** carry a single vendor-neutral `Co-authored-by` trailer:

```text
Co-authored-by: AI Assistant <ai-assistant@coalitionforsecureai.org>
```

- **Replace vendor defaults:** Suppress or overwrite tool-default trailers that embed proprietary model names or vendor no-reply domains.
- **Keep canonical agents/skills neutral:** Never introduce vendor-specific harness instructions or model names into [agents/](agents/README.md) or [skills/](skills/README.md).
