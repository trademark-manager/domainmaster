from domainmaster.log_manager import logger
from domainmaster.authentication_manager import authenticate
from domainmaster.config import load_config
from domainmaster.main import DomainMaster
import datetime
import subprocess
import json
import click


@click.command()
@click.option("--domains", "-d", multiple=True, help="Only download this domain")
@click.option("--filters", "-f", multiple=True, help="Do not download this domain")
def main(domains, filters):
    config = load_config()

    username = config["icann.account.username"]
    password = config["icann.account.password"]
    authen_base_url = config["authentication.base.url"]
    czds_base_url = config["czds.base.url"]
    working_directory = config.get("working.directory", ".")
    filter_domains = filters

    try:
        master = DomainMaster(
            credentials={"username": username, "password": password, "authen_base_url": authen_base_url},
            czds_base_url=czds_base_url,
            working_directory=working_directory,
        )

        # tlds = master.get_tlds()
        zones = master.get_zones()
        master.write_zone_links(zones)
        zones_to_download = [zone for zone in zones if zone in domains] if domains else zones
        zones_to_download = [zone for zone in zones_to_download if zone not in filter_domains] if filter_domains else zones_to_download

        downloaded_zones = master.download_zone_files(zones_to_download, parallel=True)

        for zone in downloaded_zones:
            z = f"zcat {working_directory}/zonefiles/{zone}.txt.gz | cut -f1 | uniq > {working_directory}/zonefiles/{zone}.txt"
            out = subprocess.run(z, check=True, capture_output=True, shell=True)
            logger.info(out)
    except Exception:
        logger.exception("could not get zone links")
