#!/usr/bin/env python3

""" HTTP server and launcher for Winnow """

import argparse
import logging
from pathlib import Path

import uvicorn
from appdirs import user_data_dir

from backend import create_app

# Strings used for creating a user-specific data folder
#  (APP_AUTHOR only used on Windows)
APP_NAME = "Winnow"
APP_AUTHOR = "OHTAP"

PORT = 8001
SPA_PATH = Path(__file__).parent.absolute() / "winnow" / "www-data"
TOOL_SCRIPT_PATH = Path(__file__).parent.absolute() / "winnow" / "tool_script.py"

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
    logger = logging.getLogger("logger")
    logger.setLevel(logging.DEBUG)
    data_path = Path(__file__).parent.absolute() / "data"

    logger.info(f"Starting application IN DEVELOPMENT MODE on https://localhost:{PORT}")
    logger.info(f"User data path: {data_path}")

    return create_app(SPA_PATH, TOOL_SCRIPT_PATH, data_path, debug=True)


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

    if args.dev:
        uvicorn.run(
            f"{Path(__file__).stem}:dev",
            factory=True,
            port=PORT,
            log_level="debug",
            reload=True,
        )
        raise SystemExit

    logger = logging.getLogger("logger")
    data_path = Path(user_data_dir(APP_NAME, APP_AUTHOR))
    data_path.mkdir(parents=True, exist_ok=True)

    logger.info(f"Starting application on https://localhost:{PORT}")
    logger.info(f"User data path: {data_path}")

    app = create_app(SPA_PATH, TOOL_SCRIPT_PATH, data_path)

    uvicorn.run(app, port=PORT, log_level="warning")


if __name__ == "__main__":
    main()
