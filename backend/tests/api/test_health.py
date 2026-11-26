"""NFR-1: helsesjekken svarer uten innlogging. AD-9: advarselen kommer ved oppstart."""

import logging

import pytest
from fastapi.testclient import TestClient

from rbe.config import Settings
from rbe.main import create_app


def test_nfr1_health_returns_ok() -> None:
    client = TestClient(create_app())
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_ad9_create_app_warns_once_without_secret(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    # conftest.py har allerede fjernet RBE_SESSION_SECRET og tømt get_settings-cachen.
    monkeypatch.setitem(Settings.model_config, "env_file", None)
    with caplog.at_level(logging.WARNING, logger="rbe.config"):
        create_app()
    warnings = [
        r for r in caplog.records if r.name == "rbe.config" and r.levelno == logging.WARNING
    ]
    assert len(warnings) == 1
