import asyncio
from psycopg2.extras import Json, execute_values
import uuid

from invoice_core_processor.core.database import get_postgres_connection, get_mongo_db
from invoice_core_processor.core.models import AgentCard, ToolDefinition
from invoice_core_processor.core.agent_registry import AgentRegistryService

# ... (Agent Definition remains the same) ...
AGENT_ID = "com.invoice.datastore"
DATASTORE_AGENT_CARD = AgentCard(agent_id=AGENT_ID, description="...", tools=[])


def save_validated_record(invoice_data: dict) -> dict:
    conn = None
    try:
        conn = get_postgres_connection()
        with conn.cursor() as cur:
            # 1. Upsert Vendor
            vendor = invoice_data.get('vendor', {})
            vendor_id = str(vendor.get('id', uuid.uuid4()))
            cur.execute(
                """
                INSERT INTO vendors (id, name, gstin, pan, address)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (name, gstin) DO UPDATE SET
                    pan = EXCLUDED.pan, address = EXCLUDED.address, updated_at = NOW()
                RETURNING id;
                """,
                (vendor_id, vendor.get('name'), vendor.get('gstin'), vendor.get('pan'), vendor.get('address'))
            )
            vendor_id = cur.fetchone()[0]

            # 2. Upsert Customer (similar logic)
            customer_id = None # Placeholder

            # 3. Upsert Invoice
            totals = invoice_data.get('totals', {})
            invoice_id = str(invoice_data.get('id', uuid.uuid4()))
            cur.execute(
                """
                INSERT INTO invoices (id, user_id, vendor_id, invoice_no, invoice_date, subtotal, grand_total, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (vendor_id, invoice_no, invoice_date) DO UPDATE SET
                    subtotal = EXCLUDED.subtotal, grand_total = EXCLUDED.grand_total, status = EXCLUDED.status, updated_at = NOW()
                RETURNING id;
                """,
                (invoice_id, invoice_data.get('user_id'), vendor_id, invoice_data.get('invoiceNumber'), invoice_data.get('invoiceDate'), totals.get('subtotal'), totals.get('grandTotal'), 'VALIDATED')
            )
            invoice_id = cur.fetchone()[0]

            # 4. Batch insert line items
            items = invoice_data.get('lineItems', [])
            if items:
                # First, delete existing items for this invoice to handle updates
                cur.execute("DELETE FROM invoice_items WHERE invoice_id = %s;", (invoice_id,))

                item_values = [
                    (str(uuid.uuid4()), invoice_id, i+1, item.get('description'), item.get('quantity'), item.get('unitPrice'), item.get('taxPercent'), item.get('amount'))
                    for i, item in enumerate(items)
                ]
                execute_values(
                    cur,
                    "INSERT INTO invoice_items (id, invoice_id, line_no, description, quantity, unit_price, tax_pct, amount) VALUES %s",
                    item_values
                )

            conn.commit()
            return {"status": "RECORD_SAVED", "invoice_id": str(invoice_id)}
    except Exception as e:
        if conn: conn.rollback()
        return {"status": "FAILED_RECORD_SAVE", "error": str(e)}
    finally:
        if conn: conn.close()

def check_duplicate(vendor_name: str, invoice_no: str, invoice_date: str) -> dict:
    conn = None
    try:
        conn = get_postgres_connection()
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT i.id FROM invoices i
                JOIN vendors v ON i.vendor_id = v.id
                WHERE v.name = %s AND i.invoice_no = %s AND i.invoice_date = %s;
                """,
                (vendor_name, invoice_no, invoice_date)
            )
            result = cur.fetchone()
            if result:
                return {"status": "DUPLICATE_FOUND", "invoice_id": str(result[0])}
        return {"status": "UNIQUE_RECORD"}
    except Exception as e:
        return {"status": "FAILED_DUPLICATE_CHECK", "error": str(e)}
    finally:
        if conn: conn.close()

# ... (other functions remain, but are not the focus of this step)
def save_audit_step(invoice_id: str, from_status: str, to_status: str, meta: dict) -> dict: return {"status": "AUDIT_STEP_SAVED"}
async def save_metadata(metadata: dict) -> dict: return {"status": "METADATA_SAVED"}
async def log_response(log_data: dict) -> dict: return {"status": "LOG_SAVED"}
async def save_ocr_payload(payload: dict) -> dict: return {"status": "OCR_PAYLOAD_SAVED"}


class DataStoreAgentServer:
    # ... (server class remains the same)
    def __init__(self):
        self.tools = { "postgres/save_validated_record": save_validated_record, "postgres/check_duplicate": check_duplicate, "postgres/save_audit_step": save_audit_step, "mongo/save_metadata": save_metadata, "mongo/log_response": log_response, "mongo/save_ocr_payload": save_ocr_payload }
    def run(self): pass
