import json
import requests
import sys
import datetime
from domainmaster.log_manager import logger


def authenticate(username: str, password: str, authen_base_url: str) -> str:
    authen_headers = {"Content-Type": "application/json", "Accept": "application/json"}

    credential = {"username": username, "password": password}

    authen_url = f"{authen_base_url}/api/authenticate"

    response = requests.post(authen_url, data=json.dumps(credential), headers=authen_headers)

    status_code = response.status_code

    # Return the access_token on status code 200. Otherwise, terminate the program.
    if status_code == 200:
        access_token = response.json()["accessToken"]
        logger.debug("{0}: Received access_token:".format(datetime.datetime.now()))
        return access_token
    elif status_code == 404:
        raise Exception(f"Invalid url {authen_url}")
    elif status_code == 401:
        raise Exception("Invalid username/password. Please reset your password via web")
    elif status_code == 500:
        raise Exception("Internal server error. Please try again later")
    else:
        raise Exception("Failed to authenticate user {0} with error code {1}".format(username, status_code))
