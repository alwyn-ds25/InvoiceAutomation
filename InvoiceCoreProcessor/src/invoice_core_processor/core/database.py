import psycopg2
import motor.motor_asyncio
from functools import lru_cache

from invoice_core_processor.config.settings import get_settings

@lru_cache()
def get_db_settings():
    """Cached function to get database settings."""
    return get_settings()

def get_postgres_connection():
    """Establishes and returns a connection to the PostgreSQL database."""
    settings = get_db_settings()
    conn = psycopg2.connect(settings.POSTGRES_URI)
    return conn

def get_mongo_client():
    """Establishes and returns an asynchronous client connection to MongoDB."""
    settings = get_db_settings()
    client = motor.motor_asyncio.AsyncIOMotorClient(settings.MONGO_URI)
    return client

def get_mongo_db():
    """Returns the MongoDB database instance."""
    settings = get_db_settings()
    client = get_mongo_client()
    return client[settings.MONGO_DB_NAME]
