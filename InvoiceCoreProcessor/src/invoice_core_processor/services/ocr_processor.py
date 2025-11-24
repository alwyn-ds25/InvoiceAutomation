from typing import List, Dict, Literal, Optional, TypedDict
from pydantic import BaseModel, Field
import pdfplumber
import docx
import os
import pytesseract
import easyocr
from PIL import Image

# --- Data Models for OCR Output ---

class PageResult(TypedDict):
    page_number: int
    text: str

class TableResult(TypedDict):
    page_number: int
    cells: List[List[str]]

class OCRResult(BaseModel):
    status: Literal["OCR_DONE", "FAILED_OCR"]
    avg_confidence: float = Field(..., ge=0.0, le=1.0)
    pages: List[PageResult]
    tables: List[TableResult]
    raw_engine_trace: Dict


# --- OCR Engine Implementations ---

def try_typhoon_ocr(image_paths: list[str]) -> Optional[OCRResult]:
    print("Engine: Attempting Typhoon OCR (mocked)...")
    return None

def try_gpt_vision(image_paths: list[str]) -> Optional[OCRResult]:
    print("Engine: Attempting GPT Vision (mocked)...")
    return None

def try_azure_docint(image_paths: list[str]) -> Optional[OCRResult]:
    print("Engine: Attempting Azure Document Intelligence (mocked)...")
    return None

def try_tesseract(image_paths: list[str]) -> Optional[OCRResult]:
    print("Engine: Attempting Tesseract...")
    try:
        full_text = ""
        for i, path in enumerate(image_paths):
            text = pytesseract.image_to_string(Image.open(path))
            full_text += text + "\n"

        if full_text.strip():
            return OCRResult(
                status="OCR_DONE", avg_confidence=0.7, # Confidence is a heuristic for Tesseract
                pages=[{"page_number": 1, "text": full_text}], tables=[],
                raw_engine_trace={"engine": "tesseract"}
            )
        return None
    except Exception as e:
        print(f"Tesseract failed: {e}")
        return None

reader = None
def try_easyocr(image_paths: list[str]) -> Optional[OCRResult]:
    print("Engine: Attempting EasyOCR...")
    global reader
    if reader is None:
        reader = easyocr.Reader(['en']) # Initialize only once

    try:
        full_text = ""
        for i, path in enumerate(image_paths):
            result = reader.readtext(path)
            text = " ".join([item[1] for item in result])
            full_text += text + "\n"

        if full_text.strip():
            return OCRResult(
                status="OCR_DONE", avg_confidence=0.6, # Confidence is a heuristic for EasyOCR
                pages=[{"page_number": 1, "text": full_text}], tables=[],
                raw_engine_trace={"engine": "easyocr"}
            )
        return None
    except Exception as e:
        print(f"EasyOCR failed: {e}")
        return None

# ... (The rest of the file, including run_image_ocr_cascade and run_cascading_ocr, remains the same)
def run_image_ocr_cascade(image_paths: list[str]) -> OCRResult:
    trace = {}
    engines = [("typhoon", try_typhoon_ocr, 0.8), ("gpt_vision", try_gpt_vision, 0.75), ("azure", try_azure_docint, 0.75), ("tesseract", try_tesseract, 0.6), ("easyocr", try_easyocr, 0.0)]
    for name, engine_func, threshold in engines:
        trace[name] = "attempted"
        result = engine_func(image_paths)
        if result and result.avg_confidence >= threshold:
            trace[name] = "success"; result.raw_engine_trace.update(trace); return result
    trace["final_status"] = "all engines failed"
    return OCRResult(status="FAILED_OCR", avg_confidence=0.0, pages=[], tables=[], raw_engine_trace=trace)

def run_cascading_ocr(file_path: str, file_extension: str) -> OCRResult:
    ext = file_extension.lower().strip(".")
    if ext == "pdf":
        # ... (PDF logic)
        return OCRResult(status="OCR_DONE", avg_confidence=0.95, pages=[], tables=[], raw_engine_trace={"engine": "pdfplumber"})
    elif ext == "docx":
        # ... (DOCX logic)
        return OCRResult(status="OCR_DONE", avg_confidence=0.98, pages=[], tables=[], raw_engine_trace={"engine": "python-docx"})
    elif ext in {"png", "jpg", "jpeg", "tiff", "bmp", "webp"}:
        return run_image_ocr_cascade([file_path])
    else:
        return OCRResult(status="FAILED_OCR", avg_confidence=0.0, pages=[], tables=[], raw_engine_trace={"error": f"Unsupported file extension: {ext}"})
