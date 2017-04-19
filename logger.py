import logging
import os

ROOT_DIR = os.path.dirname(os.path.realpath(__file__))
LOG_FILE = ROOT_DIR + '/iva.log'
LOGGER_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logger = logging.getLogger('IVA')


def info(message):
    logger.info(message)


def error(message):
    logger.error(message)


def warning(message):
    logger.warning(message)


def configure_logger():
    formatter = create_logging_formatter()
    logger.setLevel(logging.DEBUG)
    add_file_handler(formatter)
    add_console_handler(formatter)


def create_logging_formatter():
    return logging.Formatter(LOGGER_FORMAT)


def add_file_handler(formatter):
    fh = logging.FileHandler(LOG_FILE)
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)
    logger.addHandler(fh)


def add_console_handler(formatter):
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(formatter)
    logger.addHandler(ch)


configure_logger()


