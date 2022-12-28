from fastapi import APIRouter, Query, BackgroundTasks
from domainmaster.domain_master import DomainMaster
from domainmaster.dependencies import master

router = APIRouter()


@router.get("/")
def home():
    return {"msg": "DomainMaster Ready"}


def download_zones(zones: list[str]):
    master.download_zones(zones)


@router.get("/zones")
def get_zones(
    background_tasks: BackgroundTasks,
    domains: list[str] | None = Query(default=None),
    filters: list[str] | None = Query(default=None),
):
    downloaded_zones = master.get_zones_from_domains(domains, filters)
    # background_tasks.add_task(download_zones, downloaded_zones)
