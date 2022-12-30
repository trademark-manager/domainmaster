import logging
import logging.config
from uvicorn.config import LOGGING_CONFIG

LOGGER_NAME = "domainmaster"


def get_log_config():
    additional_loggers = {
        LOGGER_NAME: {"handlers": ["default"], "level": "DEBUG", "propagate": True},
    }

    log_config = LOGGING_CONFIG
    log_config["loggers"][LOGGER_NAME] = additional_loggers[LOGGER_NAME]
    return log_config


logger = logging.getLogger(LOGGER_NAME)
