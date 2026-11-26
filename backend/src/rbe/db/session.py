"""Engine og sessionmaker fra ``database_url`` (AD-5)."""

from pathlib import Path

from sqlalchemy import Engine, create_engine, event, make_url
from sqlalchemy.orm import Session, sessionmaker


def make_engine(url: str) -> Engine:
    """Lag en engine. For en SQLite-fil opprettes mappa først, siden den kan mangle på en ren
    klone (``backend/data/`` er gitignorert)."""
    parsed = make_url(url)
    is_sqlite = parsed.get_backend_name() == "sqlite"
    if is_sqlite and parsed.database and parsed.database != ":memory:":
        Path(parsed.database).parent.mkdir(parents=True, exist_ok=True)
    engine = create_engine(url)
    if is_sqlite:
        event.listen(engine, "connect", _enable_foreign_keys)
    return engine


def _enable_foreign_keys(dbapi_connection, _record) -> None:
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


def make_sessionmaker(engine: Engine) -> sessionmaker[Session]:
    return sessionmaker(bind=engine, expire_on_commit=False)
