"""Konfigurasjon for backend (AD-9).

All konfigurasjon leses her, fra miljøvariabler med prefikset ``RBE_`` og en valgfri
``backend/.env``. Standardstiene regnes ut fra pakkens plassering, ikke fra arbeidsmappa.
"""

import logging
import secrets
from functools import lru_cache
from pathlib import Path

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)

BACKEND_DIR = Path(__file__).resolve().parents[2]
REPO_DIR = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="RBE_",
        env_file=BACKEND_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: str = f"sqlite:///{(BACKEND_DIR / 'data' / 'rbe.db').as_posix()}"
    fixture_path: Path = REPO_DIR / "testdata/testfartoy-v1/input.json"
    session_secret: str | None = None
    demo_username: str = "demo"
    demo_password: str = "demo"

    @model_validator(mode="after")
    def _ensure_session_secret(self) -> Settings:
        if not self.session_secret:
            self.session_secret = secrets.token_urlsafe(32)
            logger.warning(
                "RBE_SESSION_SECRET er ikke satt. Bruker en tilfeldig nøkkel, "
                "så sesjonene overlever ikke en omstart."
            )
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
