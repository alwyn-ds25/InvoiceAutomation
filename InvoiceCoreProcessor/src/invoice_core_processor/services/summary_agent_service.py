from typing import Dict, Any
import json
import google.generativeai as genai
from invoice_core_processor.prompts.summary_prompt import INVOICE_VALIDATION_SUMMARY_PROMPT
from invoice_core_processor.config.settings import get_settings

class LlmClient:
    def __init__(self, model_name: str):
        self.model_name = model_name
        settings = get_settings()
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(self.model_name)

    def generate_json(self, prompt: str) -> Dict[str, Any]:
        """
        Generates a JSON response from the LLM.
        """
        response = self.model.generate_content(prompt)
        # The response from the LLM is expected to be a JSON string.
        # We need to parse it to a dictionary.
        try:
            # It's common for the LLM to wrap the JSON in markdown backticks.
            # We'll remove them before parsing.
            json_string = response.text.strip().replace("`", "").replace("json", "")
            return json.loads(json_string)
        except (json.JSONDecodeError, AttributeError) as e:
            print(f"Error decoding LLM response: {e}")
            # Return a default error response if the LLM output is not valid JSON.
            return {
                "status": "BLOCKED_BY_ERRORS",
                "headline": "Failed to generate summary due to an internal error.",
                "invoice_summary": {},
                "validation_summary": {
                    "errors": [{"category": "SYSTEM", "message": "Failed to parse LLM response."}]
                },
                "integration_summary": {},
                "next_actions": ["Please report this issue to the development team."]
            }


class SummaryAgentService:
    def __init__(self):
        settings = get_settings()
        self.llm_client = LlmClient(model_name=settings.GEMINI_MODEL)

    def generate_summary(self, invoice_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generates a summary of the invoice validation and integration status.

        Args:
            invoice_data: A dictionary containing the invoice, validation, integration, and review data.

        Returns:
            A dictionary containing the generated summary.
        """
        prompt = self._format_prompt(invoice_data)
        summary = self.llm_client.generate_json(prompt)
        return summary

    def _format_prompt(self, invoice_data: Dict[str, Any]) -> str:
        """
        Formats the prompt for the LLM.
        """
        return f"{INVOICE_VALIDATION_SUMMARY_PROMPT}\n\nHere is the latest invoice state JSON. Generate the summary as per the instructions.\n\n```json\n{json.dumps(invoice_data, indent=2)}\n```"
