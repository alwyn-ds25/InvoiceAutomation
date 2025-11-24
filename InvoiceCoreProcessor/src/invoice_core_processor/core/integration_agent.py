from invoice_core_processor.core.models import AgentCard, ToolDefinition
from invoice_core_processor.core.agent_registry import AgentRegistryService
import json
from typing import Dict, Any

# --- Agent Definition ---

AGENT_ID = "com.invoice.integration"
CAPABILITY_INTEGRATION = "CAPABILITY_INTEGRATION"

INTEGRATION_AGENT_CARD = AgentCard(
    agent_id=AGENT_ID,
    description="Takes a validated canonical invoice and produces ERP-ready payloads (JSON/XML).",
    tools=[
        ToolDefinition(
            tool_id="sync/push_to_erp",
            capability=CAPABILITY_INTEGRATION,
            description="Generates and (mock) pushes a payload to a target ERP system.",
            parameters={
                "invoice_id": {"type": "str"},
                "target_system": {"type": "str", "enum": ["TALLY", "ZOHO", "QUICKBOOKS"]},
                "mapped_schema": {"type": "dict"},
                "reliability_score": {"type": "float"}
            }
        )
    ]
)

# --- Payload Generation Logic ---

def generate_zoho_payload(schema: Dict[str, Any]) -> Dict[str, Any]:
    # ... (logic remains the same)
    return {}

def generate_tally_payload(schema: Dict[str, Any]) -> str:
    # ... (logic remains the same)
    return ""

# --- MCP Tool Implementation ---

def push_to_erp(invoice_id: str, target_system: str, mapped_schema: dict, reliability_score: float) -> dict:
    # ... (logic remains the same) ...
    return {"status": "SYNCED_SUCCESS"}

# --- MCP Server ---

class DataIntegrationAgentServer:
    def __init__(self):
        self.tools = {"sync/push_to_erp": push_to_erp}
        print("DataIntegrationAgent MCP Server initialized.")

    def register_self(self):
        """Registers the agent with the AgentRegistryService."""
        registry = AgentRegistryService()
        print(f"Attempting to register agent '{AGENT_ID}' with the registry...")
        registration_result = registry.register_agent(INTEGRATION_AGENT_CARD)
        print(f"Registration result: {registration_result}")

    def run(self):
        """Simulates the server running and listening for requests."""
        self.register_self()
        print("\nDataIntegrationAgent MCP Server running (simulation)...")

if __name__ == "__main__":
    server = DataIntegrationAgentServer()
    server.run()
