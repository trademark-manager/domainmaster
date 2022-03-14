import json
import sys
import os
from cgi import parse_header
import datetime
import asyncio
from typing import List, Dict
import pandas

from domainmaster.log_manager import logger
from domainmaster.authentication_manager import authenticate
from domainmaster.request_manager import get, async_get


class DomainMaster:
    def __init__(self, credentials: Dict, czds_base_url: str, working_directory: str):
        self.credentials = credentials
        self.czds_base_url = czds_base_url
        self.working_directory = working_directory
        self.access_token = authenticate(self.credentials["username"], self.credentials["password"], self.credentials["authen_base_url"])

    def update_authentication(self):
        try:
            self.access_token = authenticate(self.credentials["username"], self.credentials["password"], self.credentials["authen_base_url"])
        except Exception:
            logger.exception("Authentication failde")

    def write_zone_links(self, zones: List):
        with open(f"{self.working_directory}/zones.txt", "w") as zones_file:
            json.dump(zones, zones_file, indent=4, sort_keys=True)

    def get_zones(self) -> List:
        links_url = f"{self.czds_base_url}/czds/downloads/links"
        links_response = get(links_url, self.access_token)

        status_code = links_response.status_code

        if status_code == 200:
            zone_links = links_response.json()
            logger.debug(f"Zone files to be downloaded is {len(zone_links)}")
            return [z.rsplit("/", 1)[-1].split(".")[0] for z in zone_links]
        elif status_code == 401:
            logger.info(f"The access_token has been expired. Re-authenticate user {self.credentials['username']}")
            self.authenticate()
            return self.get_zone_links()
        else:
            raise Exception("Failed to get zone links from {0} with error code {1}\n".format(links_url, status_code))

    def download_one_zone(self, url: str, output_directory: str) -> str:
        logger.debug(f"Downloading zone file from {url}")

        filename = url.rsplit("/", 1)[-1].rsplit(".")[-2] + ".txt.gz"
        path = "{0}/{1}".format(output_directory, filename)

        download_zone_response = get(url, self.access_token)
        status_code = download_zone_response.status_code

        if status_code == 200:
            with open(path, "wb") as f:
                for chunk in download_zone_response.iter_content(1024):
                    f.write(chunk)

            logger.debug(f"Completed downloading zone to file {path}")
            return filename[:-7]

        elif status_code == 401:
            logger.info(f"The access_token has been expired. Re-authenticate user {self.credentials['username']}")
            authenticate()
            return self.download_one_zone(url, output_directory)
        elif status_code == 404:
            logger.error("No zone file found for {0}".format(url))
            return None
        else:
            logger.error("Failed to download zone from {0} with code {1}\n".format(url, status_code))
            return None

    async def download_zones_async(self, urls: List, output_directory: str) -> str:
        loop = asyncio.get_event_loop()
        functions = [async_get(url, self.access_token, output_directory) for url in urls]

        results = await asyncio.gather(*functions)
        self.downloaded_zones = results
        return results

    def update_tlds(self, root_zone: str):
        root_zone_url = "https://data.iana.org/TLD/tlds-alpha-by-domain.txt"
        response = get(root_zone_url)
        response.raise_for_status()
        with open(root_zone, "wb") as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)

    def get_tlds(self) -> List:
        generic_zones, country_zones = [], []
        root_zone = f"{self.working_directory}/root.zone"
        if not os.path.isfile(root_zone):
            self.update_tlds(root_zone)
        with open(root_zone, "r") as f:
            zone_list = f.readlines()

        for zone in zone_list[1:]:
            if len(zone) == 2:
                country_zones.append(zone)
            else:
                generic_zones.append(zone)

        return {"generic": generic_zones, "country": country_zones}

    # Function definition for downloading all the zone files
    def download_zone_files(self, zones_to_download: List, parallel: bool = False) -> List:
        base_uri = "https://czds-api.icann.org/czds/downloads"
        # The zone files will be saved in a sub-directory
        output_directory = f"{self.working_directory}/zonefiles"
        downloaded_zone = []

        if not os.path.exists(output_directory):
            os.makedirs(output_directory)

        if parallel:
            urls = [f"{base_uri}/{zone}.zone" for zone in zones_to_download]
            asyncio.run(self.download_zones_async(urls, output_directory))
            return self.downloaded_zones
        # Download the zone files one by one
        for zone in zones_to_download:
            link = f"{base_uri}/{zone}.zone"
            downloaded_zone.append(self.download_one_zone(link, output_directory))
        return downloaded_zone
