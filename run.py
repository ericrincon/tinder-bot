import argparse
import logging

from host.host.scraper.webbot import AutoSwiper
from host.host.config import Config

from host import argparser_utils

logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
file_handler = logging.FileHandler('errors.log')
formatter = logging.Formatter(
    '%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
handler.setFormatter(formatter)
file_handler.setLevel(logging.DEBUG)
logger.addHandler(handler)
logger.addHandler(file_handler)
logger.setLevel(logging.ERROR)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--browser", default="firefox")
    parser.add_argument("--debug", default=False, type=argparser_utils.boolean)
    parser.add_argument("--sleep-multiplier", default=True, type=argparser_utils.boolean)
    parser.add_argument("--push-to-server", default=False, type=argparser_utils.boolean)
    parser.add_argument("--location", type=argparser_utils.arg_location, default="")
    parser.add_argument("--virtual-display", default=False, type=argparser_utils.boolean)
    args = parser.parse_args()

    def start():
        while True:
            auto_swiper = AutoSwiper(
                email=Config.EMAIL,
                password=Config.PASSWORD,
                push_to_server=args.push_to_server,
                sleep_multiplier=args.sleep_multiplier, browser=args.browser, debug=args.debug)
            auto_swiper.start(args.location)

    if args.virtual_display:
        import pyvirtualdisplay

        with pyvirtualdisplay.Display(visible=False, size=(2560, 1440)):
            start()
    else:
        start()


if __name__ == '__main__':
    main()
