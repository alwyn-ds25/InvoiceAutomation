# InvoiceCoreProcessor

InvoiceCoreProcessor is a high-performance, agentic module for automated invoice ingestion, OCR, schema mapping, validation, anomaly detection, and posting into accounting systems.

## Features

- Invoice ingestion from various file formats
- Cascading OCR pipeline for text extraction
- LLM-based schema mapping
- Validation and anomaly detection
- Integration with accounting systems (Tally, Zoho, QuickBooks)
- Reporting and review capabilities

## Tech Stack

- FastAPI
- LangGraph
- Google A2A SDK
- Model Context Protocol (MCP)
- gRPC
- MongoDB
- PostgreSQL

## Getting Started

1. Clone the repository.
2. Create a virtual environment: `python -m venv venv && source venv/bin/activate`
3. Install the dependencies: `pip install -r requirements.txt`
4. Copy `.env.example` to `.env` and fill in the required values.
5. Run database migrations (if implemented).
6. Start the services:
   - DataStore MCP server
   - OCR MCP server
   - Mapper MCP server
   - Validation MCP server
   - Ingestion gRPC server
   - `main_processor.py` (FastAPI)

## API Usage

### Upload Invoice

- **URL:** `/invoice/upload`
- **Method:** `POST`
- **Body:**
  ```json
  {
    "user_id": "string",
    "file_path": "string",
    "target_system": "TALLY" | "ZOHO" | "QUICKBOOKS"
  }
  ```
- **Response:**
  ```json
  {
    "workflow_status": "string",
    "invoice_id": "string",
    "reliability_score": "float",
    "validation_flags": "array",
    "integration_status": "string"
  }
  ```

## Agent Network

The InvoiceCoreProcessor uses a network of agents to process invoices. These agents are discovered and orchestrated using the AgentRegistryService.

## Extensibility

New agents can be added to the system by creating a new MCP server and registering it with the AgentRegistryService.
