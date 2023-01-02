import json
import os
import asyncio
from typing import Dict
import subprocess
import requests
from arq.connections import ArqRedis

from domainmaster.log_manager import logger
from domainmaster.authentication_manager import authenticate
from domainmaster.request_manager import RequestManager


class DomainMaster:
    def __init__(self, credentials: Dict, czds_base_url: str, working_directory: str):
        self.credentials = credentials
        self.czds_base_url = czds_base_url
        self.working_directory = working_directory
        self.access_token = authenticate(self.credentials["username"], self.credentials["password"], self.credentials["authen_base_url"])
        self.zones_directory = f"{self.working_directory}/zones"
        self.request_manager = RequestManager(self.access_token, self.zones_directory)
        self.zone_urls = []
        self.redis = None

    def setup(self, redis: ArqRedis | None):
        self.setup_directories()
        self.zone_urls = self.get_zone_links()
        self.redis = redis

    def setup_directories(self):
        if not os.path.exists(self.working_directory):
            os.mkdir(self.working_directory)
        if not os.path.exists(self.zones_directory):
            os.mkdir(self.zones_directory)

    def update_authentication(self):
        try:
            self.access_token = authenticate(self.credentials["username"], self.credentials["password"], self.credentials["authen_base_url"])
        except Exception:
            logger.exception("Authentication failde")

    async def write_zone_links(self, zones: list):
        with open(f"{self.working_directory}/zones.txt", "w") as zones_file:
            json.dump(zones, zones_file, indent=4, sort_keys=True)

    def get_zone_links(self) -> list[str]:
        links_url = f"{self.czds_base_url}/czds/downloads/links"
        links_response = self.request_manager.get(links_url)

        status_code = links_response.status_code

        if status_code == 200:
            zone_links = links_response.json()
            logger.debug(f"Zone files to be downloaded is {len(zone_links)}")
            return [z.rsplit("/", 1)[-1].split(".")[0] for z in zone_links]
        elif status_code == 401:
            logger.info(f"The access_token has been expired. Re-authenticate user {self.credentials['username']}")
            self.update_authentication()
            return self.get_zone_links()

        raise Exception("Failed to get zone links from {0} with error code {1}\n".format(links_url, status_code))

    async def process_zones(self, zones: list[str]):
        for zone in zones:
            z = f"zcat {self.working_directory}/zonefiles/{zone}.txt.gz | cut -f1 | uniq > {self.working_directory}/zonefiles/{zone}.txt"
            out = subprocess.run(z, check=True, capture_output=True, shell=True)
            logger.info(out)

    async def update_zone_urls(self) -> list[str]:
        self.zone_urls = self.get_zone_links()
        asyncio.create_task(self.write_zone_links(self.zone_urls))
        return self.zone_urls

    async def filter_zones(self, domains: list[str] | None = None, filter_domains: list[str] | None = None) -> list[str]:
        zones_to_download = [zone for zone in self.zone_urls if zone in domains] if domains else self.zone_urls
        zones_to_download = [zone for zone in zones_to_download if zone not in filter_domains] if filter_domains else zones_to_download
        return zones_to_download

    async def get_zones_from_domains(self, domains: list[str] | None = None, filter_domains: list[str] | None = None) -> list[str]:
        zones_to_download = await self.filter_zones(domains, filter_domains)

        urls = await self.get_urls_from_zones(zones_to_download)
        if self.redis:
            return await self.queue_zones_download(urls)

        return await self.download_zones_async(urls)

    async def queue_zones_download(self, urls: list) -> list[str]:
        jobs = []
        if self.redis is not None:
            for url in urls:
                job = await self.request_manager.queue_zones_download(url, self.redis)
                if job:
                    jobs.append(job.job_id)
        return jobs

    async def download_zones_async(self, urls: list) -> list:
        functions = [self.request_manager.download_async(url) for url in urls]
        results = [await asyncio.gather(*functions)]
        self.downloaded_zones = results
        return results

    async def update_root_zone(self, root_zone: str):
        root_zone_url = "https://data.iana.org/TLD/tlds-alpha-by-domain.txt"
        response = requests.get(root_zone_url)
        response.raise_for_status()
        with open(root_zone, "wb") as f:
            for line in response.iter_lines():
                f.write(line.split()[0])

    async def get_tlds(self) -> Dict[str, list]:
        generic_zones, country_zones = [], []
        root_zone = f"{self.working_directory}/root.zone"
        if not os.path.isfile(root_zone):
            await self.update_root_zone(root_zone)
        with open(root_zone, "r") as f:
            zone_list = f.read().splitlines()

        for zone in zone_list[1:]:
            if len(zone) == 2:
                country_zones.append(zone)
            else:
                generic_zones.append(zone)

        return {"generic": generic_zones, "country": country_zones}

    # Function definition for downloading all the zone files
    async def get_urls_from_zones(self, zones_to_download: list) -> list:
        base_uri = f"{self.czds_base_url}/czds/downloads"
        return [f"{base_uri}/{zone}.zone" for zone in zones_to_download]
