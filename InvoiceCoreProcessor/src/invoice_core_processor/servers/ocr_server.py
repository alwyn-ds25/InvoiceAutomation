from invoice_core_processor.core.models import AgentCard, ToolDefinition
from invoice_core_processor.services.ocr_processor import run_cascading_ocr, OCRResult
from invoice_core_processor.core.agent_registry import AgentRegistryService
import os

# --- Agent Definition ---

AGENT_ID = "com.invoice.ocr"
CAPABILITY_OCR = "CAPABILITY_OCR"

OCR_AGENT_CARD = AgentCard(
    agent_id=AGENT_ID,
    description="Executes a file-type–aware, cascading OCR pipeline for invoices.",
    tools=[
        ToolDefinition(
            tool_id="ocr/extract_text_cascading",
            capability=CAPABILITY_OCR,
            description="Extracts structured text and tables from various document types using a cascading OCR pipeline.",
            parameters={
                "invoice_id": {"type": "str", "optional": True},
                "file_path": {"type": "str"},
                "file_extension": {"type": "str", "enum": ["pdf", "docx", "png", "jpg", "jpeg", "tiff"]},
                "user_id": {"type": "str", "optional": True}
            }
        )
    ]
)

# --- MCP Tool Implementation ---

def extract_text_cascading(
    invoice_id: str, file_path: str, file_extension: str, user_id: str
) -> dict:
    """
    MCP tool wrapper for the run_cascading_ocr service.
    """
    print(f"OCRAgent: Received request for file: {file_path}")

    if not os.path.exists(file_path):
        return {"status": "FAILED_OCR", "error": f"File not found: {file_path}"}

    result: OCRResult = run_cascading_ocr(file_path, file_extension)

    # In a real system, this would make an MCP call to the DataStoreAgent
    print("OCRAgent: OCR processing complete. Would now save payload to DB via DataStoreAgent.")

    return result.dict()

# --- MCP Server ---

class OCRAgentServer:
    def __init__(self):
        self.tools = {
            "ocr/extract_text_cascading": extract_text_cascading,
        }
        print("OCRAgent MCP Server initialized.")

    def register_self(self):
        """Registers the agent with the AgentRegistryService."""
        registry = AgentRegistryService()
        print(f"Attempting to register agent '{AGENT_ID}' with the registry...")
        registration_result = registry.register_agent(OCR_AGENT_CARD)
        print(f"Registration result: {registration_result}")

    def run(self):
        """Simulates the server running and listening for requests."""
        self.register_self()
        print("\nOCRAgent MCP Server running (simulation)...")

if __name__ == "__main__":
    server = OCRAgentServer()
    server.run()
