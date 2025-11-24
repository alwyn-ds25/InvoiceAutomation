# core/mcp_clients.py

from servers.database_server import DataStoreAgentServer
from servers.ocr_server import OCRAgentServer
from servers.mapper_server import SchemaMapperAgentServer
from servers.agent_server import AnomalyAgentServer
from core.integration_agent import DataIntegrationAgentServer
from microservices.ingestion.main import get_ingestion_service # Use the factory
import asyncio

class MCPClient:
    _server_registry = None

    def __init__(self):
        if MCPClient._server_registry is None:
            print("Initializing server registry for MCPClient simulation...")
            MCPClient._server_registry = {
                "com.invoice.datastore": DataStoreAgentServer(),
                "com.invoice.ocr": OCRAgentServer(),
                "com.invoice.mapper": SchemaMapperAgentServer(),
                "com.invoice.validation": AnomalyAgentServer(),
                "com.invoice.integration": DataIntegrationAgentServer(),
            }
            print("Server registry initialized.")

    def call_tool(self, agent_id: str, tool_id: str, **kwargs):
        print(f"[MCPClient] Calling tool '{tool_id}' on agent '{agent_id}'")
        server = self._server_registry.get(agent_id)
        if not server:
            return {"status": "ERROR", "error": f"Agent '{agent_id}' not found."}
        tool_func = server.tools.get(tool_id)
        if not tool_func:
            return {"status": "ERROR", "error": f"Tool '{tool_id}' not found."}

        if asyncio.iscoroutinefunction(tool_func):
            return asyncio.run(tool_func(**kwargs))
        else:
            return tool_func(**kwargs)

class IngestionGrpcClient:
    """
    Simulated gRPC client that now uses the factory to get the service instance.
    """
    def __init__(self):
        # The client no longer instantiates the service directly.
        # It will get it from the factory when needed.
        self.service_factory = get_ingestion_service

    async def ingest_file(self, user_id: str, file_path: str):
        # Get a service instance from the factory
        service = self.service_factory()

        from microservices.ingestion.main import MockIngestionRequest
        request = MockIngestionRequest(user_id=user_id, file_path=file_path)
        response = await service.IngestFile(request, context=None)

        return {
            "invoice_id": response.invoice_id,
            "storage_path": response.storage_path,
            "status": response.status,
            "message": response.message
        }
