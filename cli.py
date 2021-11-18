#!/usr/bin/env python3

""" HTTP server and launcher for Winnow """

import argparse
import logging
import os
from pathlib import Path

import uvicorn

from backend import create_app

PORT = 8001
SPA_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), "www-data")

log_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {"fmt": "%(message)s"},
    },
    "handlers": {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
        },
    },
    "loggers": {
        "logger": {"handlers": ["default"], "level": "INFO"},
    },
}

logging.config.dictConfig(log_config)


def dev():
    return create_app(SPA_PATH, debug=True)


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

    logger = logging.getLogger("logger")

    if args.dev:
        logger.setLevel(logging.DEBUG)
        logger.debug(
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

    logger.info(f"Starting application on https://localhost:{PORT}")
    app = create_app(SPA_PATH)

    uvicorn.run(app, port=PORT, log_level="warning")


if __name__ == "__main__":
    main()
