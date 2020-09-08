import logging, logging.handlers
import sys
import os


def set_handler_level_from_str(logger, level_name):
    try:
        logger.setLevel(level_name.upper())
    except:
        logger.setLevel(logging.CRITICAL)

def setup_handlers(path, filename):
    try:
        filehandler = logging.handlers.TimedRotatingFileHandler(
                filename=os.path.join(path, filename),
                when="W0"
                )
    except:
        filehandler = logging.handlers.TimedRotatingFileHandler(
                filename=os.path.join("/tmp", filename),
                when="W0"
                )

    termhandler = logging.StreamHandler(sys.stdout)

    formatter = logging.Formatter("%(asctime)s [%(levelname)s][%(name)s]:%(message)s",
            "%Y-%m-%d %H:%M:%S")
    filehandler.setFormatter(formatter)
    termhandler.setFormatter(formatter)

    return filehandler, termhandler

def setup_logging(config, log_name, handlers, logger=None):
    if logger is None:
        logger = logging.getLogger(log_name)

    try:
        cfg_console_log_level = config.get("GENERAL", "CONSOLE_LOG_LEVEL")
    except:
        cfg_console_log_level = "debug"

    try:
        cfg_file_log_level = config.get("GENERAL", "FILE_LOG_LEVEL")
    except:
        cfg_file_log_level = "Info"

    set_handler_level_from_str(handlers[0], cfg_file_log_level)
    set_handler_level_from_str(handlers[1], cfg_console_log_level)

    logger.setLevel("DEBUG")

    logger.addHandler(handlers[0])
    logger.addHandler(handlers[1])

    return logger
