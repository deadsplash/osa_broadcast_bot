from loguru import logger
import sys


def configure_logger():

    try:
        return configure_logger.logger
    except AttributeError:
        logger.remove()
        logger.add(sys.stdout, level="INFO", enqueue=True)
        configure_logger.logger = logger

        return configure_logger.logger
