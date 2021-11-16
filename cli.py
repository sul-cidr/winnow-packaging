#!/usr/bin/env python3

""" HTTP server and launcher for Winnow """

import argparse
import logging
import os

import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles


PORT = 8001

BUNDLE_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), "www-data")

app = FastAPI()


@app.get("/get_collections")
def get_collections():
    return {"Hello": "World"}


app.mount("/", StaticFiles(directory=BUNDLE_DIR, html=True), name="static")


def main():
    """ Command-line entry-point. """

    parser = argparse.ArgumentParser(description="Description: {}".format(__file__))

    parser.add_argument(
        "-v", "--verbose", action="store_true", default=False, help="Increase verbosity"
    )

    args = parser.parse_args()

    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=log_level, format="%(message)s")

    uvicorn.run(app)


if __name__ == "__main__":
    main()
