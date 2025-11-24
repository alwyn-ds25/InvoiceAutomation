# To allow running this file directly for testing
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.models import AgentCard, ToolDefinition
from core.agent_registry import AgentRegistryService
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
    """Generates a mock JSON payload for Zoho Books."""
    return {
        "customer_name": schema.get("vendor_name", "Unknown"),
        "invoice_number": schema.get("invoice_number"),
        "date": schema.get("invoice_date"),
        "line_items": [
            {
                "item_id": f"item_{i+1}",
                "name": item.get("description"),
                "rate": item.get("unit_price"),
                "quantity": item.get("quantity")
            } for i, item in enumerate(schema.get("line_items", []))
        ],
        "total": schema.get("total_amount")
    }

def generate_tally_payload(schema: Dict[str, Any]) -> str:
    """Generates a mock XML payload for TallyPrime."""
    items_xml = "".join([
        f"<ALLLEDGERENTRIES.LIST>\n"
        f"  <LEDGERNAME>{item.get('description')}</LEDGERNAME>\n"
        f"  <ISDEEMEDPOSITIVE>No</ISDEEMEDPOSITIVE>\n"
        f"  <AMOUNT>{item.get('total')}</AMOUNT>\n"
        f"</ALLLEDGERENTRIES.LIST>"
        for item in schema.get("line_items", [])
    ])
    return (
        f"<ENVELOPE>\n"
        f"  <TALLYREQUEST>Import Data</TALLYREQUEST>\n"
        f"  <VOUCHER VCHTYPE='Sales' ACTION='Create'>\n"
        f"    <DATE>{schema.get('invoice_date')}</DATE>\n"
        f"    <NARRATION>Invoice {schema.get('invoice_number')}</NARRATION>\n"
        f"    <PARTYLEDGERNAME>{schema.get('vendor_name')}</PARTYLEDGERNAME>\n"
        f"    {items_xml}\n"
        f"  </VOUCHER>\n"
        f"</ENVELOPE>"
    )

# --- MCP Tool Implementation ---

def push_to_erp(invoice_id: str, target_system: str, mapped_schema: dict, reliability_score: float) -> dict:
    """
    MCP tool that generates and mock-pushes a payload to an ERP.
    """
    print(f"DataIntegrationAgent: Received request to sync invoice {invoice_id} to {target_system}.")

    if reliability_score < 75.0:
        return {
            "status": "FAILED_SYNC",
            "reason": f"Reliability score ({reliability_score}) is below the sync threshold of 75.",
            "integration_metadata": None
        }

    payload = None
    if target_system == "ZOHO":
        payload = generate_zoho_payload(mapped_schema)
    elif target_system == "TALLY":
        payload = generate_tally_payload(mapped_schema)
    elif target_system == "QUICKBOOKS":
        payload = generate_zoho_payload(mapped_schema)
    else:
        return {"status": "FAILED_SYNC", "reason": f"Target system '{target_system}' not supported."}

    # Mock API call
    print(f"--- Mock API Call to {target_system} ---")
    print("Payload:")
    print(json.dumps(payload, indent=2) if isinstance(payload, dict) else payload)
    print("------------------------------------")

    return {
        "status": "SYNCED_SUCCESS",
        "payload_preview": {"customer_name": "Mock Vendor"} if isinstance(payload, dict) else str(payload)[:100] + "...",
        "integration_metadata": {"erp_invoice_id": f"erp-{invoice_id}"}
    }

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
