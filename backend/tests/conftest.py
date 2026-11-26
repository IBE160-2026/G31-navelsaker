"""Felles testoppsett: hver test starter uten RBE_-variabler og med tom innstillingscache.

Fixturene ``client`` og ``logged_in_client`` gir appen mot en midlertidig database (AD-8).
"""

from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from rbe.config import Settings, get_settings
from rbe.main import create_app


@pytest.fixture(autouse=True)
def clean_env(monkeypatch: pytest.MonkeyPatch):
    for name in (
        "DATABASE_URL",
        "FIXTURE_PATH",
        "SESSION_SECRET",
        "DEMO_USERNAME",
        "DEMO_PASSWORD",
    ):
        monkeypatch.delenv(f"RBE_{name}", raising=False)
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


@pytest.fixture(scope="session")
def fixture_dir() -> Path:
    """Mappa med fasiten for testfartøyet (AD-4). Testene leser fasiten direkte herfra."""
    return Path(__file__).resolve().parents[2] / "testdata" / "testfartoy-v1"


@pytest.fixture(scope="session")
def input_path(fixture_dir: Path) -> Path:
    """Stien til ``input.json`` i fasiten (AD-4)."""
    return fixture_dir / "input.json"


@pytest.fixture
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[TestClient]:
    """En uinnlogget testklient med ``lifespan`` mot en midlertidig SQLite-fil, uten lokal
    ``.env``. Oppstarten seeder scenario A og demobrukeren (FR-2)."""
    monkeypatch.setitem(Settings.model_config, "env_file", None)
    db_path = tmp_path / "rbe.db"
    monkeypatch.setenv("RBE_DATABASE_URL", f"sqlite:///{db_path.as_posix()}")
    get_settings.cache_clear()
    with TestClient(create_app()) as test_client:
        yield test_client


@pytest.fixture
def logged_in_client(client: TestClient) -> TestClient:
    """Samme klient som ``client``, innlogget som demobrukeren (FR-1)."""
    response = client.post("/api/auth/login", json={"username": "demo", "password": "demo"})
    assert response.status_code == 200, response.text
    return client
