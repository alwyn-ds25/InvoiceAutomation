import unittest
from unittest.mock import patch, MagicMock

from invoice_core_processor.services.metrics import get_all_metrics

@patch('invoice_core_processor.services.metrics.get_postgres_connection')
class TestMetricsCollectorAgent(unittest.TestCase):

    def test_metric_calculations(self, mock_get_pg_conn):
        """
        Tests the KPI calculation logic with a mocked database.
        """
        # --- Mock Setup ---
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_pg_conn.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        # Define the return values for each query
        mock_cursor.fetchone.side_effect = [
            (100,), # total_invoices
            (80,),  # successful_syncs
            (15,),  # flagged_invoices
            (150000.00,), # total_invoice_value
            (0.95,), # ocr_accuracy
            (85.0,), # validation_pass_rate
            (5000,), # avg_processing_time
        ]

        # --- Execute ---
        metrics = get_all_metrics()

        # --- Assertions ---
        self.assertEqual(metrics['high_impact_kpis']['total_invoices'], 100)
        self.assertEqual(metrics['high_impact_kpis']['successful_syncs'], 80)
        self.assertEqual(metrics['quality_efficiency']['ocr_accuracy'], "95.00%")
        self.assertEqual(metrics['quality_efficiency']['avg_processing_time_ms'], 5000)

        # Check that the correct number of queries were made
        self.assertEqual(mock_cursor.execute.call_count, 7)

if __name__ == '__main__':
    unittest.main()
