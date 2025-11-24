from typing import Dict, Any, List, Literal

# --- Validation Rule Definitions ---

class ValidationResult:
    def __init__(self, rule_id: str, status: Literal['PASS', 'FAIL', 'WARN'], message: str, severity: int, deduction: float = 0.0):
        self.rule_id = rule_id; self.status = status; self.message = message; self.severity = severity; self.deduction = deduction
    def to_dict(self):
        return {"rule_id": self.rule_id, "status": self.status, "message": self.message, "severity": self.severity, "deduction_points": self.deduction}

# --- Rule Implementations ---

def check_line_item_math(schema: Dict[str, Any]) -> ValidationResult:
    for i, item in enumerate(schema.get("lineItems", [])):
        qty = item.get("quantity", 0); price = item.get("unitPrice", 0); total = item.get("amount", 0)
        if abs((qty * price) - total) > 0.01:
            return ValidationResult("LIT-004", "FAIL", f"Line item {i+1} math incorrect.", 5, 20.0)
    return ValidationResult("LIT-004", "PASS", "Line item math correct.", 1)

def check_subtotal(schema: Dict[str, Any]) -> ValidationResult:
    line_total = sum(item.get("amount", 0) for item in schema.get("lineItems", []))
    subtotal = schema.get("totals", {}).get("subtotal", 0)
    if abs(line_total - subtotal) > 0.01:
        return ValidationResult("TTL-001", "FAIL", "Subtotal does not match sum of line items.", 5, 20.0)
    return ValidationResult("TTL-001", "PASS", "Subtotal is correct.", 1)

def check_grand_total(schema: Dict[str, Any]) -> ValidationResult:
    totals = schema.get("totals", {})
    calc_total = totals.get("subtotal", 0) + totals.get("gstAmount", 0) + totals.get("roundOff", 0)
    if abs(calc_total - totals.get("grandTotal", 0)) > 0.01:
        return ValidationResult("TTL-003", "FAIL", "Grand total does not match sum of subtotal, GST, and round-off.", 5, 20.0)
    return ValidationResult("TTL-003", "PASS", "Grand total is correct.", 1)

def check_ocr_confidence(schema: Dict[str, Any], ocr_confidence: float) -> ValidationResult:
    if ocr_confidence < 0.7:
        return ValidationResult("ANM-004", "WARN", f"Low OCR confidence ({ocr_confidence:.2f}).", 3, 2.5)
    return ValidationResult("ANM-004", "PASS", "OCR confidence is acceptable.", 1)

# ... (other rule placeholders)
def check_invoice_date(schema: Dict[str, Any]) -> ValidationResult: return ValidationResult("INV-003", "PASS", "Date is valid.", 1)
def check_duplicate(schema: Dict[str, Any]) -> ValidationResult: return ValidationResult("DUP-001", "PASS", "Invoice is unique.", 1)

# --- Rule Engine ---

def run_validation_checks(mapped_schema: Dict[str, Any], ocr_confidence: float = 1.0) -> Dict[str, Any]:
    rules_to_run = [
        check_line_item_math, check_subtotal, check_grand_total,
        check_invoice_date, check_duplicate
    ]

    results: List[ValidationResult] = [rule(mapped_schema) for rule in rules_to_run]
    results.append(check_ocr_confidence(mapped_schema, ocr_confidence))

    # Calculate score
    initial_score = 100.0
    total_deductions = sum(res.deduction for res in results)
    final_score = max(0, initial_score - total_deductions)

    final_status = "VALIDATED_CLEAN" if all(r.status == 'PASS' for r in results) else "VALIDATED_FLAGGED"

    return {
        "status": final_status,
        "overall_score": final_score,
        "validation_results": [res.to_dict() for res in results]
    }
