import json
import os
import asyncio
from typing import List, Dict
import subprocess

from domainmaster.log_manager import logger
from domainmaster.authentication_manager import authenticate
from domainmaster.request_manager import get, download_async


class DomainMaster:
    def __init__(self, credentials: Dict, czds_base_url: str, working_directory: str):
        self.credentials = credentials
        self.czds_base_url = czds_base_url
        self.working_directory = working_directory
        self.access_token = authenticate(self.credentials["username"], self.credentials["password"], self.credentials["authen_base_url"])

    def set_access_token(self):
        self.access_token = authenticate(self.credentials["username"], self.credentials["password"], self.credentials["authen_base_url"])

    def update_authentication(self):
        try:
            self.access_token = authenticate(self.credentials["username"], self.credentials["password"], self.credentials["authen_base_url"])
        except Exception:
            logger.exception("Authentication failde")

    def write_zone_links(self, zones: list):
        with open(f"{self.working_directory}/zones.txt", "w") as zones_file:
            json.dump(zones, zones_file, indent=4, sort_keys=True)

    def get_zones(self) -> list:
        links_url = f"{self.czds_base_url}/czds/downloads/links"
        links_response = get(links_url, self.access_token)

        status_code = links_response.status_code

        if status_code == 200:
            zone_links = links_response.json()
            logger.debug(f"Zone files to be downloaded is {len(zone_links)}")
            return [z.rsplit("/", 1)[-1].split(".")[0] for z in zone_links]
        elif status_code == 401:
            logger.info(f"The access_token has been expired. Re-authenticate user {self.credentials['username']}")
            self.set_access_token()
            return self.get_zones()

        raise Exception("Failed to get zone links from {0} with error code {1}\n".format(links_url, status_code))

    def download_zones(self, zones: list[str], parallel: bool = False):
        return
        for zone in zones:
            z = f"zcat {self.working_directory}/zonefiles/{zone}.txt.gz | cut -f1 | uniq > {self.working_directory}/zonefiles/{zone}.txt"
            out = subprocess.run(z, check=True, capture_output=True, shell=True)
            logger.info(out)

    def get_zones_from_domains(self, domains: list[str] | None = None, filter_domains: list[str] | None = None) -> list[str]:
        zones = self.get_zones()
        self.write_zone_links(zones)
        zones_to_download = [zone for zone in zones if zone in domains] if domains else zones
        zones_to_download = [zone for zone in zones_to_download if zone not in filter_domains] if filter_domains else zones_to_download

        return self.download_zone_files(zones_to_download, parallel=True)

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
            self.set_access_token()
            return self.download_one_zone(url, output_directory)
        elif status_code == 404:
            logger.error("No zone file found for {0}".format(url))
            return ""
        else:
            logger.error("Failed to download zone from {0} with code {1}\n".format(url, status_code))
            return ""

    async def download_zones_async(self, urls: List, output_directory: str) -> List:
        loop = asyncio.get_event_loop()

        def divide_chunks(l, n):
            for i in range(0, len(l), n):
                yield l[i : i + n]

        urlchuncks = divide_chunks(urls, 5)
        results = []
        for chunck in urlchuncks:
            functions = [download_async(url, self.access_token, output_directory) for url in chunck]
            results.append(await asyncio.gather(*functions))

        self.downloaded_zones = [item for sublist in results for item in sublist]
        return results

    def update_tlds(self, root_zone: str):
        root_zone_url = "https://data.iana.org/TLD/tlds-alpha-by-domain.txt"
        response = get(root_zone_url)
        response.raise_for_status()
        with open(root_zone, "wb") as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)

    def get_tlds(self) -> Dict[str, list]:
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
    def download_zone_files(self, zones_to_download: list, parallel: bool = False) -> list:
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
