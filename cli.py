#!/usr/bin/env python3

""" HTTP server and launcher for Winnow """

import argparse
import logging
import os
from pathlib import Path

import uvicorn

from backend import create_app

PORT = 8001
STATIC_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), "www-data")


def dev():
    return create_app(STATIC_PATH)


def main():
    """Command-line entry-point."""

    parser = argparse.ArgumentParser(description="Description: {}".format(__file__))

    parser.add_argument(
        "--dev",
        action="store_true",
        default=False,
        help="Launch application in development mode",
    )

    args = parser.parse_args()

    log_level = logging.DEBUG if args.dev else logging.INFO
    logging.basicConfig(level=log_level, format="%(message)s")

    if args.dev:
        logging.info(
            f"Starting application IN DEVELOPMENT MODE on https://localhost:{PORT}"
        )
        uvicorn.run(
            f"{Path(__file__).stem}:dev",
            factory=True,
            port=PORT,
            log_level="debug",
            reload=True,
        )
        raise SystemExit

    logging.info(f"Starting application on https://localhost:{PORT}")
    app = create_app(STATIC_PATH)

    uvicorn.run(app, port=PORT, log_level="warning")


if __name__ == "__main__":
    main()
