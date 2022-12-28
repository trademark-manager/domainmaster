from domainmaster.config import Settings
from domainmaster.domain_master import DomainMaster
from domainmaster.log_manager import logger
from functools import lru_cache
import json


@lru_cache()
def get_settings():
    with open("config.json") as f:
        config_data = json.load(f)
        return Settings(**config_data)


def get_domain_master(config: Settings) -> DomainMaster:
    logger.info("Creating DomainMaster instance")
    return DomainMaster(
        credentials={
            "username": config.icann_account_username,
            "password": config.icann_account_password,
            "authen_base_url": config.authentication_base_url,
        },
        czds_base_url=config.czds_base_url,
        working_directory=config.working_directory,
    )


config = get_settings()
master = get_domain_master(config)
