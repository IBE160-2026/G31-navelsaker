"""Felles testoppsett: hver test starter uten RBE_-variabler og med tom innstillingscache."""

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
