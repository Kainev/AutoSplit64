# AutoSplit64
#
# Copyright (C) 2025 Kainev
#
# This project is currently not open source and is under active development.
# You may view the code, but it is not licensed for distribution, modification, or use at this time.
#
# For more information see https://github.com/Kainev/AutoSplit64?tab=readme#license

import os
import queue

import logging
import logging.config
from logging.handlers import RotatingFileHandler, QueueHandler, QueueListener


LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_FILE = os.getenv("LOG_FILE", "application.log")

MAX_BYTES = 5 * 1024 * 1024
BACKUP_COUNT = 3

log_queue = queue.Queue()


file_handler = RotatingFileHandler(
    filename=LOG_FILE,
    maxBytes=MAX_BYTES,
    backupCount=BACKUP_COUNT,
    encoding='utf-8'
)
file_handler.setLevel(LOG_LEVEL)
file_format = logging.Formatter(
    '%(asctime)s - %(name)s - [%(levelname)s] - %(message)s'
)
file_handler.setFormatter(file_format)


console_handler = logging.StreamHandler()
console_handler.setLevel(LOG_LEVEL)
console_handler.setFormatter(file_format)


def configure_logging():
    """
    Configures an asynchronous logging system
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(LOG_LEVEL)

    root_logger.handlers = []

    queue_handler = QueueHandler(log_queue)
    queue_handler.setLevel(LOG_LEVEL)
    root_logger.addHandler(queue_handler)

    listener = QueueListener(log_queue, file_handler, console_handler, respect_handler_level=True)
    listener.start()

def get_logger(name: str = None) -> logging.Logger:
    """Retrieve a module-level logger, or the root if None is given."""
    return logging.getLogger(name)
