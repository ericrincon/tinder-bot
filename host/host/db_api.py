import requests

from typing import Dict
from config import Config

from requests.exceptions import HTTPError


def create_user(user_info: Dict) -> bool:
    keys = {"name", "age", "bio", "images"}
    missing_keys = list(keys - set(user_info.keys()))

    if len(missing_keys):
        missing_keys = ", ".join(missing_keys)
        raise ValueError("Keys {} are missing!".format(missing_keys))

    try:
        response = requests.put(Config.APIURL + "/api/profiles/add", data=user_info)

        response.raise_for_status()
    except HTTPError as http_err:
        print("HTTP error occurred: {}".format(http_err))
    except Exception as err:
        print("Other error occurred: {}".format(err))
    else:
        return True
