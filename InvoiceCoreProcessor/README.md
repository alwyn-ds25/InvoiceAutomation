# InvoiceCoreProcessor

A high-performance, agentic microservice for automated invoice ingestion, OCR, schema mapping, validation, anomaly detection, and posting into accounting systems (Tally, Zoho, QuickBooks).

## 1. Overview

### 1.1 Service Name & Purpose

**InvoiceCoreProcessor** is a multi-agent microservice that orchestrates the complete invoice processing pipeline from file upload to accounting system integration. It handles invoice ingestion and validation in the accounting platform, providing automated extraction, validation, and integration capabilities.

### 1.2 Responsibilities & Boundaries

**What this service owns:**
- Invoice ingestion and file management
- OCR text extraction via cascading pipeline
- LLM-based schema mapping to target accounting systems
- Validation rules and anomaly detection
- Invoice data persistence (PostgreSQL for structured data, MongoDB for unstructured)
- Workflow orchestration using LangGraph
- Agent registry and discovery via A2A (Agent-to-Agent) protocol

**What it explicitly does NOT do:**
- Does not send emails or notifications
- Does not manage user accounts or authentication
- Does not handle payment processing
- Does not manage accounting system credentials (assumes they are provided)

### 1.3 Architecture Overview

**Sync APIs:**
- REST API (FastAPI) on port `8000` (`/invoice/upload`, `/metrics`, `/invoice/summary`)
- gRPC Ingestion Service on port `50051` (`IngestFile`)

**Async Interfaces:**
- Agent-to-Agent (A2A) protocol for agent discovery and communication
- Model Context Protocol (MCP) for standardized tool invocation between agents

**Dependencies:**
- **PostgreSQL**: Stores structured invoice data, validation rules, workflow audit logs
- **MongoDB**: Stores unstructured invoice metadata and OCR payloads
- **A2A Registry**: Agent discovery service (configured via `A2A_REGISTRY_URL`)
- **LLM Services**: OpenAI GPT-4, GPT-4 Vision, Gemini, Azure Document Intelligence (optional)
- **OCR Services**: Typhoon OCR API, Tesseract, EasyOCR (cascading fallback)

**Architecture Diagram:**

```mermaid
graph TB
    Client[External Client] -->|HTTP POST| FastAPI[FastAPI REST API<br/>:8000]
    Client -->|gRPC| gRPC[gRPC Ingestion Service<br/>:50051]
    
    FastAPI --> LangGraph[LangGraph Orchestrator<br/>Workflow Engine]
    gRPC --> LangGraph
    
    LangGraph --> A2A[A2A Registry<br/>Agent Discovery]
    
    A2A --> OCR[OCR Agent<br/>MCP Server]
    A2A --> Mapper[Mapping Agent<br/>MCP Server]
    A2A --> Validator[Validation Agent<br/>MCP Server]
    A2A --> Integrator[Integration Agent<br/>MCP Server]
    A2A --> DataStore[DataStore Agent<br/>MCP Server]
    A2A --> Metrics[Metrics Agent<br/>MCP Server]
    A2A --> Summary[Summary Agent<br/>MCP Server]
    
    OCR --> OCRServices[OCR Services<br/>Typhoon/Tesseract/EasyOCR]
    Mapper --> LLM[LLM Services<br/>OpenAI/Gemini/Azure]
    Validator --> LLM
    Summary --> LLM
    
    DataStore --> PostgreSQL[(PostgreSQL<br/>Structured Data)]
    DataStore --> MongoDB[(MongoDB<br/>Unstructured Data)]
    
    Integrator --> Accounting[Accounting Systems<br/>Tally/Zoho/QuickBooks]
    
    style FastAPI fill:#4A90E2,stroke:#2E5C8A,color:#fff
    style LangGraph fill:#7B68EE,stroke:#5A4FCF,color:#fff
    style PostgreSQL fill:#336791,stroke:#1E4A6B,color:#fff
    style MongoDB fill:#47A248,stroke:#2D6E2F,color:#fff
    style OCR fill:#FF6B6B,stroke:#CC5555,color:#fff
    style Mapper fill:#4ECDC4,stroke:#3BA39C,color:#fff
    style Validator fill:#FFE66D,stroke:#CCB857,color:#000
    style Integrator fill:#95E1D3,stroke:#77B8A8,color:#000
```



**Workflow Diagram:**

```mermaid
flowchart LR
    Start([Invoice Upload]) --> Ingestion[Ingestion Step<br/>File Storage & Metadata]
    Ingestion --> OCR[OCR Step<br/>Text Extraction]
    OCR --> Mapping[Mapping Step<br/>Schema Transformation]
    Mapping --> Validation[Validation Step<br/>Rules & Anomaly Detection]
    Validation --> Decision{Validation<br/>Status?}
    Decision -->|Clean| Integration[Integration Step<br/>Post to Accounting System]
    Decision -->|Flagged| Integration
    Decision -->|Failed| Error[Error Handler]
    Integration --> Summary[Summary Step<br/>Generate Report]
    Summary --> End([Complete])
    Error --> End
    
    style Start fill:#4ECDC4,stroke:#3BA39C,color:#000
    style Ingestion fill:#95E1D3,stroke:#77B8A8,color:#000
    style OCR fill:#FF6B6B,stroke:#CC5555,color:#fff
    style Mapping fill:#4A90E2,stroke:#2E5C8A,color:#fff
    style Validation fill:#FFE66D,stroke:#CCB857,color:#000
    style Decision fill:#7B68EE,stroke:#5A4FCF,color:#fff
    style Integration fill:#95E1D3,stroke:#77B8A8,color:#000
    style Summary fill:#4ECDC4,stroke:#3BA39C,color:#000
    style End fill:#4ECDC4,stroke:#3BA39C,color:#000
    style Error fill:#FF6B6B,stroke:#CC5555,color:#fff
```

## 2. Getting Started (Local Development)

### 2.1 Prerequisites

**Languages & Runtimes:**
- Python 3.9+ (tested with Python 3.11)
- pip (Python package manager)

**Tools:**
- Docker & Docker Compose (for local PostgreSQL and MongoDB)
- Git

**Required Services:**
- PostgreSQL 12+ (local or Docker)
- MongoDB 4.4+ (local or Docker)
- A2A Registry service (configured via `A2A_REGISTRY_URL`)

**Optional (for OCR):**
- Tesseract OCR (for local OCR processing)
- EasyOCR dependencies (if using EasyOCR fallback)

### 2.2 Quick Start

**Windows (PowerShell):**
```powershell
# Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -e .

# Copy environment file
Copy-Item .env.example .env
# Edit .env with your configuration

# Seed validation rules
python -m invoice_core_processor.database.seed_rules

# Start services (run in separate terminals)
# Terminal 1: DataStore MCP Server
python -m invoice_core_processor.servers.database_server

# Terminal 2: OCR MCP Server
python -m invoice_core_processor.servers.ocr_server

# Terminal 3: Mapper MCP Server
python -m invoice_core_processor.servers.mapper_server

# Terminal 4: Validation MCP Server
python -m invoice_core_processor.servers.agent_server

# Terminal 5: Ingestion gRPC Server
python -m invoice_core_processor.microservices.ingestion.main

# Terminal 6: FastAPI Main Server
python main_processor.py
```

**Linux/macOS:**
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -e .

# Copy environment file
cp .env.example .env
# Edit .env with your configuration

# Seed validation rules
python -m invoice_core_processor.database.seed_rules

# Start services (run in separate terminals)
# Terminal 1: DataStore MCP Server
python -m invoice_core_processor.servers.database_server

# Terminal 2: OCR MCP Server
python -m invoice_core_processor.servers.ocr_server

# Terminal 3: Mapper MCP Server
python -m invoice_core_processor.servers.mapper_server

# Terminal 4: Validation MCP Server
python -m invoice_core_processor.servers.agent_server

# Terminal 5: Ingestion gRPC Server
python -m invoice_core_processor.microservices.ingestion.main

# Terminal 6: FastAPI Main Server
python main_processor.py
```

**Expected URLs:**
- FastAPI: http://localhost:8000
- FastAPI Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/ (root endpoint)
- Metrics: http://localhost:8000/metrics
- gRPC Ingestion: localhost:50051

### 2.3 Configuration

All configuration is managed via environment variables (loaded from `.env` file using `pydantic-settings`).

| Variable | Description | Required | Default / Example |
|----------|-------------|----------|-------------------|
| `POSTGRES_URI` | PostgreSQL connection string | Yes | `postgresql://user:pass@localhost:5432/invoices` |
| `MONGO_URI` | MongoDB connection string | Yes | `mongodb://localhost:27017` |
| `MONGO_DB_NAME` | MongoDB database name | Yes | `invoice_processor` |
| `A2A_REGISTRY_URL` | A2A registry service URL | Yes | `http://localhost:8080` |
| `ENV` | Environment name (dev/staging/prod) | No | `dev` |
| `OPENAI_API_KEY` | OpenAI API key for LLM services | No* | - |
| `OPENAI_MODEL` | OpenAI model to use | No | `gpt-4` |
| `OPENAI_ENABLED` | Enable OpenAI integration | No | `true` |
| `TYPHOON_OCR_API_KEY` | Typhoon OCR API key | No* | - |
| `TYPHOON_BASE_URL` | Typhoon OCR base URL | No | `https://api.opentyphoon.ai/v1` |
| `TYPHOON_MODEL` | Typhoon OCR model | No | `typhoon-ocr` |
| `GPT4_VISION_API_KEY` | GPT-4 Vision API key | No* | - |
| `GPT4_VISION_MODEL` | GPT-4 Vision model | No | `gpt-4o` |
| `AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT` | Azure Document Intelligence endpoint | No* | - |
| `AZURE_DOCUMENT_INTELLIGENCE_KEY` | Azure Document Intelligence key | No* | - |
| `TESSERACT_CMD_PATH` | Path to Tesseract executable | No* | Auto-detected |
| `EASYOCR_LANGUAGES` | EasyOCR language codes | No | `en` |
| `GEMINI_API_KEY` | Google Gemini API key | No* | - |
| `GEMINI_MODEL` | Gemini model | No | `gemini-2.0-flash` |

\* Required if using the corresponding OCR/LLM service

**Secrets Management:**
- Local development: Use `.env` file (never commit to version control)
- Production: Use environment variables or secrets management service (AWS Secrets Manager, HashiCorp Vault, etc.)
- The `.env` file is automatically loaded by `pydantic-settings` from the project root

### 2.4 Database & Migrations

**Starting Databases Locally:**

Using Docker Compose (recommended):
```bash
# Create docker-compose.yml if not present
docker-compose up -d postgres mongodb
```

Or manually:
- PostgreSQL: `docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=postgres postgres:15`
- MongoDB: `docker run -d -p 27017:27017 mongo:6`

**Running Migrations:**

The database schema is defined in `src/invoice_core_processor/database/schema.sql`. To apply it:

```bash
# Using psql
psql -U postgres -d invoices -f src/invoice_core_processor/database/schema.sql

# Or using connection string from .env
psql $POSTGRES_URI -f src/invoice_core_processor/database/schema.sql
```

**Note:** Alembic is included as a dependency but migrations are currently managed via SQL scripts. Future versions may use Alembic for migration management.

**Seed Data:**

Populate validation rules:
```bash
python -m invoice_core_processor.database.seed_rules
```

This creates default validation rules in the `validation_rule` table.

## 3. API & Contracts

### 3.1 REST APIs

**OpenAPI/Swagger Documentation:**
- Available at: http://localhost:8000/docs (Swagger UI)
- Available at: http://localhost:8000/redoc (ReDoc)

**Key Endpoints:**

#### `POST /invoice/upload`
Uploads an invoice file for processing.

**Request:**
```json
{
  "user_id": "user-123",
  "file_path": "/path/to/invoice.pdf",
  "target_system": "TALLY" | "ZOHO" | "QUICKBOOKS"
}
```

**Response:**
```json
{
  "workflow_status": "SYNCED_SUCCESS",
  "invoice_id": "uuid-here"
}
```

**Status Codes:**
- `200 OK`: Processing completed successfully
- `400 Bad Request`: Invalid request body
- `500 Internal Server Error`: Processing failed

#### `GET /metrics`
Retrieves comprehensive KPIs and metrics.

**Response:**
```json
{
  "total_invoices": 100,
  "processing_times": {...},
  "error_rates": {...}
}
```

#### `POST /invoice/summary`
Generates a summary of invoice validation and integration status.

**Request:**
```json
{
  "invoice": {...},
  "validation": {...},
  "integration": {...}
}
```

**Response:**
```json
{
  "summary": "Invoice processed successfully...",
  "status": "SUMMARY_GENERATED"
}
```

#### `GET /`
Health check endpoint.

**Response:**
```json
{
  "message": "InvoiceCoreProcessor is running."
}
```

### 3.2 gRPC APIs

**Service Definition:**
- Service: `ingestion.IngestionService`
- Method: `IngestFile`
- Port: `50051`

**Request:**
```protobuf
message IngestFileRequest {
  string user_id = 1;
  string file_path = 2;
}
```

**Response:**
```protobuf
message IngestFileResponse {
  string invoice_id = 1;
  string storage_path = 2;
  string status = 3;
  string message = 4;
}
```

**Example (Python):**
```python
import grpc
from invoice_core_processor.microservices.ingestion.protos import ingestion_pb2_grpc

channel = grpc.insecure_channel('localhost:50051')
stub = ingestion_pb2_grpc.IngestionServiceStub(channel)
# ... make RPC call
```

### 3.3 Async Interfaces

**Agent-to-Agent (A2A) Protocol:**
- Used for agent discovery and registration
- Agents register with the A2A registry on startup
- Orchestrator discovers agents by capability (e.g., `CAPABILITY_OCR`, `CAPABILITY_VALIDATION`)

**Model Context Protocol (MCP):**
- Standardized tool invocation between agents
- Each agent exposes tools via MCP
- Tools are called by agent ID and tool ID

**Message Flow:**
1. FastAPI receives upload request
2. LangGraph orchestrator invokes workflow
3. Workflow steps call agents via MCP
4. Agents interact with databases via DataStore agent
5. Final state returned to client

### 3.4 Versioning & Compatibility

**API Versioning:**
- Current version: `v1` (implicit)
- Future versions may use path-based versioning (`/api/v1/...`, `/api/v2/...`)

**Deprecation Policy:**
- Breaking changes will be communicated via release notes
- Deprecated endpoints will be supported for at least 2 major versions
- Migration guides will be provided for breaking changes

## 4. Observability & Ops

### 4.1 Logging

**Log Format:**
- Uses `loguru` for structured logging
- Plaintext format with timestamps
- Logs to both console and files

**Log Levels:**
- `INFO`: General operational messages
- `ERROR`: Error conditions requiring attention
- `DEBUG`: Detailed diagnostic information (enable via log level configuration)

**Log Files:**
- `app.log`: All INFO level and above logs (rotates at 10 MB, retains 7 days)
- `error.log`: ERROR level logs only (rotates at 10 MB, retains 7 days)

**Log Location:**
- Local: Project root directory
- Production: Configure via logging service (e.g., CloudWatch, ELK stack)

**Configuration:**
Logging is configured in `src/invoice_core_processor/config/logging_config.py`. To enable debug logging, modify the log level in the configuration.

### 4.2 Metrics

**Metrics Endpoint:**
- `GET /metrics`: Returns comprehensive KPIs

**Key Metrics:**
- Total invoices processed
- Processing times (average, p50, p95, p99)
- Error rates by step (ingestion, OCR, mapping, validation, integration)
- Queue lag (if async processing is implemented)
- Database connection pool status

**Future Enhancements:**
- Prometheus-compatible `/metrics` endpoint (Prometheus format)
- Custom business metrics (validation pass rate, integration success rate)

### 4.3 Tracing

**Current State:**
- Distributed tracing is not yet implemented
- Workflow steps are logged with correlation IDs (invoice_id)

**Future Plans:**
- OpenTelemetry integration
- Trace export to Jaeger/Zipkin
- Span creation for each workflow step

### 4.4 Health & Readiness

**Health Endpoints:**
- `GET /`: Basic health check (returns service status)
- Future: `/health` (liveness), `/ready` (readiness)

**Health Checks:**
- Service is running and can handle requests
- Future: Database connectivity, downstream service availability

**Readiness Checks (Future):**
- PostgreSQL connection
- MongoDB connection
- A2A registry connectivity
- All required MCP agents registered

## 5. Security & Compliance

### 5.1 Authentication

**Current State:**
- No authentication implemented (development phase)
- All endpoints are publicly accessible

**Future Plans:**
- JWT Bearer token authentication
- API key authentication for service-to-service calls
- mTLS for gRPC services

### 5.2 Authorization

**Authorization Model:**
- Not yet implemented
- Future: Role-Based Access Control (RBAC)
- Roles: `service`, `admin`, `user`

### 5.3 Secrets Management

**Secrets Storage:**
- Never stored in repository
- Local: `.env` file (gitignored)
- Production: Environment variables or secrets management service
- Sensitive keys: API keys, database credentials, JWT keys

**Best Practices:**
- Rotate API keys regularly
- Use least-privilege access for database users
- Encrypt secrets at rest in production

### 5.4 Data Classification

**Data Handled:**
- **PII**: User IDs, vendor/customer information
- **Financial Data**: Invoice amounts, tax information, payment details
- **Business Data**: Invoice numbers, vendor names, line items

**Compliance:**
- Audit logging: Workflow audit table tracks all state transitions
- Data retention: Configured per environment
- GDPR considerations: User data can be deleted via data retention policies

## 6. Deployment

### 6.1 Environments

**Environments:**
- `dev`: Development environment
- `staging`: Staging environment (mirrors production)
- `prod`: Production environment

**Environment URLs:**
- Dev: `http://localhost:8000` (local)
- Staging: Configure per deployment
- Prod: Configure per deployment

### 6.2 Deployment Process

**CI/CD Pipeline:**
- Not yet configured
- Future: GitHub Actions / GitLab CI

**Deployment Steps (Manual):**
1. Build Docker image (if containerized)
2. Run database migrations
3. Deploy service with environment-specific configuration
4. Verify health endpoints
5. Monitor logs for errors

**Rollback:**
- Revert to previous version
- Rollback database migrations if needed
- Verify service health

### 6.3 Config Differences Per Environment

**Environment-Specific Variables:**
- `ENV`: Set to `dev`, `staging`, or `prod`
- Database URIs: Different per environment
- API keys: Different keys per environment
- Log levels: More verbose in dev, less in prod

**Feature Flags:**
- `OPENAI_ENABLED`: Enable/disable OpenAI integration
- Future: Feature flags for new capabilities

## 7. Testing & Quality

### 7.1 Running Tests Locally

**Unit Tests:**
```bash
# Run all tests
python -m pytest tests/

# Run specific test file
python -m pytest tests/test_workflow.py

# Run with coverage
python -m pytest tests/ --cov=invoice_core_processor --cov-report=html
```

**Test Files:**
- `tests/test_workflow.py`: Workflow orchestration tests
- `tests/test_ocr_agent.py`: OCR agent tests
- `tests/test_validation_agent.py`: Validation agent tests
- `tests/test_datastore_agent.py`: DataStore agent tests
- `tests/test_metrics_agent.py`: Metrics agent tests
- `tests/test_summary_agent.py`: Summary agent tests

**Integration Tests:**
- Not yet implemented
- Future: End-to-end tests with test databases

### 7.2 Code Style & Linting

**Linting:**
```bash
# Using ruff (if configured)
ruff check .

# Using pylint (if configured)
pylint src/
```

**Code Formatting:**
```bash
# Using black (if configured)
black src/ tests/

# Using ruff format
ruff format .
```

**Type Checking:**
```bash
# Using mypy (if configured)
mypy src/
```

### 7.3 Contract Tests

**Contract Testing:**
- Not yet implemented
- Future: Pact tests for inter-service contracts

## 8. Failure Modes & Troubleshooting

### 8.1 Common Errors

**500 Error on `/invoice/upload`:**
- **Cause**: Database connection failure
- **Diagnosis**: Check `POSTGRES_URI` and `MONGO_URI` in `.env`
- **Solution**: Ensure databases are running and accessible

**"Agent not found" errors:**
- **Cause**: MCP agent not registered or A2A registry unreachable
- **Diagnosis**: Check A2A registry logs, verify `A2A_REGISTRY_URL`
- **Solution**: Ensure all MCP servers are running and can reach the registry

**OCR failures:**
- **Cause**: Missing API keys or file not found
- **Diagnosis**: Check OCR service logs, verify file path exists
- **Solution**: Configure `TYPHOON_OCR_API_KEY` or other OCR service keys

**Database migration errors:**
- **Cause**: Schema not applied or version mismatch
- **Diagnosis**: Check PostgreSQL logs, verify schema.sql was applied
- **Solution**: Re-run schema.sql or check for conflicting migrations

### 8.2 Known Limitations

- Bulk uploads > 100 invoices not optimized (processes sequentially)
- Large files (> 50 MB) may timeout (configure timeout settings)
- Concurrent processing limited by database connection pool
- No retry mechanism for failed OCR calls (future enhancement)

### 8.3 Debug Logging

**Enable Debug Logging:**
Modify `src/invoice_core_processor/config/logging_config.py`:
```python
logger.add(sys.stderr, level="DEBUG")  # Change from "INFO" to "DEBUG"
```

**View Logs:**
```bash
# Windows
Get-Content app.log -Tail 50
Get-Content error.log -Tail 50

# Linux/macOS
tail -f app.log
tail -f error.log
```

### 8.4 Where to Look When Something Fails

1. **Application Logs**: `app.log`, `error.log` in project root
2. **FastAPI Logs**: Console output from `main_processor.py`
3. **Database Logs**: PostgreSQL and MongoDB logs
4. **Agent Logs**: Console output from MCP servers
5. **Workflow Audit**: Check `workflow_audit` table in PostgreSQL for state transitions

## 9. Contribution Guide

### 9.1 Branching Strategy

- **Main branch**: `main` (production-ready code)
- **Feature branches**: `feature/description` (new features)
- **Bug fixes**: `fix/description` (bug fixes)
- **Hotfixes**: `hotfix/description` (urgent production fixes)

### 9.2 Commit Message Conventions

Follow conventional commits:
- `feat: Add new validation rule`
- `fix: Resolve OCR timeout issue`
- `docs: Update README with deployment steps`
- `refactor: Simplify workflow orchestration`
- `test: Add integration tests for mapping agent`

### 9.3 Code Review Rules

- All changes require at least one approval
- Tests must pass before merging
- Code must follow style guidelines
- Documentation must be updated for API changes

### 9.4 Adding a New Endpoint

1. Add endpoint to `main_processor.py`
2. Define request/response models using Pydantic
3. Add OpenAPI documentation (docstrings)
4. Write unit tests
5. Update this README's API section

### 9.5 Adding a New Agent

1. Create agent server in `src/invoice_core_processor/servers/`
2. Define agent card with capabilities and tools
3. Register agent with AgentRegistryService
4. Add agent to workflow if needed
5. Write tests for the agent
6. Update `docs/agents.md`

## 10. Project Structure

**Directory Structure Diagram:**

```mermaid
graph TD
    Root[InvoiceCoreProcessor/] --> Main[main_processor.py<br/>FastAPI Entry Point]
    Root --> Config[pyproject.toml<br/>Dependencies]
    Root --> Scripts[start-services.ps1<br/>start-services.sh]
    Root --> Docs[docs/]
    Root --> Src[src/invoice_core_processor/]
    Root --> Tests[tests/]
    
    Docs --> Arch[architecture.md]
    Docs --> API[api.md]
    Docs --> Schema[db_schema.md]
    Docs --> Agents[agents.md]
    
    Src --> ConfigDir[config/]
    Src --> Core[core/]
    Src --> Database[database/]
    Src --> Microservices[microservices/]
    Src --> Prompts[prompts/]
    Src --> Servers[servers/]
    Src --> Services[services/]
    
    ConfigDir --> Settings[settings.py<br/>Environment Config]
    ConfigDir --> Logging[logging_config.py]
    ConfigDir --> Schemas[accounting_schemas.py]
    
    Core --> Workflow[workflow.py<br/>LangGraph Orchestration]
    Core --> Registry[agent_registry.py<br/>A2A Integration]
    Core --> Models[models.py<br/>Data Models]
    Core --> MCP[mcp_clients.py<br/>MCP Client]
    Core --> DB[database.py<br/>DB Connections]
    
    Database --> SchemaSQL[schema.sql<br/>PostgreSQL Schema]
    Database --> Seed[seed_rules.py<br/>Validation Rules]
    
    Microservices --> Ingestion[ingestion/<br/>gRPC Service]
    Ingestion --> Proto[protos/<br/>gRPC Definitions]
    
    Servers --> OCRServer[ocr_server.py]
    Servers --> MapperServer[mapper_server.py]
    Servers --> ValidServer[agent_server.py]
    Servers --> DataServer[database_server.py]
    Servers --> MetricsServer[metrics_agent.py]
    Servers --> SummaryServer[summary_server.py]
    
    Services --> OCRService[ocr_processor.py<br/>Cascading OCR]
    Services --> MappingService[mapping.py<br/>Schema Mapping]
    Services --> ValidationService[validation.py<br/>Validation Engine]
    Services --> IngestionService[ingestion.py<br/>File Ingestion]
    Services --> MetricsService[metrics.py<br/>KPI Collection]
    
    Prompts --> SchemaPrompt[schema.py]
    Prompts --> ValidationPrompt[validation_prompt.py]
    Prompts --> OCRPrompt[typhoon_ocr.py]
    Prompts --> SummaryPrompt[summary_prompt.py]
    
    Tests --> TestWorkflow[test_workflow.py]
    Tests --> TestOCR[test_ocr_agent.py]
    Tests --> TestValidation[test_validation_agent.py]
    Tests --> TestDataStore[test_datastore_agent.py]
    Tests --> TestMetrics[test_metrics_agent.py]
    Tests --> TestSummary[test_summary_agent.py]
    
    style Root fill:#4A90E2,stroke:#2E5C8A,color:#fff
    style Src fill:#7B68EE,stroke:#5A4FCF,color:#fff
    style Core fill:#FF6B6B,stroke:#CC5555,color:#fff
    style Servers fill:#4ECDC4,stroke:#3BA39C,color:#000
    style Services fill:#FFE66D,stroke:#CCB857,color:#000
    style Tests fill:#95E1D3,stroke:#77B8A8,color:#000
```

**Key Directories:**

- **`main_processor.py`**: FastAPI application entry point
- **`src/invoice_core_processor/core/`**: Core orchestration logic (LangGraph workflow, agent registry)
- **`src/invoice_core_processor/servers/`**: MCP agent servers (OCR, Mapping, Validation, etc.)
- **`src/invoice_core_processor/services/`**: Business logic services (OCR processing, validation engine)
- **`src/invoice_core_processor/microservices/`**: gRPC microservices (ingestion service)
- **`src/invoice_core_processor/database/`**: Database schemas and seed scripts
- **`src/invoice_core_processor/prompts/`**: LLM prompts for various agents
- **`src/invoice_core_processor/config/`**: Configuration management
- **`tests/`**: Unit and integration tests
- **`docs/`**: Additional documentation

## 11. Additional Resources

- **Architecture Documentation**: `docs/architecture.md`
- **API Documentation**: `docs/api.md`
- **Database Schema**: `docs/db_schema.md`
- **Agent Documentation**: `docs/agents.md`
- **Project Root README**: `../README.md`

---

**Version**: 1.0.0  
**Last Updated**: 2024
