from typing import Dict, Any
import json

# To allow running this file directly for testing
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from prompts.schema import SCHEMA_MAPPING_PROMPT

def map_text_to_schema(extracted_text: str, target_system: str) -> Dict[str, Any]:
    """
    Simulates a more realistic LLM-based mapping process.
    It formats a detailed prompt, simulates an LLM call, and parses the response.
    """
    print(f"Mapping extracted text for target system: {target_system}")

    # 1. Format the prompt with the extracted text
    prompt = SCHEMA_MAPPING_PROMPT.format(extracted_text=extracted_text)

    # 2. Simulate the LLM call
    print("--- Simulating LLM Call ---")
    print("Prompt being sent to LLM (first 500 chars):")
    print(prompt[:500] + "...")

    # This is the part where you would make an API call to OpenAI, Anthropic, etc.
    # For now, we'll return a hardcoded JSON string, as if it were the LLM's response.
    mock_llm_response = json.dumps({
        "vendor_name": "LLM Mapped Vendor Inc.",
        "invoice_number": "LLM-INV-9876",
        "invoice_date": "2023-11-15",
        "total_amount": 1500.75,
        "currency": "INR",
        "line_items": [
            {
                "description": "Consulting Services",
                "quantity": 10,
                "unit_price": 150.00,
                "total": 1500.00
            },
            {
                "description": "Tax Adjustment",
                "quantity": 1,
                "unit_price": 0.75,
                "total": 0.75
            }
        ]
    })

    print("\nMock LLM Response:")
    print(mock_llm_response)
    print("--------------------------")

    # 3. Parse the LLM's response
    try:
        mapped_data = json.loads(mock_llm_response)
        return {
            "status": "MAPPING_COMPLETE",
            "mapped_schema": mapped_data
        }
    except json.JSONDecodeError:
        return {
            "status": "FAILED_MAPPING",
            "error": "Failed to parse LLM JSON response."
        }
