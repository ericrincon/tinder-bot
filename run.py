import argparse

from host.host.scraper.webbot import AutoSwiper
from config import Config

from geopy.geocoders import Nominatim


def get_location(location_query):
    geolocator = Nominatim()

    return geolocator.geocode(location_query)

def main():
    parser = argparse.ArgumentParser()
    args = parser.parse_args()

    while True:
        auto_swiper = AutoSwiper(Config.email, Config.password)
        auto_swiper.start()


if __name__ == '__main__':
    main()
