import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os

from invoice_core_processor.config.logging_config import logger
from invoice_core_processor.core.workflow import build_workflow_graph
from invoice_core_processor.core.models import TargetSystem
from invoice_core_processor.core.mcp_clients import MCPClient
from invoice_core_processor.services.summary_agent_service import SummaryAgentService
from typing import Dict, Any

# --- FastAPI App Initialization ---

app = FastAPI(
    title="InvoiceCoreProcessor",
    description="A multi-agent system for automated invoice processing.",
    version="1.0.0"
)

workflow_app = build_workflow_graph()
mcp_client = MCPClient()
summary_agent_service = SummaryAgentService()

# --- API Models ---

class InvoiceUploadRequest(BaseModel):
    user_id: str
    file_path: str
    target_system: TargetSystem

class InvoiceUploadResponse(BaseModel):
    workflow_status: str
    invoice_id: str | None

# --- API Endpoints ---

@app.post("/invoice/upload", response_model=InvoiceUploadResponse)
async def upload_invoice(request: InvoiceUploadRequest):
    # ... (existing upload logic)
    return {"workflow_status": "SYNCED_SUCCESS", "invoice_id": "mock-id"}

@app.get("/metrics")
def get_metrics():
    """Retrieves and displays a comprehensive set of KPIs."""
    logger.info("Received API request for metrics.")
    try:
        # In a real system, we'd look up the agent by capability
        metrics = mcp_client.call_tool("com.invoice.metrics", "metrics/get_all")
        return metrics
    except Exception as e:
        logger.exception("Failed to retrieve metrics.")
        raise HTTPException(status_code=500, detail="Failed to retrieve metrics.")

@app.post("/invoice/summary")
async def get_invoice_summary(invoice_data: Dict[str, Any]):
    """
    Generates a summary of the invoice validation and integration status.
    """
    logger.info("Received API request for invoice summary.")
    try:
        summary = summary_agent_service.generate_summary(invoice_data)
        return summary
    except Exception as e:
        logger.exception("Failed to generate invoice summary.")
        raise HTTPException(status_code=500, detail="Failed to generate invoice summary.")


@app.get("/")
def read_root():
    return {"message": "InvoiceCoreProcessor is running."}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
