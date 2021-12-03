#!/usr/bin/env python3

""" HTTP server and launcher for Winnow """

import argparse
import logging
import subprocess
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
    """Returns `True` if executed from within a PyInstaller bundle."""
    return getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS")


def dev():
    """Factory function to return a FastAPI app without needing to take arguments."""
    return create_app(SPA_PATH, DEV_STORAGE_PATH, is_bundled(), debug=True)


def main():
    """Command-line entry-point."""

    parser = argparse.ArgumentParser(description="Description: {}".format(__file__))

    parser.add_argument(
        "--no-launch-browser",
        action="store_true",
        default=False,
        help="Disable automatic opening of a browser tab/window",
    )

    parser.add_argument(
        "--dev",
        action="store_true",
        default=False,
        help="Launch application in development mode (not available on Windows)",
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
        if sys.platform == "win32":
            logger.fatal("Development mode not available on Windows")
            raise SystemError

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

    app_url = f"http://localhost:{PORT}"

    logger.info(f"Starting application on {app_url}")
    logger.info(f"App storage path: {storage_path}")

    app = create_app(SPA_PATH, storage_path, is_bundled())

    if sys.platform == "win32":
        # Although asyncio.ProactorEventLoop is the default on Python >= 3.8, Uvicorn
        #   uses asyncio.SelectorEventLoop which doesn't support subprocesses on Windows:
        #  (https://docs.python.org/3/library/asyncio-platforms.html#asyncio-windows-subprocess)
        # The solution here is to manually create a ProactorEventLoop and pass it to
        #  Uvicorn directly.
        import asyncio
        import os
        from uvicorn import Config, Server

        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        loop = asyncio.new_event_loop()
        config = Config(app, port=PORT, log_level="warning", loop=loop)
        server = Server(config)
        if not args.no_launch_browser:
            os.startfile(app_url)
        loop.run_until_complete(server.serve())
        raise SystemExit

    if not args.no_launch_browser:
        if sys.platform == "darwin":
            subprocess.Popen(["open", app_url])
        else:
            subprocess.Popen(["xdg-open", app_url])

    uvicorn.run(app, port=PORT, log_level="warning")


if __name__ == "__main__":
    main()
