import unittest
from unittest.mock import patch, MagicMock
import uuid

from invoice_core_processor.servers.database_server import save_validated_record, check_duplicate

class TestDataStoreAgent(unittest.TestCase):

    @patch('invoice_core_processor.servers.database_server.execute_values')
    @patch('invoice_core_processor.servers.database_server.get_postgres_connection')
    def test_save_validated_record_transaction(self, mock_get_pg_conn, mock_execute_values):
        """Tests the full transactional logic of saving a validated record."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_pg_conn.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchone.side_effect = [(uuid.uuid4(),), (uuid.uuid4(),)]

        invoice_data = {
            "user_id": "test-user", "invoiceNumber": "test-inv-123", "invoiceDate": "2023-01-01",
            "vendor": { "name": "Test Vendor", "gstin": "123" },
            "totals": { "subtotal": 100.0, "grandTotal": 118.0 },
            "lineItems": [{"description": "Item 1", "quantity": 1, "unitPrice": 100, "taxPercent": 18, "amount": 118.0}]
        }

        result = save_validated_record(invoice_data)

        self.assertEqual(result['status'], 'RECORD_SAVED')
        self.assertEqual(mock_cursor.execute.call_count, 3) # Upsert Vendor, Upsert Invoice, Delete Items
        mock_execute_values.assert_called_once()
        mock_conn.commit.assert_called_once()

    @patch('invoice_core_processor.servers.database_server.get_postgres_connection')
    def test_check_duplicate_query(self, mock_get_pg_conn):
        """Tests that the check_duplicate function uses the correct query."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_pg_conn.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        check_duplicate("Test Vendor", "test-inv-123", "2023-01-01")

        mock_cursor.execute.assert_called_once()
        self.assertIn("JOIN vendors", mock_cursor.execute.call_args[0][0])

if __name__ == '__main__':
    unittest.main()
