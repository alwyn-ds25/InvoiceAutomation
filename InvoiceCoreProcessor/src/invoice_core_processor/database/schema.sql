-- Agent registry
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

-- Core invoices
CREATE TABLE invoice (
    id UUID PRIMARY KEY,
    external_ref TEXT,
    vendor_id UUID,
    invoice_no TEXT NOT NULL,
    invoice_date DATE NOT NULL,
    currency TEXT NOT NULL DEFAULT 'INR',
    total_amount NUMERIC(18,2) NOT NULL,
    status TEXT NOT NULL,
    created_at TIMESTAMTz NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (vendor_id, invoice_no, invoice_date)
);

-- Validation rule master
CREATE TABLE validation_rule (
    id SERIAL PRIMARY KEY,
    rule_id TEXT NOT NULL UNIQUE,
    category TEXT NOT NULL,
    description TEXT NOT NULL,
    severity SMALLINT NOT NULL CHECK (severity BETWEEN 1 AND 5),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Validation run
CREATE TABLE invoice_validation_run (
    id UUID PRIMARY KEY,
    invoice_id UUID NOT NULL REFERENCES invoice(id) ON DELETE CASCADE,
    run_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    engine_version TEXT NOT NULL,
    overall_score NUMERIC(5,2),
    status TEXT NOT NULL,
    summary JSONB,
    created_by TEXT
);

-- Per-rule result
CREATE TABLE invoice_validation_result (
    id BIGSERIAL PRIMARY KEY,
    validation_run_id UUID NOT NULL REFERENCES invoice_validation_run(id) ON DELETE CASCADE,
    rule_id TEXT NOT NULL REFERENCES validation_rule(rule_id),
    status TEXT NOT NULL CHECK (status IN ('PASS','FAIL','WARN')),
    message TEXT,
    severity SMALLINT NOT NULL,
    deduction_points NUMERIC(5,2) NOT NULL DEFAULT 0,
    meta JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE VIEW invoice_latest_validation AS
SELECT DISTINCT ON (ivr.invoice_id)
    ivr.invoice_id,
    ivr.id AS validation_run_id,
    ivr.run_at,
    ivr.overall_score,
    ivr.status
FROM invoice_validation_run ivr
ORDER BY ivr.invoice_id, ivr.run_at DESC;

-- Workflow audit table
CREATE TABLE workflow_audit (
    id BIGSERIAL PRIMARY KEY,
    invoice_id UUID NOT NULL,
    from_status TEXT NOT NULL,
    to_status TEXT NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    meta JSONB
);
