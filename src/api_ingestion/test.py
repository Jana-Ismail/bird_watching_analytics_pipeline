import os
from src.config.app_settings import LOG_FILE
from src.utils.logging_utils import setup_logger

log_name = os.path.basename(__file__)
logger = setup_logger(log_name, LOG_FILE, level='DEBUG')

def main():
    logger.debug('This is a test DEBUG message for logging setup')
    logger.info('This is a test INFO message for logging setup')

if __name__ == "__main__":
    main()