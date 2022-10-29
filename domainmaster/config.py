from jsonschema import validate
import json
import os
import logging
from domainmaster.log_manager import logger
from typing import Dict

schema = {
    "type": "object",
    "properties": {
        "icann.account.username": {"type": "string"},
        "icann.account.password": {"type": "string"},
        "authentication.base.url": {"type": "string"},
        "czds.base.url": {"type": "string"},
        "debug": {"type": "boolean"},
        "working.directory": {"type": "string"},
        "zones.to.download": {"type": "array"},
    },
}


def load_config() -> Dict[str, str]:
    try:
        config = {}
        if "CZDS_CONFIG" in os.environ:
            config_data = os.environ["CZDS_CONFIG"]
            config = json.loads(config_data)
        else:
            with open("config.json", "r") as config_file:
                config = json.load(config_file)
    except Exception:
        logger.exception("Error loading config.json file.\n")

    if config.get("debug"):
        logger.setLevel(logging.DEBUG)
    validate(instance=config, schema=schema)

    return config
