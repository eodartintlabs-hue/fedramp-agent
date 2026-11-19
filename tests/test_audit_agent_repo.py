#!/usr/bin/env python3
"""Unit tests for tools/audit_agent_repo.py and tools/generate_compliance_report.py."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.audit_agent_repo import audit_repository, main as audit_main  # noqa: E402
from tools.generate_compliance_report import main as report_main  # noqa: E402


class TestAuditAgentRepoAndReports(unittest.TestCase):
    """Test suite verifying repository audit and dual Markdown/JSON compliance report generation."""

    def setUp(self) -> None:
        self.templates_dir = REPO_ROOT / "templates"
        self.fixtures_dir = REPO_ROOT / "tests" / "fixtures"
        self.class_c_manifest = self.templates_dir / "agent-manifest.example.class-c.json"
        self.class_d_manifest = self.templates_dir / "agent-manifest.example.class-d.json"
        self.invalid_d_manifest = self.fixtures_dir / "invalid-class-d.manifest.json"

    def test_audit_repo_passes_for_class_c_and_class_d_examples(self) -> None:
        report_c = audit_repository(REPO_ROOT, self.class_c_manifest, strict=False)
        self.assertTrue(report_c.passed, f"Repo audit failed for Class C: {report_c.errors}")

        report_d = audit_repository(REPO_ROOT, self.class_d_manifest, strict=False)
        self.assertTrue(report_d.passed, f"Repo audit failed for Class D: {report_d.errors}")

    def test_audit_repo_fails_on_invalid_manifest(self) -> None:
        report_bad = audit_repository(REPO_ROOT, self.invalid_d_manifest, strict=False)
        self.assertFalse(report_bad.passed)
        self.assertGreater(len(report_bad.errors), 0)

    def test_audit_cli_writes_json_out(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            json_out = Path(tmpdir) / "audit-out.json"
            rc = audit_main(
                [
                    "--repo",
                    str(REPO_ROOT),
                    "--manifest",
                    str(self.class_d_manifest),
                    "--json-out",
                    str(json_out),
                ]
            )
            self.assertEqual(rc, 0)
            self.assertTrue(json_out.is_file())
            payload = json.loads(json_out.read_text(encoding="utf-8"))
            self.assertTrue(payload["passed"])
            self.assertEqual(payload["service_class"], "D")

    def test_generate_compliance_report_dual_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            md_out = Path(tmpdir) / "report.md"
            json_out = Path(tmpdir) / "report.json"
            rc = report_main(
                [
                    "--manifest",
                    str(self.class_d_manifest),
                    "--md-out",
                    str(md_out),
                    "--json-out",
                    str(json_out),
                ]
            )
            self.assertEqual(rc, 0)
            self.assertTrue(md_out.is_file())
            self.assertTrue(json_out.is_file())

            md_text = md_out.read_text(encoding="utf-8")
            self.assertIn("FedRAMP CR-26 AI Agent Compliance & SDR Report", md_text)
            self.assertIn("mission-incident-response-agent-d", md_text)

            bundle = json.loads(json_out.read_text(encoding="utf-8"))
            self.assertEqual(bundle["cr26_dataset_version"], "2026.11.02.01")
            self.assertTrue(bundle["validation_status"]["passed"])
            self.assertEqual(bundle["agent_manifest_summary"]["service_class"], "D")
            self.assertIsNotNone(bundle["ksi_coverage"]["class_d_20x_notice"])


if __name__ == "__main__":
    unittest.main()
