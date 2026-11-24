import logging

from fastapi import FastAPI

from rbe.api import health
from rbe.config import get_settings


def create_app() -> FastAPI:
    logging.basicConfig(level=logging.INFO)
    get_settings()
    app = FastAPI(title="Red Ball Express")
    app.include_router(health.router)
    return app


app = create_app()
