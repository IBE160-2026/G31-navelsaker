"""Innlogging og utlogging med signert sesjonscookie (FR-1, AD-8).

``public_router`` har bare innloggingen og tas med uten ``require_user``. ``router`` tas med
med ``require_user`` i ``create_app()``.
"""

import logging

from fastapi import APIRouter, HTTPException, Request, Response, status
from pydantic import BaseModel
from sqlalchemy import select

from rbe.api.deps import CurrentUser, DbSession
from rbe.db.models import UserRow
from rbe.db.seed import password_hash

logger = logging.getLogger(__name__)

WRONG_CREDENTIALS = "Feil brukernavn eller passord."

# Verifiseres mot ved ukjent brukernavn, så svartiden ikke røper om brukeren finnes.
_DUMMY_HASH = password_hash.hash("ikke-et-ekte-passord")

public_router = APIRouter(prefix="/api/auth", tags=["auth"])
router = APIRouter(prefix="/api/auth", tags=["auth"])


class LoginRequest(BaseModel):
    username: str
    password: str


class UserOut(BaseModel):
    username: str


@public_router.post("/login")
def login(credentials: LoginRequest, request: Request, session: DbSession) -> UserOut:
    user = session.scalar(select(UserRow).where(UserRow.username == credentials.username))
    if user is None:
        password_hash.verify(credentials.password, _DUMMY_HASH)
        valid = False
    else:
        valid = password_hash.verify(credentials.password, user.password_hash)
    if user is None or not valid:
        logger.info("Mislykket innlogging for «%s».", credentials.username)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=WRONG_CREDENTIALS)
    request.session.clear()
    request.session["user_id"] = user.id
    logger.info("«%s» logget inn.", user.username)
    return UserOut(username=user.username)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(request: Request, user: CurrentUser) -> Response:
    request.session.clear()
    logger.info("«%s» logget ut.", user.username)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/me")
def me(user: CurrentUser) -> UserOut:
    return UserOut(username=user.username)
