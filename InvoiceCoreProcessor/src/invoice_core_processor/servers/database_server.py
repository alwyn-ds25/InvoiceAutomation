import asyncio
from psycopg2.extras import Json, execute_values
import uuid
import datetime

from invoice_core_processor.core.database import get_postgres_connection, get_mongo_db
from invoice_core_processor.core.models import AgentCard, ToolDefinition
from invoice_core_processor.core.agent_registry import AgentRegistryService

# ... (Agent Definition remains the same) ...
AGENT_ID = "com.invoice.datastore"
DATASTORE_AGENT_CARD = AgentCard(agent_id=AGENT_ID, description="...", tools=[
    ToolDefinition(tool_id="postgres/update_processing_time", capability="CAPABILITY_DB_WRITE", description="Updates processing timestamps.", parameters={})
])


def save_validated_record(data: dict):
    conn = get_postgres_connection()
    with conn.cursor() as cur:

        # 1. UPSERT VENDOR
        vendor_query = """
            INSERT INTO vendors (name, gstin)
            VALUES (%s, %s)
            ON CONFLICT (name, gstin)
            DO UPDATE SET name = EXCLUDED.name
            RETURNING id;
        """
        cur.execute(
            vendor_query,
            (data["vendor"]["name"], data["vendor"]["gstin"])
        )
        vendor_id = cur.fetchone()[0]

        # 2. UPSERT INVOICE
        invoice_query = """
            INSERT INTO invoices (vendor_id, invoice_no, invoice_date, total_amount, user_id)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (vendor_id, invoice_no, invoice_date)
            DO UPDATE SET total_amount = EXCLUDED.total_amount
            RETURNING id;
        """
        cur.execute(
            invoice_query,
            (
                vendor_id,
                data["invoiceNumber"],
                data["invoiceDate"],
                data["totals"]["grandTotal"],
                data["user_id"]
            )
        )
        invoice_id = cur.fetchone()[0]

        # 3. DELETE EXISTING LINE ITEMS
        delete_query = "DELETE FROM invoice_items WHERE invoice_id = %s;"
        cur.execute(delete_query, (invoice_id,))

        # 4. INSERT NEW LINE ITEMS
        line_items = [
            (
                invoice_id,
                item["description"],
                item["quantity"],
                item["unitPrice"],
                item["taxPercent"],
                item["amount"]
            )
            for item in data["lineItems"]
        ]

        execute_values(
            cur,
            """
            INSERT INTO invoice_items
                (invoice_id, description, quantity, unit_price, tax_pct, amount)
            VALUES %s;
            """,
            line_items
        )

        conn.commit()

    return {
        "status": "RECORD_SAVED",
        "invoice_id": str(invoice_id),
        "vendor_id": str(vendor_id)
    }

def update_processing_time(invoice_id: str) -> dict:
    """Updates the end time and duration for a processed invoice."""
    conn = None
    try:
        conn = get_postgres_connection()
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE invoices
                SET
                    processing_end_time = %s,
                    processing_duration_ms = EXTRACT(EPOCH FROM (%s - processing_start_time)) * 1000
                WHERE id = %s;
                """,
                (datetime.datetime.now(datetime.UTC), datetime.datetime.now(datetime.UTC), invoice_id)
            )
            conn.commit()
        return {"status": "TIME_UPDATED"}
    except Exception as e:
        if conn: conn.rollback()
        return {"status": "FAILED_TIME_UPDATE", "error": str(e)}
    finally:
        if conn: conn.close()

# ... (other functions remain) ...
def check_duplicate(vendor_name: str, invoice_number: str, invoice_date: str):
    conn = get_postgres_connection()
    with conn.cursor() as cur:
        query = """
            SELECT i.id
            FROM invoices i
            JOIN vendors v ON v.id = i.vendor_id
            WHERE v.name = %s
              AND i.invoice_no = %s
              AND i.invoice_date = %s
            LIMIT 1;
        """
        cur.execute(query, (vendor_name, invoice_number, invoice_date))
        row = cur.fetchone()
        return row is not None
def save_audit_step(invoice_id: str, from_status: str, to_status: str, meta: dict) -> dict: return {"status": "AUDIT_STEP_SAVED"}
async def save_metadata(metadata: dict) -> dict: return {"status": "METADATA_SAVED"}
async def log_response(log_data: dict) -> dict: return {"status": "LOG_SAVED"}
async def save_ocr_payload(payload: dict) -> dict: return {"status": "OCR_PAYLOAD_SAVED"}


class DataStoreAgentServer:
    def __init__(self):
        self.tools = {
            "postgres/save_validated_record": save_validated_record,
            "postgres/update_processing_time": update_processing_time,
            # ... other tools
        }
    def run(self): pass
