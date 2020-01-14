import argparse

from host.host.scraper.webbot import AutoSwiper
from config import Config

from host import argparser_utils


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--browser", default="firefox")
    parser.add_argument("--debug", default="false", type=argparser_utils.boolean)
    parser.add_argument("--sleep-multiplier", default=1, type=argparser_utils.boolean)
    parser.add_argument("--push-to-server", default=0, type=argparser_utils.boolean)
    parser.add_argument("--location", type=argparser_utils.arg_location, default="")
    args = parser.parse_args()

    while True:
        auto_swiper = AutoSwiper(
            Config.email, Config.password,
            push_to_server=args.push_to_server,
            sleep_multiplier=args.sleep_multiplier, browser=args.browser, debug=args.debug)
        auto_swiper.start(args.location)


if __name__ == '__main__':
    main()
