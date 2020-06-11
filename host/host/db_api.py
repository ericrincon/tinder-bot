import requests

import urllib.parse

from typing import Dict
from host.host.config import Config

from requests.exceptions import HTTPError


def create_user(user_info: Dict) -> bool:
    headers = {"content-type": "application/json"}

    keys = {"name", "age", "bio", "images", "city", "state", "country"}
    missing_keys = list(keys - set(user_info.keys()))
    url = urllib.parse.urljoin(Config.APIURL, "/api/profiles/add")

    if len(missing_keys):
        missing_keys = ", ".join(missing_keys)
        raise ValueError("Keys {} are missing!".format(missing_keys))

    try:
        response = requests.put(url, json=user_info, headers=headers)

        response.raise_for_status()
    except HTTPError as http_err:
        print("HTTP error occurred: {}".format(http_err))
    except Exception as err:
        print("Other error occurred: {}".format(err))
    else:
        return True
