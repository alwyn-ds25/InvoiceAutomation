# Database Schema

## PostgreSQL

The PostgreSQL database is used to store structured data, including the core invoice records, agent registry, and validation results.

### Normalized Schema

```sql
-- Master tables for vendors and customers
CREATE TABLE vendors (
    id           UUID PRIMARY KEY,
    name         TEXT NOT NULL,
    gstin        TEXT,
    pan          TEXT,
    address      TEXT,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (name, gstin)
);

CREATE TABLE customers (
    id           UUID PRIMARY KEY,
    name         TEXT NOT NULL,
    gstin        TEXT,
    address      TEXT,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Normalized invoices table
CREATE TABLE invoices (
    id               UUID PRIMARY KEY,
    user_id          TEXT NOT NULL,
    vendor_id        UUID REFERENCES vendors(id),
    customer_id      UUID REFERENCES customers(id),
    invoice_no       TEXT NOT NULL,
    invoice_date     DATE NOT NULL,
    due_date         DATE,
    subtotal         NUMERIC(18, 2) NOT NULL,
    gst_amount       NUMERIC(18, 2),
    total_amount     NUMERIC(18, 2),
    round_off        NUMERIC(18, 2),
    grand_total      NUMERIC(18, 2) NOT NULL,
    payment_mode     TEXT,
    payment_reference TEXT,
    payment_status   TEXT,
    upload_timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    extraction_confidence NUMERIC(5, 4),
    status           TEXT NOT NULL DEFAULT 'PENDING',
    created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (vendor_id, invoice_no, invoice_date)
);

-- Invoice line items
CREATE TABLE invoice_items (
    id              UUID PRIMARY KEY,
    invoice_id      UUID NOT NULL REFERENCES invoices(id) ON DELETE CASCADE,
    line_no         INTEGER NOT NULL,
    description     TEXT NOT NULL,
    quantity        NUMERIC(18, 4) NOT NULL,
    unit_price      NUMERIC(18, 4) NOT NULL,
    tax_pct         NUMERIC(5, 2),
    amount          NUMERIC(18, 2) NOT NULL,
    hsn             TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

### Other Tables

-   **agent_registry:** Stores information about the agents in the network.
-   **agent_tools:** Stores the capabilities of each agent.
-   **validation_rule:** A master table for the validation rules.
-   **invoice_validation_run:** Records each validation run.
-   **invoice_validation_result:** Stores the result of each individual validation rule.
-   **workflow_audit:** Logs the state transitions of the invoice processing workflow.

## MongoDB

The MongoDB database is used to store unstructured or semi-structured data.

-   **invoice_metadata:** Stores metadata about ingested invoices.
-   **agent_process_logs:** Logs agent executions.
-   **ocr_extraction_data:** Stores raw OCR extraction data.
-   **invoice_validations:** Stores a document-based view of validation runs.
