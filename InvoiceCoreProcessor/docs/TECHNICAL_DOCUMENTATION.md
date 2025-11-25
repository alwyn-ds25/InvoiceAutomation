# Technical Documentation

## 1. Introduction

### 1.1 Purpose of This Document

This document provides comprehensive technical documentation for the **InvoiceCoreProcessor** microservice. It describes:

- **Technical Architecture**: Internal mechanics, code structure, and design patterns
- **Implementation Details**: How features are built, not just what they do
- **Developer Guide**: Everything needed to maintain, extend, test, and deploy the system
- **Deep Dive**: Complements high-level documentation with implementation specifics

This document is intended for:
- **Developers** working on the codebase
- **DevOps Engineers** deploying and maintaining the service
- **QA Engineers** writing tests and validating functionality
- **Technical Architects** making design decisions

### 1.2 Scope

This document covers:

- **Code Structure**: Directory layout, module organization, design patterns
- **API Design**: Internal API contracts, request/response models, error handling
- **Data Models**: Database schemas, domain models, validation rules
- **Tech Stack**: All technologies, frameworks, and libraries used
- **Dependencies**: External services, APIs, and integrations
- **Internal Workflows**: Detailed processing flows and state management
- **Testing Strategy**: Unit, integration, and E2E testing approaches
- **Deployment Model**: Infrastructure, CI/CD, and operational procedures

### 1.3 Document Structure

- **Sections 1-3**: Introduction, tech stack, repository structure
- **Sections 4-5**: Configuration and APIs
- **Sections 6-8**: Architecture, data models, business logic
- **Sections 9-11**: Integrations, security, observability
- **Sections 12-14**: Testing, local development, deployment
- **Sections 15-16**: Limitations and future enhancements

---

## 2. Technology Stack

### 2.1 Backend

**Language:**
- **Python 3.9+** (tested with Python 3.11)
- Type hints used throughout for better code clarity
- Async/await patterns for I/O operations

**Frameworks:**
- **FastAPI 0.104+**: REST API framework with automatic OpenAPI documentation
- **LangGraph**: Workflow orchestration and state machine management
- **Pydantic**: Data validation and settings management
- **Uvicorn**: ASGI server for FastAPI

**Key Libraries:**
- **psycopg2-binary**: PostgreSQL database adapter
- **motor**: Async MongoDB driver
- **grpcio / grpcio-tools**: gRPC support for microservice communication
- **loguru**: Structured logging
- **python-dotenv**: Environment variable management

### 2.2 Storage

**Databases:**
- **PostgreSQL 12+**: Primary database for structured data
  - Stores invoices, vendors, customers, validation rules, audit logs
  - ACID transactions for financial data integrity
  - JSONB support for flexible metadata storage
  
- **MongoDB 4.4+**: Document store for unstructured data
  - Stores OCR payloads, raw extracted text, metadata
  - Flexible schema for varying invoice formats
  - Async operations via Motor driver

**Query Frameworks:**
- **Raw SQL**: Direct SQL queries via psycopg2 for PostgreSQL
- **Motor**: Async MongoDB operations
- **No ORM**: Direct database access for performance and control

**Migration Tools:**
- **SQL Scripts**: Manual schema management via `schema.sql`
- **Alembic**: Included as dependency (future migration tool)

### 2.3 Messaging & Communication

**Protocols:**
- **REST (HTTP)**: FastAPI endpoints for external API
- **gRPC**: Internal microservice communication (Ingestion Service)
- **A2A (Agent-to-Agent)**: Agent discovery and registration protocol
- **MCP (Model Context Protocol)**: Standardized tool invocation between agents

**Current State:**
- Synchronous processing (no message queues yet)
- Direct function calls between agents via MCP
- Future: Kafka/RabbitMQ for async processing

### 2.4 Integrations

**OCR Services:**
- **Typhoon OCR API**: Primary cloud OCR service
- **OpenAI GPT-4 Vision**: Fallback OCR with vision capabilities
- **Azure Document Intelligence**: Enterprise OCR option
- **Tesseract OCR**: Local OCR fallback
- **EasyOCR**: Final fallback OCR engine

**LLM Services:**
- **OpenAI GPT-4**: Schema mapping and extraction
- **Google Gemini**: Alternative LLM provider
- **Azure OpenAI**: Enterprise OpenAI option

**Accounting Systems:**
- **Tally**: XML-based integration (planned)
- **Zoho Books**: REST API integration (planned)
- **QuickBooks**: REST API integration (planned)

### 2.5 Dev Tools

**Containerization:**
- **Docker**: Container runtime
- **docker-compose**: Local development orchestration (planned)

**CI/CD:**
- **GitHub Actions**: Planned CI/CD pipeline
- **Git**: Version control

**Code Quality:**
- **pytest**: Testing framework
- **unittest.mock**: Mocking for tests
- **ruff**: Linting and formatting (planned)
- **black**: Code formatting (planned)
- **mypy**: Type checking (planned)

**Documentation:**
- **Markdown**: Documentation format
- **Mermaid**: Diagram generation
- **Sphinx**: API documentation generation (planned)

---

## 3. Repository Structure

### 3.1 Directory Layout

```
InvoiceCoreProcessor/
├── main_processor.py              # FastAPI application entry point
├── pyproject.toml                 # Python project configuration and dependencies
├── README.md                       # Service-level documentation
├── HIGH_LEVEL_DOCUMENTATION.md     # System-level architecture docs
├── start-services.ps1             # Windows startup script
├── start-services.sh              # Linux/macOS startup script
│
├── src/
│   └── invoice_core_processor/     # Main package
│       ├── __init__.py
│       │
│       ├── config/                # Configuration management
│       │   ├── __init__.py
│       │   ├── settings.py        # Environment variables and settings
│       │   ├── logging_config.py  # Logging configuration
│       │   └── accounting_schemas.py  # Accounting system mappings
│       │
│       ├── core/                  # Core orchestration logic
│       │   ├── __init__.py
│       │   ├── workflow.py        # LangGraph workflow definition
│       │   ├── models.py          # Domain models and data structures
│       │   ├── agent_registry.py  # A2A agent discovery service
│       │   ├── mcp_clients.py     # MCP client implementation
│       │   ├── database.py        # Database connection factories
│       │   └── integration_agent.py  # Integration agent definition
│       │
│       ├── services/              # Business logic services
│       │   ├── __init__.py
│       │   ├── ingestion.py       # File ingestion service
│       │   ├── ocr_processor.py   # Cascading OCR pipeline
│       │   ├── mapping.py         # LLM-based schema mapping
│       │   ├── validation.py      # Validation rule engine
│       │   ├── metrics.py         # Metrics collection service
│       │   └── summary_agent_service.py  # Summary generation
│       │
│       ├── servers/               # MCP agent servers
│       │   ├── __init__.py
│       │   ├── database_server.py # DataStore agent server
│       │   ├── ocr_server.py      # OCR agent server
│       │   ├── mapper_server.py   # Mapping agent server
│       │   ├── agent_server.py    # Validation agent server
│       │   ├── metrics_agent.py   # Metrics agent server
│       │   └── summary_server.py # Summary agent server
│       │
│       ├── microservices/         # gRPC microservices
│       │   ├── __init__.py
│       │   └── ingestion/
│       │       ├── __init__.py
│       │       ├── main.py        # gRPC ingestion service
│       │       └── protos/        # Protocol buffer definitions
│       │           ├── ingestion_pb2.py
│       │           └── ingestion_pb2_grpc.py
│       │
│       ├── database/              # Database management
│       │   ├── schema.sql         # PostgreSQL schema definition
│       │   └── seed_rules.py      # Validation rules seed data
│       │
│       └── prompts/               # LLM prompts
│           ├── __init__.py
│           ├── schema.py          # Schema extraction prompt
│           ├── validation_prompt.py  # Validation prompt
│           ├── typhoon_ocr.py     # Typhoon OCR prompt
│           ├── summary_prompt.py  # Summary generation prompt
│           └── gpt_vision_model.py  # GPT Vision prompt
│
├── tests/                         # Test suite
│   ├── __init__.py
│   ├── test_workflow.py          # Workflow integration tests
│   ├── test_ocr_agent.py        # OCR agent tests
│   ├── test_validation_agent.py # Validation agent tests
│   ├── test_datastore_agent.py  # DataStore agent tests
│   ├── test_metrics_agent.py   # Metrics agent tests
│   └── test_summary_agent.py   # Summary agent tests
│
└── docs/                         # Documentation
    ├── API_DOCUMENTATION.md     # API reference
    ├── HIGH_LEVEL_DOCUMENTATION.md  # System architecture
    ├── TECHNICAL_DOCUMENTATION.md   # This document
    ├── architecture.md          # Architecture details
    ├── api.md                   # Legacy API docs
    ├── agents.md                # Agent documentation
    └── db_schema.md             # Database schema docs
```

### 3.2 Directory Responsibilities

**Root Level:**
- `main_processor.py`: FastAPI application entry point, route definitions
- `pyproject.toml`: Python package configuration, dependencies, metadata
- `README.md`: Service documentation for developers
- Startup scripts: Convenience scripts for local development

**`src/invoice_core_processor/config/`:**
- Configuration management and environment variable handling
- Logging setup and configuration
- Accounting system schema mappings

**`src/invoice_core_processor/core/`:**
- Workflow orchestration (LangGraph state machine)
- Domain models and data structures
- Agent registry and discovery
- MCP client implementation
- Database connection management

**`src/invoice_core_processor/services/`:**
- Business logic implementations
- OCR processing pipeline
- LLM-based mapping
- Validation rule engine
- Metrics collection

**`src/invoice_core_processor/servers/`:**
- MCP agent server implementations
- Agent registration and tool exposure
- Agent-to-agent communication

**`src/invoice_core_processor/microservices/`:**
- gRPC service implementations
- Protocol buffer definitions
- Service-to-service communication

**`src/invoice_core_processor/database/`:**
- Database schema definitions
- Migration scripts
- Seed data scripts

**`src/invoice_core_processor/prompts/`:**
- LLM prompt templates
- Prompt engineering for extraction and validation

**`tests/`:**
- Unit tests for individual components
- Integration tests for workflows
- Mock implementations for external services

**`docs/`:**
- API documentation
- Architecture documentation
- Technical documentation

---

## 4. Configuration & Environment Variables

### 4.1 Environment Variables

All configuration is managed via environment variables loaded from `.env` file using `pydantic-settings`.

| Variable | Description | Required | Default | Example |
|----------|-------------|----------|---------|---------|
| **Core Settings** |
| `POSTGRES_URI` | PostgreSQL connection string | Yes | - | `postgresql://user:pass@localhost:5432/invoices` |
| `MONGO_URI` | MongoDB connection string | Yes | - | `mongodb://localhost:27017` |
| `MONGO_DB_NAME` | MongoDB database name | Yes | - | `invoice_processor` |
| `A2A_REGISTRY_URL` | A2A registry service URL | Yes | - | `http://localhost:8080` |
| `ENV` | Environment name | No | `dev` | `dev`, `staging`, `prod` |
| **LLM Settings** |
| `OPENAI_API_KEY` | OpenAI API key | No* | - | `sk-...` |
| `OPENAI_MODEL` | OpenAI model name | No | `gpt-4` | `gpt-4`, `gpt-4-turbo` |
| `OPENAI_ENABLED` | Enable OpenAI integration | No | `true` | `true`, `false` |
| `GEMINI_API_KEY` | Google Gemini API key | No* | - | `...` |
| `GEMINI_MODEL` | Gemini model name | No | `gemini-2.0-flash` | `gemini-2.0-flash` |
| **OCR Settings** |
| `TYPHOON_OCR_API_KEY` | Typhoon OCR API key | No* | - | `...` |
| `TYPHOON_BASE_URL` | Typhoon OCR base URL | No | `https://api.opentyphoon.ai/v1` | - |
| `TYPHOON_MODEL` | Typhoon OCR model | No | `typhoon-ocr` | - |
| `TYPHOON_TASK_TYPE` | Typhoon task type | No | `default` | - |
| `TYPHOON_MAX_TOKENS` | Typhoon max tokens | No | `16000` | - |
| `TYPHOON_TEMPERATURE` | Typhoon temperature | No | `0.1` | - |
| `TYPHOON_TOP_P` | Typhoon top-p | No | `0.6` | - |
| `GPT4_VISION_API_KEY` | GPT-4 Vision API key | No* | - | `sk-...` |
| `GPT4_VISION_MODEL` | GPT-4 Vision model | No | `gpt-4o` | - |
| `GPT4_VISION_MAX_TOKENS` | GPT-4 Vision max tokens | No | `4000` | - |
| `AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT` | Azure DI endpoint | No* | - | `https://...` |
| `AZURE_DOCUMENT_INTELLIGENCE_KEY` | Azure DI key | No* | - | `...` |
| `TESSERACT_CMD_PATH` | Tesseract executable path | No* | Auto-detected | `/usr/bin/tesseract` |
| `EASYOCR_LANGUAGES` | EasyOCR language codes | No | `en` | `en`, `en,hi` |

\* Required if using the corresponding service

**Configuration Loading:**
- Environment variables take precedence over `.env` file
- `.env` file is loaded from project root (`InvoiceCoreProcessor/.env`)
- Settings are cached using `@lru_cache()` for performance
- Type validation via Pydantic models

### 4.2 Secrets Management

**Local Development:**
- Secrets stored in `.env` file (gitignored)
- Never committed to version control
- `.env.example` template provided (without actual secrets)

**Production:**
- Environment variables set in deployment platform
- Secrets stored in external vault (AWS Secrets Manager, HashiCorp Vault)
- Secrets rotated regularly (quarterly recommended)
- No secrets in code or configuration files

**Secret Rotation:**
- API keys rotated quarterly
- Database credentials rotated monthly
- JWT signing keys rotated annually (when implemented)

### 4.3 Feature Flags

**Current Implementation:**
- Environment-based flags via `ENV` variable
- Service enablement flags (e.g., `OPENAI_ENABLED`)

**Feature Flags:**
- `OPENAI_ENABLED`: Enable/disable OpenAI integration (default: `true`)
- `ENV`: Environment name affects logging levels and debug features

**Future Implementation:**
- Feature flag service (LaunchDarkly, Unleash)
- Per-user feature flags
- Gradual rollout capabilities
- A/B testing support

---

## 5. APIs

### 5.1 REST Endpoints

**Base URL:** `http://localhost:8000` (local), `https://api.invoice-automation.example.com` (production)

**OpenAPI Documentation:** Available at `/docs` (Swagger UI) and `/redoc` (ReDoc)

#### POST /invoice/upload

**Path:** `/invoice/upload`

**Method:** `POST`

**Auth:** Required (planned: JWT Bearer token)

**Request Body:**
```json
{
  "user_id": "user-123",
  "file_path": "/path/to/invoice.pdf",
  "target_system": "TALLY"
}
```

**Response:**
```json
{
  "workflow_status": "SYNCED_SUCCESS",
  "invoice_id": "inv-abc123-def456"
}
```

**Status Codes:**
- `200 OK`: Processing completed
- `400 Bad Request`: Invalid request body
- `404 Not Found`: File not found
- `500 Internal Server Error`: Processing failed

**Error Codes:**
- `INVALID_PAYLOAD`: Request validation failed
- `NOT_FOUND`: File not found
- `INTERNAL_ERROR`: Processing error

#### GET /metrics

**Path:** `/metrics`

**Method:** `GET`

**Auth:** Required (planned: `admin:metrics` scope)

**Query Parameters:** None

**Response:**
```json
{
  "total_invoices": 532,
  "processing_times": {...},
  "error_rates": {...}
}
```

**Status Codes:**
- `200 OK`: Metrics retrieved
- `403 Forbidden`: Insufficient permissions
- `500 Internal Server Error`: Metrics retrieval failed

#### POST /invoice/summary

**Path:** `/invoice/summary`

**Method:** `POST`

**Auth:** Required (planned: `invoice:read` scope)

**Request Body:**
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

### 5.2 gRPC Endpoints

**Service:** `ingestion.IngestionService`

**Port:** `50051`

**Method:** `IngestFile`

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

### 5.3 Event-based Interfaces

**Current State:** Synchronous processing, no message queues

**Planned Events:**

**Consumed Events:**
- `invoice.uploaded`: Invoice file uploaded (future)

**Produced Events:**
- `invoice.extracted`: OCR and extraction completed (future)
- `invoice.validated`: Validation completed (future)
- `invoice.posted`: Posted to accounting system (future)

**Event Schema (Planned):**
```json
{
  "event_type": "invoice.validated",
  "invoice_id": "inv-abc123",
  "timestamp": "2025-01-15T10:00:45Z",
  "data": {
    "status": "VALIDATED_FLAGGED",
    "reliability_score": 75.5
  },
  "metadata": {
    "correlation_id": "corr-123",
    "source": "invoice-core-processor"
  }
}
```

**Idempotency:**
- Events include `idempotency_key` based on invoice_id + timestamp
- Duplicate events are ignored

**Retry Policy:**
- Exponential backoff: 1s, 2s, 4s, 8s
- Maximum 3 retries
- Failed events sent to DLQ after retries exhausted

**DLQ Behavior:**
- Failed events stored in DLQ for manual review
- DLQ events can be reprocessed manually
- DLQ retention: 7 days

---

## 6. Internal Architecture

### 6.1 Core Components

#### Controllers

**FastAPI Routes (`main_processor.py`):**
- `POST /invoice/upload`: Invoice upload endpoint
- `GET /metrics`: Metrics retrieval endpoint
- `POST /invoice/summary`: Summary generation endpoint
- `GET /`: Health check endpoint

**Responsibilities:**
- Request validation (Pydantic models)
- Response formatting
- Error handling and HTTP status codes
- Authentication/authorization (planned)

#### Services

**Business Logic Services (`services/`):**

1. **`ingestion.py`**: File ingestion service
   - File copying to uploads directory
   - Metadata creation
   - MongoDB storage

2. **`ocr_processor.py`**: Cascading OCR pipeline
   - File type detection
   - OCR engine selection and fallback
   - Confidence scoring

3. **`mapping.py`**: LLM-based schema mapping
   - Prompt construction
   - LLM API calls
   - JSON schema extraction

4. **`validation.py`**: Validation rule engine
   - Rule execution
   - Score calculation
   - Flag generation

5. **`metrics.py`**: Metrics collection
   - KPI calculation
   - Aggregation
   - Reporting

6. **`summary_agent_service.py`**: Summary generation
   - LLM-based summarization
   - Report formatting

#### Adapters

**Database Adapters (`core/database.py`):**
- `get_postgres_connection()`: PostgreSQL connection factory
- `get_mongo_client()`: MongoDB client factory
- `get_mongo_db()`: MongoDB database instance

**API Integrations:**
- OpenAI client (in `mapping.py`)
- Typhoon OCR client (planned)
- Accounting system clients (planned)

#### Worker Jobs

**Current:** Synchronous processing, no background workers

**Planned:**
- Async job queue for bulk processing
- Background workers for OCR processing
- Scheduled jobs for metrics aggregation

#### Background Schedulers

**Current:** None

**Planned:**
- Periodic metrics aggregation
- Validation rule updates
- Agent health checks

### 6.2 Internal Flow

#### Invoice Upload Flow

```mermaid
sequenceDiagram
    participant Client
    participant FastAPI
    participant LangGraph
    participant Ingestion
    participant OCR
    participant Mapping
    participant Validation
    participant Integration
    participant DataStore
    participant PostgreSQL
    participant MongoDB

    Client->>FastAPI: POST /invoice/upload
    FastAPI->>LangGraph: Invoke workflow
    LangGraph->>Ingestion: ingestion_step()
    Ingestion->>MongoDB: Store metadata
    Ingestion->>DataStore: Save audit step
    DataStore->>PostgreSQL: INSERT workflow_audit
    LangGraph->>OCR: ocr_step()
    OCR->>OCR: Cascading OCR pipeline
    OCR->>DataStore: Save OCR payload
    DataStore->>MongoDB: Store OCR results
    LangGraph->>Mapping: mapping_step()
    Mapping->>Mapping: LLM extraction
    Mapping->>DataStore: Save audit step
    LangGraph->>Validation: validation_step()
    Validation->>PostgreSQL: Query validation rules
    Validation->>Validation: Run validation checks
    Validation->>DataStore: Save validation results
    DataStore->>PostgreSQL: INSERT validation_run
    LangGraph->>Integration: integration_step()
    Integration->>Integration: Generate payload
    Integration->>Integration: Post to accounting system
    Integration->>DataStore: Save audit step
    LangGraph->>FastAPI: Return final state
    FastAPI->>Client: Return response
```

#### Agent Communication Flow

```mermaid
sequenceDiagram
    participant Orchestrator
    participant A2A Registry
    participant Agent
    participant MCP Client
    participant Tool

    Orchestrator->>A2A Registry: lookup_agent_by_capability("CAPABILITY_OCR")
    A2A Registry->>Orchestrator: Return agent_id, tool_id
    Orchestrator->>MCP Client: call_tool(agent_id, tool_id, params)
    MCP Client->>Agent: Invoke tool
    Agent->>Tool: Execute tool function
    Tool->>Tool: Process request
    Tool->>Agent: Return result
    Agent->>MCP Client: Return response
    MCP Client->>Orchestrator: Return result
```

#### Error Handling Flow

```mermaid
flowchart TD
    Start[Request Received] --> Validate{Validate Request}
    Validate -->|Invalid| Error1[Return 400 Bad Request]
    Validate -->|Valid| Process[Process Request]
    Process --> Try{Try Operation}
    Try -->|Success| Success[Return 200 OK]
    Try -->|Error| Catch{Catch Exception}
    Catch -->|Validation Error| Error2[Return 422 Validation Error]
    Catch -->|Not Found| Error3[Return 404 Not Found]
    Catch -->|External Service Error| Retry{Retry?}
    Retry -->|Yes| Process
    Retry -->|No| Error4[Return 503 Service Unavailable]
    Catch -->|Internal Error| Error5[Return 500 Internal Error]
    Error5 --> Log[Log Error]
    Log --> End[End]
```

---

## 7. Data Models

### 7.1 ERD / DB Schema

**PostgreSQL Schema:**

**Core Tables:**

1. **`invoices`**
   - Primary key: `id` (UUID)
   - Foreign keys: `vendor_id`, `customer_id`
   - Unique constraint: `(vendor_id, invoice_no, invoice_date)`
   - Indexes: `invoice_no`, `invoice_date`, `user_id`

2. **`vendors`**
   - Primary key: `id` (UUID)
   - Unique constraint: `(name, gstin)`
   - Indexes: `name`, `gstin`

3. **`customers`**
   - Primary key: `id` (UUID)
   - Indexes: `name`, `gstin`

4. **`invoice_items`**
   - Primary key: `id` (UUID)
   - Foreign key: `invoice_id` → `invoices.id` (CASCADE DELETE)
   - Indexes: `invoice_id`

5. **`validation_rule`**
   - Primary key: `id` (SERIAL)
   - Unique constraint: `rule_id`
   - Indexes: `rule_id`, `category`, `is_active`

6. **`invoice_validation_run`**
   - Primary key: `id` (UUID)
   - Foreign key: `invoice_id` → `invoices.id` (CASCADE DELETE)
   - Indexes: `invoice_id`, `run_at`

7. **`invoice_validation_result`**
   - Primary key: `id` (BIGSERIAL)
   - Foreign key: `validation_run_id` → `invoice_validation_run.id` (CASCADE DELETE)
   - Foreign key: `rule_id` → `validation_rule.rule_id`
   - Indexes: `validation_run_id`, `rule_id`

8. **`workflow_audit`**
   - Primary key: `id` (BIGSERIAL)
   - Indexes: `invoice_id`, `timestamp`

9. **`agent_registry`**
   - Primary key: `id` (SERIAL)
   - Unique constraint: `agent_id`
   - Indexes: `agent_id`, `last_heartbeat`

10. **`agent_tools`**
    - Primary key: `id` (SERIAL)
    - Foreign key: `agent_id` → `agent_registry.agent_id` (CASCADE DELETE)
    - Unique constraint: `(agent_id, tool_id)`
    - Indexes: `agent_id`, `capability`

**MongoDB Collections:**

1. **`invoice_metadata`**
   - Stores ingestion metadata
   - Fields: `invoice_id`, `user_id`, `file_path`, `storage_path`, `upload_timestamp`

2. **`ocr_payloads`**
   - Stores OCR extraction results
   - Fields: `invoice_id`, `pages`, `tables`, `confidence`, `engine_trace`

### 7.2 Domain Models

**Python Domain Models (`core/models.py`):**

```python
# Invoice Processing Protocol
class InvoiceProcessingProtocol(BaseModel):
    user_id: str
    file_path: str
    target_system: TargetSystem  # "TALLY" | "ZOHO" | "QUICKBOOKS"
    status: Status
    invoice_id: Optional[str]
    extracted_text: Optional[str]
    mapped_schema: Optional[Dict]
    validation_flags: List[str]
    reliability_score: Optional[float]
    anomaly_details: Optional[List[Dict]]
    integration_payload_preview: Optional[Dict]

# Invoice Graph State (LangGraph)
class InvoiceGraphState(TypedDict):
    user_id: str
    file_path: str
    target_system: TargetSystem
    status: Status
    invoice_id: Optional[str]
    extracted_text: Optional[str]
    mapped_schema: Optional[Dict]
    validation_flags: List[str]
    validation_results: List[Dict]
    reliability_score: Optional[float]
    anomaly_details: Optional[List[Dict]]
    integration_payload_preview: Optional[Dict]
    integration_status: Optional[str]
    current_step: str
    history: List[Dict]
    summary: Optional[Dict]

# Agent Models
class ToolDefinition(BaseModel):
    tool_id: str
    capability: str
    description: str
    parameters: Optional[Dict] = None

class AgentCard(BaseModel):
    agent_id: str
    description: str
    tools: List[ToolDefinition]
```

**Canonical Invoice Schema:**

```python
{
    "invoiceNumber": str,
    "invoiceDate": str,  # YYYY-MM-DD
    "vendor": {
        "name": str,
        "gstin": Optional[str],
        "pan": Optional[str],
        "address": Optional[str]
    },
    "customer": {
        "name": Optional[str],
        "gstin": Optional[str],
        "address": Optional[str]
    },
    "lineItems": [
        {
            "description": str,
            "quantity": float,
            "unitPrice": float,
            "amount": float,
            "taxPercent": Optional[float],
            "hsn": Optional[str]
        }
    ],
    "totals": {
        "subtotal": float,
        "gstAmount": Optional[float],
        "roundOff": Optional[float],
        "grandTotal": float
    },
    "payment": {
        "mode": Optional[str],
        "reference": Optional[str],
        "status": Optional[str]
    }
}
```

### 7.3 Validation Rules

**Mandatory Fields:**
- `invoiceNumber`: Required, non-empty string
- `invoiceDate`: Required, valid date format (YYYY-MM-DD)
- `vendor.name`: Required, non-empty string
- `lineItems`: Required, non-empty array
- `totals.grandTotal`: Required, positive number

**Format Constraints:**
- `invoiceDate`: Must be valid date, not in future
- `vendor.gstin`: If present, must match GSTIN format (15 alphanumeric)
- `vendor.pan`: If present, must match PAN format (10 alphanumeric)
- `lineItems[].quantity`: Must be positive
- `lineItems[].unitPrice`: Must be non-negative
- `lineItems[].amount`: Must be non-negative
- `totals.grandTotal`: Must be positive

**Cross-Field Validation:**
- `sum(lineItems[].amount) == totals.subtotal` (within 0.01 tolerance)
- `totals.subtotal + totals.gstAmount + totals.roundOff == totals.grandTotal` (within 0.01 tolerance)
- `lineItems[].quantity * lineItems[].unitPrice == lineItems[].amount` (within 0.01 tolerance)

**Business Rules:**
- Duplicate detection: `(vendor.name, invoice_no, invoice_date)` must be unique
- Date validation: Invoice date not more than 1 year in past
- Amount validation: Grand total must match sum of line items + tax + round-off

---

## 8. Business Logic

### 8.1 Calculations

**Tax Computations:**
- GST calculated per line item: `item.amount * (item.taxPercent / 100)`
- Total GST: `sum(item_gst for all items)`
- Round-off: `grandTotal - (subtotal + gstAmount)` (typically ±0.01)

**Totals:**
- Subtotal: `sum(lineItems[].amount)`
- GST Amount: `sum(item_gst for all items)`
- Grand Total: `subtotal + gstAmount + roundOff`

**Rounding Logic:**
- All amounts stored with 2 decimal places (NUMERIC(18, 2))
- Round-off tolerance: ±0.01 (to handle floating-point precision)
- Validation allows 0.01 difference for rounding errors

### 8.2 Duplicate Detection

**Matching Strategy:**
- Exact match on: `(vendor.name, invoice_no, invoice_date)`
- Case-insensitive vendor name matching
- Date matching (ignoring time component)

**Fuzzy Matching (Planned):**
- Vendor name similarity (Levenshtein distance < 3)
- Invoice number similarity (handles OCR errors)
- Date proximity (±1 day tolerance)

**Implementation:**
```python
def check_duplicate(vendor_name: str, invoice_number: str, invoice_date: str) -> bool:
    query = """
        SELECT i.id
        FROM invoices i
        JOIN vendors v ON v.id = i.vendor_id
        WHERE LOWER(v.name) = LOWER(%s)
          AND i.invoice_no = %s
          AND i.invoice_date = %s
        LIMIT 1;
    """
    # Execute query and return True if duplicate found
```

### 8.3 Anomaly Detection Rules

**Confidence Score Thresholds:**
- **High Confidence**: ≥ 90% - Auto-approve
- **Medium Confidence**: 70-89% - Review recommended
- **Low Confidence**: < 70% - Manual review required

**Data Integrity Checks:**
1. **Math Validation:**
   - Line item totals: `quantity * unitPrice == amount` (±0.01)
   - Subtotal: `sum(lineItems) == subtotal` (±0.01)
   - Grand total: `subtotal + gst + roundOff == grandTotal` (±0.01)

2. **Field Completeness:**
   - Required fields present
   - Optional fields have valid format if present

3. **Business Rules:**
   - Invoice date not in future
   - Amounts are positive
   - Quantities are positive
   - Tax percentages are reasonable (0-100%)

4. **OCR Confidence:**
   - Low OCR confidence (< 0.7) triggers warning
   - Very low confidence (< 0.5) triggers failure

**Anomaly Scoring:**
- Initial score: 100
- Deduct points for each failure:
  - Critical (severity 5): -20 points
  - High (severity 4): -15 points
  - Medium (severity 3): -10 points
  - Low (severity 2): -5 points
  - Info (severity 1): -2.5 points
- Final score: `max(0, 100 - total_deductions)`

### 8.4 Error Handling

**Exception Types:**

1. **ValidationError**: Request validation failed
   - HTTP 400 Bad Request
   - Returns field-level error details

2. **NotFoundError**: Resource not found
   - HTTP 404 Not Found
   - Returns resource identifier

3. **ConflictError**: Duplicate resource
   - HTTP 409 Conflict
   - Returns conflicting resource details

4. **ExternalServiceError**: External API failure
   - HTTP 503 Service Unavailable
   - Retries with exponential backoff

5. **InternalError**: Unexpected server error
   - HTTP 500 Internal Server Error
   - Logged with full stack trace

**Error Translation:**
```python
try:
    result = process_invoice(data)
except ValidationError as e:
    return JSONResponse(
        status_code=400,
        content={"error": {"code": "VALIDATION_ERROR", "message": str(e)}}
    )
except NotFoundError as e:
    return JSONResponse(
        status_code=404,
        content={"error": {"code": "NOT_FOUND", "message": str(e)}}
    )
except Exception as e:
    logger.exception("Unexpected error")
    return JSONResponse(
        status_code=500,
        content={"error": {"code": "INTERNAL_ERROR", "message": "Internal server error"}}
    )
```

**Retry Logic for External Services:**

**OCR Services:**
- Max retries: 3
- Backoff: Exponential (1s, 2s, 4s)
- Timeout: 30 seconds per attempt
- Fallback: Next OCR engine in cascade

**LLM Services:**
- Max retries: 2
- Backoff: Exponential (2s, 4s)
- Timeout: 60 seconds per attempt
- Fallback: Alternative LLM provider (if configured)

**Accounting Systems:**
- Max retries: 3
- Backoff: Exponential (5s, 10s, 20s)
- Timeout: 30 seconds per attempt
- Idempotency: Uses idempotency key to prevent duplicates

---

## 9. Integrations

### 9.1 OCR Integration

#### Typhoon OCR API

**Endpoint:** `https://api.opentyphoon.ai/v1/ocr`

**Authentication:** API key in header
```
Authorization: Bearer <TYPHOON_OCR_API_KEY>
```

**Request:**
```json
POST /v1/ocr
Content-Type: application/json

{
  "model": "typhoon-ocr",
  "task_type": "default",
  "file": "<base64_encoded_file>",
  "max_tokens": 16000,
  "temperature": 0.1,
  "top_p": 0.6
}
```

**Response:**
```json
{
  "status": "success",
  "pages": [
    {
      "page_number": 1,
      "text": "Extracted text...",
      "confidence": 0.95
    }
  ],
  "tables": [
    {
      "page_number": 1,
      "cells": [["Header1", "Header2"], ["Value1", "Value2"]]
    }
  ]
}
```

**Rate Limits:**
- 100 requests per minute
- 1000 requests per hour

**Error Handling:**
- 429 Too Many Requests: Retry after `Retry-After` header
- 500 Internal Server Error: Retry with exponential backoff
- Timeout: Fallback to next OCR engine

#### Tesseract OCR

**Implementation:** Local OCR via `pytesseract`

**Configuration:**
- Executable path: `TESSERACT_CMD_PATH` (auto-detected if not set)
- Language: English (configurable)

**Usage:**
```python
import pytesseract
from PIL import Image

text = pytesseract.image_to_string(Image.open(image_path))
```

**Limitations:**
- Lower accuracy than cloud OCR
- Slower processing
- Requires Tesseract installation

#### EasyOCR

**Implementation:** Local OCR via `easyocr` library

**Configuration:**
- Languages: `EASYOCR_LANGUAGES` (default: "en")
- Initialization: Lazy-loaded singleton

**Usage:**
```python
import easyocr

reader = easyocr.Reader(['en'])
result = reader.readtext(image_path)
text = " ".join([item[1] for item in result])
```

**Limitations:**
- Requires GPU for optimal performance
- Slower than Tesseract
- Higher memory usage

### 9.2 ERP / Accounting Integration

#### Zoho Books Integration

**API Endpoint:** `https://books.zoho.com/api/v3/invoices`

**Authentication:** OAuth 2.0 with access token

**Request:**
```json
POST /api/v3/invoices
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "customer_name": "Acme Ltd",
  "invoice_number": "INV-1002",
  "date": "2025-05-10",
  "line_items": [
    {
      "item_id": "item_1",
      "name": "Software Development Services",
      "rate": 50000.00,
      "quantity": 1.0
    }
  ],
  "total": 82600.00
}
```

**Response:**
```json
{
  "code": 0,
  "message": "success",
  "invoice": {
    "invoice_id": "zoho-inv-789",
    "invoice_number": "INV-1002"
  }
}
```

**Mapping Details:**
- Canonical schema → Zoho Books JSON format
- Field mappings defined in `config/accounting_schemas.py`
- Line items transformed to Zoho line item format

**Idempotency Strategy:**
- Use `invoice_number` as idempotency key
- Check for existing invoice before creating
- Return existing invoice if duplicate detected

**Throttling:**
- Rate limit: 100 requests per minute
- Retry after: Respect `Retry-After` header
- Exponential backoff on 429 errors

#### Tally Integration

**Format:** XML-based integration

**Request Format:**
```xml
<ENVELOPE>
  <HEADER>
    <VERSION>1</VERSION>
    <TALLYREQUEST>Import</TALLYREQUEST>
  </HEADER>
  <BODY>
    <IMPORTDATA>
      <REQUESTDESC>
        <REPORTNAME>Vouchers</REPORTNAME>
      </REQUESTDESC>
      <REQUESTDATA>
        <TALLYMESSAGE>
          <VOUCHER>
            <DATE>20250510</DATE>
            <PARTYLEDGERNAME>Acme Ltd</PARTYLEDGERNAME>
            <ALLLEDGERENTRIES.LIST>
              <LEDGERNAME>Software Services</LEDGERNAME>
              <AMOUNT>50000.00</AMOUNT>
            </ALLLEDGERENTRIES.LIST>
          </VOUCHER>
        </TALLYMESSAGE>
      </REQUESTDATA>
    </IMPORTDATA>
  </BODY>
</ENVELOPE>
```

**Mapping Details:**
- Canonical schema → Tally XML format
- Date format: YYYYMMDD
- Amount format: Decimal with 2 places

**Idempotency Strategy:**
- Use `(vendor_name, invoice_no, invoice_date)` as key
- Check for existing voucher before creating

**Authentication:**
- Tally Exchange Server authentication
- Username/password or certificate-based

#### QuickBooks Integration

**API Endpoint:** `https://sandbox-quickbooks.api.intuit.com/v3/company/{companyId}/invoice`

**Authentication:** OAuth 2.0 with access token

**Request:**
```json
POST /v3/company/{companyId}/invoice
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "Line": [
    {
      "DetailType": "SalesItemLineDetail",
      "Amount": 50000.00,
      "SalesItemLineDetail": {
        "ItemRef": {
          "value": "1",
          "name": "Software Services"
        },
        "Qty": 1.0,
        "UnitPrice": 50000.00
      }
    }
  ],
  "CustomerRef": {
    "value": "1",
    "name": "Acme Ltd"
  },
  "TxnDate": "2025-05-10",
  "DocNumber": "INV-1002",
  "TotalAmt": 82600.00
}
```

**Response:**
```json
{
  "Invoice": {
    "Id": "123",
    "DocNumber": "INV-1002",
    "SyncToken": "0"
  }
}
```

**Mapping Details:**
- Canonical schema → QuickBooks JSON format
- Line items mapped to `Line` array with `SalesItemLineDetail`
- Customer reference required

**Idempotency Strategy:**
- Use `DocNumber` as idempotency key
- Check for existing invoice by `DocNumber`
- Return existing invoice if duplicate

**Throttling:**
- Rate limit: 500 requests per minute
- Retry after: Exponential backoff
- OAuth token refresh on 401

---

## 10. Security

### 10.1 Authentication

**Current State:**
- Authentication not yet implemented
- All endpoints are publicly accessible

**Planned Implementation:**

**JWT (JSON Web Tokens):**
- Token format: `Bearer <token>`
- Algorithm: RS256 (asymmetric)
- Token expiry: 1 hour (access), 7 days (refresh)
- Issuer: Identity provider service
- Audience: InvoiceCoreProcessor service

**Token Structure:**
```json
{
  "sub": "user-123",
  "iss": "identity-provider",
  "aud": "invoice-processor",
  "exp": 1737129600,
  "iat": 1737126000,
  "scopes": ["invoice:read", "invoice:write"],
  "roles": ["user"]
}
```

**Validation:**
- Verify signature using public key
- Check expiry (`exp` claim)
- Validate issuer (`iss` claim)
- Validate audience (`aud` claim)
- Check scopes for endpoint access

### 10.2 Authorization Model

**Role-Based Access Control (RBAC):**

**Roles:**
- `user`: Standard user (read/write own invoices)
- `reviewer`: Can approve invoices (read/write/approve)
- `admin`: Full access (all operations)

**Scopes:**
- `invoice:read`: Read invoice data
- `invoice:write`: Upload and process invoices
- `invoice:approve`: Approve and post invoices
- `admin:metrics`: Access metrics and reports
- `admin:config`: Manage validation rules

**Authorization Checks:**
```python
# Example authorization check
def require_scope(scope: str):
    def decorator(func):
        def wrapper(*args, **kwargs):
            token = extract_token(request)
            if scope not in token.scopes:
                raise HTTPException(403, "Insufficient permissions")
            return func(*args, **kwargs)
        return wrapper
    return decorator
```

### 10.3 Input Sanitization

**Validation:**
- All inputs validated using Pydantic models
- Type checking and format validation
- SQL injection prevention via parameterized queries
- XSS prevention via input sanitization

**File Upload Security:**
- File type validation (whitelist)
- File size limits (50 MB)
- Virus scanning (planned)
- Content-type verification

**Example:**
```python
from pydantic import BaseModel, validator

class InvoiceUploadRequest(BaseModel):
    user_id: str
    file_path: str
    target_system: str
    
    @validator('target_system')
    def validate_target_system(cls, v):
        allowed = ['TALLY', 'ZOHO', 'QUICKBOOKS']
        if v not in allowed:
            raise ValueError(f'target_system must be one of {allowed}')
        return v
```

### 10.4 Logging Policies

**PII Handling:**
- No PII in logs (user IDs, invoice numbers hashed)
- Sensitive data redacted before logging
- Correlation IDs used instead of direct identifiers

**Log Redaction:**
```python
def redact_sensitive_data(data: dict) -> dict:
    """Redact sensitive fields from log data."""
    sensitive_fields = ['gstin', 'pan', 'account_number']
    redacted = data.copy()
    for field in sensitive_fields:
        if field in redacted:
            redacted[field] = "***REDACTED***"
    return redacted
```

**Audit Logs:**
- Immutable audit trail in `workflow_audit` table
- All state transitions logged
- User actions tracked (when auth implemented)

### 10.5 Encryption

**In Transit:**
- HTTPS/TLS 1.2+ required
- TLS 1.3 preferred
- Certificate pinning (planned)

**At Rest:**
- Database encryption: PostgreSQL encryption at rest
- MongoDB encryption: WiredTiger encryption
- Secret encryption: Environment variables encrypted

**Secret Management:**
- Secrets stored in `.env` (local) or Vault (production)
- Never committed to repository
- Rotation policy: Quarterly for API keys

### 10.6 Secret Rotation Policy

**Rotation Schedule:**
- API keys: Every 90 days
- Database passwords: Every 180 days
- JWT signing keys: Every 365 days

**Rotation Process:**
1. Generate new secret
2. Update in secrets manager
3. Deploy with new secret
4. Verify service health
5. Revoke old secret after 7 days

---

## 11. Observability

### 11.1 Logging

**Log Format:**
- Format: Plaintext with structured fields
- Library: `loguru`
- Output: Console + files (`app.log`, `error.log`)

**Log Levels:**
- `DEBUG`: Detailed diagnostic information
- `INFO`: General operational messages
- `WARNING`: Warning conditions
- `ERROR`: Error conditions
- `CRITICAL`: Critical failures

**Log Structure:**
```
2025-01-15 10:30:45.123 | INFO     | invoice_core_processor.core.workflow:ingestion_step:34 | Invoice ingested: inv-abc123
```

**Correlation IDs:**
- Each request gets a unique `trace_id`
- Passed through all service calls
- Included in all log entries
- Format: `abc-123-def-456`

**Error Logging:**
```python
from loguru import logger

try:
    result = process_invoice(invoice_id)
except Exception as e:
    logger.exception(
        "Failed to process invoice",
        invoice_id=invoice_id,
        error=str(e),
        trace_id=trace_id
    )
    raise
```

**Log Files:**
- `app.log`: All INFO+ logs (rotates at 10 MB, retains 7 days)
- `error.log`: ERROR+ logs only (rotates at 10 MB, retains 7 days)

### 11.2 Metrics

**Key Metrics:**

**Processing Metrics:**
- `invoice_processing_duration_ms`: Processing time per invoice
- `invoice_processing_total`: Total invoices processed
- `invoice_processing_errors_total`: Processing errors

**Stage Metrics:**
- `ocr_duration_ms`: OCR processing time
- `ocr_success_rate`: OCR success percentage
- `mapping_duration_ms`: Schema mapping time
- `validation_duration_ms`: Validation time
- `integration_duration_ms`: Integration posting time

**Quality Metrics:**
- `validation_reliability_score_avg`: Average reliability score
- `validation_flags_total`: Total validation flags
- `duplicate_detection_total`: Duplicates detected

**Error Metrics:**
- `ocr_failure_rate`: OCR failure percentage
- `mapping_failure_rate`: Mapping failure percentage
- `integration_failure_rate`: Integration failure percentage

**Metrics Endpoint:**
- `GET /metrics`: Returns comprehensive KPIs
- Format: JSON (future: Prometheus format)

**Example Metric:**
```python
from prometheus_client import Counter, Histogram

processing_duration = Histogram(
    'invoice_processing_duration_seconds',
    'Time spent processing invoices',
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
)

processing_errors = Counter(
    'invoice_processing_errors_total',
    'Total processing errors',
    ['stage', 'error_type']
)
```

### 11.3 Tracing

**Current State:**
- Distributed tracing not yet implemented
- Correlation IDs used for request tracking

**Planned Implementation:**

**OpenTelemetry:**
- Instrumentation: OpenTelemetry Python SDK
- Export: OTLP (OpenTelemetry Protocol)
- Collector: OpenTelemetry Collector

**Span Creation:**
```python
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

def process_invoice(invoice_id: str):
    with tracer.start_as_current_span("process_invoice") as span:
        span.set_attribute("invoice_id", invoice_id)
        
        with tracer.start_as_current_span("ocr_step"):
            # OCR processing
            pass
        
        with tracer.start_as_current_span("mapping_step"):
            # Mapping processing
            pass
```

**Trace Propagation:**
- W3C Trace Context headers
- `traceparent` header for distributed tracing
- Correlation IDs included in spans

### 11.4 Dashboards

**Planned Dashboards:**

**Grafana Dashboards:**
- Processing metrics dashboard
- Error rates dashboard
- Processing time dashboard
- Integration success rates

**Key Visualizations:**
- Processing time over time (line chart)
- Success/failure rates (pie chart)
- Error breakdown by stage (bar chart)
- Reliability score distribution (histogram)

**Dashboard Links:**
- Production: `https://grafana.example.com/d/invoice-processor`
- Staging: `https://staging-grafana.example.com/d/invoice-processor`

---

## 12. Testing

### 12.1 Unit Tests

**Coverage:**
- Business logic functions
- Validation rules
- Data transformations
- Utility functions

**Test Framework:**
- `pytest` for test execution
- `unittest.mock` for mocking
- `pytest-cov` for coverage

**Running Tests:**
```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=invoice_core_processor --cov-report=html

# Run specific test file
pytest tests/test_workflow.py

# Run with verbose output
pytest tests/ -v
```

**Example Unit Test:**
```python
import unittest
from invoice_core_processor.services.validation import check_subtotal

class TestValidation(unittest.TestCase):
    def test_check_subtotal_pass(self):
        schema = {
            "lineItems": [
                {"amount": 100.0},
                {"amount": 200.0}
            ],
            "totals": {"subtotal": 300.0}
        }
        result = check_subtotal(schema)
        self.assertEqual(result.status, "PASS")
    
    def test_check_subtotal_fail(self):
        schema = {
            "lineItems": [
                {"amount": 100.0},
                {"amount": 200.0}
            ],
            "totals": {"subtotal": 250.0}  # Mismatch
        }
        result = check_subtotal(schema)
        self.assertEqual(result.status, "FAIL")
```

**Test Files:**
- `tests/test_workflow.py`: Workflow orchestration tests
- `tests/test_ocr_agent.py`: OCR agent tests
- `tests/test_validation_agent.py`: Validation agent tests
- `tests/test_datastore_agent.py`: DataStore agent tests
- `tests/test_metrics_agent.py`: Metrics agent tests
- `tests/test_summary_agent.py`: Summary agent tests

### 12.2 Integration Tests

**Coverage:**
- Database operations
- Agent interactions
- Workflow execution
- External API mocks

**Test Database:**
- Separate test database instance
- Schema created from `schema.sql`
- Data cleaned between tests

**Mocking External Services:**
```python
from unittest.mock import patch, MagicMock

@patch('invoice_core_processor.services.ocr_processor.try_typhoon_ocr')
def test_ocr_integration(mock_typhoon):
    mock_typhoon.return_value = OCRResult(
        status="OCR_DONE",
        avg_confidence=0.95,
        pages=[{"page_number": 1, "text": "Test"}],
        tables=[],
        raw_engine_trace={}
    )
    
    result = run_cascading_ocr("test.pdf", "pdf")
    assert result.status == "OCR_DONE"
```

**Running Integration Tests:**
```bash
# Run integration tests
pytest tests/integration/ -v

# Run with test database
pytest tests/integration/ --db-url=postgresql://test:test@localhost/test_db
```

### 12.3 E2E Tests

**Coverage:**
- Complete workflow execution
- End-to-end invoice processing
- Error scenarios
- Integration with external systems (mocked)

**E2E Test Example:**
```python
def test_e2e_invoice_processing():
    # Upload invoice
    response = client.post("/invoice/upload", json={
        "user_id": "user-123",
        "file_path": "test_invoice.pdf",
        "target_system": "ZOHO"
    })
    assert response.status_code == 200
    invoice_id = response.json()["invoice_id"]
    
    # Check status
    status_response = client.get(f"/invoice/{invoice_id}/status")
    assert status_response.json()["status"] == "SYNCED_SUCCESS"
    
    # Verify extracted data
    extracted = client.get(f"/invoice/{invoice_id}/extracted")
    assert extracted.json()["invoice_no"] is not None
```

**Running E2E Tests:**
```bash
# Run E2E tests
pytest tests/e2e/ -v

# Run with real services (local)
pytest tests/e2e/ --use-real-services
```

### 12.4 Load Testing

**Tools:**
- `k6` for HTTP load testing
- `Locust` for Python-based load testing

**Target Thresholds:**
- Throughput: 100 invoices/minute
- P95 latency: < 2 minutes
- P99 latency: < 5 minutes
- Error rate: < 1%

**Load Test Script (k6):**
```javascript
import http from 'k6/http';
import { check } from 'k6';

export let options = {
  stages: [
    { duration: '1m', target: 10 },
    { duration: '3m', target: 50 },
    { duration: '2m', target: 100 },
    { duration: '1m', target: 0 },
  ],
};

export default function () {
  let response = http.post('http://localhost:8000/invoice/upload', JSON.stringify({
    user_id: 'user-123',
    file_path: '/test/invoice.pdf',
    target_system: 'ZOHO'
  }), {
    headers: { 'Content-Type': 'application/json' },
  });
  
  check(response, {
    'status is 200': (r) => r.status === 200,
    'response time < 2s': (r) => r.timings.duration < 2000,
  });
}
```

**Running Load Tests:**
```bash
# Run k6 load test
k6 run load_test.js

# Run Locust load test
locust -f load_test.py --host=http://localhost:8000
```

---

## 13. Local Development Setup

### 13.1 Prerequisites

**Required:**
- Python 3.9+ (tested with 3.11)
- PostgreSQL 12+
- MongoDB 4.4+
- Docker & Docker Compose (optional)

**Optional:**
- Tesseract OCR (for local OCR)
- EasyOCR dependencies

### 13.2 Running the Application Locally

**Step 1: Clone and Setup**
```bash
git clone <repository-url>
cd InvoiceCoreProcessor
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or
.\venv\Scripts\Activate.ps1  # Windows PowerShell
```

**Step 2: Install Dependencies**
```bash
pip install -e .
```

**Step 3: Configure Environment**
```bash
cp .env.example .env
# Edit .env with your configuration
```

**Step 4: Start Databases**
```bash
# Using Docker Compose
docker-compose up -d postgres mongodb

# Or manually
docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=postgres postgres:15
docker run -d -p 27017:27017 mongo:6
```

**Step 5: Setup Database Schema**
```bash
psql -U postgres -d invoices -f src/invoice_core_processor/database/schema.sql
python -m invoice_core_processor.database.seed_rules
```

**Step 6: Start Services**
```bash
# Windows
.\start-services.ps1

# Linux/macOS
./start-services.sh

# Or manually in separate terminals:
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

### 13.3 Mock Services

**Mock OCR Service:**
```python
# In tests or local development
from unittest.mock import patch

@patch('invoice_core_processor.services.ocr_processor.try_typhoon_ocr')
def use_mock_ocr(mock_func):
    mock_func.return_value = OCRResult(
        status="OCR_DONE",
        avg_confidence=0.95,
        pages=[{"page_number": 1, "text": "Mock OCR text"}],
        tables=[],
        raw_engine_trace={"engine": "mock"}
    )
```

**Mock LLM Service:**
```python
# Set OPENAI_API_KEY to empty to use mock
# Or use mock client in tests
```

**Mock Accounting Systems:**
```python
# Mock Zoho/Tally/QuickBooks responses
@patch('invoice_core_processor.core.integration_agent.post_to_zoho')
def use_mock_zoho(mock_func):
    mock_func.return_value = {
        "status": "SYNCED_SUCCESS",
        "external_id": "mock-zoho-123"
    }
```

### 13.4 Seeding Data

**Validation Rules:**
```bash
python -m invoice_core_processor.database.seed_rules
```

**Test Invoices:**
```python
# Create test invoice data
from invoice_core_processor.core.database import get_postgres_connection

conn = get_postgres_connection()
# Insert test data...
```

### 13.5 Useful Dev Commands

```bash
# Run tests
pytest tests/

# Run with coverage
pytest tests/ --cov=invoice_core_processor --cov-report=html

# Lint code
ruff check .

# Format code
ruff format .

# Type check
mypy src/

# Start all services
./start-services.sh  # or .ps1 on Windows

# View logs
tail -f app.log
tail -f error.log

# Database migrations (future)
alembic upgrade head

# Reset database
psql -U postgres -d invoices -f src/invoice_core_processor/database/schema.sql
```

---

## 14. Deployment

### 14.1 Environments

**Development:**
- Purpose: Local development and testing
- Database: Local PostgreSQL and MongoDB
- Config: `.env` file
- URL: `http://localhost:8000`

**Staging:**
- Purpose: Pre-production testing
- Database: Staging instances
- Config: Environment variables
- URL: `https://staging-api.invoice-automation.example.com`

**Production:**
- Purpose: Live system
- Database: Production instances (high availability)
- Config: Secrets manager (Vault/AWS Secrets Manager)
- URL: `https://api.invoice-automation.example.com`

### 14.2 CI/CD Pipelines

**Current State:**
- CI/CD not yet configured
- Manual deployment process

**Planned CI/CD (GitHub Actions):**

**Build Steps:**
1. Checkout code
2. Setup Python environment
3. Install dependencies
4. Run linting (`ruff check .`)
5. Run type checking (`mypy src/`)
6. Run tests (`pytest tests/`)
7. Build Docker image
8. Push to container registry

**Deployment Triggers:**
- `main` branch → Production
- `staging` branch → Staging
- Pull requests → Run tests only

**Example GitHub Actions Workflow:**
```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [main, staging]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -e .
      - run: ruff check .
      - run: pytest tests/ --cov=invoice_core_processor
  
  deploy:
    needs: test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to production
        run: |
          # Deployment steps
```

### 14.3 Infrastructure

**Current:**
- Monolithic deployment (all services in one process)
- Local development with separate terminal windows

**Planned:**

**Docker Containers:**
- One container per service
- Multi-stage builds for optimization
- Health checks configured

**Kubernetes:**
- Deployment manifests for each service
- Service definitions for internal communication
- ConfigMaps for configuration
- Secrets for sensitive data

**Helm Charts:**
- Chart structure:
  ```
  helm/
    invoice-processor/
      Chart.yaml
      values.yaml
      templates/
        deployment.yaml
        service.yaml
        configmap.yaml
        secret.yaml
  ```

**Autoscaling Rules:**
- CPU threshold: 70%
- Memory threshold: 80%
- Min replicas: 2
- Max replicas: 10
- Scale-up: 2 minutes
- Scale-down: 5 minutes

### 14.4 Rollback Procedure

**Manual Rollback:**
1. Identify previous working version
2. Update deployment to previous version
3. Verify service health
4. Monitor for issues

**Automated Rollback:**
- Health check failures trigger automatic rollback
- Rollback to previous version if error rate > 5%
- Notification sent to team

**Blue-Green Deployment (Planned):**
1. Deploy new version to green environment
2. Run smoke tests
3. Switch traffic from blue to green
4. Monitor for 10 minutes
5. Keep blue as backup for 1 hour
6. Decommission blue if successful

**Canary Deployment (Planned):**
1. Deploy new version to 10% of traffic
2. Monitor metrics for 15 minutes
3. Increase to 50% if healthy
4. Monitor for 15 minutes
5. Increase to 100% if healthy
6. Rollback if issues detected

---

## 15. Known Limitations

### 15.1 Performance Limits

**Processing Capacity:**
- Maximum concurrent processing: 20 invoices (database connection pool limit)
- Processing time: 30 seconds to 2 minutes per invoice
- Bulk uploads: Processed sequentially (not optimized)

**File Size Limits:**
- Maximum file size: 50 MB
- Large files (> 20 MB) may timeout
- OCR processing slows down with large images

### 15.2 External API Constraints

**OCR Services:**
- Typhoon OCR: 100 requests/minute
- Azure Document Intelligence: 500 requests/minute
- Rate limiting may cause delays

**Accounting Systems:**
- Zoho Books: 100 requests/minute
- QuickBooks: 500 requests/minute
- Tally: No documented limits (local/network dependent)

### 15.3 Data Constraints

**Database:**
- PostgreSQL connection pool: 20 connections
- MongoDB connection pool: 100 connections
- Large result sets may cause memory issues

**Storage:**
- Invoice files stored locally (not scalable)
- No distributed storage (planned: S3/Azure Blob)

### 15.4 Feature Limitations

**Current:**
- No async processing (all synchronous)
- No batch upload endpoint
- No webhook support
- No authentication/authorization
- No retry mechanism for failed OCR calls
- No circuit breakers for external services

**Workarounds:**
- Use multiple service instances for scaling
- Process invoices in smaller batches
- Manual retry for failed invoices

---

## 16. Future Enhancements

### 16.1 Short-Term (Next 3 Months)

**Authentication & Authorization:**
- JWT authentication implementation
- Role-based access control (RBAC)
- API key management

**Async Processing:**
- Background job processing
- Job status tracking
- Retry mechanisms

**Batch Operations:**
- Batch upload endpoint
- Bulk processing API
- Progress tracking

### 16.2 Medium-Term (3-6 Months)

**Webhook Support:**
- Event-driven webhooks
- Webhook subscription management
- Retry policies

**Enhanced OCR:**
- Multi-page PDF support
- Table extraction improvements
- Handwriting recognition

**Advanced Validation:**
- Machine learning-based anomaly detection
- Custom validation rules API
- Rule versioning

### 16.3 Long-Term (6-12 Months)

**Distributed Architecture:**
- Microservices separation
- Service mesh (Istio)
- Event-driven architecture (Kafka)

**Scalability:**
- Horizontal auto-scaling
- Distributed storage (S3/Azure Blob)
- Caching layer (Redis)

**Advanced Features:**
- Real-time processing dashboard
- Predictive analytics
- Invoice approval workflows
- Multi-tenant support

**Observability:**
- Distributed tracing (OpenTelemetry)
- Advanced metrics (Prometheus)
- Log aggregation (ELK stack)

**Security:**
- mTLS for service-to-service communication
- API rate limiting per user
- Advanced threat detection

---

**Document Version**: 1.0.0  
**Last Updated**: 2024  
**Maintained By**: Development Team