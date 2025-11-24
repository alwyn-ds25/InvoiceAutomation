-- Agent registry (no changes)
CREATE TABLE agent_registry (
    id SERIAL PRIMARY KEY,
    agent_id TEXT NOT NULL UNIQUE,
    agent_card JSONB NOT NULL,
    last_heartbeat TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE agent_tools (
    id SERIAL PRIMARY KEY,
    agent_id TEXT NOT NULL REFERENCES agent_registry(agent_id) ON DELETE CASCADE,
    tool_id TEXT NOT NULL,
    capability TEXT NOT NULL,
    description TEXT NOT NULL,
    parameters JSONB,
    UNIQUE (agent_id, tool_id)
);

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

-- Validation tables (updated for the new checklist)
CREATE TABLE validation_rule (
    id SERIAL PRIMARY KEY,
    rule_id TEXT NOT NULL UNIQUE,
    category TEXT NOT NULL,
    description TEXT NOT NULL,
    severity SMALLINT NOT NULL CHECK (severity BETWEEN 1 AND 5),
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE invoice_validation_run (
    id UUID PRIMARY KEY,
    invoice_id UUID NOT NULL REFERENCES invoices(id) ON DELETE CASCADE,
    run_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    engine_version TEXT NOT NULL,
    overall_score NUMERIC(5,2),
    status TEXT NOT NULL
);

CREATE TABLE invoice_validation_result (
    id BIGSERIAL PRIMARY KEY,
    validation_run_id UUID NOT NULL REFERENCES invoice_validation_run(id) ON DELETE CASCADE,
    rule_id TEXT NOT NULL REFERENCES validation_rule(rule_id),
    status TEXT NOT NULL CHECK (status IN ('PASS','FAIL','WARN')),
    message TEXT,
    severity SMALLINT NOT NULL,
    deduction_points NUMERIC(5,2) NOT NULL DEFAULT 0
);

-- Workflow audit table (no changes)
CREATE TABLE workflow_audit (
    id BIGSERIAL PRIMARY KEY,
    invoice_id UUID NOT NULL,
    from_status TEXT NOT NULL,
    to_status TEXT NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    meta JSONB
);
