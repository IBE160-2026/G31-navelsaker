---
title: 'Story 1.4: Innlogging i backend'
type: 'feature'
created: '2026-11-26'
status: 'done'
baseline_commit: 'a0d73ffe908565d23b3833e2ca652917f00ba7c3'
route: 'dispatch'
review_loop_iteration: 0
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-1-context.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Hvem som helst som når backend, kan i dag lese alt API-et gir. Planleggeren skal logge inn og ut med demobrukeren, og alle `/api`-ruter utenom innlogging og helsesjekk skal avvise uinnloggede (FR-1, AD-8).

**Approach:** Legg til `SessionMiddleware` med signert cookie, endepunktene `POST /api/auth/login`, `POST /api/auth/logout` og `GET /api/auth/me`, og avhengigheten `require_user` som settes på ruterne, ikke på hver rute. En rutetest går gjennom `app.routes` og feiler hvis en rute er åpen uten å stå på unntakslista.

## Boundaries & Constraints

**Always:**
- Avhengighet med `==`: `itsdangerous==2.2.0`. Stopp og før avviket hvis `uv lock` ikke klarer å løse den.
- `SessionMiddleware` med `secret_key=settings.session_secret`, `same_site="lax"` og `https_only=False` (lokal http, AD-11). Cookien heter `rbe_session` og varer 8 timer (`max_age=8*3600`). Starlette setter alltid httpOnly.
- Sesjonen lagrer bare `user_id`. `require_user` henter brukeren fra databasen og gir 401 hvis sesjonen mangler eller brukeren ikke finnes lenger. Den gir brukerraden videre til ruten.
- En avhengighet `get_session` gir en SQLAlchemy-sesjon fra `request.app.state.sessionmaker`.
- `POST /api/auth/login` tar JSON `{"username", "password"}`. Riktig gir 200 med `{"username": ...}`. Sesjonen tømmes før `user_id` settes. Feil brukernavn og feil passord gir 401 med `detail` «Feil brukernavn eller passord.». Ved ukjent brukernavn kjøres likevel en verifisering mot en fast dummy-hash, så svartiden ikke røper om brukeren finnes. Passordet logges aldri.
- `POST /api/auth/logout` tømmer sesjonen og gir 204. `GET /api/auth/me` gir `{"username": ...}`. Begge krever innlogging.
- Uinnlogget gir 401 med `detail` «Du er ikke logget inn.».
- `require_user` settes med `dependencies=[Depends(require_user)]` når ruteren tas med i `create_app()`. Offentlige ruter (`GET /api/health` og `POST /api/auth/login`) ligger i egne rutere som tas med uten. Unntakslista i rutetesten har nøyaktig disse to.
- Rutetesten sjekker to ting for hver `APIRoute` under `/api` som ikke står på unntakslista: at `require_user` finnes i avhengighetstreet (`route.dependant`), og at et kall uten innlogging gir 401. Stiparametre fylles med en dummyverdi. En egen test viser at sjekken finner en åpen rute som legges til en app i testen.
- `tests/conftest.py` får fixturene `client` (app med `lifespan` mot en midlertidig SQLite-fil, uten lokal `.env`) og `logged_in_client` (innlogget som demobrukeren). Senere stories bruker dem.
- Testfunksjoner har kravnummeret i navnet, for eksempel `test_fr1_login_sets_session_cookie`.

**Never:**
- Ingen JWT eller token i frontend (AD-8). Ingen CORS (AD-11).
- Ingen registrering, flere brukere, passordbytte eller begrensning av antall forsøk.
- Ikke endre `testdata/` eller oppstarten i `rbe.db.seed`, utover å gjenbruke `password_hash`.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Riktig innlogging | `demo`/`demo` | 200, `{"username": "demo"}`, `Set-Cookie: rbe_session=…; HttpOnly; SameSite=lax`. `GET /api/auth/me` gir `demo` | – |
| Feil passord | `demo`/`feil` | 401, «Feil brukernavn eller passord.», ingen sesjon | – |
| Ukjent bruker | `ukjent`/`demo` | Nøyaktig samme svar som feil passord | – |
| Manglende felt | `{}` eller ikke JSON | 422 fra FastAPI | – |
| Utlogging | Innlogget, så `POST /api/auth/logout` | 204. `GET /api/auth/me` gir 401 etterpå | – |
| Uinnlogget | Ingen cookie | `me` og `logout` gir 401, «Du er ikke logget inn.» | – |
| Tuklet cookie | Cookie med feil signatur | 401, som uinnlogget | – |
| Brukeren slettet | Gyldig cookie, men raden er borte | 401 | – |
| Ny åpen rute | En rute under `/api` uten `require_user` | Rutetesten feiler og nevner ruten | – |

</frozen-after-approval>

## Code Map

- `backend/src/rbe/main.py` -- `create_app()` legger til middleware og rutere. `lifespan` legger `sessionmaker` på `app.state`. `get_settings()` kalles allerede her, så sesjonsnøkkelen kan hentes derfra.
- `backend/src/rbe/config.py` -- `session_secret` er alltid satt (tilfeldig med advarsel). Skal ikke endres.
- `backend/src/rbe/db/seed.py` -- `password_hash = PasswordHash.recommended()`. Gjenbrukes til `verify` og til dummy-hashen.
- `backend/src/rbe/db/models.py` -- `UserRow` (`id`, `username`, `password_hash`).
- `backend/src/rbe/api/health.py` -- mønsteret for rutere (`APIRouter(prefix="/api")`). Forblir offentlig.
- `backend/tests/conftest.py` -- `clean_env` (autouse). Nye fixturer kommer her.
- `backend/tests/api/test_seed.py` -- `no_env_file` og `db_file` viser hvordan en midlertidig database og `cache_clear()` settes opp. Kan stå som den er.
- `backend/tests/api/test_health.py` -- bruker `TestClient` uten `with`. Må fortsatt bestå med middlewaren.

## Tasks & Acceptance

**Execution:**
- [x] `backend/pyproject.toml`, `backend/uv.lock` -- legg til `itsdangerous==2.2.0`
- [x] `backend/src/rbe/api/deps.py` -- `get_session` og `require_user`
- [x] `backend/src/rbe/api/auth.py` -- `public_router` (login) og `router` (logout, me) med pydantic-modeller for inn og ut
- [x] `backend/src/rbe/main.py` -- `SessionMiddleware` og rutere, der `router` får `require_user`
- [x] `backend/tests/conftest.py` -- `client` og `logged_in_client`
- [x] `backend/tests/api/test_auth.py` -- radene i I/O-matrisen
- [x] `backend/tests/api/test_routes_require_login.py` -- rutetesten og testen som viser at den finner en åpen rute
- [x] `docs/ai-log.md` -- oppføring for story 1.4

**Commit-plan:** (1) avhengighet, `deps.py` og auth-endepunktene med middleware (FR-1), (2) testklienter, auth-tester og rutetest (FR-1, AD-8), (3) AI-logg.

**Acceptance Criteria:**
- Given `backend/`, when testene, `ruff check` og `ruff format --check` kjøres, then består alt med 0 funn.
- Given at `require_user` fjernes midlertidig fra `router` i `create_app()`, when rutetesten kjøres, then feiler den og nevner `/api/auth/me` og `/api/auth/logout`.

## Design Notes

Påkrevd som standard ligger i hvordan ruterne tas med, så nye stories bare legger sin ruter i samme kall:

```python
app.include_router(health.router)
app.include_router(auth.public_router)
for protected in (auth.router,):  # senere: items.router, runs.router …
    app.include_router(protected, dependencies=[Depends(require_user)])
```

Avgjørelser som brukeren ikke merker: 204 ved utlogging, cookienavnet `rbe_session` og 8 timers levetid (én arbeidsdag, så en glemt fane ikke er innlogget i to uker, som er standard i Starlette).

## Verification

**Commands:**
- `uv run python -m pytest` (i `backend/`, Windows-sperre, se spec 1.1) -- expected: alle tester består
- `uv run ruff check` og `uv run ruff format --check` (i `backend/`) -- expected: 0 funn

## Implementation Notes

- FastAPI 0.165 legger en inkludert ruter inn i `app.routes` som ett `_IncludedRouter`-objekt, ikke som enkeltruter. Rutetesten går derfor gjennom `fastapi.routing.iter_route_contexts(app.routes)`. Den gir hver `APIRoute` med effektiv sti og et `dependant` som tar med avhengighetene fra `include_router`. En første versjon som filtrerte `app.routes` på `APIRoute`, fant ingen ruter og besto uten å sjekke noe.
- Rutene avhenger ikke av `require_user` selv. Da ville den alltid finnes i avhengighetstreet, og akseptansekriteriet (testen feiler når `require_user` fjernes fra ruteren) kunne ikke oppfylles. `require_user` returnerer brukerraden og legger den i tillegg på `request.state.user`. Rutene leser den med `current_user` (`CurrentUser`), som gir 401 hvis brukeren mangler, så en ruter som glemmer kravet fortsatt avviser.
- Prøvd: med `require_user` fjernet fra `include_router` feiler rutetesten med `POST /api/auth/logout: mangler require_user` og `GET /api/auth/me: mangler require_user`.
- **Etter gjennomgangen (`56d2387`, `29d942e`):**
  - En ny test viser at cookien signeres med `RBE_SESSION_SECRET`. Den feiler med en hardkodet nøkkel i `create_app()`.
  - En ny test viser at innlogging tømmer en eksisterende sesjon. Den feiler når `session.clear()` fjernes.
  - En ny test viser at `CurrentUser` uten `require_user` gir 401.
  - Mislykket innlogging logger brukernavnet med `%r`.
  - AD-8 i arkitekturen er presisert med `CurrentUser`-mønsteret og `iter_route_contexts`.
  - 107 tester består.

## Spec Change Log

## Review Triage Log

Runde 1 (2026-11-26, lagene blind-hunter (BH), edge-case-hunter (ECH) og verification-gap (VG)). Rute: patch (P), defer (D) eller avvist (A).

| # | Lag | Funn | Vurdering | Begrunnelse | Rute |
|---|---|---|---|---|---|
| 1 | VG | Ingen test viser at cookien signeres med `RBE_SESSION_SECRET` | medium | Alle cookietestene kjører i én appinstans, så en hardkodet eller tilfeldig nøkkel i `create_app()` ville passert | P |
| 2 | BH | Ingen test viser at innlogging tømmer en eksisterende sesjon | medium | Specen krever det, og `session.clear()` kan fjernes uten at noe feiler | P |
| 3 | BH | Reserveveien i `current_user` er ikke testet | low | Den gjør at en ruter uten kravet fortsatt avviser. Testen er billig | P |
| 4 | ECH, BH | Brukernavnet logges rått ved mislykket innlogging (logginjeksjon) | low | Linjeskift fra en uinnlogget bruker gir falske logglinjer. Med `%r` er det rettet på én linje | P |
| 5 | BH | AD-8 er ikke oppdatert med `CurrentUser`-mønsteret og `iter_route_contexts` | medium | CLAUDE.md krever at avvik føres tilbake. Uten det kan neste story bruke `Depends(require_user)` i ruten og gjøre rutetesten blind | P (orkestrator, AD-8 presisert) |
| 6 | ECH, BH | `LoginRequest` har ingen lengdegrense (argon2 på store input) | low | Lokal demoapp med én bruker (AD-11). En grense ville også gi 422 for tomme felt i stedet for den felles feilmeldingen | A |
| 7 | ECH | En kopiert cookie er gyldig i opptil 8 timer etter utlogging | low | Det følger av den tilstandsløse signerte cookien i AD-8. En sperre ville kreve tilstand i databasen | A |
| 8 | ECH | Mislykket innlogging mens man er innlogget beholder sesjonen | false | Det er ikke en feil: ingen ny identitet er gitt, og den gamle var gyldig | A |
| 9 | ECH, BH | En tilfeldig nøkkel per prosess gir utlogging ved flere workere eller `--reload` | false | Én prosess (AD-11). Omstart uten nøkkel er dokumentert i AD-9 og `.env.example` | A |
| 10 | ECH | Rutetesten sjekker bare `APIRoute`, ikke mount eller websocket under `/api` | low | Ingen slike ruter er planlagt. Sjekken ville kreve en ny gren | A |
| 11 | BH | Diffen mangler `uv.lock`, og specen er ikke sporet | false | Låsefila var bevisst utelatt fra diffen for gjennomgangen. Specen committes ved avslutningen | A |
| 12 | BH | `isinstance(user_id, int)` godtar `bool` | low | Krever en gyldig signatur, og bare appen skriver sesjonen | A |
| 13 | BH | Sprintstatus er `in-progress` og ikke `review` | false | Den settes ved avslutningen av arbeidsflyten | A |
| 14 | BH | Ingen begrensning av antall innloggingsforsøk | false | Er utenfor omfanget etter specens Never-liste | A |
| 15 | BH | Rutetesten bygger på lite dokumenterte deler av FastAPI | false | FastAPI er låst med `==`, og `test_ad8_public_routes_exist` feiler hvis rutelista blir tom | A |
