import argparse

from host.host.scraper.webbot import AutoSwiper
from config import Config

from geopy.geocoders import Nominatim


def get_location(location_query):
    geolocator = Nominatim()

    return geolocator.geocode(location_query)


def boolean(arg):
    arg = str(arg)

    arg = arg.lower()

    if arg in ("y", "t", "yes", "1", "true"):
        return True
    else:
        return False


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--browser", default="firefox")
    parser.add_argument("--debug", default="false", type=boolean)
    args = parser.parse_args()

    while True:
        auto_swiper = AutoSwiper(Config.email, Config.password, browser=args.browser)
        auto_swiper.start()


if __name__ == '__main__':
    main()
