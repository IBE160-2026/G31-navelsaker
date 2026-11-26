"""FR-1, AD-8: innlogging og utlogging med signert sesjonscookie.

Testene bruker ``client`` og ``logged_in_client`` fra ``conftest.py``, som kjører appen med
``lifespan`` mot en midlertidig SQLite-fil med demobrukeren.
"""

import logging
from pathlib import Path

import pytest
from fastapi import Request
from fastapi.testclient import TestClient
from sqlalchemy import delete

from rbe.api import auth
from rbe.config import Settings, get_settings
from rbe.db.models import UserRow
from rbe.main import SESSION_COOKIE, create_app

WRONG = {"detail": "Feil brukernavn eller passord."}
NOT_LOGGED_IN = {"detail": "Du er ikke logget inn."}


def _login(client: TestClient, username: str, password: str):
    return client.post("/api/auth/login", json={"username": username, "password": password})


def test_fr1_login_sets_session_cookie(client: TestClient) -> None:
    response = _login(client, "demo", "demo")
    assert response.status_code == 200
    assert response.json() == {"username": "demo"}
    cookie = response.headers["set-cookie"].lower()
    assert cookie.startswith(f"{SESSION_COOKIE}=")
    assert "httponly" in cookie
    assert "samesite=lax" in cookie
    assert "max-age=28800" in cookie
    assert "secure" not in cookie
    me = client.get("/api/auth/me")
    assert me.status_code == 200
    assert me.json() == {"username": "demo"}


def test_fr1_wrong_password_gives_401_and_no_session(client: TestClient) -> None:
    response = _login(client, "demo", "feil")
    assert response.status_code == 401
    assert response.json() == WRONG
    assert "set-cookie" not in response.headers
    assert SESSION_COOKIE not in client.cookies
    assert client.get("/api/auth/me").status_code == 401


def test_fr1_unknown_user_gives_same_answer_as_wrong_password(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    wrong_password = _login(client, "demo", "feil")
    calls: list[str] = []
    real_verify = auth.password_hash.verify

    def spy(password: str, hash: str) -> bool:
        calls.append(hash)
        return real_verify(password, hash)

    monkeypatch.setattr(auth.password_hash, "verify", spy)
    unknown = _login(client, "ukjent", "demo")
    assert unknown.status_code == wrong_password.status_code == 401
    assert unknown.json() == wrong_password.json() == WRONG
    assert "set-cookie" not in unknown.headers
    # Ukjent bruker verifiseres likevel, mot dummy-hashen, så svartiden ikke røper noe.
    assert calls == [auth._DUMMY_HASH]


@pytest.mark.parametrize(
    "kwargs",
    [{"json": {}}, {"json": {"username": "demo"}}, {"content": "ikke json"}],
    ids=["tomt", "mangler-passord", "ikke-json"],
)
def test_fr1_login_with_missing_fields_gives_422(client: TestClient, kwargs: dict) -> None:
    assert client.post("/api/auth/login", **kwargs).status_code == 422


def test_fr1_password_is_never_logged(client: TestClient, caplog: pytest.LogCaptureFixture) -> None:
    with caplog.at_level(logging.DEBUG):
        _login(client, "demo", "hemmelig-feil-passord")
        _login(client, "ukjent", "hemmelig-feil-passord")
        _login(client, "demo", "demo")
    assert "hemmelig-feil-passord" not in caplog.text
    assert "ukjent" in caplog.text  # Loggen ble faktisk fanget.


def test_fr1_logout_clears_session(logged_in_client: TestClient) -> None:
    response = logged_in_client.post("/api/auth/logout")
    assert response.status_code == 204
    assert response.content == b""
    me = logged_in_client.get("/api/auth/me")
    assert me.status_code == 401
    assert me.json() == NOT_LOGGED_IN


@pytest.mark.parametrize("method, path", [("GET", "/api/auth/me"), ("POST", "/api/auth/logout")])
def test_fr1_not_logged_in_gives_401(client: TestClient, method: str, path: str) -> None:
    response = client.request(method, path)
    assert response.status_code == 401
    assert response.json() == NOT_LOGGED_IN


def test_fr1_tampered_cookie_gives_401(logged_in_client: TestClient) -> None:
    value = logged_in_client.cookies[SESSION_COOKIE]
    tampered = value[:-4] + ("BBBB" if value.endswith("AAAA") else "AAAA")
    logged_in_client.cookies.clear()
    logged_in_client.cookies.set(SESSION_COOKIE, tampered)
    response = logged_in_client.get("/api/auth/me")
    assert response.status_code == 401
    assert response.json() == NOT_LOGGED_IN


def test_fr1_cookie_for_deleted_user_gives_401(logged_in_client: TestClient) -> None:
    with logged_in_client.app.state.sessionmaker.begin() as session:
        session.execute(delete(UserRow))
    response = logged_in_client.get("/api/auth/me")
    assert response.status_code == 401
    assert response.json() == NOT_LOGGED_IN


def test_fr1_login_clears_existing_session(client: TestClient) -> None:
    """Sesjonen tømmes før ``user_id`` settes, så ingenting fra en tidligere sesjon blir med."""

    @client.app.post("/test/session/extra")
    def set_extra(request: Request) -> None:
        request.session["extra"] = "gammel"

    @client.app.get("/test/session")
    def read_session(request: Request) -> dict:
        return dict(request.session)

    client.post("/test/session/extra")
    assert client.get("/test/session").json() == {"extra": "gammel"}
    assert _login(client, "demo", "demo").status_code == 200
    assert set(client.get("/test/session").json()) == {"user_id"}


def test_ad9_session_cookie_signed_with_configured_secret(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Cookien signeres med RBE_SESSION_SECRET: samme nøkkel godtar den, en annen avviser den."""
    monkeypatch.setitem(Settings.model_config, "env_file", None)
    monkeypatch.setenv("RBE_DATABASE_URL", f"sqlite:///{(tmp_path / 'rbe.db').as_posix()}")
    monkeypatch.setenv("RBE_SESSION_SECRET", "nøkkel-en")
    get_settings.cache_clear()
    with TestClient(create_app()) as first:
        assert _login(first, "demo", "demo").status_code == 200
        cookie = first.cookies[SESSION_COOKIE]

    get_settings.cache_clear()
    with TestClient(create_app()) as same_secret:
        same_secret.cookies.set(SESSION_COOKIE, cookie)
        response = same_secret.get("/api/auth/me")
        assert response.status_code == 200
        assert response.json() == {"username": "demo"}

    monkeypatch.setenv("RBE_SESSION_SECRET", "nøkkel-to")
    get_settings.cache_clear()
    with TestClient(create_app()) as other_secret:
        other_secret.cookies.set(SESSION_COOKIE, cookie)
        response = other_secret.get("/api/auth/me")
        assert response.status_code == 401
        assert response.json() == NOT_LOGGED_IN
