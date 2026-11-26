"""FR-2 og FR-1: oppstarten seeder scenario A og demobrukeren i en tom database (AD-5).

Testene kjører appen med ``with TestClient(...)`` slik at ``lifespan`` kjøres, mot en
midlertidig SQLite-fil. Fasiten leses direkte fra ``testdata/testfartoy-v1/`` (scenario A).
"""

import logging
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import replace
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from pwdlib import PasswordHash
from sqlalchemy import create_engine, inspect, select, update
from sqlalchemy.orm import Session

from rbe.config import get_settings
from rbe.db.models import ItemRow, UserRow
from rbe.db.repository import read_input
from rbe.fixture import FixtureError, load_input
from rbe.main import create_app
from rbe.mrp.types import MrpInput

TABLES = {"items", "bom_lines", "mps_lines", "scheduled_receipts", "planning_settings", "users"}


@pytest.fixture
def db_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """En databasesti i en mappe som ikke finnes ennå, med mellomrom i navnet."""
    path = tmp_path / "mappe med mellomrom" / "rbe.db"
    monkeypatch.setenv("RBE_DATABASE_URL", f"sqlite:///{path.as_posix()}")
    get_settings.cache_clear()
    return path


def _start() -> None:
    """Start og stopp appen én gang, slik at oppstarten i ``lifespan`` kjøres."""
    get_settings.cache_clear()
    with TestClient(create_app()) as client:
        assert client.app.state.engine is not None
        assert client.app.state.sessionmaker is not None


@contextmanager
def _session(db_file: Path) -> Iterator[Session]:
    engine = create_engine(f"sqlite:///{db_file.as_posix()}")
    try:
        with Session(engine) as session:
            yield session
    finally:
        engine.dispose()


def _sorted(data: MrpInput) -> MrpInput:
    """Sorter som ``read_input``: varer på id, BOM på (forelder, barn), resten i fasitens orden."""
    return replace(
        data,
        items=tuple(sorted(data.items, key=lambda item: item.id)),
        bom=tuple(sorted(data.bom, key=lambda line: (line.parent, line.child))),
    )


def _users(session: Session) -> list[UserRow]:
    return list(session.scalars(select(UserRow)))


def test_fr2_seed_matches_fixture(db_file: Path, input_path: Path) -> None:
    """Scenario A: en tom database uten mappe får nøyaktig fasitens inndata."""
    assert not db_file.parent.exists()
    _start()
    assert db_file.is_file()
    with _session(db_file) as session:
        assert set(inspect(session.get_bind()).get_table_names()) == TABLES
        data = read_input(session)
        assert data == _sorted(load_input(input_path, "A"))
        assert data.horizon.weeks == 16
        assert (len(data.items), len(data.bom), len(data.mps), len(data.scheduled_receipts)) == (
            11,
            12,
            2,
            2,
        )
        assert [user.username for user in _users(session)] == ["demo"]


def test_fr2_read_input_is_sorted(db_file: Path) -> None:
    _start()
    with _session(db_file) as session:
        data = read_input(session)
    assert [item.id for item in data.items] == sorted(item.id for item in data.items)
    keys = [(line.parent, line.child) for line in data.bom]
    assert keys == sorted(keys)


def test_fr2_restart_does_not_reseed(
    db_file: Path, input_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    """Scenario A: en endret lagerbeholdning overlever en omstart."""
    _start()
    with _session(db_file) as session, session.begin():
        session.execute(update(ItemRow).where(ItemRow.id == "PLT-900").values(on_hand=999))
    with caplog.at_level(logging.INFO, logger="rbe.db.seed"):
        _start()
    assert "allerede data" in caplog.text
    with _session(db_file) as session:
        data = read_input(session)
        assert len(_users(session)) == 1
    on_hand = {item.id: item.on_hand for item in data.items}
    assert on_hand["PLT-900"] == 999
    assert len(data.items) == len(load_input(input_path, "A").items)


def test_fr1_only_missing_user_is_created(db_file: Path) -> None:
    """Scenario A: mangler bare brukeren, opprettes den, og inndataene røres ikke."""
    _start()
    with _session(db_file) as session, session.begin():
        session.execute(update(ItemRow).where(ItemRow.id == "PLT-900").values(on_hand=7))
        for user in _users(session):
            session.delete(user)
    _start()
    with _session(db_file) as session:
        assert [user.username for user in _users(session)] == ["demo"]
        assert session.get_one(ItemRow, "PLT-900").on_hand == 7


def test_fr1_changed_demo_password_updates_hash(
    db_file: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _start()
    with _session(db_file) as session:
        before = read_input(session)
    monkeypatch.setenv("RBE_DEMO_PASSWORD", "nytt")
    _start()
    hasher = PasswordHash.recommended()
    with _session(db_file) as session:
        users = _users(session)
        assert len(users) == 1
        assert hasher.verify("nytt", users[0].password_hash)
        assert not hasher.verify("demo", users[0].password_hash)
        assert read_input(session) == before


def test_fr1_other_users_are_untouched(db_file: Path) -> None:
    _start()
    with _session(db_file) as session, session.begin():
        session.add(UserRow(username="annen", password_hash="uendret"))
    _start()
    with _session(db_file) as session:
        other = session.scalar(select(UserRow).where(UserRow.username == "annen"))
        assert other is not None
        assert other.password_hash == "uendret"


def test_fr1_password_is_hashed_with_argon2(db_file: Path) -> None:
    _start()
    with _session(db_file) as session:
        (user,) = _users(session)
    assert user.password_hash.startswith("$argon2")
    assert user.password_hash != "demo"
    assert PasswordHash.recommended().verify("demo", user.password_hash)


@pytest.mark.parametrize("seeded", [False, True], ids=["tom", "seedet"])
def test_fr2_missing_fixture_stops_startup(
    db_file: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, seeded: bool
) -> None:
    if seeded:
        _start()
    missing = tmp_path / "finnes ikke" / "input.json"
    monkeypatch.setenv("RBE_FIXTURE_PATH", str(missing))
    with pytest.raises(FixtureError, match="finnes ikke"):
        _start()
