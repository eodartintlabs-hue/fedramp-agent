#!/usr/bin/env python3
"""Unit tests for tools/check_neutrality.py (CoSAI ADR-033 vendor neutrality, SKILL.md frontmatter, and evals.json)."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.check_neutrality import check_paths, main as neutrality_main  # noqa: E402


class TestCheckNeutrality(unittest.TestCase):
    """Test suite verifying CoSAI ADR-033 neutrality, frontmatter ceiling, and skill evals checks."""

    def setUp(self) -> None:
        self.neutrality_fixtures = REPO_ROOT / "tests" / "fixtures" / "neutrality"
        self.valid_surface = self.neutrality_fixtures / "valid_surface"
        self.invalid_surface = self.neutrality_fixtures / "invalid_surface"

    def test_valid_neutral_surface_passes(self) -> None:
        """Clean skill with only name/description frontmatter, allowlisted authorities, and evals.json passes."""
        violations = check_paths([self.valid_surface / "skills"])
        self.assertEqual(len(violations), 0, f"Unexpected violations: {violations}")
        self.assertEqual(neutrality_main([str(self.valid_surface / "skills"), "--json"]), 0)

    def test_invalid_surface_catches_vendor_frontmatter_and_missing_evals(self) -> None:
        """Dirty skill with vendor names, forbidden frontmatter keys, and missing evals/evals.json fails."""
        violations = check_paths([self.invalid_surface / "skills"])
        self.assertGreater(len(violations), 0)
        rule_ids = {v.rule_id for v in violations}
        self.assertIn("COSAI-ADR-033-D5-DENYLIST", rule_ids)
        self.assertIn("COSAI-ADR-033-D2A-SKILL-KEYS", rule_ids)
        self.assertIn("COSAI-ADR-033-D6-EVALS", rule_ids)

        tokens = {v.token for v in violations}
        for expected_token in ("OpenAI", "Anthropic", "Gemini", "Cursor", "Copilot", "Antigravity", "LangChain", "Bedrock", ".claude/", ".cursor/"):
            self.assertIn(expected_token, tokens, f"Expected denylist token {expected_token!r} to be flagged")

        self.assertEqual(neutrality_main([str(self.invalid_surface / "skills"), "--json"]), 1)

    def test_agent_frontmatter_forbidden_keys_caught(self) -> None:
        """Top-level agent markdown under agents/ must not declare runtime-binding frontmatter keys."""
        with tempfile.TemporaryDirectory() as tmpdir:
            agents_dir = Path(tmpdir) / "agents"
            agents_dir.mkdir(parents=True)
            bad_agent = agents_dir / "bad-agent.md"
            bad_agent.write_text(
                "---\nname: bad-agent\nmodel: enterprise-default\ntools: [read, write]\n---\n\n# Clean prose\n",
                encoding="utf-8",
            )
            violations = check_paths([agents_dir])
            rule_ids = {v.rule_id for v in violations}
            self.assertIn("COSAI-ADR-033-D2A-AGENT-KEYS", rule_ids)

    def test_allowlist_does_not_suppress_denylist_on_same_line(self) -> None:
        """An allowlisted authority (e.g., NIST or MITRE ATLAS) must not mask a vendor hit on the same line."""
        with tempfile.TemporaryDirectory() as tmpdir:
            doc = Path(tmpdir) / "doc.md"
            doc.write_text("Aligned with NIST SP 800-53 and MITRE ATLAS using OpenAI and Claude.\n", encoding="utf-8")
            violations = check_paths([doc])
            tokens = {v.token for v in violations}
            self.assertIn("OpenAI", tokens)
            self.assertIn("Claude", tokens)


if __name__ == "__main__":
    unittest.main()
