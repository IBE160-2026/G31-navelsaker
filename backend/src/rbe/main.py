import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from rbe.api import health
from rbe.config import get_settings
from rbe.db.seed import startup
from rbe.db.session import make_engine, make_sessionmaker


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Åpne databasen, seed den ved behov og legg engine og sessionmaker på ``app.state``."""
    settings = get_settings()
    engine = make_engine(settings.database_url)
    try:
        startup(engine, settings)
        app.state.engine = engine
        app.state.sessionmaker = make_sessionmaker(engine)
        yield
    finally:
        engine.dispose()


def create_app() -> FastAPI:
    logging.basicConfig(level=logging.INFO)
    get_settings()  # Gjør at advarselen om manglende sesjonsnøkkel kommer ved oppstart (AD-9).
    app = FastAPI(title="Red Ball Express", lifespan=lifespan)
    app.include_router(health.router)
    return app


app = create_app()
