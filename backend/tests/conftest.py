"""Felles testoppsett: hver test starter uten RBE_-variabler og med tom innstillingscache."""

from pathlib import Path

import pytest

from rbe.config import get_settings


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
