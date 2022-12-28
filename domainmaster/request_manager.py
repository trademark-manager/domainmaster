import os
import datetime
import aiohttp
import aiofiles
import requests
from typing import Dict
from domainmaster.log_manager import logger


def get(url: str, access_token: str = "") -> requests.Response:
    if access_token:
        bearer_headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": "Bearer {0}".format(access_token),
        }
        return requests.get(url, params=None, headers=bearer_headers, stream=True)
    return requests.get(url, stream=True)


async def async_get(url: str, bearer_headers: dict[str, str], file):
    logger.debug(f"Downloading {url}")

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=bearer_headers, timeout=300) as response:
            assert response.status == 200
            async for data in response.content.iter_chunked(1024):
                await file.write(data)


async def download_async(url: str, access_token: str, output_directory: str) -> str:
    filename = url.rsplit("/", 1)[-1].rsplit(".")[-2] + ".txt.gz"
    path = "{0}/{1}".format(output_directory, filename)
    bearer_headers = {"Content-Type": "application/json", "Accept": "application/json", "Authorization": "Bearer {0}".format(access_token)}

    if local_file_valid(url, path, bearer_headers):
        return filename[:-7]

    async with aiofiles.open(path, "wb") as f:
        await async_get(url, bearer_headers, f)

    return filename[:-7]


def local_file_valid(url: str, dest_file: str, headers: Dict) -> bool:
    """
    Checks local file timestamp aginst Last-Modified Header
    :param url: url to check Last-Modified header
    :param dest_file: local filename to timestamp
    :return: True if localtimestamp <= remote
    """
    r = requests.head(url, headers=headers)
    r.raise_for_status()

    if not os.path.isfile(dest_file):
        return False
    if "Last-Modified" not in r.headers:
        return False
    url_date = datetime.datetime.strptime(r.headers["Last-Modified"], "%a, %d %b %Y %H:%M:%S GMT")
    file_date = datetime.datetime.utcfromtimestamp(os.path.getmtime(dest_file))
    # Wenn url_date neuer 'größer timestamp' dann download
    if url_date > file_date:
        return False
    logger.debug(f"skipping: {url} URL_DATE: {url_date} FILE_DATE: {file_date}")
    return True
