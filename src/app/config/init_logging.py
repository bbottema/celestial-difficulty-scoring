import logging.config
import os
from pathlib import Path


def configure_logging(file__):
    logging.config.fileConfig(Path(os.path.dirname(file__)) / 'logging.ini', disable_existing_loggers=False)
    logging.getLogger(__name__).info("Logging configuration loaded")
