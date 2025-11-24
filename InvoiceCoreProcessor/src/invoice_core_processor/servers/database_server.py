import asyncio
from psycopg2.extras import Json
import uuid

from invoice_core_processor.core.database import get_postgres_connection, get_mongo_db
from invoice_core_processor.core.models import AgentCard, ToolDefinition
from invoice_core_processor.core.agent_registry import AgentRegistryService

# ... (Agent Definition remains the same) ...
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

# ... (Tool Implementations remain the same) ...
def save_audit_step(invoice_id: str, from_status: str, to_status: str, meta: dict) -> dict:
    conn = None
    try:
        conn = get_postgres_connection()
        with conn.cursor() as cur: cur.execute("INSERT INTO workflow_audit (invoice_id, from_status, to_status, meta) VALUES (%s, %s, %s, %s);", (invoice_id, from_status, to_status, Json(meta or {}))); conn.commit()
        return {"status": "AUDIT_STEP_SAVED"}
    except Exception as e:
        if conn: conn.rollback()
        return {"status": "FAILED_AUDIT_SAVE", "error": str(e)}
    finally:
        if conn: conn.close()
# ... (other postgres tools) ...
def check_duplicate(vendor_id: str, invoice_no: str, invoice_date: str) -> dict: return {"status": "UNIQUE_RECORD"}
def save_validated_record(invoice_data: dict) -> dict: return {"status": "RECORD_SAVED"}

async def save_metadata(metadata: dict) -> dict:
    try:
        db = get_mongo_db(); await db.invoice_metadata.insert_one(metadata)
        return {"status": "METADATA_SAVED"}
    except Exception as e: return {"status": "FAILED_METADATA_SAVE", "error": str(e)}
# ... (other mongo tools) ...
async def log_response(log_data: dict) -> dict: return {"status": "LOG_SAVED"}
async def save_ocr_payload(payload: dict) -> dict: return {"status": "OCR_PAYLOAD_SAVED"}


class DataStoreAgentServer:
    # ... (class remains the same) ...
    def __init__(self):
        self.tools = { "postgres/check_duplicate": check_duplicate, "postgres/save_validated_record": save_validated_record, "postgres/save_audit_step": save_audit_step, "mongo/save_metadata": save_metadata, "mongo/log_response": log_response, "mongo/save_ocr_payload": save_ocr_payload, }
        print("DataStoreAgent MCP Server initialized.")
    def register_self(self):
        registry = AgentRegistryService(); registry.register_agent(DATASTORE_AGENT_CARD)
    def run(self):
        self.register_self(); print("\nDataStoreAgent MCP Server running (simulation)...")

if __name__ == "__main__":
    server = DataStoreAgentServer()
    server.run()
