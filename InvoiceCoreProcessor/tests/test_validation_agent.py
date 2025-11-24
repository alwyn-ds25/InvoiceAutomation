import unittest

from invoice_core_processor.services.validation import run_validation_checks

class TestValidationAgent(unittest.TestCase):

    def test_clean_invoice_validation(self):
        """
        Tests the validation service with a perfectly valid invoice schema.
        Expects a score of 100 and a 'VALIDATED_CLEAN' status.
        """
        mapped_schema = {
            "total_amount": 1150.00,
            "line_items": [
                {"quantity": 2, "unit_price": 500.00, "total": 1000.00},
                {"quantity": 1, "unit_price": 150.00, "total": 150.00}
            ]
        }

        result = run_validation_checks(mapped_schema, ocr_confidence=0.99)

        self.assertEqual(result['status'], 'VALIDATED_CLEAN')
        self.assertEqual(result['overall_score'], 100.0)

    def test_flagged_invoice_with_deductions(self):
        """
        Tests the validation service with a flawed invoice.
        Checks if deductions are applied correctly to the final score.
        """
        mapped_schema = {
            # Total amount doesn't match sum of line items (20 points deduction)
            "total_amount": 1200.00,
            "line_items": [
                # Line item math is incorrect (20 points deduction)
                {"quantity": 2, "unit_price": 500.00, "total": 990.00},
                {"quantity": 1, "unit_price": 150.00, "total": 150.00}
            ]
        }

        # Low OCR confidence adds another 5 points deduction
        result = run_validation_checks(mapped_schema, ocr_confidence=0.80)

        self.assertEqual(result['status'], 'VALIDATED_FLAGGED')
        # Expected score: 100 - 20 (total mismatch) - 20 (line item) - 5 (ocr) = 55
        self.assertEqual(result['overall_score'], 55.0)

if __name__ == '__main__':
    unittest.main()
