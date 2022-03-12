import json
import sys
import cgi
import os
import datetime

from domainmaster.log_manager import logger
from domainmaster.authentication_manager import authenticate
from domainmaster.request_manager import do_get

access_token = ""


def set_access_token(token: str):
    global access_token
    access_token = token


def get_zone_links(czds_base_url):
    global access_token

    links_url = f"{czds_base_url}/czds/downloads/links"
    links_response = do_get(links_url, access_token)

    status_code = links_response.status_code

    if status_code == 200:
        zone_links = links_response.json()
        logger.debug("{0}: The number of zone files to be downloaded is {1}".format(datetime.datetime.now(), len(zone_links)))
        return zone_links
    elif status_code == 401:
        logger.info("The access_token has been expired. Re-authenticate user {0}".format(username))
        access_token = authenticate(username, password, authen_base_url)
        get_zone_links(czds_base_url)
    else:
        raise Exception("Failed to get zone links from {0} with error code {1}\n".format(links_url, status_code))


def download_one_zone(url, output_directory):
    logger.debug("{0}: Downloading zone file from {1}".format(str(datetime.datetime.now()), url))

    global access_token
    download_zone_response = do_get(url, access_token)

    status_code = download_zone_response.status_code

    if status_code == 200:
        # Try to get the filename from the header
        _, option = cgi.parse_header(download_zone_response.headers["content-disposition"])
        filename = option.get("filename")

        # If could get a filename from the header, then makeup one like [tld].txt.gz
        if not filename:
            filename = url.rsplit("/", 1)[-1].rsplit(".")[-2] + ".txt.gz"

        # This is where the zone file will be saved
        path = "{0}/{1}".format(output_directory, filename)

        with open(path, "wb") as f:
            for chunk in download_zone_response.iter_content(1024):
                f.write(chunk)

        logger.debug("{0}: Completed downloading zone to file {1}".format(str(datetime.datetime.now()), path))

    elif status_code == 401:
        print("The access_token has been expired. Re-authenticate user {0}".format(username))
        access_token = authenticate(username, password, authen_base_url)
        download_one_zone(url, output_directory)
    elif status_code == 404:
        print("No zone file found for {0}".format(url))
    else:
        sys.stderr.write("Failed to download zone from {0} with code {1}\n".format(url, status_code))


# Function definition for downloading all the zone files
def download_zone_files(urls, working_directory, zones_to_download):
    base_uri = "https://czds-api.icann.org/czds/downloads"
    # The zone files will be saved in a sub-directory
    output_directory = f"{working_directory}/zonefiles"

    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # Download the zone files one by one
    for zone in zones_to_download:
        link = f"{base_uri}/{zone}.zone"
        if link in urls:
            download_one_zone(link, output_directory)
