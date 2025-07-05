import logging
import os
from datetime import datetime

# Setup a logger for the application
def setup_logger(log_level=logging.INFO):

    if not os.path.exists('logs'):
        os.makedirs('logs')

    # Create log filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = f'logs/scraper_{timestamp}.log'

    # Configure logging
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_filename, encoding='utf-8'),

        ]
    )

    # Create a logger for different components
    scraper_logger = logging.getLogger('scraper')
    crawler_logger = logging.getLogger('crawler')
    pdf_finder_logger = logging.getLogger('downloader')

    return log_filename


