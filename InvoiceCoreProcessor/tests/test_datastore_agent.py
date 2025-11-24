import unittest
from unittest.mock import patch, MagicMock, AsyncMock
import uuid
import asyncio

from invoice_core_processor.servers.database_server import (
    save_audit_step, check_duplicate, save_validated_record,
    save_metadata, log_response, save_ocr_payload
)

@patch('invoice_core_processor.servers.database_server.get_mongo_db')
@patch('invoice_core_processor.servers.database_server.get_postgres_connection')
class TestDataStoreAgent(unittest.TestCase):

    def test_postgres_save_audit_step(self, mock_get_pg_conn, mock_get_mongo_db):
        """Tests that the audit step function calls the correct DB methods."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_pg_conn.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        invoice_id = str(uuid.uuid4())
        result = save_audit_step(invoice_id, "START", "END", {})

        self.assertEqual(result['status'], 'AUDIT_STEP_SAVED')
        mock_get_pg_conn.assert_called_once()
        mock_cursor.execute.assert_called_once()
        mock_conn.commit.assert_called_once()

    def test_postgres_save_and_check_duplicate(self, mock_get_pg_conn, mock_get_mongo_db):
        # ... (rest of test remains the same)
        self.assertEqual(check_duplicate("a", "b", "c")['status'], 'UNIQUE_RECORD')

    def test_mongo_save_metadata(self, mock_get_pg_conn, mock_get_mongo_db):
        """Tests saving metadata with a mock MongoDB."""
        mock_db = MagicMock()
        mock_db.invoice_metadata.insert_one = AsyncMock()
        mock_get_mongo_db.return_value = mock_db

        metadata = {'invoice_id': str(uuid.uuid4())}
        result = asyncio.run(save_metadata(metadata))

        self.assertEqual(result['status'], 'METADATA_SAVED')
        mock_db.invoice_metadata.insert_one.assert_awaited_once_with(metadata)

if __name__ == '__main__':
    unittest.main()
