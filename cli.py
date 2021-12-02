#!/usr/bin/env python3

""" HTTP server and launcher for Winnow """

import argparse
import logging
import sys
from importlib import import_module
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
DEV_STORAGE_PATH = Path(__file__).parent.absolute()

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


def is_bundled():
    return getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS")


def dev():
    return create_app(SPA_PATH, DEV_STORAGE_PATH, is_bundled(), debug=True)


def main():
    """Command-line entry-point."""

    parser = argparse.ArgumentParser(description="Description: {}".format(__file__))

    parser.add_argument(
        "--dev",
        action="store_true",
        default=False,
        help="Launch application in development mode",
    )

    parser.add_argument(
        "--tool-script",
        action="store",
        default=False,
        help="Execute Winnow's tool_script.py and pass it the provided JSON payload",
    )

    args = parser.parse_args()

    if args.tool_script:
        # Flush the sys.stdout buffer on newlines
        #  (a suitable alternative here for PYTHONUNBUFFERED or `-u` etc.)
        sys.stdout.reconfigure(line_buffering=True)

        # tool_script.py looks for its configuration at `sys.argv[1]`, so we need
        #  to rewrite sys.argv here
        sys.argv = [sys.executable, args.tool_script]

        import_module(".tool_script", "winnow").main()
        raise SystemExit

    logger = logging.getLogger("logger")

    if args.dev:
        logger.setLevel(logging.DEBUG)
        logger.info(
            f"Starting application IN DEVELOPMENT MODE on https://localhost:{PORT}"
        )
        logger.info(f"App storage path: {DEV_STORAGE_PATH}")

        uvicorn.run(
            f"{Path(__file__).stem}:dev",
            factory=True,
            port=PORT,
            log_level="debug",
            reload=True,
        )
        raise SystemExit

    storage_path = Path(user_data_dir(APP_NAME, APP_AUTHOR))
    storage_path.mkdir(parents=True, exist_ok=True)

    logger.info(f"Starting application on https://localhost:{PORT}")
    logger.info(f"App storage path: {storage_path}")

    app = create_app(SPA_PATH, storage_path, is_bundled())

    uvicorn.run(app, port=PORT, log_level="warning")


if __name__ == "__main__":
    main()
