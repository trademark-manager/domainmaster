import os
import datetime
import aiohttp
import aiofiles
import requests
from domainmaster.log_manager import logger
from arq.connections import ArqRedis
from arq.jobs import Job


class RequestManager:
    def __init__(self, access_token: str, zones_directory: str):
        self.access_token = access_token
        self.bearer_headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": "Bearer {0}".format(access_token),
        }
        self.zones_directory = zones_directory

    def get(self, url: str) -> requests.Response:
        return requests.get(url, params=None, headers=self.bearer_headers, stream=True)

    async def async_get(self, url: str, file):
        logger.debug(f"Downloading {url}")
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.bearer_headers, timeout=300) as response:
                assert response.status == 200
                async for data in response.content.iter_chunked(1024):
                    await file.write(data)

    async def download_async(self, url: str) -> str:
        filename = url.rsplit("/", 1)[-1].rsplit(".")[-2]
        path = f"{self.zones_directory}/{filename}.txt.gz"

        if self.local_file_valid(url, path):
            return filename

        async with aiofiles.open(path, "wb") as f:
            await self.async_get(url, f)

        return filename

    async def queue_zones_download(self, url: str, queue: ArqRedis) -> Job | None:
        return await queue.enqueue_job("download_async", url)

    def local_file_valid(self, url: str, dest_file: str) -> bool:
        """
        Checks local file timestamp aginst Last-Modified Header
        :param url: url to check Last-Modified header
        :param dest_file: local filename to timestamp
        :return: True if localtimestamp <= remote if url_date newer 'bigger timestamp' -> download
        """
        r = requests.head(url, headers=self.bearer_headers)
        r.raise_for_status()

        if not os.path.isfile(dest_file):
            return False
        if "Last-Modified" not in r.headers:
            return False
        url_date = datetime.datetime.strptime(r.headers["Last-Modified"], "%a, %d %b %Y %H:%M:%S GMT")
        file_date = datetime.datetime.utcfromtimestamp(os.path.getmtime(dest_file))
        if url_date > file_date:
            return False
        logger.debug(f"skipping: {url} URL_DATE: {url_date} FILE_DATE: {file_date}")
        return True
