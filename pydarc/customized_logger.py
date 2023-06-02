from logging import getLogger as loggingGetLogger, Formatter, StreamHandler, DEBUG
import sys


def getLogger(name: str):
    logger = loggingGetLogger(name)
    logger.setLevel(DEBUG)
    log_handler = StreamHandler(sys.stdout)
    log_handler.setLevel(DEBUG)
    log_handler.setFormatter(
        Formatter(
            "[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s"
        )
    )
    logger.addHandler(log_handler)
    return logger
