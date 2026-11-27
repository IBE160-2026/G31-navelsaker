"""Felles testoppsett: hver test starter uten RBE_-variabler og med tom innstillingscache.

Fixturene ``client`` og ``logged_in_client`` gir appen mot en midlertidig database (AD-8).
Fasitstien har én kilde her (``FIXTURE_DIR``, AD-4). ``pytest_generate_tests`` lager ett
fasittilfelle per scenario × FR × vare × felt for tester som tar argumentet ``fasit_case``.
FR-nummeret kommer fra modulens ``FIELD_FR``, eller fra ``fasit_fr`` hvis modulen har den.
Krokene ``pytest_runtest_makereport`` og ``pytest_collectreport`` gjør alle skip og xfail til
feil (SM-1), så en test som ikke sjekker noe, ikke kan stå som grønn.
"""

import json
from collections.abc import Generator, Iterator
from functools import cache
from pathlib import Path
from typing import Any, NamedTuple

import pytest
from fastapi.testclient import TestClient

from rbe.config import Settings, get_settings
from rbe.main import create_app

NO_SKIP = "skip og xfail er ikke lov (SM-1)"


def _skip_reason(longrepr: Any) -> str:
    if isinstance(longrepr, tuple) and len(longrepr) == 3:
        return str(longrepr[2])
    return str(longrepr)


@pytest.hookimpl(wrapper=True)
def pytest_runtest_makereport(
    item: pytest.Item, call: pytest.CallInfo[None]
) -> Generator[None, pytest.TestReport, pytest.TestReport]:
    """Gjør skip i oppsett eller test, og xfail, om til feil med grunnen i meldingen."""
    report = yield
    xfail = getattr(report, "wasxfail", None)
    if xfail is not None:
        del report.wasxfail
        report.outcome = "failed"
        report.longrepr = f"{NO_SKIP}: xfail {xfail}".rstrip()
    elif report.skipped:
        report.outcome = "failed"
        report.longrepr = f"{NO_SKIP}: {_skip_reason(report.longrepr)}"
    return report


@pytest.hookimpl(tryfirst=True)
def pytest_collectreport(report: pytest.CollectReport) -> None:
    """Gjør skip på modulnivå om til feil, før terminalrapporten teller den som skipped."""
    if report.skipped:
        report.outcome = "failed"
        report.longrepr = f"{NO_SKIP}: {_skip_reason(report.longrepr)}"


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

    Har modulen funksjonen ``fasit_fr(scenario, field, fr)``, gir den FR-nummeret for
    tilfellet, både i id-en og i ``case.fr`` (f.eks. FR-12 for feltene R11 påvirker i D).
    """
    if "fasit_case" not in metafunc.fixturenames:
        return
    fr_for = getattr(metafunc.module, "fasit_fr", None)
    cases = fasit_cases(metafunc.module.FIELD_FR)
    if fr_for:
        cases = [case._replace(fr=fr_for(case.scenario, case.field, case.fr)) for case in cases]
    params = [
        pytest.param(case, id=f"{case.scenario}-{case.fr}-{case.item}-{case.field}")
        for case in cases
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
