# To allow running this file directly for testing
import sys
import os
import asyncio
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import get_postgres_connection, get_mongo_db
from core.models import AgentCard, ToolDefinition
from core.agent_registry import AgentRegistryService
from psycopg2.extras import Json
import uuid

# --- Agent Definition (remains the same) ---
AGENT_ID = "com.invoice.datastore"
DATASTORE_AGENT_CARD = AgentCard(
    agent_id=AGENT_ID,
    description="Provides secure, transactional access to MongoDB and PostgreSQL.",
    tools=[
        ToolDefinition(tool_id="mongo/save_metadata", capability="CAPABILITY_DB_WRITE", description="Saves ingestion metadata.", parameters={}),
        ToolDefinition(tool_id="mongo/log_response", capability="CAPABILITY_LOGGING", description="Logs agent responses.", parameters={}),
        ToolDefinition(tool_id="mongo/save_ocr_payload", capability="CAPABILITY_DB_WRITE", description="Saves raw OCR payload.", parameters={}),
        ToolDefinition(tool_id="postgres/check_duplicate", capability="CAPABILITY_DB_READ", description="Checks for duplicate invoices.", parameters={}),
        ToolDefinition(tool_id="postgres/save_validated_record", capability="CAPABILITY_DB_WRITE", description="Saves a validated invoice record.", parameters={}),
        ToolDefinition(tool_id="postgres/save_audit_step", capability="CAPABILITY_AUDIT", description="Saves a workflow audit step.", parameters={}),
    ]
)

# --- PostgreSQL Tool Implementations ---

def save_audit_step(invoice_id: str, from_status: str, to_status: str, meta: dict) -> dict:
    conn = None
    try:
        conn = get_postgres_connection()
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO workflow_audit (invoice_id, from_status, to_status, meta)
                VALUES (%s, %s, %s, %s);
                """,
                (invoice_id, from_status, to_status, Json(meta or {}))
            )
            conn.commit()
        return {"status": "AUDIT_STEP_SAVED"}
    except Exception as e:
        if conn: conn.rollback()
        return {"status": "FAILED_AUDIT_SAVE", "error": str(e)}
    finally:
        if conn: conn.close()

def check_duplicate(vendor_id: str, invoice_no: str, invoice_date: str) -> dict:
    conn = None
    try:
        conn = get_postgres_connection()
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id FROM invoice WHERE vendor_id = %s AND invoice_no = %s AND invoice_date = %s;",
                (vendor_id, invoice_no, invoice_date)
            )
            result = cur.fetchone()
            if result:
                return {"status": "DUPLICATE_FOUND", "invoice_id": str(result[0])}
        return {"status": "UNIQUE_RECORD"}
    except Exception as e:
        return {"status": "FAILED_DUPLICATE_CHECK", "error": str(e)}
    finally:
        if conn: conn.close()

def save_validated_record(invoice_data: dict) -> dict:
    # A more robust implementation would use Pydantic models for validation
    conn = None
    try:
        conn = get_postgres_connection()
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO invoice (id, vendor_id, invoice_no, invoice_date, currency, total_amount, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (vendor_id, invoice_no, invoice_date) DO UPDATE SET
                    currency = EXCLUDED.currency,
                    total_amount = EXCLUDED.total_amount,
                    status = EXCLUDED.status,
                    updated_at = NOW();
                """,
                (
                    invoice_data.get('id', str(uuid.uuid4())),
                    invoice_data.get('vendor_id'),
                    invoice_data.get('invoice_no'),
                    invoice_data.get('invoice_date'),
                    invoice_data.get('currency', 'INR'),
                    invoice_data.get('total_amount'),
                    invoice_data.get('status', 'VALIDATED')
                )
            )
            conn.commit()
        return {"status": "RECORD_SAVED"}
    except Exception as e:
        if conn: conn.rollback()
        return {"status": "FAILED_RECORD_SAVE", "error": str(e)}
    finally:
        if conn: conn.close()

# --- MongoDB Tool Implementations ---

async def save_metadata(metadata: dict) -> dict:
    try:
        db = get_mongo_db()
        await db.invoice_metadata.insert_one(metadata)
        return {"status": "METADATA_SAVED"}
    except Exception as e:
        return {"status": "FAILED_METADATA_SAVE", "error": str(e)}

async def log_response(log_data: dict) -> dict:
    try:
        db = get_mongo_db()
        await db.agent_process_logs.insert_one(log_data)
        return {"status": "LOG_SAVED"}
    except Exception as e:
        return {"status": "FAILED_LOG_SAVE", "error": str(e)}

async def save_ocr_payload(payload: dict) -> dict:
    try:
        db = get_mongo_db()
        # Use invoice_id as a unique identifier for upserting
        await db.ocr_extraction_data.update_one(
            {'invoice_id': payload.get('invoice_id')},
            {'$set': payload},
            upsert=True
        )
        return {"status": "OCR_PAYLOAD_SAVED"}
    except Exception as e:
        return {"status": "FAILED_OCR_PAYLOAD_SAVE", "error": str(e)}


# --- MCP Server ---
class DataStoreAgentServer:
    def __init__(self):
        self.tools = {
            "postgres/check_duplicate": check_duplicate,
            "postgres/save_validated_record": save_validated_record,
            "postgres/save_audit_step": save_audit_step,
            "mongo/save_metadata": save_metadata,
            "mongo/log_response": log_response,
            "mongo/save_ocr_payload": save_ocr_payload,
        }
        print("DataStoreAgent MCP Server initialized.")

    def register_self(self):
        registry = AgentRegistryService()
        print(f"Attempting to register agent '{AGENT_ID}' with the registry...")
        registration_result = registry.register_agent(DATASTORE_AGENT_CARD)
        print(f"Registration result: {registration_result}")

    def run(self):
        self.register_self()
        print("\nDataStoreAgent MCP Server running (simulation)...")

# --- Async Runner for MongoDB functions ---
def run_async(coro):
    return asyncio.run(coro)

if __name__ == "__main__":
    server = DataStoreAgentServer()
    server.run()

    # Example of how to run the async MongoDB functions from a sync context
    print("\n--- Testing async MongoDB tool ---")
    test_meta = {"invoice_id": "test-mongo-123", "user_id": "test-user"}
    # result = run_async(server.tools["mongo/save_metadata"](test_meta))
    # print(f"Result of save_metadata: {result}")
