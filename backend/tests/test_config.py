"""AD-9, NFR-1, NFR-2: konfigurasjon via RBE_-variabler, valgfri .env og trygge standarder."""

import ast
import logging
from pathlib import Path

import pytest

from rbe import config
from rbe.config import BACKEND_DIR, REPO_DIR, Settings, get_settings

FORBIDDEN_OS_NAMES = {"environ", "environb", "getenv", "getenvb", "putenv"}
SRC_DIR = BACKEND_DIR / "src" / "rbe"


def _secret_warnings(caplog: pytest.LogCaptureFixture) -> list[logging.LogRecord]:
    return [r for r in caplog.records if r.name == "rbe.config" and r.levelno == logging.WARNING]


def test_ad9_defaults_without_env(caplog: pytest.LogCaptureFixture) -> None:
    with caplog.at_level(logging.WARNING, logger="rbe.config"):
        settings = Settings(_env_file=None)
    assert settings.database_url == f"sqlite:///{(BACKEND_DIR / 'data' / 'rbe.db').as_posix()}"
    assert settings.fixture_path == REPO_DIR / "testdata" / "testfartoy-v1" / "input.json"
    assert settings.demo_username == "demo"
    assert settings.demo_password == "demo"
    assert settings.session_secret
    assert len(_secret_warnings(caplog)) == 1


def test_ad9_random_secret_warns(caplog: pytest.LogCaptureFixture) -> None:
    with caplog.at_level(logging.WARNING, logger="rbe.config"):
        first = Settings(_env_file=None)
        second = Settings(_env_file=None)
    assert first.session_secret != second.session_secret
    assert len(first.session_secret) >= 32
    assert len(_secret_warnings(caplog)) == 2


def test_ad9_session_secret_from_env(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    monkeypatch.setenv("RBE_SESSION_SECRET", "hemmelig-testnokkel")
    with caplog.at_level(logging.WARNING, logger="rbe.config"):
        settings = Settings(_env_file=None)
    assert settings.session_secret == "hemmelig-testnokkel"
    assert _secret_warnings(caplog) == []


def test_ad9_empty_session_secret_counts_as_missing(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    monkeypatch.setenv("RBE_SESSION_SECRET", "")
    with caplog.at_level(logging.WARNING, logger="rbe.config"):
        settings = Settings(_env_file=None)
    assert settings.session_secret
    assert len(_secret_warnings(caplog)) == 1


def test_ad9_whitespace_session_secret_counts_as_missing(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    monkeypatch.setenv("RBE_SESSION_SECRET", "   ")
    with caplog.at_level(logging.WARNING, logger="rbe.config"):
        settings = Settings(_env_file=None)
    assert settings.session_secret.strip()
    assert len(_secret_warnings(caplog)) == 1


def test_ad9_fixture_path_and_demo_user_from_env(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    fixture = tmp_path / "annen fasit.json"
    monkeypatch.setenv("RBE_FIXTURE_PATH", str(fixture))
    monkeypatch.setenv("RBE_DEMO_USERNAME", "sensor")
    monkeypatch.setenv("RBE_DEMO_PASSWORD", "hemmelig")
    settings = Settings(_env_file=None)
    assert settings.fixture_path == fixture
    assert settings.demo_username == "sensor"
    assert settings.demo_password == "hemmelig"


def test_ad9_default_env_file_is_in_backend_dir() -> None:
    assert Settings.model_config["env_file"] == BACKEND_DIR / ".env"


def test_ad9_database_url_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("RBE_DATABASE_URL", "sqlite:///annen.db")
    assert Settings(_env_file=None).database_url == "sqlite:///annen.db"


def test_ad9_env_file_is_read(tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text(
        "RBE_DATABASE_URL=sqlite:///fra-fil.db\n"
        "RBE_SESSION_SECRET=nokkel-fra-fil\n"
        "RBE_DEMO_USERNAME=sensor\n",
        encoding="utf-8",
    )
    with caplog.at_level(logging.WARNING, logger="rbe.config"):
        settings = Settings(_env_file=env_file)
    assert settings.database_url == "sqlite:///fra-fil.db"
    assert settings.session_secret == "nokkel-fra-fil"
    assert settings.demo_username == "sensor"
    assert _secret_warnings(caplog) == []


def test_nfr1_paths_independent_of_cwd(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(BACKEND_DIR)
    from_backend = Settings(_env_file=None)
    other = tmp_path / "mappe med mellomrom"
    other.mkdir()
    monkeypatch.chdir(other)
    from_other = Settings(_env_file=None)
    assert from_other.database_url == from_backend.database_url
    assert from_other.fixture_path == from_backend.fixture_path
    assert from_other.fixture_path.is_file()


def test_ad9_get_settings_is_cached() -> None:
    assert get_settings() is get_settings()


def _env_access(source: str) -> list[str]:
    """Finn lesing/skriving av miljøvariabler via os i en kildetekst."""
    tree = ast.parse(source)
    os_aliases: set[str] = set()
    found: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.asname is None and (alias.name == "os" or alias.name.startswith("os.")):
                    os_aliases.add("os")
                elif alias.asname is not None and alias.name == "os":
                    os_aliases.add(alias.asname)
        elif isinstance(node, ast.ImportFrom) and node.module == "os":
            for alias in node.names:
                if alias.name in FORBIDDEN_OS_NAMES or alias.name == "*":
                    found.append(f"from os import {alias.name}")
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Attribute)
            and node.attr in FORBIDDEN_OS_NAMES
            and isinstance(node.value, ast.Name)
            and node.value.id in os_aliases
        ):
            found.append(f"{node.value.id}.{node.attr}")
    return found


def test_ad9_env_access_check_finds_all_variants() -> None:
    snippet = (
        "import os as o\n"
        "o.environ\n"
        "from os import getenv\n"
        "import os\n"
        "os.environ.get('X')\n"
        "os.environb\n"
    )
    dotted = "import os.path\nos.getenv('X')\n"
    found = _env_access(snippet)
    assert _env_access(dotted) == ["os.getenv"]
    assert "o.environ" in found
    assert "from os import getenv" in found
    assert found.count("os.environ") == 1
    assert "os.environb" in found
    assert _env_access("import os\nos.path.join('a', 'b')\n") == []


def test_ad9_only_config_reads_environment() -> None:
    files = list(SRC_DIR.rglob("*.py"))
    assert files
    offenders = {
        str(path.relative_to(SRC_DIR)): hits
        for path in files
        if path != Path(config.__file__).resolve()
        and (hits := _env_access(path.read_text(encoding="utf-8")))
    }
    assert offenders == {}
