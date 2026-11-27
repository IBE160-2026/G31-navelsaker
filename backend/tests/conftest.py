"""Felles testoppsett: hver test starter uten RBE_-variabler og med tom innstillingscache.

Fixturene ``client`` og ``logged_in_client`` gir appen mot en midlertidig database (AD-8).
Fasitstien har én kilde her (``FIXTURE_DIR``, AD-4). ``pytest_generate_tests`` lager ett
fasittilfelle per scenario × FR × vare × felt for tester som tar argumentet ``fasit_case``.
"""

import json
from collections.abc import Iterator
from functools import cache
from pathlib import Path
from typing import Any, NamedTuple

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


FIXTURE_DIR = Path(__file__).resolve().parents[2] / "testdata" / "testfartoy-v1"
"""Mappa med fasiten for testfartøyet (AD-4). Testene leser fasiten direkte herfra."""


class FasitCase(NamedTuple):
    """Én forventet verdi i ``expected.json``: scenario, FR, vare, felt og verdien."""

    scenario: str
    fr: str
    item: str
    field: str
    expected: Any


@cache
def expected_scenarios() -> dict[str, Any]:
    """``scenarios`` fra ``expected.json``, lest én gang per testkjøring."""
    text = (FIXTURE_DIR / "expected.json").read_text(encoding="utf-8")
    return json.loads(text)["scenarios"]


def fasit_cases(field_fr: dict[str, str]) -> list[FasitCase]:
    """Ett tilfelle per scenario × vare × felt i ``field_fr`` (felt → FR-nummer)."""
    return [
        FasitCase(scenario, fr, item_id, field, values[field])
        for scenario, result in expected_scenarios().items()
        for item_id, values in result["items"].items()
        for field, fr in field_fr.items()
    ]


def pytest_generate_tests(metafunc: pytest.Metafunc) -> None:
    """Parametriser ``fasit_case`` fra fasiten med modulens tabell ``FIELD_FR``.

    Har modulen funksjonen ``fasit_marks(case)``, får hvert tilfelle marks fra den (f.eks.
    ``skip`` for felt som en senere story fyller inn).
    """
    if "fasit_case" not in metafunc.fixturenames:
        return
    marks_for = getattr(metafunc.module, "fasit_marks", None)
    params = [
        pytest.param(
            case,
            id=f"{case.scenario}-{case.fr}-{case.item}-{case.field}",
            marks=marks_for(case) if marks_for else (),
        )
        for case in fasit_cases(metafunc.module.FIELD_FR)
    ]
    metafunc.parametrize("fasit_case", params)


@pytest.fixture(scope="session")
def fixture_dir() -> Path:
    """Mappa med fasiten for testfartøyet (AD-4). Testene leser fasiten direkte herfra."""
    return FIXTURE_DIR


@pytest.fixture(scope="session")
def expected() -> dict[str, Any]:
    """``scenarios`` fra ``expected.json`` (AD-4)."""
    return expected_scenarios()


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
