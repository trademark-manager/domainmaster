from domainmaster.config import Settings
from domainmaster.domain_master import DomainMaster
from domainmaster.log_manager import logger
from arq import create_pool
from arq.connections import RedisSettings, ArqRedis
from redis.exceptions import ConnectionError
from functools import lru_cache
import json
import os


@lru_cache()
def get_settings():
    config_data = {}
    if os.path.isfile("config.json"):
        with open("config.json", mode="r") as f:
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


async def get_queue_pool(config: Settings) -> ArqRedis | None:
    if config.redis_host:
        try:
            logger.info("Creating Redis pool")
            return await create_pool(RedisSettings(host=config.redis_host))
        except ConnectionError:
            logger.error("Redis connection error")
    return None


async def setup_redis():
    redis = await get_queue_pool(config)
    master.setup(redis)


config = get_settings()
master = get_domain_master(config)
