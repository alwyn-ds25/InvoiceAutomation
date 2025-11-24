from invoice_core_processor.core.models import AgentCard, ToolDefinition
from invoice_core_processor.services.mapping import map_text_to_schema
from invoice_core_processor.core.agent_registry import AgentRegistryService
import json

# --- Agent Definition ---

AGENT_ID = "com.invoice.mapper"
CAPABILITY_MAPPING = "CAPABILITY_MAPPING"

MAPPER_AGENT_CARD = AgentCard(
    agent_id=AGENT_ID,
    description="Uses an LLM to map extracted OCR text to a canonical invoice schema.",
    tools=[
        ToolDefinition(
            tool_id="map/execute",
            capability=CAPABILITY_MAPPING,
            description="Takes raw extracted text and maps it to a structured canonical invoice JSON.",
            parameters={
                "extracted_text": {"type": "str"},
                "target_system": {"type": "str", "enum": ["TALLY", "ZOHO", "QUICKBOOKS"]}
            }
        )
    ]
)

# --- MCP Tool Implementation ---

def execute_mapping(extracted_text: str, target_system: str) -> dict:
    """
    MCP tool wrapper for the map_text_to_schema service.
    """
    print(f"SchemaMapperAgent: Received request to map text for {target_system}.")
    return map_text_to_schema(extracted_text, target_system)

# --- MCP Server ---

class SchemaMapperAgentServer:
    def __init__(self):
        self.tools = {
            "map/execute": execute_mapping,
        }
        print("SchemaMapperAgent MCP Server initialized.")

    def register_self(self):
        """Registers the agent with the AgentRegistryService."""
        registry = AgentRegistryService()
        print(f"Attempting to register agent '{AGENT_ID}' with the registry...")
        registration_result = registry.register_agent(MAPPER_AGENT_CARD)
        print(f"Registration result: {registration_result}")

    def run(self):
        """Simulates the server running and listening for requests."""
        self.register_self()
        print("\nSchemaMapperAgent MCP Server running (simulation)...")

if __name__ == "__main__":
    server = SchemaMapperAgentServer()
    server.run()
