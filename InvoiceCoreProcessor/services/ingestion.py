# services/ingestion.py
import os
import shutil
import uuid
from datetime import datetime

def copy_file_to_uploads(source_path: str, uploads_dir: str) -> str:
    """
    Copies a file to the specified uploads directory with a unique name.
    Returns the new path of the copied file.
    """
    if not os.path.exists(source_path):
        raise FileNotFoundError(f"Source file not found: {source_path}")

    file_extension = os.path.splitext(source_path)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    storage_path = os.path.join(uploads_dir, unique_filename)

    shutil.copy(source_path, storage_path)
    return storage_path

def create_ingestion_metadata(user_id: str, original_path: str, storage_path: str) -> dict:
    """
    Creates a dictionary containing the metadata for the ingested file.
    """
    file_extension = os.path.splitext(original_path)[1]
    return {
        "invoice_id": str(uuid.uuid4()),
        "user_id": user_id,
        "original_path": original_path,
        "storage_path": storage_path,
        "file_extension": file_extension,
        "timestamp": datetime.utcnow()
    }
