import json
import requests
import logging
from domainmaster.log_manager import logger


def authenticate(username: str, password: str, authen_base_url: str) -> str:
    authen_headers = {"Content-Type": "application/json", "Accept": "application/json"}
    credential = {"username": username, "password": password}
    authen_url = f"{authen_base_url}/api/authenticate"

    response = requests.post(authen_url, data=json.dumps(credential), headers=authen_headers)
    response.raise_for_status()
    logger.info(f"User {username} successfully authenticated")
    return response.json()["accessToken"]
