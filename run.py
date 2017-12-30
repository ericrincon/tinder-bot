import argparse

from tinder.scraper.webbot import AutoSwiper
from tinder.config import Config

from geopy.geocoders import Nominatim

def get_locatino(location_query):
    geolocator = Nominatim()

    return geolocator.geocode(location_query)
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--location')
    args = parser.parse_args()

    location = args.location

    if location:
        location = get_locatino(location)

    auto_swiper = AutoSwiper(Config.email, Config.password, location)
    auto_swiper.start()


if __name__ == '__main__':
    main()