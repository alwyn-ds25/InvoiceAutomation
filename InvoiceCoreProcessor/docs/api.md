# API Documentation

## Endpoints

### `/invoice/upload`

- **Method:** `POST`
- **Description:** Uploads an invoice for processing.
- **Request Body:**
  ```json
  {
    "user_id": "string",
    "file_path": "string",
    "target_system": "TALLY" | "ZOHO" | "QUICKBOOKS"
  }
  ```
- **Response Body:**
  ```json
  {
    "workflow_status": "string",
    "invoice_id": "string",
    "reliability_score": "float",
    "validation_flags": "array",
    "integration_status": "string"
  }
  ```

### `/reports/summary` (Future)

- **Method:** `GET`
- **Description:** Retrieves a summary of processed invoices.
- **Query Parameters:**
  - `start_date` (optional)
  - `end_date` (optional)
  - `user_id` (optional)
