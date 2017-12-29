import argparse

from tinder.scraper.scraper import AutoSwiper
from tinder.config import Config

def main():
    parser = argparse.ArgumentParser()

    args = parser.parse_args()

    auto_swiper = AutoSwiper(Config.email, Config.password)
    auto_swiper.start()


if __name__ == '__main__':
    main()