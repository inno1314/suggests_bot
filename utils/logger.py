from logging import getLogger, Formatter, INFO
from logging.handlers import RotatingFileHandler

logger = getLogger(__name__)
file_logger = RotatingFileHandler("logs.txt", encoding='utf-8')
file_logger.setLevel(INFO)
file_logger.setFormatter(Formatter("%(asctime)s - %(message)s"))

logger.addHandler(file_logger)

