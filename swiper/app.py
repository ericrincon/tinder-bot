import argparse
from swiper import app


def main():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("--host", default="0.0.0.0")
    arg_parser.add_argument("--port", default=5000, type=int)
    arg_parser.add_argument("--debug", default=1, type=int)
    args = arg_parser.parse_args()

    app.run(debug=args.debug == 1, host=args.host,  port=args.port)


if __name__ == '__main__':
    main()
