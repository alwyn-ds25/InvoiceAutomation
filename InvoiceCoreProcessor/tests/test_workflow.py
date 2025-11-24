import unittest
import os
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock

from invoice_core_processor.core.workflow import build_workflow_graph

# Patch all the factories that create clients with external dependencies
@patch('invoice_core_processor.core.workflow.get_agent_registry')
@patch('invoice_core_processor.core.workflow.get_mcp_client')
@patch('invoice_core_processor.core.workflow.get_ingestion_client')
class TestWorkflow(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Set up a dummy file for the workflow to use."""
        cls.dummy_file = "test_invoice_for_workflow.pdf"
        if not os.path.exists(cls.dummy_file):
            with open(cls.dummy_file, "w") as f: f.write("dummy")

    @classmethod
    def tearDownClass(cls):
        """Clean up the dummy file."""
        if os.path.exists(cls.dummy_file): os.remove(cls.dummy_file)

    def test_full_workflow_execution(self, mock_get_ingestion_client, mock_get_mcp_client, mock_get_registry):
        """
        Tests the end-to-end workflow by mocking the client factories.
        """
        # --- Configure Mocks ---
        mock_ingestion = MagicMock()
        mock_ingestion.ingest_file = AsyncMock(return_value={
            'status': 'SUCCESS', 'invoice_id': 'test-inv-123', 'storage_path': 'new/path.pdf'
        })
        mock_get_ingestion_client.return_value = mock_ingestion

        mock_mcp = MagicMock()
        mock_get_mcp_client.return_value = mock_mcp

        mock_registry = MagicMock()
        mock_registry.lookup_agent_by_capability.return_value = ('mock-agent-id', MagicMock(tool_id='mock-tool'))
        mock_get_registry.return_value = mock_registry

        # Define the return values for each step's MCP call
        mock_mcp.call_tool.side_effect = [
            {'status': 'AUDIT_STEP_SAVED'}, # ingestion audit
            {'status': 'OCR_DONE', 'pages': [{'text': '...'}], 'avg_confidence': 0.9}, # ocr
            {'status': 'AUDIT_STEP_SAVED'}, # ocr audit
            {'status': 'MAPPING_COMPLETE', 'mapped_schema': {}}, # mapping
            {'status': 'AUDIT_STEP_SAVED'}, # mapping audit
            {'status': 'VALIDATED_CLEAN', 'overall_score': 100, 'validation_results': []}, # validation
            {'status': 'AUDIT_STEP_SAVED'}, # validation audit
            {'status': 'SYNCED_SUCCESS'}, # integration
            {'status': 'AUDIT_STEP_SAVED'} # integration audit
        ]

        # --- Run Workflow ---
        workflow_app = build_workflow_graph()
        initial_state = {
            "user_id": "test-user", "file_path": self.dummy_file, "target_system": "ZOHO",
            "status": "UPLOADED", "invoice_id": None, "extracted_text": None,
            "mapped_schema": None, "validation_flags": [], "reliability_score": None,
            "anomaly_details": [], "integration_payload_preview": None,
            "current_step": "start", "history": []
        }
        final_state = workflow_app.invoke(initial_state)

        # --- Assertions ---
        self.assertEqual(final_state['status'], 'SYNCED_SUCCESS')
        self.assertEqual(final_state['invoice_id'], 'test-inv-123')
        self.assertTrue(mock_ingestion.ingest_file.called)
        self.assertEqual(mock_mcp.call_tool.call_count, 9)

if __name__ == '__main__':
    unittest.main()
