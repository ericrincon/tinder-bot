import geocoder

from typing import Dict


def get_location() -> Dict:
    location = geocoder.ip("me")

    return {"state": location.state, "city": location.city, "country": location.country}
