from typing import Dict, Any, List, Literal

# --- Validation Rule Definitions ---

class ValidationResult:
    def __init__(self, rule_id: str, status: Literal['PASS', 'FAIL', 'WARN'], message: str, severity: int, deduction: float = 0.0):
        self.rule_id = rule_id
        self.status = status
        self.message = message
        self.severity = severity
        self.deduction = deduction

    def to_dict(self):
        return {
            "rule_id": self.rule_id,
            "status": self.status,
            "message": self.message,
            "severity": self.severity,
            "deduction_points": self.deduction
        }

# --- Individual Rule Functions ---

def check_line_item_math(mapped_schema: Dict[str, Any]) -> ValidationResult:
    """Checks if quantity * unit_price equals the line item total."""
    for i, item in enumerate(mapped_schema.get("line_items", [])):
        # Use .get() to avoid KeyErrors for missing fields
        qty = item.get("quantity", 0)
        price = item.get("unit_price", 0)
        total = item.get("total", 0)

        # Adding a small tolerance for floating point inaccuracies
        if abs((qty * price) - total) > 0.01:
            return ValidationResult(
                rule_id="ANM-001",
                status="FAIL",
                message=f"Line item {i+1} math is incorrect: {qty} * {price} != {total}",
                severity=5,
                deduction=20.0
            )
    return ValidationResult("ANM-001", "PASS", "All line item math is correct.", 1)


def check_total_amount(mapped_schema: Dict[str, Any]) -> ValidationResult:
    """Checks if the sum of line items equals the invoice total."""
    line_total = sum(item.get("total", 0) for item in mapped_schema.get("line_items", []))
    invoice_total = mapped_schema.get("total_amount", 0)

    if abs(line_total - invoice_total) > 0.01:
        return ValidationResult(
            rule_id="ANM-002",
            status="FAIL",
            message=f"Sum of line items ({line_total}) does not match invoice total ({invoice_total}).",
            severity=5,
            deduction=20.0
        )
    return ValidationResult("ANM-002", "PASS", "Invoice total matches sum of line items.", 1)

def check_for_round_numbers(mapped_schema: Dict[str, Any]) -> ValidationResult:
    """Flags invoices with unusually round numbers, which can be a fraud indicator."""
    total = mapped_schema.get("total_amount", 0)
    if total > 1000 and total % 1000 == 0:
        return ValidationResult(
            rule_id="ANM-003",
            status="WARN",
            message=f"Invoice total ({total}) is a round number, which can be an anomaly.",
            severity=3,
            deduction=2.5 # 50% of severity 3 deduction
        )
    return ValidationResult("ANM-003", "PASS", "Total amount is not a suspicious round number.", 1)


# --- Rule Engine ---

def run_validation_checks(mapped_schema: Dict[str, Any], ocr_confidence: float = 0.95) -> Dict[str, Any]:
    """
    Runs all validation rules against the mapped invoice schema and calculates a reliability score.
    """
    rules_to_run = [
        check_line_item_math,
        check_total_amount,
        check_for_round_numbers,
    ]

    results: List[ValidationResult] = [rule(mapped_schema) for rule in rules_to_run]

    # Example of a rule that depends on data from a previous step (OCR)
    if ocr_confidence < 0.85:
        results.append(ValidationResult(
            rule_id="ANM-004",
            status="WARN",
            message=f"Low OCR confidence ({ocr_confidence:.2f}) may impact accuracy.",
            severity=4,
            deduction=5.0 # 50% of severity 4
        ))
    else:
        results.append(ValidationResult("ANM-004", "PASS", "OCR confidence is acceptable.", 1))

    # Calculate final score
    initial_score = 100.0
    total_deductions = sum(res.deduction for res in results)
    final_score = max(0, initial_score - total_deductions)

    final_status = "VALIDATED_CLEAN" if all(r.status == 'PASS' for r in results) else "VALIDATED_FLAGGED"

    return {
        "status": final_status,
        "overall_score": final_score,
        "validation_results": [res.to_dict() for res in results]
    }
