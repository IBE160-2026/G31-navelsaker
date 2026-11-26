"""AD-8, FR-1: alle ``/api``-ruter krever innlogging, utenom unntakslista.

Testen går gjennom ``app.routes``. FastAPI 0.165 legger en inkludert ruter inn som ett objekt,
så rutene og avhengighetene de får fra ``include_router`` hentes med ``iter_route_contexts``.
For hver rute under ``/api`` som ikke er unntatt, sjekkes at ``require_user`` finnes i
avhengighetstreet, og at et kall uten innlogging gir 401. En ny rute som glemmer innloggingen,
får dermed testen til å feile og nevne ruten.
"""

import re

from fastapi import FastAPI
from fastapi.dependencies.models import Dependant
from fastapi.routing import APIRoute, RouteContext, iter_route_contexts
from fastapi.testclient import TestClient

from rbe.api.deps import CurrentUser, require_user

PUBLIC_ROUTES = {("GET", "/api/health"), ("POST", "/api/auth/login")}


def _depends_on_require_user(dependant: Dependant) -> bool:
    return any(
        dep.call is require_user or _depends_on_require_user(dep) for dep in dependant.dependencies
    )


def api_routes(client: TestClient) -> list[RouteContext]:
    """Alle ``APIRoute`` under ``/api``, med stien og avhengighetene fra ``include_router``."""
    return [
        route
        for route in iter_route_contexts(client.app.routes)
        if isinstance(route.original_route, APIRoute) and route.path.startswith("/api")
    ]


def find_open_routes(client: TestClient) -> list[str]:
    """Gi rutene under ``/api`` som ikke er unntatt og som ikke krever innlogging."""
    problems: list[str] = []
    for route in api_routes(client):
        for method in sorted(route.methods):
            if (method, route.path) in PUBLIC_ROUTES:
                continue
            name = f"{method} {route.path}"
            if not _depends_on_require_user(route.dependant):
                problems.append(f"{name}: mangler require_user")
            url = re.sub(r"\{[^}]+\}", "1", route.path)  # Stiparametre får en dummyverdi.
            status = client.request(method, url).status_code
            if status != 401:
                problems.append(f"{name}: ga {status} uten innlogging, ikke 401")
    return problems


def test_ad8_all_api_routes_require_login(client: TestClient) -> None:
    assert find_open_routes(client) == []


def test_ad8_public_routes_exist(client: TestClient) -> None:
    """Unntakslista skal bare inneholde ruter som finnes."""
    routes = {(method, route.path) for route in api_routes(client) for method in route.methods}
    assert PUBLIC_ROUTES <= routes
    assert {"/api/auth/me", "/api/auth/logout"} <= {path for _, path in routes}


def test_ad8_route_check_finds_open_route(client: TestClient) -> None:
    """Sjekken fanger en rute under ``/api`` som er lagt til uten ``require_user``."""

    @client.app.get("/api/open-items/{item_id}")
    def open_route(item_id: str) -> dict[str, str]:
        return {"item_id": item_id}

    assert find_open_routes(client) == [
        "GET /api/open-items/{item_id}: mangler require_user",
        "GET /api/open-items/{item_id}: ga 200 uten innlogging, ikke 401",
    ]


def test_ad8_current_user_without_require_user_gives_401() -> None:
    """Reserveveien: en rute med ``CurrentUser`` på en ruter uten ``require_user`` avviser."""
    app = FastAPI()

    @app.get("/api/whoami")
    def whoami(user: CurrentUser) -> dict[str, str]:
        return {"username": user.username}

    response = TestClient(app).get("/api/whoami")
    assert response.status_code == 401
    assert response.json() == {"detail": "Du er ikke logget inn."}
