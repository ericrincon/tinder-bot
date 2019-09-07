import argparse

from host.host.scraper.webbot import AutoSwiper
from config import Config

from geopy.geocoders import Nominatim

from host import argparser_utils


def get_location(location_query):
    geolocator = Nominatim()

    return geolocator.geocode(location_query)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--browser", default="firefox")
    parser.add_argument("--debug", default="false", type=argparser_utils.boolean)
    parser.add_argument("--sleep-multiplier", default=1, type=int)
    args = parser.parse_args()

    while True:
        auto_swiper = AutoSwiper(Config.email, Config.password,
                                 sleep_multiplier=args.sleep_multiplier, browser=args.browser, debug=args.debug)
        auto_swiper.start()


if __name__ == '__main__':
    main()
