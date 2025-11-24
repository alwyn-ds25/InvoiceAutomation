from invoice_core_processor.core.models import AgentCard, ToolDefinition
from invoice_core_processor.services.validation import run_validation_checks
from invoice_core_processor.core.agent_registry import AgentRegistryService
import json

# --- Agent Definition ---

AGENT_ID = "com.invoice.validation"
CAPABILITY_VALIDATION = "CAPABILITY_VALIDATION"

ANOMALY_AGENT_CARD = AgentCard(
    agent_id=AGENT_ID,
    description="Implements validation, anomaly detection, and invoice reliability scoring.",
    tools=[
        ToolDefinition(
            tool_id="validate/run_checks",
            capability=CAPABILITY_VALIDATION,
            description="Runs a series of validation rules and computes a reliability score for a mapped invoice.",
            parameters={
                "mapped_schema": {"type": "dict"},
                "invoice_id": {"type": "str", "optional": True},
                "ocr_confidence": {"type": "float", "optional": True, "default": 1.0}
            }
        )
    ]
)

# --- MCP Tool Implementation ---

def run_checks(mapped_schema: dict, invoice_id: str, ocr_confidence: float) -> dict:
    """
    MCP tool wrapper for the run_validation_checks service.
    """
    print(f"AnomalyAgent: Received request to validate invoice {invoice_id}.")
    result = run_validation_checks(mapped_schema, ocr_confidence)
    print("AnomalyAgent: Validation complete. Would now save results to DB via DataStoreAgent.")
    return result

# --- MCP Server ---

class AnomalyAgentServer:
    def __init__(self):
        self.tools = {
            "validate/run_checks": run_checks,
        }
        print("AnomalyAgent MCP Server initialized.")

    def register_self(self):
        """Registers the agent with the AgentRegistryService."""
        registry = AgentRegistryService()
        print(f"Attempting to register agent '{AGENT_ID}' with the registry...")
        registration_result = registry.register_agent(ANOMALY_AGENT_CARD)
        print(f"Registration result: {registration_result}")

    def run(self):
        """Simulates the server running and listening for requests."""
        self.register_self()
        print("\nAnomalyAgent MCP Server running (simulation)...")

if __name__ == "__main__":
    server = AnomalyAgentServer()
    server.run()
