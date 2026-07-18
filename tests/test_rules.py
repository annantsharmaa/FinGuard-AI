import unittest
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from compliance import rules
from risk import scoring


CLEAN_TEXT = """
Invoice Number: INV-2026-0451
Vendor Address: 42 Industrial Estate, Gurugram
GST Number: 07ABCDE1234F1Z5
Subtotal: 100000.00
Tax: 18000.00
Total: 118000.00
Payment Terms: Net 30
Authorized Signatory: R. Sharma
Signature: ____________________
"""

BROKEN_TEXT = """
Bill To: Northline Logistics
Subtotal: 50000.00
Tax: 9000.00
Total: 60000.00
Payment Terms: Net 90
"""


class TestComplianceRules(unittest.TestCase):

    def test_clean_document_passes_all_deterministic_checks(self):
        findings = rules.run_all_checks(CLEAN_TEXT)
        failed = [f for f in findings if not f["passed"]]
        self.assertEqual(failed, [], f"Expected no failures, got: {failed}")

    def test_broken_document_flags_missing_fields(self):
        findings = rules.run_all_checks(BROKEN_TEXT)
        failed_rules = {f["rule_name"] for f in findings if not f["passed"]}
        self.assertIn("missing_signature", failed_rules)
        self.assertIn("missing_invoice_number", failed_rules)
        self.assertIn("missing_gst", failed_rules)
        self.assertIn("incorrect_payment_terms", failed_rules)  # Net 90 not approved

    def test_amount_reconciliation_catches_mismatch(self):
        bad_math = "Subtotal: 100.00\nTax: 10.00\nTotal: 999.00"
        result = rules.check_amount_mismatch(bad_math)
        self.assertFalse(result["passed"])

    def test_amount_reconciliation_passes_when_correct(self):
        good_math = "Subtotal: 100.00\nTax: 10.00\nTotal: 110.00"
        result = rules.check_amount_mismatch(good_math)
        self.assertTrue(result["passed"])


class TestRiskScoring(unittest.TestCase):

    def test_score_is_zero_for_clean_document(self):
        findings = rules.run_all_checks(CLEAN_TEXT)
        score, breakdown = scoring.compute_risk_score(findings)
        self.assertEqual(score, 0)
        self.assertEqual(breakdown, {})

    def test_score_accumulates_for_broken_document(self):
        findings = rules.run_all_checks(BROKEN_TEXT)
        score, breakdown = scoring.compute_risk_score(findings)
        self.assertGreater(score, 0)
        self.assertIn("missing_signature", breakdown)

    def test_score_caps_at_100(self):
        all_fail = [{"rule_name": r, "passed": False, "detail": ""}
                    for r in ["missing_signature", "missing_invoice_number", "missing_gst",
                              "incorrect_payment_terms", "amount_mismatch",
                              "missing_vendor_address", "policy_violation"]]
        score, _ = scoring.compute_risk_score(all_fail)
        self.assertEqual(score, 100)

    def test_status_threshold(self):
        self.assertEqual(scoring.determine_status(59), "auto_cleared")
        self.assertEqual(scoring.determine_status(60), "pending_review")

    def test_fallback_reasons_are_deterministic_and_accurate(self):
        findings = rules.run_all_checks(BROKEN_TEXT)
        score, breakdown = scoring.compute_risk_score(findings)
        reasons = scoring.build_reasons_fallback(breakdown, findings)
        for rule_name in breakdown:
            self.assertIn(rule_name.replace("_", " ").title(), reasons)


if __name__ == "__main__":
    unittest.main()
