import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os

from core.workflow import build_workflow_graph
from core.models import InvoiceProcessingProtocol, TargetSystem

# --- FastAPI App Initialization ---

app = FastAPI(
    title="InvoiceCoreProcessor",
    description="A multi-agent system for automated invoice processing.",
    version="1.0.0"
)

# Build the LangGraph workflow application on startup
workflow_app = build_workflow_graph()

# --- API Models ---

class InvoiceUploadRequest(BaseModel):
    user_id: str
    file_path: str
    target_system: TargetSystem

class InvoiceUploadResponse(BaseModel):
    workflow_status: str
    invoice_id: str | None
    reliability_score: float | None
    validation_flags: list[str]
    integration_status: str | None


# --- API Endpoints ---

@app.post("/invoice/upload", response_model=InvoiceUploadResponse)
async def upload_invoice(request: InvoiceUploadRequest):
    """
    Receives an invoice file path and triggers the processing workflow.
    """
    print(f"Received API request to process file: {request.file_path}")

    # Check if the source file exists before starting the workflow
    if not os.path.exists(request.file_path):
        raise HTTPException(status_code=400, detail=f"File not found: {request.file_path}")

    # Prepare the initial state for the LangGraph workflow
    initial_state = {
        "user_id": request.user_id,
        "file_path": request.file_path,
        "target_system": request.target_system,
        "status": "UPLOADED", # Initial status for the workflow to pick up
        "invoice_id": None, "extracted_text": None, "mapped_schema": None,
        "validation_flags": [], "reliability_score": None, "anomaly_details": [],
        "integration_payload_preview": None, "current_step": "start", "history": []
    }

    try:
        # Invoke the workflow synchronously. For production, you might use
        # a background task runner like Celery.
        final_state = workflow_app.invoke(initial_state)

        # Format the final response
        response = InvoiceUploadResponse(
            workflow_status=final_state.get('status'),
            invoice_id=final_state.get('invoice_id'),
            reliability_score=final_state.get('reliability_score'),
            validation_flags=final_state.get('validation_flags', []),
            integration_status=final_state.get('status') if 'SYNCED' in final_state.get('status', '') else None
        )
        return response

    except Exception as e:
        print(f"An unexpected error occurred during workflow execution: {e}")
        raise HTTPException(status_code=500, detail="Internal server error during invoice processing.")


@app.get("/")
def read_root():
    return {"message": "InvoiceCoreProcessor is running."}


# --- Main Execution ---

if __name__ == "__main__":
    # Create a dummy file for testing the API endpoint
    dummy_file = "test_invoice.pdf"
    if not os.path.exists(dummy_file):
        with open(dummy_file, "w") as f:
            f.write("This is a test invoice file for the API.")

    print("\n--- To test the API, run the following command in a new terminal: ---")
    print(f"curl -X POST http://127.0.0.1:8000/invoice/upload \\")
    print(f"-H 'Content-Type: application/json' \\")
    print(f"-d '{{\"user_id\": \"api-user-123\", \"file_path\": \"{os.path.abspath(dummy_file)}\", \"target_system\": \"ZOHO\"}}'")
    print("\nStarting FastAPI server...")

    uvicorn.run(app, host="127.0.0.1", port=8000)
