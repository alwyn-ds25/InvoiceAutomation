# prompts/schema.py

# This prompt template is designed to be used with an LLM to extract structured
# data from raw OCR text extracted from an invoice.

SCHEMA_MAPPING_PROMPT = """
You are an expert data extraction agent. Your task is to extract key information from the following invoice text and convert it into a structured JSON object.

Please adhere to the following JSON schema strictly. Do not add any fields that are not in the schema. All monetary values should be parsed as floats, not strings.

**JSON Schema:**
```json
{{
    "vendor_name": "string",
    "invoice_number": "string",
    "invoice_date": "YYYY-MM-DD",
    "total_amount": "float",
    "currency": "string (e.g., 'USD', 'INR')",
    "line_items": [
        {{
            "description": "string",
            "quantity": "float",
            "unit_price": "float",
            "total": "float"
        }}
    ]
}}
```

**Instructions:**
1.  **vendor_name**: Identify the name of the company that issued the invoice.
2.  **invoice_number**: Find the unique identifier for the invoice (e.g., "INV-12345", "Order #9876").
3.  **invoice_date**: Extract the date the invoice was issued in YYYY-MM-DD format.
4.  **total_amount**: Find the final, total amount due.
5.  **currency**: Identify the currency of the invoice amounts.
6.  **line_items**: Extract each line item from the invoice. For each item, capture its description, quantity, unit price, and the total for that line.

Here is the invoice text:
---
{extracted_text}
---

Please provide only the JSON object as your response.
"""
