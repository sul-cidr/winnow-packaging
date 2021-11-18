import json
import logging
import shutil
from pathlib import Path
from typing import List

from fastapi import FastAPI, Request, Form, File, UploadFile
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

    @app.post("/add_collection")
    async def add_collection(request: Request):
        request_payload = await request.json()
        collection_id = request_payload["id"]

        logger.info("Adding collection '%s'", collection_id)

        data["collections"][collection_id] = {
            "id": collection_id,
            "name": request_payload["name"],
            "collection-count": request_payload["collection_count"],
            "shortened-name": request_payload["shortenedName"],
            "description": request_payload["description"],
            "themes": request_payload["themes"],
            "notes": request_payload["notes"],
        }

        save_session_file(data)

        return

    @app.post("/edit_collection")
    async def edit_collection(request: Request):
        request_payload = await request.json()
        collection_id = request_payload["id"]

        logger.info("Editing collection '%s'", collection_id)

        data["collections"][collection_id].update(
            {
                "name": request_payload["name"],
                "shortened-name": request_payload["shortenedName"],
                "description": request_payload["description"],
                "themes": request_payload["themes"],
                "notes": request_payload["notes"],
            }
        )

        save_session_file(data)

        return

    @app.post("/upload_collection")
    async def upload_collection(
        collectionId: str = Form(...), file: List[UploadFile] = File(...)
    ):
        collection_path = COLLECTIONS_PATH / collectionId
        collection_path.mkdir(parents=True, exist_ok=True)

        for _file in file:
            target_path = collection_path / _file.filename
            logger.debug("Writing file '%s'", target_path)
            with target_path.open("wb") as _fh:
                _fh.write(_file.file.read())

        return

    @app.post("/delete_collection")
    async def delete_collection(request: Request):
        request_payload = await request.json()
        collection_id = request_payload["id"]

        logger.info("Deleting collection '%s'", collection_id)

        collection_path = COLLECTIONS_PATH / collection_id
        if collection_path.is_dir():
            shutil.rmtree(collection_path)

        del data["collections"][collection_id]
        save_session_file(data)

        return

    app.mount("/", StaticFiles(directory=static_path, html=True), name="static")

    data = initialize_data()

    return app
