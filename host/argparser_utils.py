from typing import Dict
from host.host.utils.location import get_location


def boolean(arg: str) -> bool:
    arg = str(arg)

    arg = arg.lower()

    if arg in ("y", "t", "yes", "1", "true"):
        return True
    else:
        return False


def arg_location(arg: str) -> Dict[str, str]:
    if arg == "":
        return get_location()
    else:
        info = arg.split(",")
        keys = ["city", "state", "country"]

        location = dict(map(lambda x: (x[0], x[1].strip()), zip(keys, info)))

        return location
