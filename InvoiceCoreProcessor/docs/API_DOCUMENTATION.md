# API Documentation

## 1. Overview

### 1.1 Purpose

The **Invoice Processing API** provides a comprehensive REST API for automating the complete invoice processing lifecycle. The API enables:

- **Invoice Upload**: Accept invoice files in various formats (PDF, DOCX, images)
- **OCR & Extraction**: Extract structured data from invoices using cascading OCR and LLM-based mapping
- **Validation**: Apply business rules to detect anomalies, duplicates, and data quality issues
- **Integration**: Post validated invoices to external accounting systems (Tally, Zoho Books, QuickBooks)
- **Reporting**: Retrieve metrics, summaries, and processing status
- **Workflow Management**: Track invoice processing through all stages

The API is built on FastAPI and follows RESTful principles with JSON request/response formats.

### 1.2 Authentication

**Current State:**
- Authentication is not yet implemented (development phase)
- All endpoints are publicly accessible

**Planned Implementation:**

**Token Type:** JWT (JSON Web Tokens)

**Header Format:**
```
Authorization: Bearer <token>
```

**Token Expiry:**
- Access tokens: 1 hour
- Refresh tokens: 7 days

**Required Scopes/Roles:**
- `invoice:read` - Read invoice data
- `invoice:write` - Upload and process invoices
- `invoice:approve` - Approve and post invoices
- `admin:metrics` - Access metrics and reports
- `admin:config` - Manage validation rules and configuration

**Roles:**
- `user` - Standard user (invoice:read, invoice:write)
- `reviewer` - Can approve invoices (invoice:read, invoice:write, invoice:approve)
- `admin` - Full access (all scopes)

### 1.3 Base URL

**Environments:**

| Environment | Base URL | Description |
|-------------|----------|-------------|
| Production | `https://api.invoice-automation.example.com` | Live production API |
| Staging | `https://staging-api.invoice-automation.example.com` | Pre-production testing |
| Local | `http://localhost:8000` | Local development |

**API Versioning:**
- Current version: `v1` (implicit)
- Future versions: `/api/v1/...`, `/api/v2/...`
- Version specified in path or header (planned)

---

## 2. Common API Conventions

### 2.1 Request Format

**Content-Type:**
- `application/json` for JSON request bodies
- `multipart/form-data` for file uploads

**Character Encoding:**
- UTF-8

**Date/Time Format:**
- ISO 8601 format: `YYYY-MM-DDTHH:mm:ssZ`
- Example: `2025-01-15T10:30:00Z`

### 2.2 Standard Response Model

All API responses follow a consistent envelope structure:

**Success Response:**
```json
{
  "success": true,
  "data": {
    // Response data here
  },
  "error": null,
  "meta": {
    "trace_id": "abc-123-def-456",
    "timestamp": "2025-01-15T10:30:00Z",
    "request_id": "req-789"
  }
}
```

**Error Response:**
```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invoice number is missing",
    "details": [
      "invoice_no is required",
      "invoice_date is required"
    ],
    "field": "invoice_no"
  },
  "meta": {
    "trace_id": "abc-123-def-456",
    "timestamp": "2025-01-15T10:30:00Z",
    "request_id": "req-789"
  }
}
```

**Response Fields:**
- `success`: Boolean indicating request success
- `data`: Response payload (null on error)
- `error`: Error object (null on success)
- `meta`: Metadata including trace_id, timestamp, request_id

### 2.3 Error Handling

**Standard Error Structure:**
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": ["Additional error details"],
    "field": "field_name" // Optional: field that caused error
  }
}
```

**Error Codes:**

| Code | HTTP Status | Meaning | Description |
|------|-------------|---------|-------------|
| `INVALID_PAYLOAD` | 400 | Bad Request | JSON/body validation error, missing required fields |
| `UNAUTHORIZED` | 401 | Unauthorized | Missing or invalid authentication token |
| `FORBIDDEN` | 403 | Forbidden | User lacks required permissions/roles |
| `NOT_FOUND` | 404 | Not Found | Resource (invoice, endpoint) doesn't exist |
| `CONFLICT` | 409 | Conflict | Duplicate invoice, resource already exists |
| `VALIDATION_ERROR` | 422 | Unprocessable Entity | Business rule validation failed |
| `RATE_LIMIT_EXCEEDED` | 429 | Too Many Requests | Rate limit exceeded |
| `INTERNAL_ERROR` | 500 | Internal Server Error | Unexpected server error |
| `SERVICE_UNAVAILABLE` | 503 | Service Unavailable | Downstream service unavailable |

**Error Examples:**

**Invalid Payload:**
```json
{
  "success": false,
  "error": {
    "code": "INVALID_PAYLOAD",
    "message": "Request validation failed",
    "details": [
      "user_id: field required",
      "target_system: must be one of TALLY, ZOHO, QUICKBOOKS"
    ]
  }
}
```

**Not Found:**
```json
{
  "success": false,
  "error": {
    "code": "NOT_FOUND",
    "message": "Invoice not found",
    "details": ["Invoice with ID 'inv_123' does not exist"]
  }
}
```

**Conflict (Duplicate):**
```json
{
  "success": false,
  "error": {
    "code": "CONFLICT",
    "message": "Duplicate invoice detected",
    "details": [
      "Invoice with number 'INV-1001' from vendor 'Acme Ltd' on date '2025-01-15' already exists"
    ]
  }
}
```

---

## 3. Endpoints

### 3.1 Health Check

**GET** `/`

**Summary:** Health check endpoint to verify API availability.

**Description:** Returns a simple status message indicating the API is running.

**Auth:** Not required

**Query Parameters:** None

**Request Body:** None

**Response:**

**Status Code:** `200 OK`

```json
{
  "message": "InvoiceCoreProcessor is running."
}
```

**Error Responses:**
- `503 Service Unavailable` - Service is down or unhealthy

---

### 3.2 Upload Invoice

**POST** `/invoice/upload`

**Summary:** Upload an invoice file and initiate the processing workflow.

**Description:** 
Accepts an invoice file and initiates the complete processing pipeline:
1. Ingestion (file storage and metadata creation)
2. OCR (text extraction)
3. Mapping (LLM-based schema transformation)
4. Validation (business rules and anomaly detection)
5. Integration (posting to accounting system)

The processing happens synchronously, and the response includes the final workflow status.

**Auth:** Required (`invoice:write`)

**Query Parameters:** None

**Request Body:**

```json
{
  "user_id": "user-123",
  "file_path": "/path/to/invoice.pdf",
  "target_system": "TALLY"
}
```

**Request Fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `user_id` | string | Yes | Unique identifier for the user uploading the invoice |
| `file_path` | string | Yes | Path to the invoice file (must be accessible by the service) |
| `target_system` | enum | Yes | Target accounting system: `TALLY`, `ZOHO`, or `QUICKBOOKS` |

**Response:**

**Status Code:** `200 OK`

```json
{
  "workflow_status": "SYNCED_SUCCESS",
  "invoice_id": "inv-abc123-def456"
}
```

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `workflow_status` | string | Final status of the workflow. Possible values: `SYNCED_SUCCESS`, `SYNCED_FAILED`, `VALIDATED_FLAGGED`, `FAILED_INGESTION`, `FAILED_OCR`, `FAILED_MAPPING`, `FAILED_SYNC` |
| `invoice_id` | string | Unique identifier for the processed invoice (null if ingestion failed) |

**Status Values:**

- `SYNCED_SUCCESS` - Invoice successfully processed and posted to accounting system
- `SYNCED_FAILED` - Processing completed but posting to accounting system failed
- `VALIDATED_FLAGGED` - Invoice validated but has anomalies requiring review
- `FAILED_INGESTION` - File ingestion failed
- `FAILED_OCR` - OCR extraction failed
- `FAILED_MAPPING` - Schema mapping failed
- `FAILED_SYNC` - Integration/posting failed

**Error Responses:**

**400 Bad Request:**
```json
{
  "success": false,
  "error": {
    "code": "INVALID_PAYLOAD",
    "message": "Request validation failed",
    "details": ["target_system: must be one of TALLY, ZOHO, QUICKBOOKS"]
  }
}
```

**404 Not Found:**
```json
{
  "success": false,
  "error": {
    "code": "NOT_FOUND",
    "message": "File not found",
    "details": ["File at path '/path/to/invoice.pdf' does not exist"]
  }
}
```

**500 Internal Server Error:**
```json
{
  "success": false,
  "error": {
    "code": "INTERNAL_ERROR",
    "message": "Processing failed",
    "details": ["OCR service unavailable"]
  }
}
```

**Example Request (cURL):**
```bash
curl -X POST "http://localhost:8000/invoice/upload" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user-123",
    "file_path": "/uploads/invoice.pdf",
    "target_system": "ZOHO"
  }'
```

**Example Request (Python):**
```python
import requests

url = "http://localhost:8000/invoice/upload"
headers = {
    "Authorization": "Bearer <token>",
    "Content-Type": "application/json"
}
data = {
    "user_id": "user-123",
    "file_path": "/uploads/invoice.pdf",
    "target_system": "ZOHO"
}

response = requests.post(url, json=data, headers=headers)
print(response.json())
```

---

### 3.3 Get Invoice Processing Status

**GET** `/invoice/{invoice_id}/status`

**Summary:** Get the current processing status of an invoice.

**Description:** 
Returns real-time processing state showing progress through all stages:
- Upload/Ingestion
- OCR
- Mapping/Extraction
- Validation
- Integration/Posting

**Auth:** Required (`invoice:read`)

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `invoice_id` | string | Yes | Unique identifier of the invoice |

**Query Parameters:** None

**Request Body:** None

**Response:**

**Status Code:** `200 OK`

```json
{
  "invoice_id": "inv-abc123-def456",
  "status": "VALIDATED",
  "stages": {
    "upload": {
      "status": "done",
      "timestamp": "2025-01-15T10:00:00Z"
    },
    "ocr": {
      "status": "done",
      "timestamp": "2025-01-15T10:00:15Z",
      "confidence": 0.95
    },
    "extraction": {
      "status": "done",
      "timestamp": "2025-01-15T10:00:30Z"
    },
    "validation": {
      "status": "done",
      "timestamp": "2025-01-15T10:00:45Z",
      "reliability_score": 85.5,
      "flags_count": 2
    },
    "posting": {
      "status": "pending",
      "timestamp": null
    }
  },
  "processing_time_ms": 45000,
  "estimated_completion": "2025-01-15T10:01:00Z"
}
```

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `invoice_id` | string | Invoice identifier |
| `status` | string | Current overall status |
| `stages` | object | Status of each processing stage |
| `stages.upload.status` | string | `pending`, `processing`, `done`, `failed` |
| `stages.ocr.status` | string | OCR stage status |
| `stages.ocr.confidence` | float | OCR confidence score (0-1) |
| `stages.extraction.status` | string | Mapping/extraction stage status |
| `stages.validation.status` | string | Validation stage status |
| `stages.validation.reliability_score` | float | Overall reliability score (0-100) |
| `stages.validation.flags_count` | integer | Number of validation flags |
| `stages.posting.status` | string | Integration/posting stage status |
| `processing_time_ms` | integer | Total processing time in milliseconds |
| `estimated_completion` | string | Estimated completion time (ISO 8601) |

**Error Responses:**

**404 Not Found:**
```json
{
  "success": false,
  "error": {
    "code": "NOT_FOUND",
    "message": "Invoice not found",
    "details": ["Invoice with ID 'inv-abc123-def456' does not exist"]
  }
}
```

---

### 3.4 Get Extracted Invoice Data

**GET** `/invoice/{invoice_id}/extracted`

**Summary:** Retrieve all extracted fields from an invoice in canonical schema format.

**Description:** 
Returns the complete extracted invoice data including:
- Invoice metadata (number, date, vendor, customer)
- Line items with quantities, prices, amounts
- Totals (subtotal, tax, grand total)
- Confidence scores for each extracted field

**Auth:** Required (`invoice:read`)

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `invoice_id` | string | Yes | Unique identifier of the invoice |

**Query Parameters:** None

**Request Body:** None

**Response:**

**Status Code:** `200 OK`

```json
{
  "invoice_id": "inv-abc123-def456",
  "invoice_no": "INV-1002",
  "invoice_date": "2025-05-10",
  "due_date": "2025-06-10",
  "vendor": {
    "name": "Acme Ltd",
    "gstin": "27AAAAA0000A1Z5",
    "pan": "AAAAA0000A",
    "address": "123 Business St, Mumbai, MH 400001"
  },
  "customer": {
    "name": "Tech Corp",
    "gstin": "29BBBBB0000B2Z6",
    "address": "456 Tech Ave, Bangalore, KA 560001"
  },
  "line_items": [
    {
      "line_no": 1,
      "description": "Software Development Services",
      "quantity": 1.0,
      "unit_price": 50000.00,
      "amount": 50000.00,
      "tax_pct": 18.0,
      "hsn": "998314",
      "confidence": 0.98
    },
    {
      "line_no": 2,
      "description": "Consulting Services",
      "quantity": 10.0,
      "unit_price": 2000.00,
      "amount": 20000.00,
      "tax_pct": 18.0,
      "hsn": "998315",
      "confidence": 0.95
    }
  ],
  "totals": {
    "subtotal": 70000.00,
    "gst_amount": 12600.00,
    "round_off": 0.00,
    "grand_total": 82600.00,
    "confidence": 0.97
  },
  "payment": {
    "mode": "Bank Transfer",
    "reference": "TXN-12345",
    "status": "Pending"
  },
  "extraction_metadata": {
    "ocr_confidence": 0.95,
    "mapping_confidence": 0.98,
    "extracted_at": "2025-01-15T10:00:30Z"
  }
}
```

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `invoice_id` | string | Invoice identifier |
| `invoice_no` | string | Invoice number |
| `invoice_date` | string | Invoice date (YYYY-MM-DD) |
| `due_date` | string | Payment due date (YYYY-MM-DD) |
| `vendor` | object | Vendor information |
| `vendor.name` | string | Vendor name |
| `vendor.gstin` | string | Vendor GSTIN |
| `vendor.pan` | string | Vendor PAN |
| `vendor.address` | string | Vendor address |
| `customer` | object | Customer information |
| `line_items` | array | Invoice line items |
| `line_items[].line_no` | integer | Line item number |
| `line_items[].description` | string | Item description |
| `line_items[].quantity` | float | Quantity |
| `line_items[].unit_price` | float | Unit price |
| `line_items[].amount` | float | Line total amount |
| `line_items[].tax_pct` | float | Tax percentage |
| `line_items[].hsn` | string | HSN code |
| `line_items[].confidence` | float | Extraction confidence (0-1) |
| `totals` | object | Invoice totals |
| `totals.subtotal` | float | Subtotal before tax |
| `totals.gst_amount` | float | GST/tax amount |
| `totals.round_off` | float | Round-off amount |
| `totals.grand_total` | float | Grand total |
| `totals.confidence` | float | Totals confidence (0-1) |
| `payment` | object | Payment information |
| `extraction_metadata` | object | Extraction metadata |

**Error Responses:**

**404 Not Found:**
```json
{
  "success": false,
  "error": {
    "code": "NOT_FOUND",
    "message": "Invoice not found or extraction not completed",
    "details": ["Invoice with ID 'inv-abc123-def456' does not exist or OCR not completed"]
  }
}
```

---

### 3.5 Get Validation Results

**GET** `/invoice/{invoice_id}/validation`

**Summary:** Get validation results including anomalies, flags, and reliability score.

**Description:** 
Returns comprehensive validation results including:
- Overall validation status (PASS, FAIL, WARN)
- Reliability score (0-100)
- List of validation flags with details
- Rule-level results
- Anomaly detection results

**Auth:** Required (`invoice:read`)

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `invoice_id` | string | Yes | Unique identifier of the invoice |

**Query Parameters:** None

**Request Body:** None

**Response:**

**Status Code:** `200 OK`

```json
{
  "invoice_id": "inv-abc123-def456",
  "is_valid": false,
  "overall_status": "VALIDATED_FLAGGED",
  "reliability_score": 75.5,
  "validation_run_id": "val-run-789",
  "run_at": "2025-01-15T10:00:45Z",
  "engine_version": "1.0.0",
  "flags": [
    {
      "rule_id": "TTL-001",
      "category": "TOTALS",
      "type": "AMOUNT_MISMATCH",
      "status": "FAIL",
      "severity": 5,
      "message": "Subtotal does not match sum of line items",
      "field": "totals.subtotal",
      "expected": 70000.00,
      "actual": 69000.00,
      "deduction_points": 20.0
    },
    {
      "rule_id": "ANM-004",
      "category": "ANOMALY",
      "type": "LOW_CONFIDENCE",
      "status": "WARN",
      "severity": 3,
      "message": "Low OCR confidence (0.75)",
      "field": "extraction_metadata.ocr_confidence",
      "deduction_points": 2.5
    }
  ],
  "validation_results": [
    {
      "rule_id": "LIT-004",
      "category": "LINE_ITEMS",
      "status": "PASS",
      "message": "Line item math correct",
      "severity": 1,
      "deduction_points": 0.0
    },
    {
      "rule_id": "TTL-001",
      "category": "TOTALS",
      "status": "FAIL",
      "message": "Subtotal does not match sum of line items",
      "severity": 5,
      "deduction_points": 20.0
    },
    {
      "rule_id": "TTL-003",
      "category": "TOTALS",
      "status": "PASS",
      "message": "Grand total is correct",
      "severity": 1,
      "deduction_points": 0.0
    },
    {
      "rule_id": "DUP-001",
      "category": "DUPLICATE",
      "status": "PASS",
      "message": "Invoice is unique",
      "severity": 1,
      "deduction_points": 0.0
    },
    {
      "rule_id": "ANM-004",
      "category": "ANOMALY",
      "status": "WARN",
      "message": "Low OCR confidence (0.75)",
      "severity": 3,
      "deduction_points": 2.5
    }
  ],
  "summary": {
    "total_rules": 5,
    "passed": 3,
    "failed": 1,
    "warnings": 1,
    "requires_review": true
  }
}
```

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `invoice_id` | string | Invoice identifier |
| `is_valid` | boolean | Whether invoice passed all validation rules |
| `overall_status` | string | `VALIDATED_CLEAN`, `VALIDATED_FLAGGED`, `VALIDATION_FAILED` |
| `reliability_score` | float | Overall reliability score (0-100) |
| `validation_run_id` | string | Unique identifier for this validation run |
| `run_at` | string | When validation was run (ISO 8601) |
| `engine_version` | string | Validation engine version |
| `flags` | array | Validation flags (only failures and warnings) |
| `flags[].rule_id` | string | Validation rule identifier |
| `flags[].category` | string | Rule category (TOTALS, LINE_ITEMS, DUPLICATE, ANOMALY, etc.) |
| `flags[].type` | string | Flag type (AMOUNT_MISMATCH, MISSING_FIELD, LOW_CONFIDENCE, etc.) |
| `flags[].status` | string | `PASS`, `FAIL`, `WARN` |
| `flags[].severity` | integer | Severity level (1-5, 5 is most severe) |
| `flags[].message` | string | Human-readable message |
| `flags[].field` | string | Field that caused the flag (optional) |
| `flags[].expected` | float/string | Expected value (optional) |
| `flags[].actual` | float/string | Actual value (optional) |
| `flags[].deduction_points` | float | Points deducted from reliability score |
| `validation_results` | array | Complete list of all validation rule results |
| `summary` | object | Summary statistics |

**Error Responses:**

**404 Not Found:**
```json
{
  "success": false,
  "error": {
    "code": "NOT_FOUND",
    "message": "Invoice not found or validation not completed",
    "details": ["Invoice with ID 'inv-abc123-def456' does not exist or validation not run"]
  }
}
```

---

### 3.6 Approve & Post Invoice

**POST** `/invoice/{invoice_id}/approve`

**Summary:** Approve a validated invoice and trigger posting to the accounting system.

**Description:** 
Approves a validated invoice (even if flagged) and initiates the posting process to the target accounting system. This endpoint:
- Validates that the invoice is in a postable state
- Generates the accounting system-specific payload
- Posts to the target system (Tally, Zoho, QuickBooks)
- Updates invoice status to `SYNCED_SUCCESS` or `SYNCED_FAILED`

**Auth:** Required (`invoice:approve`)

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `invoice_id` | string | Yes | Unique identifier of the invoice |

**Query Parameters:** None

**Request Body:**

```json
{
  "approved_by": "user-456",
  "notes": "Approved after manual review",
  "force_post": false
}
```

**Request Fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `approved_by` | string | Yes | User ID of the approver |
| `notes` | string | No | Optional notes about the approval |
| `force_post` | boolean | No | Force posting even if validation failed (default: false) |

**Response:**

**Status Code:** `200 OK`

```json
{
  "invoice_id": "inv-abc123-def456",
  "status": "POSTING_INITIATED",
  "external_system": "ZOHO",
  "idempotency_key": "post-abc123-20250115",
  "posted_at": "2025-01-15T10:01:30Z",
  "external_id": "zoho-inv-789",
  "payload_preview": {
    "customer_name": "Acme Ltd",
    "invoice_number": "INV-1002",
    "total": 82600.00
  }
}
```

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `invoice_id` | string | Invoice identifier |
| `status` | string | Posting status: `POSTING_INITIATED`, `SYNCED_SUCCESS`, `SYNCED_FAILED` |
| `external_system` | string | Target accounting system |
| `idempotency_key` | string | Idempotency key for the posting operation |
| `posted_at` | string | When posting was initiated (ISO 8601) |
| `external_id` | string | Invoice ID in the external system (if successful) |
| `payload_preview` | object | Preview of the posted payload |

**Error Responses:**

**400 Bad Request:**
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invoice cannot be posted",
    "details": ["Invoice is not in a valid state for posting", "Status: FAILED_OCR"]
  }
}
```

**404 Not Found:**
```json
{
  "success": false,
  "error": {
    "code": "NOT_FOUND",
    "message": "Invoice not found",
    "details": ["Invoice with ID 'inv-abc123-def456' does not exist"]
  }
}
```

**409 Conflict:**
```json
{
  "success": false,
  "error": {
    "code": "CONFLICT",
    "message": "Invoice already posted",
    "details": ["Invoice was already posted to ZOHO with external_id 'zoho-inv-789'"]
  }
}
```

---

### 3.7 Get Metrics/Reports

**GET** `/metrics`

**Summary:** Retrieve comprehensive KPIs and processing metrics.

**Description:** 
Returns aggregated metrics and KPIs including:
- Total invoices processed
- Success/failure rates
- Processing times
- Validation statistics
- Integration success rates
- Total monetary value processed

**Auth:** Required (`admin:metrics`)

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `start_date` | string | No | Start date for metrics (YYYY-MM-DD) |
| `end_date` | string | No | End date for metrics (YYYY-MM-DD) |
| `user_id` | string | No | Filter by user ID |

**Request Body:** None

**Response:**

**Status Code:** `200 OK`

```json
{
  "period": {
    "start_date": "2025-01-01",
    "end_date": "2025-01-15"
  },
  "summary": {
    "total_invoices": 532,
    "processed": 532,
    "synced": 491,
    "flagged": 41,
    "failed": 0,
    "total_value": 1849200.55
  },
  "processing_times": {
    "avg_ms": 45000,
    "p50_ms": 42000,
    "p95_ms": 78000,
    "p99_ms": 120000,
    "min_ms": 15000,
    "max_ms": 150000
  },
  "success_rates": {
    "ingestion": 1.0,
    "ocr": 0.98,
    "mapping": 0.97,
    "validation": 0.95,
    "integration": 0.92
  },
  "validation_stats": {
    "avg_reliability_score": 87.5,
    "flags_by_category": {
      "TOTALS": 15,
      "LINE_ITEMS": 8,
      "DUPLICATE": 3,
      "ANOMALY": 12,
      "DATES": 3
    }
  },
  "integration_stats": {
    "tally": {
      "posted": 150,
      "failed": 5,
      "success_rate": 0.97
    },
    "zoho": {
      "posted": 200,
      "failed": 8,
      "success_rate": 0.96
    },
    "quickbooks": {
      "posted": 141,
      "failed": 2,
      "success_rate": 0.99
    }
  }
}
```

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `period` | object | Time period for metrics |
| `summary` | object | Overall summary statistics |
| `summary.total_invoices` | integer | Total invoices in period |
| `summary.processed` | integer | Successfully processed |
| `summary.synced` | integer | Successfully posted to accounting systems |
| `summary.flagged` | integer | Flagged for review |
| `summary.failed` | integer | Failed processing |
| `summary.total_value` | float | Total monetary value processed |
| `processing_times` | object | Processing time statistics (milliseconds) |
| `success_rates` | object | Success rates by stage |
| `validation_stats` | object | Validation statistics |
| `integration_stats` | object | Integration statistics by target system |

**Error Responses:**

**403 Forbidden:**
```json
{
  "success": false,
  "error": {
    "code": "FORBIDDEN",
    "message": "Insufficient permissions",
    "details": ["Requires 'admin:metrics' scope"]
  }
}
```

---

### 3.8 Generate Invoice Summary

**POST** `/invoice/summary`

**Summary:** Generate a human-readable summary of invoice processing results.

**Description:** 
Uses LLM to generate a natural language summary of the invoice processing workflow, including:
- Processing status
- Validation results
- Integration status
- Key highlights and issues

**Auth:** Required (`invoice:read`)

**Query Parameters:** None

**Request Body:**

```json
{
  "invoice": {
    "invoice_no": "INV-1002",
    "invoice_date": "2025-05-10",
    "vendor": {
      "name": "Acme Ltd"
    },
    "totals": {
      "grand_total": 82600.00
    }
  },
  "validation": {
    "status": "VALIDATED_FLAGGED",
    "overall_score": 75.5,
    "rules": [
      {
        "rule_id": "TTL-001",
        "status": "FAIL",
        "message": "Subtotal mismatch"
      }
    ]
  },
  "integration": {
    "target_system": "ZOHO",
    "status": "SYNCED_SUCCESS"
  },
  "review": {
    "required": true
  }
}
```

**Request Fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `invoice` | object | Yes | Invoice data (canonical schema) |
| `validation` | object | Yes | Validation results |
| `integration` | object | Yes | Integration status |
| `review` | object | Yes | Review requirements |

**Response:**

**Status Code:** `200 OK`

```json
{
  "summary": "Invoice INV-1002 from Acme Ltd dated 2025-05-10 has been processed successfully. The invoice totals ₹82,600.00 and has been posted to Zoho Books. However, the invoice was flagged during validation with a reliability score of 75.5%. A subtotal mismatch was detected (expected ₹70,000.00, found ₹69,000.00), which requires manual review. The invoice has been successfully integrated into Zoho with external ID 'zoho-inv-789'.",
  "status": "SUMMARY_GENERATED",
  "highlights": [
    "Invoice successfully posted to Zoho Books",
    "Subtotal validation failed - requires review",
    "Overall reliability score: 75.5%"
  ],
  "recommendations": [
    "Review subtotal calculation",
    "Verify line item amounts",
    "Consider manual correction if needed"
  ]
}
```

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `summary` | string | Natural language summary |
| `status` | string | Summary generation status |
| `highlights` | array | Key highlights |
| `recommendations` | array | Recommended actions |

**Error Responses:**

**400 Bad Request:**
```json
{
  "success": false,
  "error": {
    "code": "INVALID_PAYLOAD",
    "message": "Request validation failed",
    "details": ["invoice: field required"]
  }
}
```

---

## 4. Webhooks (Future)

**Status:** Not yet implemented

**Planned Events:**

The API will support webhooks for the following events:

### 4.1 Invoice Processed

**Event:** `invoice.processed`

**Description:** Triggered when invoice processing completes (successfully or with failures).

**Payload:**
```json
{
  "event": "invoice.processed",
  "invoice_id": "inv-abc123-def456",
  "status": "SYNCED_SUCCESS",
  "timestamp": "2025-01-15T10:01:30Z",
  "data": {
    "workflow_status": "SYNCED_SUCCESS",
    "reliability_score": 95.5,
    "validation_flags_count": 0
  }
}
```

### 4.2 Invoice Validated

**Event:** `invoice.validated`

**Description:** Triggered when validation completes.

**Payload:**
```json
{
  "event": "invoice.validated",
  "invoice_id": "inv-abc123-def456",
  "timestamp": "2025-01-15T10:00:45Z",
  "data": {
    "status": "VALIDATED_FLAGGED",
    "reliability_score": 75.5,
    "flags": [...]
  }
}
```

### 4.3 Invoice Posted

**Event:** `invoice.posted`

**Description:** Triggered when invoice is successfully posted to accounting system.

**Payload:**
```json
{
  "event": "invoice.posted",
  "invoice_id": "inv-abc123-def456",
  "timestamp": "2025-01-15T10:01:30Z",
  "data": {
    "external_system": "ZOHO",
    "external_id": "zoho-inv-789",
    "idempotency_key": "post-abc123-20250115"
  }
}
```

### 4.4 Invoice Failed

**Event:** `invoice.failed`

**Description:** Triggered when processing fails at any stage.

**Payload:**
```json
{
  "event": "invoice.failed",
  "invoice_id": "inv-abc123-def456",
  "timestamp": "2025-01-15T10:00:15Z",
  "data": {
    "failed_stage": "OCR",
    "error_code": "OCR_SERVICE_UNAVAILABLE",
    "error_message": "OCR service timeout"
  }
}
```

**Webhook Configuration:**
- Retry policy: Exponential backoff (3 retries)
- Signature verification: HMAC-SHA256
- Timeout: 5 seconds

---

## 5. SDK / Client Libraries

### 5.1 Python SDK Example

```python
from invoice_api import InvoiceClient

client = InvoiceClient(
    base_url="http://localhost:8000",
    api_key="your-api-key"
)

# Upload invoice
response = client.upload_invoice(
    user_id="user-123",
    file_path="/path/to/invoice.pdf",
    target_system="ZOHO"
)
print(f"Invoice ID: {response['invoice_id']}")

# Get status
status = client.get_status(response['invoice_id'])
print(f"Status: {status['status']}")

# Get extracted data
data = client.get_extracted(response['invoice_id'])
print(f"Total: {data['totals']['grand_total']}")

# Get validation results
validation = client.get_validation(response['invoice_id'])
print(f"Reliability: {validation['reliability_score']}%")

# Approve and post
approval = client.approve_invoice(
    invoice_id=response['invoice_id'],
    approved_by="user-456"
)
print(f"Posted to: {approval['external_system']}")
```

### 5.2 JavaScript/TypeScript SDK Example

```typescript
import { InvoiceClient } from '@invoice/api-client';

const client = new InvoiceClient({
  baseUrl: 'http://localhost:8000',
  apiKey: 'your-api-key'
});

// Upload invoice
const response = await client.uploadInvoice({
  userId: 'user-123',
  filePath: '/path/to/invoice.pdf',
  targetSystem: 'ZOHO'
});
console.log(`Invoice ID: ${response.invoiceId}`);

// Get status
const status = await client.getStatus(response.invoiceId);
console.log(`Status: ${status.status}`);

// Get extracted data
const data = await client.getExtracted(response.invoiceId);
console.log(`Total: ${data.totals.grandTotal}`);

// Get validation results
const validation = await client.getValidation(response.invoiceId);
console.log(`Reliability: ${validation.reliabilityScore}%`);

// Approve and post
const approval = await client.approveInvoice({
  invoiceId: response.invoiceId,
  approvedBy: 'user-456'
});
console.log(`Posted to: ${approval.externalSystem}`);
```

### 5.3 cURL Examples

**Upload Invoice:**
```bash
curl -X POST "http://localhost:8000/invoice/upload" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user-123",
    "file_path": "/uploads/invoice.pdf",
    "target_system": "ZOHO"
  }'
```

**Get Status:**
```bash
curl -X GET "http://localhost:8000/invoice/inv-abc123-def456/status" \
  -H "Authorization: Bearer <token>"
```

**Get Extracted Data:**
```bash
curl -X GET "http://localhost:8000/invoice/inv-abc123-def456/extracted" \
  -H "Authorization: Bearer <token>"
```

**Get Validation Results:**
```bash
curl -X GET "http://localhost:8000/invoice/inv-abc123-def456/validation" \
  -H "Authorization: Bearer <token>"
```

**Approve Invoice:**
```bash
curl -X POST "http://localhost:8000/invoice/inv-abc123-def456/approve" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "approved_by": "user-456",
    "notes": "Approved after review",
    "force_post": false
  }'
```

**Get Metrics:**
```bash
curl -X GET "http://localhost:8000/metrics?start_date=2025-01-01&end_date=2025-01-15" \
  -H "Authorization: Bearer <token>"
```

### 5.4 Postman Collection

A Postman collection is available at:
- Collection URL: `docs/postman/Invoice_API.postman_collection.json`
- Environment templates: `docs/postman/Environments/`

**Import Instructions:**
1. Open Postman
2. Click "Import"
3. Select the collection JSON file
4. Import environment variables for your environment

---

## 6. Rate Limits & Throttling

### 6.1 Rate Limits

**Current Limits:**

| Endpoint Type | Limit | Window |
|---------------|-------|--------|
| Upload | 10 requests | Per minute |
| Read operations | 60 requests | Per minute |
| Metrics | 20 requests | Per minute |
| Summary generation | 30 requests | Per minute |

**Per-User Limits:**
- Standard users: 100 requests/hour
- Reviewers: 200 requests/hour
- Admins: 500 requests/hour

### 6.2 File Upload Limits

| Limit Type | Value |
|------------|-------|
| Maximum file size | 50 MB |
| Supported formats | PDF, DOCX, PNG, JPG, JPEG, TIFF |
| Maximum files per request | 1 |

### 6.3 Batch Processing Limits

**Current:**
- Batch uploads: Not supported (process sequentially)
- Maximum concurrent processing: 20 invoices (database connection pool limit)

**Planned:**
- Batch upload endpoint: `/api/v1/invoices/batch-upload`
- Maximum batch size: 100 invoices
- Async processing with job tracking

### 6.4 Retry-After Strategies

**Rate Limit Exceeded Response:**

**Status Code:** `429 Too Many Requests`

```json
{
  "success": false,
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded",
    "details": ["Too many requests. Please try again later."]
  },
  "meta": {
    "retry_after": 60,
    "rate_limit": {
      "limit": 60,
      "remaining": 0,
      "reset_at": "2025-01-15T10:31:00Z"
    }
  }
}
```

**Headers:**
- `X-RateLimit-Limit`: Maximum requests allowed
- `X-RateLimit-Remaining`: Remaining requests in window
- `X-RateLimit-Reset`: Unix timestamp when limit resets
- `Retry-After`: Seconds to wait before retrying

**Retry Strategy:**
- Exponential backoff: 1s, 2s, 4s, 8s
- Maximum retries: 3
- Respect `Retry-After` header

---

## 7. Changelog

### Version 1.0.0 (2024)

**Initial Release:**

**Added:**
- `/invoice/upload` - Upload and process invoices
- `/invoice/{invoice_id}/status` - Get processing status
- `/invoice/{invoice_id}/extracted` - Get extracted data
- `/invoice/{invoice_id}/validation` - Get validation results
- `/invoice/{invoice_id}/approve` - Approve and post invoices
- `/metrics` - Get processing metrics
- `/invoice/summary` - Generate invoice summary
- `/` - Health check endpoint

**Features:**
- Synchronous invoice processing workflow
- OCR extraction with cascading pipeline
- LLM-based schema mapping
- Business rule validation
- Integration with Tally, Zoho, QuickBooks
- Comprehensive error handling
- Standardized response format

**Known Limitations:**
- Authentication not yet implemented
- No webhook support
- No batch upload endpoint
- Synchronous processing only (no async jobs)

### Version 1.1.0 (Planned)

**Planned Features:**
- JWT authentication
- Webhook support
- Batch upload endpoint
- Async processing with job tracking
- File upload via multipart/form-data
- API versioning support

---

**Document Version**: 1.0.0  
**Last Updated**: 2024  
**API Version**: 1.0.0

