# InvoiceCoreProcessor

InvoiceCoreProcessor is a high-performance, agentic microservice for automated invoice ingestion, OCR, schema mapping, validation, anomaly detection, and posting into accounting systems.

## 1. Overview

- **Purpose**: To provide a centralized, automated solution for processing invoices, from initial ingestion to final integration with accounting systems.
- **Boundaries**: This service owns the entire invoice processing workflow, including data extraction, validation, and integration. It does **not** manage user accounts, authentication, or notifications.

## 2. Architecture

- **Sync APIs**: The service exposes a RESTful API on port `8000` for uploading invoices and retrieving metrics and summaries.
- **Async**: The core of the service is a `LangGraph` workflow that orchestrates a series of agents to process invoices asynchronously.
- **Dependencies**:
  - **PostgreSQL**: Used for storing structured data, such as invoice metadata, agent registry, and validation results.
  - **MongoDB**: Used for storing unstructured data, such as OCR text and logs.
  - **gRPC**: Used for communication between the main processor and the ingestion microservice.
  - **MCP (Model Context Protocol)**: Used for communication between the LangGraph orchestrator and the various agents in the workflow.

## 3. Getting Started

### Prerequisites

- Python 3.9+
- `pip` and `venv`

### Quick Start

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/example/InvoiceCoreProcessor.git
    cd InvoiceCoreProcessor
    ```

2.  **Create a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -e .
    ```

4.  **Set up the environment:**
    ```bash
    cp .env.example .env
    ```
    Fill in the required values in the `.env` file.

5.  **Run database migrations:**
    ```bash
    alembic upgrade head
    ```

6.  **Seed the database:**
    ```bash
    python -m invoice_core_processor.database.seed_rules
    ```

7.  **Run the service:**
    ```bash
    uvicorn invoice_core_processor.main_processor:app --host 127.0.0.1 --port 8000
    ```

The service will be available at `http://localhost:8000`.

### Configuration

| Variable                            | Description                               | Required | Default            |
| ----------------------------------- | ----------------------------------------- | -------- | ------------------ |
| `POSTGRES_URI`                      | PostgreSQL connection string.             | Yes      | -                  |
| `MONGO_URI`                         | MongoDB connection string.                | Yes      | -                  |
| `MONGO_DB_NAME`                     | MongoDB database name.                    | Yes      | -                  |
| `A2A_REGISTRY_URL`                  | The URL of the Agent Registry service.    | Yes      | -                  |
| `ENV`                               | The environment the service is running in | No       | `dev`              |
| `OPENAI_API_KEY`                    | The API key for the OpenAI service.       | No       | -                  |
| `TYPHOON_OCR_API_KEY`               | The API key for the Typhoon OCR service.  | No       | -                  |
| `GEMINI_API_KEY`                    | The API key for the Gemini service.       | No       | -                  |

## 4. API

The OpenAPI documentation is available at `http://localhost:8000/docs`.

### Example: Upload Invoice

**POST** `/invoice/upload`

**Request Body:**
```json
{
  "user_id": "string",
  "file_path": "string",
  "target_system": "TALLY"
}
```

**Response Body:**
```json
{
  "workflow_status": "string",
  "invoice_id": "string"
}
```

## 5. Observability

- **Health**: `GET /`
- **Metrics**: `GET /metrics`

## 6. Security

- Secrets are managed via the `.env` file.

## 7. Testing

- **Unit tests**: `python -m unittest discover`
- **Lint**: `ruff check .`

## 8. Deployment

- The CI/CD pipeline is managed by GitHub Actions.
- The service is deployed as a Docker container.

## 9. Troubleshooting

- **500 on `/invoice/upload`**: Ensure that all the required services are running and that the environment variables are set correctly.
- **High latency**: Check the logs for errors and warnings.
