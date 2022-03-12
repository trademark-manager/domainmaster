from domainmaster.log_manager import logger
from domainmaster.authentication_manager import authenticate
from domainmaster.request_manager import do_get
from domainmaster.config import load_config
from domainmaster.download import download_zone_files, get_zone_links, set_access_token
import datetime


def main():
    config = load_config()
    logger.debug(config)

    username = config["icann.account.username"]
    password = config["icann.account.password"]
    authen_base_url = config["authentication.base.url"]
    czds_base_url = config["czds.base.url"]
    zones_to_download = config.get("zones.to.download", [])
    working_directory = config.get("working.directory", ".")
    zone_links = []

    try:
        access_token = authenticate(username, password, authen_base_url)
        set_access_token(access_token)
    except:
        logger.fatal(f"Authentictaion for username: {username} failed")

    try:
        zone_links = get_zone_links(czds_base_url)
    except Exception:
        logger.exception("could not get zone links")

    start_time = datetime.datetime.now()
    download_zone_files(zone_links, working_directory, zones_to_download)
    end_time = datetime.datetime.now()

    logger.info("{0}: DONE DONE. Completed downloading all zone files. Time spent: {1}".format(str(end_time), (end_time - start_time)))
