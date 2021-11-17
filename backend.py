import logging

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

logger = logging.getLogger("logger")


def create_app(static_path, debug=False):
    if debug:
        logger.setLevel("DEBUG")

    app = FastAPI()

    @app.get("/get_collections")
    def get_collections():
        return {"Hello": "World"}

    app.mount("/", StaticFiles(directory=static_path, html=True), name="static")

    return app
