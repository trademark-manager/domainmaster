from domainmaster.dependencies import master, config
from domainmaster.domain_master import DomainMaster
from arq.connections import RedisSettings


async def download_async(ctx, url):
    master: DomainMaster = ctx["master"]
    return await master.request_manager.download_async(url)


async def startup(ctx):
    ctx["master"] = master


class WorkerSettings:
    functions = [download_async]
    on_startup = startup
    redis_settings = RedisSettings(host=config.redis_host)
