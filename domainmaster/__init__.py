from domainmaster.log_manager import logger
from domainmaster.authentication_manager import authenticate
from domainmaster.config import load_config
from domainmaster.download import download_zone_files, get_zone_links, set_access_token
import datetime
import subprocess
import json


def main():
    config = load_config()

    username = config["icann.account.username"]
    password = config["icann.account.password"]
    authen_base_url = config["authentication.base.url"]
    czds_base_url = config["czds.base.url"]
    zones_to_download = config.get("zones.to.download", [])
    working_directory = config.get("working.directory", ".")
    zones = []

    try:
        access_token = authenticate(username, password, authen_base_url)
        set_access_token(access_token)
    except:
        logger.fatal(f"Authentictaion for username: {username} failed")

    try:
        zone_links = get_zone_links(czds_base_url)
        zones = [z.rsplit("/", 1)[-1].split(".")[0] for z in zone_links]
        with open(f"{working_directory}/zones.txt", "w") as zones_file:
            json.dump(zones, zones_file, indent=4, sort_keys=True)
    except Exception:
        logger.exception("could not get zone links")

    start_time = datetime.datetime.now()
    downloaded_zones = download_zone_files(working_directory, zones)
    end_time = datetime.datetime.now()

    logger.info(f"{str(end_time)}: DONE Completed downloading {downloaded_zones}. Time spent: {(end_time - start_time)}")

    for zone in downloaded_zones:
        z = f"zcat {working_directory}/zonefiles/{zone}.txt.gz | cut -f1 | uniq > {working_directory}/zonefiles/{zone}.txt"
        out = subprocess.run(z, check=True, capture_output=True, shell=True)
        logger.info(out)
