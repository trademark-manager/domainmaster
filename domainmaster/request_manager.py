import aiohttp
import requests
from bs4 import BeautifulSoup
from typing import List


def do_get(url, access_token) -> requests.Response():

    bearer_headers = {"Content-Type": "application/json", "Accept": "application/json", "Authorization": "Bearer {0}".format(access_token)}
    #     async with aiohttp.ClientSession() as session:
    #         async with session.get('http://python.org') as response:

    #             print("Status:", response.status)
    #             print("Content-type:", response.headers['content-type'])

    #             html = await response.text()

    return requests.get(url, params=None, headers=bearer_headers, stream=True)


def get_brand_gtlds() -> List:
    gtlds = []
    url = "https://icannwiki.org/New_gTLD_Brand_Applications"
    req = requests.get(url)
    soup = BeautifulSoup(req.content, "html.parser")
    for tr in soup.find_all("tr"):
        td = tr.find("td")
        if td is not None:
            gtlds.append(td.find("a").get_text())

    return gtlds
