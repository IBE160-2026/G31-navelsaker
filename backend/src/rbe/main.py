import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from starlette.middleware.sessions import SessionMiddleware

from rbe.api import auth, health
from rbe.api.deps import require_user
from rbe.config import get_settings
from rbe.db.seed import startup
from rbe.db.session import make_engine, make_sessionmaker

SESSION_COOKIE = "rbe_session"
SESSION_MAX_AGE = 8 * 3600  # Én arbeidsdag, ikke Starlettes standard på to uker.


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
    # Hentes her, så advarselen om manglende sesjonsnøkkel kommer ved oppstart (AD-9).
    settings = get_settings()
    app = FastAPI(title="Red Ball Express", lifespan=lifespan)
    # Signert cookie, alltid httpOnly. https_only=False fordi appen kjøres lokalt over http (AD-11).
    app.add_middleware(
        SessionMiddleware,
        secret_key=settings.session_secret,
        session_cookie=SESSION_COOKIE,
        max_age=SESSION_MAX_AGE,
        same_site="lax",
        https_only=False,
    )
    # Offentlige rutere (unntakene i AD-8).
    app.include_router(health.router)
    app.include_router(auth.public_router)
    # Alle andre rutere krever innlogging. Nye rutere legges i denne lista.
    for protected in (auth.router,):
        app.include_router(protected, dependencies=[Depends(require_user)])
    return app


app = create_app()
