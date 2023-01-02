from fastapi import APIRouter, Query
from domainmaster.dependencies import master
from domainmaster.log_manager import logger

router = APIRouter()


@router.get("/")
def home():
    return {"msg": "DomainMaster Ready"}


@router.get("/tlds")
async def get_tlds():
    logger.debug("Downloading TLDs")
    return await master.get_tlds()


@router.get("/zone-urls")
async def get_zone_urls():
    logger.debug("Getting Zone URLs")
    return await master.update_zone_urls()


@router.get("/zones")
async def get_zones(
    domains: list[str] | None = Query(default=None),
    filters: list[str] | None = Query(default=None),
):
    return await master.get_zones_from_domains(domains, filters)


@router.get("/queue")
async def get_queue():
    return await master.get_queue()


@router.get("/keys")
async def get_keys():
    return await master.get_keys()


@router.delete("/queue")
async def reset_queue():
    jobs = await master.reset_queue()
    return {"msg": f"Deleted {jobs} jobs from queue"}
