import unittest
from unittest.mock import patch, MagicMock, AsyncMock
import uuid
import asyncio

# To allow running tests from the root directory
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# The settings import needs to be after the path is appended
from InvoiceCoreProcessor.servers.database_server import (
    save_audit_step, check_duplicate, save_validated_record,
    save_metadata, log_response, save_ocr_payload
)

@patch('InvoiceCoreProcessor.servers.database_server.get_mongo_db')
@patch('InvoiceCoreProcessor.servers.database_server.get_postgres_connection')
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
        """Tests the save and duplicate check logic with a mock database."""
        # --- Part 1: Save the record ---
        mock_conn_save = MagicMock()
        mock_cursor_save = MagicMock()
        mock_get_pg_conn.return_value = mock_conn_save
        mock_conn_save.cursor.return_value.__enter__.return_value = mock_cursor_save

        invoice_data = { 'id': str(uuid.uuid4()), 'vendor_id': str(uuid.uuid4()), 'invoice_no': 'test-123', 'invoice_date': '2023-01-01' }
        save_result = save_validated_record(invoice_data)
        self.assertEqual(save_result['status'], 'RECORD_SAVED')
        mock_cursor_save.execute.assert_called_once()

        # --- Part 2: Check for the duplicate ---
        mock_conn_check = MagicMock()
        mock_cursor_check = MagicMock()
        mock_get_pg_conn.return_value = mock_conn_check
        mock_conn_check.cursor.return_value.__enter__.return_value = mock_cursor_check
        # Simulate that the DB finds a record
        mock_cursor_check.fetchone.return_value = (str(uuid.uuid4()),)

        dup_result = check_duplicate(invoice_data['vendor_id'], invoice_data['invoice_no'], invoice_data['invoice_date'])
        self.assertEqual(dup_result['status'], 'DUPLICATE_FOUND')
        mock_cursor_check.execute.assert_called_once()

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
