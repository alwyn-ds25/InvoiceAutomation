from functools import lru_cache
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

# This will resolve to the `InvoiceCoreProcessor` directory
BASE_DIR = Path(__file__).resolve().parents[1]

class Settings(BaseSettings):
    """
    Application settings, loaded automatically from an .env file
    and environment variables by pydantic-settings.
    """
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Core settings
    POSTGRES_URI: str
    MONGO_URI: str
    MONGO_DB_NAME: str
    A2A_REGISTRY_URL: str
    ENV: str = "dev"

    # LLM and OCR Service Settings
    LLM_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4"
    OPENAI_ENABLED: bool = True

    TYPHOON_OCR_API_KEY: Optional[str] = None
    TYPHOON_BASE_URL: str = "https://api.opentyphoon.ai/v1"
    TYPHOON_MODEL: str = "typhoon-ocr"
    TYPHOON_TASK_TYPE: str = "default"
    TYPHOON_MAX_TOKENS: int = 16000
    TYPHOON_TEMPERATURE: float = 0.1
    TYPHOON_TOP_P: float = 0.6

    GPT4_VISION_API_KEY: Optional[str] = None
    GPT4_VISION_MODEL: str = "gpt-4o"
    GPT4_VISION_MAX_TOKENS: int = 4000

    AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT: Optional[str] = None
    AZURE_DOCUMENT_INTELLIGENCE_KEY: Optional[str] = None

    TESSERACT_CMD_PATH: Optional[str] = None

    EASYOCR_LANGUAGES: str = "en"

    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-2.0-flash"


@lru_cache()
def get_settings() -> Settings:
    """
    Returns the application settings.
    """
    return Settings()
