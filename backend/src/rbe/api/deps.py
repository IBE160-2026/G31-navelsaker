"""Felles avhengigheter for API-et: databasesesjon og innloggingskrav (FR-1, AD-8)."""

from collections.abc import Iterator
from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from rbe.db.models import UserRow

NOT_LOGGED_IN = "Du er ikke logget inn."


def get_session(request: Request) -> Iterator[Session]:
    """Gi en SQLAlchemy-sesjon fra ``sessionmaker`` som ``lifespan`` la på ``app.state``."""
    with request.app.state.sessionmaker() as session:
        yield session


DbSession = Annotated[Session, Depends(get_session)]


def _unauthorized() -> HTTPException:
    return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=NOT_LOGGED_IN)


def require_user(request: Request, session: DbSession) -> UserRow:
    """Gi den innloggede brukeren, eller 401 hvis sesjonen mangler eller brukeren er borte.

    Settes på ruterne i ``create_app()``, ikke på hver rute. Sesjonen lagrer bare ``user_id``,
    og brukeren hentes fra databasen ved hvert kall. Raden legges også på ``request.state``,
    så rutene kan lese den med ``current_user``.
    """
    user_id = request.session.get("user_id")
    user = session.get(UserRow, user_id) if isinstance(user_id, int) else None
    if user is None:
        raise _unauthorized()
    request.state.user = user
    return user


def current_user(request: Request) -> UserRow:
    """Gi brukeren som ``require_user`` på ruteren allerede har hentet.

    Rutene bruker denne i stedet for å avhenge av ``require_user`` selv. Da finner rutetesten
    en ruter som mangler ``require_user``. Mangler brukeren, avvises kallet (401).
    """
    user = getattr(request.state, "user", None)
    if user is None:
        raise _unauthorized()
    return user


CurrentUser = Annotated[UserRow, Depends(current_user)]
