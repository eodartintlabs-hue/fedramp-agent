#!/usr/bin/env python3
"""Unit tests for tools/validate_manifest.py (Class C, Class D, and CR-26 semantic invariants)."""

from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.validate_manifest import (  # noqa: E402
    main as validate_main,
    validate_manifest_data,
    validate_manifest_file,
)


class TestValidateManifest(unittest.TestCase):
    """Test suite verifying Class C and Class D FedRAMP CR-26 manifest validation."""

    def setUp(self) -> None:
        self.fixtures_dir = REPO_ROOT / "tests" / "fixtures"
        self.templates_dir = REPO_ROOT / "templates"
        self.valid_c_path = self.fixtures_dir / "valid-class-c.manifest.json"
        self.valid_d_path = self.fixtures_dir / "valid-class-d.manifest.json"
        self.invalid_c_path = self.fixtures_dir / "invalid-class-c.manifest.json"
        self.invalid_d_path = self.fixtures_dir / "invalid-class-d.manifest.json"
        self.valid_c_data = json.loads(self.valid_c_path.read_text(encoding="utf-8"))
        self.valid_d_data = json.loads(self.valid_d_path.read_text(encoding="utf-8"))

    def test_example_templates_pass(self) -> None:
        """Both shipped example templates (Class C and Class D) must pass validate_manifest.py cleanly."""
        c_template = self.templates_dir / "agent-manifest.example.class-c.json"
        d_template = self.templates_dir / "agent-manifest.example.class-d.json"

        res_c = validate_manifest_file(c_template)
        self.assertTrue(res_c.passed, f"Class C example template failed: {res_c.errors}")
        self.assertEqual(len(res_c.errors), 0)

        res_d = validate_manifest_file(d_template)
        self.assertTrue(res_d.passed, f"Class D example template failed: {res_d.errors}")
        self.assertEqual(len(res_d.errors), 0)
        # Class D with 20x track emits the non-fatal 2027 notice warning
        warning_rules = {w.rule_id for w in res_d.warnings}
        self.assertIn("CR26-20X-CLASS-D-2027", warning_rules)

    def test_valid_class_c_fixture_passes(self) -> None:
        res = validate_manifest_file(self.valid_c_path)
        self.assertTrue(res.passed)
        self.assertEqual(res.service_class, "C")
        self.assertEqual(len(res.errors), 0)

    def test_valid_class_d_fixture_passes(self) -> None:
        res = validate_manifest_file(self.valid_d_path)
        self.assertTrue(res.passed)
        self.assertEqual(res.service_class, "D")
        self.assertEqual(len(res.errors), 0)

    def test_class_c_non_fips_emits_warning_not_error(self) -> None:
        """CMU-CSO-UVM is SHOULD for Class C: fips_140_3_validated_modules=false emits a WARNING, not an ERROR."""
        data = copy.deepcopy(self.valid_c_data)
        data["cryptography"]["fips_140_3_validated_modules"] = False
        res = validate_manifest_data(data)
        self.assertTrue(res.passed)
        self.assertEqual(len(res.errors), 0)
        self.assertTrue(any(w.rule_id == "CMU-CSO-UVM" for w in res.warnings))

    def test_class_d_strict_escalations_fail_when_violated(self) -> None:
        """Class D must fail hard on non-FIPS (CMU-CSO-UVM), IAL2 (CTL.IA.IA-05), non-US residency (CTL.SA.SA-09-05), missing per-service artifacts (CDS-CSO-PSM), and SLA > 2d (VER-TFR-EVU)."""
        res = validate_manifest_file(self.invalid_d_path)
        self.assertFalse(res.passed)
        error_rule_ids = {e.rule_id for e in res.errors}
        self.assertIn("CMU-CSO-UVM", error_rule_ids)
        self.assertIn("CTL.IA.IA-05", error_rule_ids)
        self.assertIn("CTL.SA.SA-09-05", error_rule_ids)
        self.assertIn("CDS-CSO-PSM", error_rule_ids)
        self.assertIn("VER-TFR-EVU", error_rule_ids)
        self.assertIn("FRC-CSO-CAT", error_rule_ids)

    def test_class_c_failures_detected(self) -> None:
        """Invalid Class C fixture must fail on MAS scope, PEPs, unmitigated non-certified TPIR, certified TPIR missing package ID, telemetry redaction, VDR SLA > 5d, and invalid CoSAI IDs."""
        res = validate_manifest_file(self.invalid_c_path)
        self.assertFalse(res.passed)
        error_rule_ids = {e.rule_id for e in res.errors}
        self.assertIn("MAS-CSO-IIR", error_rule_ids)
        self.assertIn("MAS-CSO-TPR", error_rule_ids)
        self.assertIn("MAS-CSO-MDI", error_rule_ids)
        self.assertIn("CMU-CSO-CMD", error_rule_ids)
        self.assertIn("CTL.IA.IA-05", error_rule_ids)
        self.assertIn("KSI-IAM-MFA", error_rule_ids)
        self.assertIn("KSI-CNA-EIS", error_rule_ids)
        self.assertIn("KSI-IAM-ATP", error_rule_ids)
        self.assertIn("SCG-CSO-SDF", error_rule_ids)
        self.assertIn("CTL.AU.AU-09", error_rule_ids)
        self.assertIn("VER-TFR-EVU", error_rule_ids)
        self.assertIn("COSAI-ADR-033-D6", error_rule_ids)
        self.assertIn("COSAI-ADR-030", error_rule_ids)
        self.assertIn("COSAI-RISK-MAP", error_rule_ids)

    def test_individual_class_d_escalations(self) -> None:
        """Verify each Class D escalation rule independently."""
        # 1. Non-FIPS in Class D -> fail CMU-CSO-UVM
        d1 = copy.deepcopy(self.valid_d_data)
        d1["cryptography"]["fips_140_3_validated_modules"] = False
        r1 = validate_manifest_data(d1)
        self.assertFalse(r1.passed)
        self.assertTrue(any(e.rule_id == "CMU-CSO-UVM" for e in r1.errors))

        # 2. IAL2 in Class D -> fail CTL.IA.IA-05
        d2 = copy.deepcopy(self.valid_d_data)
        d2["identity_access"]["digital_identity_level"] = "IAL2/AAL2/FAL2"
        r2 = validate_manifest_data(d2)
        self.assertFalse(r2.passed)
        self.assertTrue(any(e.rule_id == "CTL.IA.IA-05" for e in r2.errors))

        # 3. Non-US jurisdiction in Class D -> fail CTL.SA.SA-09-05
        d3 = copy.deepcopy(self.valid_d_data)
        d3["model_serving"]["us_jurisdiction_only"] = False
        r3 = validate_manifest_data(d3)
        self.assertFalse(r3.passed)
        self.assertTrue(any(e.rule_id == "CTL.SA.SA-09-05" for e in r3.errors))

        # 4. Missing per_service_certification_artifacts in Class D -> fail CDS-CSO-PSM
        d4 = copy.deepcopy(self.valid_d_data)
        d4["lifecycle"]["per_service_certification_artifacts"] = False
        r4 = validate_manifest_data(d4)
        self.assertFalse(r4.passed)
        self.assertTrue(any(e.rule_id == "CDS-CSO-PSM" for e in r4.errors))

        # 5. VDR SLA = 3 days in Class D -> fail VER-TFR-EVU
        d5 = copy.deepcopy(self.valid_d_data)
        d5["lifecycle"]["vdr_triage_sla_days"] = 3
        r5 = validate_manifest_data(d5)
        self.assertFalse(r5.passed)
        self.assertTrue(any(e.rule_id == "VER-TFR-EVU" for e in r5.errors))

    def test_cli_exit_codes(self) -> None:
        self.assertEqual(validate_main([str(self.valid_c_path), "--json"]), 0)
        self.assertEqual(validate_main([str(self.valid_d_path), "--json"]), 0)
        self.assertEqual(validate_main([str(self.invalid_c_path), "--json"]), 1)
        self.assertEqual(validate_main([str(self.invalid_d_path), "--json"]), 1)


if __name__ == "__main__":
    unittest.main()
