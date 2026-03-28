import logging
from logging.handlers import RotatingFileHandler

from .config import LOG_DIR


def setup_logging() -> logging.Logger:
    """Configure shared logger for pipeline execution and monitoring."""
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("hospital_pipeline")
    logger.setLevel(logging.INFO)

    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )

    file_handler = RotatingFileHandler(
        LOG_DIR / "pipeline.log",
        maxBytes=1_000_000,
        backupCount=3,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    return logger
