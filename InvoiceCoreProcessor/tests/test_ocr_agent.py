import unittest
from unittest.mock import patch, MagicMock

from invoice_core_processor.services.ocr_processor import run_image_ocr_cascade, OCRResult

class TestOCRCascade(unittest.TestCase):

    @patch('invoice_core_processor.services.ocr_processor.try_easyocr')
    @patch('invoice_core_processor.services.ocr_processor.try_tesseract')
    @patch('invoice_core_processor.services.ocr_processor.try_azure_docint')
    @patch('invoice_core_processor.services.ocr_processor.try_gpt_vision')
    @patch('invoice_core_processor.services.ocr_processor.try_typhoon_ocr')
    def test_full_cascade_fallback(self, mock_typhoon, mock_gpt, mock_azure, mock_tesseract, mock_easyocr):
        """
        Tests that the image OCR pipeline correctly falls back through all engines.
        """
        # --- Setup Mocks ---
        # All engines except the last one will fail (return None)
        mock_typhoon.return_value = None
        mock_gpt.return_value = None
        mock_azure.return_value = None
        mock_tesseract.return_value = None

        # EasyOCR (the last resort) will succeed
        mock_easyocr.return_value = OCRResult(
            status="OCR_DONE",
            avg_confidence=0.5,
            pages=[{"page_number": 1, "text": "Success from EasyOCR"}],
            tables=[],
            raw_engine_trace={"engine": "easyocr"}
        )

        # --- Run the Cascade ---
        result = run_image_ocr_cascade(["dummy_image.png"])

        # --- Assertions ---
        # Check that all engines were attempted
        mock_typhoon.assert_called_once()
        mock_gpt.assert_called_once()
        mock_azure.assert_called_once()
        mock_tesseract.assert_called_once()
        mock_easyocr.assert_called_once()

        # Check that the final result is from EasyOCR
        self.assertEqual(result.status, "OCR_DONE")
        self.assertIn("easyocr", result.raw_engine_trace)
        self.assertEqual(result.raw_engine_trace["easyocr"], "success")
        self.assertEqual(result.pages[0]["text"], "Success from EasyOCR")

if __name__ == '__main__':
    unittest.main()
