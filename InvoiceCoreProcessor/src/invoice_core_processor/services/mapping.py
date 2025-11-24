from typing import Dict, Any
import json
from unittest.mock import MagicMock

from invoice_core_processor.prompts.schema import EXTRACTION_SCHEMA_PROMPT
from invoice_core_processor.config.settings import get_settings

# --- OpenAI Client Initialization ---

try:
    from openai import OpenAI
    settings = get_settings()
    if settings.OPENAI_API_KEY:
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
    else:
        print("Warning: OPENAI_API_KEY not set. Using a mock client.")
        client = MagicMock()
        mock_response = MagicMock()
        mock_choice = MagicMock()
        mock_choice.message.content = json.dumps({
            "invoiceNumber": "mock-inv-123", "invoiceDate": "2023-01-01",
            "vendor": {"name": "Mock Vendor"}, "totals": {"grandTotal": 100.0}
        })
        mock_response.choices = [mock_choice]
        client.chat.completions.create.return_value = mock_response
except ImportError:
    print("Warning: 'openai' library not found. Using a mock client.")
    client = MagicMock()

def map_text_to_schema(extracted_text: str, target_system: str) -> Dict[str, Any]:
    """
    Uses a real LLM call (or a mock if the key is not set) to map text to schema.
    """
    print(f"Mapping extracted text for target system: {target_system}")

    prompt = EXTRACTION_SCHEMA_PROMPT.format(extracted_text=extracted_text)
    settings = get_settings()

    try:
        response = client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You are a data extraction expert."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )

        llm_response_content = response.choices[0].message.content
        mapped_data = json.loads(llm_response_content)

        return {
            "status": "MAPPING_COMPLETE",
            "mapped_schema": mapped_data
        }
    except Exception as e:
        print(f"LLM call failed: {e}")
        return {
            "status": "FAILED_MAPPING",
            "error": str(e)
        }
