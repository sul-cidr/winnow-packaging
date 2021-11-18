import json
import logging
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

logger = logging.getLogger("logger")

DATA_FILE = Path("./data/session.json")
COLLECTIONS_PATH = Path("./data/corpus-files")


def initialize_data():
    logger.info("Initializing data from session.json...")

    if DATA_FILE.is_file():
        data = json.load(DATA_FILE.open("r", encoding="utf8"))
    else:
        logger.warning(f"Data file at {DATA_FILE} not found -- creating empty file!")
        data = {"keyword-lists": {}, "collections": {}, "runs": {}}

    collections_dirs = []
    if COLLECTIONS_PATH.is_dir():
        collections_dirs = [_ for _ in COLLECTIONS_PATH.iterdir() if _.is_dir()]

    # Deletes any collections in the data JSON structure that don't appear
    # within our folder and prints a warning message.
    for collection_id in data["collections"]:
        if COLLECTIONS_PATH / collection_id not in collections_dirs:
            logger.warning(
                "WARNING: collection '%s' doesn't exist in '%s'. Please either add the "
                "files or delete the entry from '%s'.",
                collection_id,
                COLLECTIONS_PATH,
                DATA_FILE,
            )

    return data


def save_session_file(data):
    json.dump(data, DATA_FILE.open("w", encoding="utf8"), indent=2)


def create_app(static_path, debug=False):
    if debug:
        logger.setLevel("DEBUG")

    app = FastAPI()

    @app.get("/get_collections")
    def get_collections():
        return data["collections"]

    app.mount("/", StaticFiles(directory=static_path, html=True), name="static")

    data = initialize_data()

    return app
