import sys
from loguru import logger

def configure_logging():
    """
    Configures the application-wide logger using loguru.
    - Logs INFO level and above to app.log.
    - Logs ERROR level and above to error.log.
    - Also logs to the console.
    """
    logger.remove() # Remove default handler

    # Console logger
    logger.add(sys.stderr, level="INFO")

    # File loggers
    logger.add("app.log", level="INFO", rotation="10 MB", retention="7 days", backtrace=True, diagnose=True)
    logger.add("error.log", level="ERROR", rotation="10 MB", retention="7 days", backtrace=True, diagnose=True)

    logger.info("Logging configured.")

# Configure logging on import
configure_logging()
