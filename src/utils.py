import logging
import sys
logger_name = "console"


def get_push_date():
    from time import time, strftime, localtime
    fmt = '%Y-%m-%d %H:%M:%S'
    return strftime(fmt, localtime(time()))


def get_logger() -> logging.Logger:
    FMT = logging.Formatter("%(asctime)s %(levelname)s %(filename)s:%(lineno)s %(message)s")
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(FMT)
    logging.getLogger(logger_name).addHandler(console_handler)
    logger =  logging.getLogger(logger_name)
    logger.setLevel(logging.INFO)
    # logger.info("hi")
    return logger


if __name__ == '__main__':
    logger = get_logger()
    logger.info("realtime_staked: %d", 123)