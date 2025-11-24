import psycopg2
from psycopg2.extras import execute_values
import os
import sys

# Add the project root to the path to allow importing the settings
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from invoice_core_processor.config.settings import get_settings
from invoice_core_processor.core.database import get_postgres_connection

VALIDATION_RULES = [
    # Document Integrity
    ('DOC-001', 'Document Integrity', 'File is readable and not corrupted.', 4),
    ('DOC-002', 'Document Integrity', 'OCR confidence threshold met.', 3),
    # Vendor Validation
    ('VND-001', 'Vendor Validation', 'Vendor name is extracted.', 5),
    ('VND-002', 'Vendor Validation', 'GSTIN / Tax ID format is valid.', 4),
    # Invoice Header
    ('INV-001', 'Invoice Header', 'Invoice number exists.', 5),
    ('INV-002', 'Invoice Header', 'Invoice number is unique.', 5),
    ('INV-003', 'Invoice Header', 'Invoice date is valid (not in future).', 4),
    # Line Items
    ('LIT-001', 'Line Items', 'At least one line item exists.', 5),
    ('LIT-004', 'Line Items', 'Amount = qty × unit_price for each item.', 5),
    # Tax
    ('TAX-002', 'Tax', 'Intra/inter-state tax logic is correct.', 4),
    ('TAX-003', 'Tax', 'GST value calculation is correct.', 4),
    # Totals
    ('TTL-001', 'Totals', 'Subtotal matches sum of line items.', 5),
    ('TTL-003', 'Totals', 'Grand total matches subtotal + taxes ± round-off.', 5),
    # Duplicate Detection
    ('DUP-001', 'Duplicate Detection', 'Duplicate invoice number for the same vendor.', 5),
    # Anomaly Detection
    ('ANM-001', 'Anomaly Detection', 'Suspicious round values detected.', 2),
    ('ANM-004', 'Anomaly Detection', 'Low OCR confidence.', 3),
]

def seed_validation_rules():
    """Connects to the database and inserts the predefined validation rules."""
    conn = None
    try:
        conn = get_postgres_connection()
        with conn.cursor() as cur:
            execute_values(
                cur,
                """
                INSERT INTO validation_rule (rule_id, category, description, severity, is_active)
                VALUES %s
                ON CONFLICT (rule_id) DO UPDATE SET
                    category = EXCLUDED.category,
                    description = EXCLUDED.description,
                    severity = EXCLUDED.severity;
                """,
                [(rule[0], rule[1], rule[2], rule[3], True) for rule in VALIDATION_RULES]
            )
            conn.commit()
            print(f"Successfully seeded {len(VALIDATION_RULES)} validation rules.")
    except Exception as e:
        if conn: conn.rollback()
        print(f"Failed to seed validation rules: {e}")
    finally:
        if conn: conn.close()

if __name__ == "__main__":
    # This requires a running database and a configured .env file.
    # To run: python -m src.invoice_core_processor.database.seed_rules
    seed_validation_rules()
