from functools import lru_cache
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

# This will resolve to the `InvoiceCoreProcessor` directory
BASE_DIR = Path(__file__).resolve().parents[1]

class Settings(BaseSettings):
    """
    Application settings, loaded automatically from an .env file
    and environment variables by pydantic-settings.
    """
    # Pydantic-settings configuration
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Define the application settings
    POSTGRES_URI: str
    MONGO_URI: str
    MONGO_DB_NAME: str
    A2A_REGISTRY_URL: str
    LLM_API_KEY: str
    OCR_TESSERACT_PATH: str
    ENV: str = "dev"

@lru_cache()
def get_settings() -> Settings:
    """
    Returns the application settings.
    The lru_cache decorator ensures that the settings are loaded only once.
    """
    return Settings()
