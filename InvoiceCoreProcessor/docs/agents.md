# Agent Documentation

This document describes the agents used in the InvoiceCoreProcessor system.

## DataStoreAgent

-   **Agent ID:** `com.invoice.datastore`
-   **Description:** Provides secure, transactional access to MongoDB and PostgreSQL.
-   **MCP Tools:**
    -   `mongo/save_metadata`
    -   `mongo/log_response`
    -   `mongo/save_ocr_payload`
    -   `postgres/check_duplicate`
    -   `postgres/save_validated_record`
    -   `postgres/register_agent`
    -   `postgres/save_tool`
    -   `postgres/save_audit_step`

## OCRAgent

-   **Agent ID:** `com.invoice.ocr`
-   **Description:** Executes a file-type-aware, cascading OCR pipeline.
-   **MCP Tools:**
    -   `ocr/extract_text_cascading`

## SchemaMapperAgent

-   **Agent ID:** `com.invoice.mapper`
-   **Description:** Uses an LLM to map extracted text to a canonical invoice schema.
-   **MCP Tools:**
    -   `map/execute`

## AnomalyAgent

-   **Agent ID:** `com.invoice.validation`
-   **Description:** Implements validation and anomaly detection.
-   **MCP Tools:**
    -   `validate/run_checks`

## DataIntegrationAgent

-   **Agent ID:** `com.invoice.integration`
-   **Description:** Generates ERP-ready payloads.
-   **MCP Tools:**
    -   `sync/push_to_erp`
