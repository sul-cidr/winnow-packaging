from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles


def create_app(static_path):
    app = FastAPI()

    @app.get("/get_collections")
    def get_collections():
        return {"Hello": "World"}

    app.mount("/", StaticFiles(directory=static_path, html=True), name="static")

    return app
