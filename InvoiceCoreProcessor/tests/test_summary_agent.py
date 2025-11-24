import unittest
from unittest.mock import patch, MagicMock, AsyncMock
import os

class TestSummaryAgentWorkflow(unittest.TestCase):

    def test_full_workflow_with_summary(self):
        with patch.dict(os.environ, {
            "POSTGRES_URI": "postgresql://test:test@localhost:5432/test",
            "MONGO_URI": "mongodb://localhost:27017/",
            "MONGO_DB_NAME": "test",
            "A2A_REGISTRY_URL": "local",
            "OPENAI_API_KEY": "test",
            "TYPHOON_OCR_API_KEY": "test",
            "GEMINI_API_KEY": "test",
            "GEMINI_MODEL": "gemini-1.5-pro",
            "ENV": "dev",
            "AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT": "test",
            "AZURE_DOCUMENT_INTELLIGENCE_KEY": "test",
            "TESSERACT_CMD_PATH": "test",
            "EASYOCR_LANGUAGES": "en",
            "GPT4_VISION_MODEL": "gpt-4o",
            "OPENAI_MODEL": "gpt-4",
            "OPENAI_ENABLED": "true"
        }):
            from invoice_core_processor.core.workflow import build_workflow_graph
            from invoice_core_processor.core.models import InvoiceGraphState

            with patch('invoice_core_processor.core.workflow.get_mcp_client') as mock_mcp_client, \
                 patch('invoice_core_processor.core.workflow.get_ingestion_client') as mock_ingestion_client, \
                 patch('invoice_core_processor.core.workflow.get_agent_registry') as mock_agent_registry:

                # Mocking the MCP client to simulate responses from other agents
                mock_mcp = MagicMock()
                mock_mcp.call_tool.side_effect = [
                    # Mock response for save_audit_step after ingestion
                    None,
                    # Mock response for OCR agent
                    {'status': 'OCR_DONE', 'pages': [{'text': 'mock_text'}], 'avg_confidence': 0.95},
                    # Mock response for save_audit_step after OCR
                    None,
                    # Mock response for mapping agent
                    {'status': 'MAPPED', 'mapped_schema': {'invoice_no': 'INV-123'}},
                    # Mock response for save_audit_step after mapping
                    None,
                    # Mock response for validation agent
                    {
                        'status': 'VALIDATED_FLAGGED',
                        'overall_score': 80.0,
                        'validation_results': [
                            {
                                'rule_id': 'TAX-002',
                                'status': 'WARN',
                                'message': 'Uncommon tax rate of 18% applied for consulting services.',
                                'severity': 3,
                                'deduction_points': 2.5,
                                'meta': {
                                    'field': 'tax_pct',
                                    'expected': 'one of [5,12]'
                                }
                            }
                        ]
                    },
                    # Mock response for save_audit_step after validation
                    None,
                    # Mock response for integration agent
                    {'status': 'SYNCED_SUCCESS', 'integration_status': 'SUCCESS'},
                    # Mock response for save_audit_step after integration
                    None,
                    # Mock response for summary agent
                    {'status': 'NEEDS_REVIEW', 'headline': '...'},
                    # Mock response for save_audit_step after summary
                    None
                ]
                mock_mcp_client.return_value = mock_mcp

                # Mocking the ingestion client
                mock_ingestion = MagicMock()
                mock_ingestion.ingest_file = AsyncMock(return_value={
                    'status': 'SUCCESS',
                    'invoice_id': 'mock_invoice_id',
                    'storage_path': '/path/to/mock_invoice.pdf'
                })
                mock_ingestion_client.return_value = mock_ingestion

                # Mocking the agent registry
                mock_registry = MagicMock()
                mock_registry.lookup_agent_by_capability.side_effect = [
                    ("com.invoice.ocr", MagicMock(tool_id="ocr/extract")),
                    ("com.invoice.mapper", MagicMock(tool_id="map/execute")),
                    ("com.invoice.validation", MagicMock(tool_id="validation/run")),
                    ("com.invoice.integration", MagicMock(tool_id="integration/post")),
                    ("com.invoice.summary", MagicMock(tool_id="summary/generate"))
                ]
                mock_agent_registry.return_value = mock_registry

                # Initial state for the workflow
                initial_state = InvoiceGraphState(
                    user_id="test_user",
                    file_path="/path/to/invoice.pdf",
                    target_system="TALLY"
                )

                # Build and run the workflow
                workflow = build_workflow_graph()
                final_state = workflow.invoke(initial_state)

                # Assertions to ensure the workflow ran as expected
                self.assertEqual(final_state['status'], 'SUMMARY_GENERATED')
                self.assertIn('summary', final_state)
                self.assertEqual(final_state['summary']['status'], 'NEEDS_REVIEW')

                # Check that the correct validation status was passed to the summary agent
                summary_agent_call = mock_mcp.call_tool.call_args_list[-2]
                self.assertEqual(summary_agent_call[1]['invoice_data']['validation']['status'], 'REVIEW')

if __name__ == '__main__':
    unittest.main()
