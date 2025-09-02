import logging

from src.utils.file_utils import ensure_directory_exists
from src.config.app_settings import LOG_DIR, LOG_FILE


def setup_logger(name, log_file=LOG_FILE, level='INFO'):
    """Set up a logger with file and console handlers"""
    ensure_directory_exists(LOG_DIR)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    # Avoid duplicate handlers
    if logger.handlers:
        return logger
    
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger

