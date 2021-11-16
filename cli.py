#!/usr/bin/env python3

""" HTTP server and launcher for Winnow """

import argparse
import logging
import os

import uvicorn

from backend import create_app

PORT = 8001
STATIC_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), "www-data")


def main():
    """Command-line entry-point."""

    parser = argparse.ArgumentParser(description="Description: {}".format(__file__))

    parser.add_argument(
        "-v", "--verbose", action="store_true", default=False, help="Increase verbosity"
    )

    args = parser.parse_args()

    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=log_level, format="%(message)s")

    app = create_app(STATIC_PATH)
    uvicorn.run(app)


if __name__ == "__main__":
    main()
