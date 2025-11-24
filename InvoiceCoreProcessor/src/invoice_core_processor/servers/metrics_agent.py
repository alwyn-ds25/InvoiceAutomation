from invoice_core_processor.core.models import AgentCard, ToolDefinition
from invoice_core_processor.services.metrics import get_all_metrics
from invoice_core_processor.core.agent_registry import AgentRegistryService

# --- Agent Definition ---

AGENT_ID = "com.invoice.metrics"
CAPABILITY_METRICS = "CAPABILITY_METRICS"

METRICS_AGENT_CARD = AgentCard(
    agent_id=AGENT_ID,
    description="Collects and reports on key performance indicators (KPIs) for the invoice processing system.",
    tools=[
        ToolDefinition(
            tool_id="metrics/get_all",
            capability=CAPABILITY_METRICS,
            description="Retrieves a comprehensive set of KPIs.",
            parameters={}
        )
    ]
)

# --- MCP Tool Implementation ---

def get_all_kpis() -> dict:
    """MCP tool wrapper for the get_all_metrics service."""
    print("MetricsCollectorAgent: Received request to get all KPIs.")
    return get_all_metrics()

# --- MCP Server ---

class MetricsCollectorAgentServer:
    def __init__(self):
        self.tools = {
            "metrics/get_all": get_all_kpis,
        }
        print("MetricsCollectorAgent MCP Server initialized.")

    def register_self(self):
        """Registers the agent with the AgentRegistryService."""
        registry = AgentRegistryService()
        print(f"Attempting to register agent '{AGENT_ID}' with the registry...")
        registration_result = registry.register_agent(METRICS_AGENT_CARD)
        print(f"Registration result: {registration_result}")

    def run(self):
        """Simulates the server running and listening for requests."""
        self.register_self()
        print("\nMetricsCollectorAgent MCP Server running (simulation)...")

if __name__ == "__main__":
    server = MetricsCollectorAgentServer()
    server.run()
