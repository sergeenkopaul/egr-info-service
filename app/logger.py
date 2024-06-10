import logging
import sys

logger = logging.getLogger('root')

formatter = logging.Formatter(
    '%(asctime)s - %(levelname)s - %(filename)s - %(name)s - %(funcName)s - %(message)s'
)

stream_handler = logging.StreamHandler(sys.stdout)
file_handler = logging.FileHandler('app.log', mode='w')

stream_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

logger.handlers = [stream_handler, file_handler]

logger.setLevel(logging.DEBUG)

logging.getLogger('urllib3.connectionpool').setLevel(logging.WARNING)
logging.getLogger('selenium.webdriver.remote.remote_connection').setLevel(logging.WARNING)
logging.getLogger('selenium.webdriver.remote').setLevel(logging.WARNING)
logging.getLogger('selenium.webdriver.common.selenium_manager').setLevel(logging.WARNING)
logging.getLogger('selenium.webdriver.common.driver_finder').setLevel(logging.WARNING)
logging.getLogger('selenium.webdriver.common').setLevel(logging.WARNING)