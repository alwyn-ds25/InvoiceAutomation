from invoice_core_processor.core.models import AgentCard, ToolDefinition
from invoice_core_processor.services.summary_agent_service import SummaryAgentService
from invoice_core_processor.core.agent_registry import AgentRegistryService
from typing import Dict, Any

# --- Agent Definition ---

AGENT_ID = "com.invoice.summary"
CAPABILITY_SUMMARY = "CAPABILITY_SUMMARY"

SUMMARY_AGENT_CARD = AgentCard(
    agent_id=AGENT_ID,
    description="Generates a human-readable summary of the invoice validation and integration status.",
    tools=[
        ToolDefinition(
            tool_id="summary/generate",
            capability=CAPABILITY_SUMMARY,
            description="Takes invoice data and generates a summary.",
            parameters={
                "invoice_data": {"type": "dict"}
            }
        )
    ]
)

# --- MCP Tool Implementation ---

def generate_summary(invoice_data: Dict[str, Any]) -> dict:
    """
    MCP tool wrapper for the SummaryAgentService.
    """
    print(f"SummaryAgent: Received request to generate summary.")
    service = SummaryAgentService()
    return service.generate_summary(invoice_data)

# --- MCP Server ---

class SummaryAgentServer:
    def __init__(self):
        self.tools = {
            "summary/generate": generate_summary,
        }
        print("SummaryAgent MCP Server initialized.")

    def register_self(self):
        """Registers the agent with the AgentRegistryService."""
        registry = AgentRegistryService()
        print(f"Attempting to register agent '{AGENT_ID}' with the registry...")
        registration_result = registry.register_agent(SUMMARY_AGENT_CARD)
        print(f"Registration result: {registration_result}")

    def run(self):
        """Simulates the server running and listening for requests."""
        self.register_self()
        print("\nSummaryAgent MCP Server running (simulation)...")

if __name__ == "__main__":
    server = SummaryAgentServer()
    server.run()
