import logging
import sys

def setup_logging() -> None:
    """
    Configures basic logging for the application.
    For an enterprise setup, this can be expanded to use structured JSON logging,
    Logstash formatters, or advanced external services (Sentry, ELK).
    """
    logging.basicConfig(
        stream=sys.stdout,
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    
    # Silence spammy third-party loggers if needed
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

logger = logging.getLogger("aryacrypt")
