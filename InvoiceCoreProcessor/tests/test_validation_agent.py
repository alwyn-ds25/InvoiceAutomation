import unittest
from invoice_core_processor.services.validation import run_validation_checks

class TestValidationAgent(unittest.TestCase):

    def test_clean_invoice_validation(self):
        """Tests the validation service with a valid schema."""
        mapped_schema = {
            "lineItems": [{"quantity": 2, "unitPrice": 500.00, "amount": 1000.00}],
            "totals": {"subtotal": 1000.00, "gstAmount": 180.0, "roundOff": 0.0, "grandTotal": 1180.00}
        }
        result = run_validation_checks(mapped_schema, ocr_confidence=0.99)
        self.assertEqual(result['status'], 'VALIDATED_CLEAN')
        self.assertEqual(result['overall_score'], 100.0)

    def test_flagged_invoice_with_deductions(self):
        """Tests the validation service with multiple errors."""
        mapped_schema = {
            "lineItems": [{"quantity": 2, "unitPrice": 500.00, "amount": 999.00}], # LIT-004 fails (-20)
            "totals": {"subtotal": 1000.00, "gstAmount": 180.0, "roundOff": 0.0, "grandTotal": 1200.00} # TTL-001 & TTL-003 fail (-20, -20)
        }
        result = run_validation_checks(mapped_schema, ocr_confidence=0.6) # ANM-004 fails (-2.5)

        self.assertEqual(result['status'], 'VALIDATED_FLAGGED')
        # Expected score: 100 - 20 - 20 - 20 - 2.5 = 37.5
        self.assertEqual(result['overall_score'], 37.5)

if __name__ == '__main__':
    unittest.main()
