import grpc
from concurrent import futures
import os
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from functools import lru_cache

# ... (Mock Protobuf code remains the same) ...
class MockIngestionRequest:
    def __init__(self, user_id, file_path): self.user_id = user_id; self.file_path = file_path
class MockIngestionResponse:
    def __init__(self, invoice_id, storage_path, status, message):
        self.invoice_id = invoice_id; self.storage_path = storage_path; self.status = status; self.message = message
class MockIngestionServiceServicer:
    def IngestFile(self, request, context):
        context.set_code(grpc.StatusCode.UNIMPLEMENTED); context.set_details('Method not implemented!'); raise NotImplementedError('Method not implemented!')
def add_IngestionServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {'IngestFile': grpc.unary_unary_rpc_method_handler(servicer.IngestFile, request_deserializer=MockIngestionRequest, response_serializer=MockIngestionResponse)}
    generic_handler = grpc.method_handlers_generic_handler('ingestion.IngestionService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config.settings import get_settings
from services.ingestion import copy_file_to_uploads, create_ingestion_metadata
from core.database import get_mongo_client

class IngestionService(MockIngestionServiceServicer):
    def __init__(self, db_client: AsyncIOMotorClient):
        settings = get_settings()
        self.db = db_client[settings.MONGO_DB_NAME]
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.upload_dir = os.path.join(project_root, "uploads")
        if not os.path.exists(self.upload_dir):
            os.makedirs(self.upload_dir)
        print(f"Ingestion service initialized with DB. Uploads dir: {self.upload_dir}")

    async def IngestFile(self, request, context):
        try:
            storage_path = copy_file_to_uploads(request.file_path, self.upload_dir)
            metadata = create_ingestion_metadata(request.user_id, request.file_path, storage_path)
            await self.db.invoice_metadata.insert_one(metadata)
            return MockIngestionResponse(invoice_id=metadata['invoice_id'], storage_path=storage_path, status="SUCCESS", message="File ingested successfully.")
        except Exception as e:
            return MockIngestionResponse(invoice_id="", storage_path="", status="FAILURE", message=str(e))

# --- Factory Function ---

@lru_cache()
def get_ingestion_service() -> IngestionService:
    """
    Factory function to create and return a cached instance of the IngestionService.
    This encapsulates the dependency injection logic.
    """
    print("Creating new IngestionService instance...")
    db_client = get_mongo_client()
    return IngestionService(db_client)


# --- Server Boilerplate ---
async def serve():
    server = grpc.aio.server(futures.ThreadPoolExecutor(max_workers=10))
    ingestion_service_instance = get_ingestion_service() # Use the factory
    add_IngestionServiceServicer_to_server(ingestion_service_instance, server)
    server.add_insecure_port('[::]:50051')
    print("gRPC Ingestion Server starting on port 50051...")
    await server.start()
    await server.wait_for_termination()

if __name__ == '__main__':
    if not os.path.exists(".env"):
        with open(".env", "w") as f: f.write("POSTGRES_URI=postgresql://user:pass@localhost:5432/invoicedb\nMONGO_URI=mongodb://user:pass@localhost:27017\nMONGO_DB_NAME=invoice_core\nA2A_REGISTRY_URL=local\nLLM_API_KEY=\nOCR_TESSERACT_PATH=\nENV=dev\n")
    asyncio.run(serve())
