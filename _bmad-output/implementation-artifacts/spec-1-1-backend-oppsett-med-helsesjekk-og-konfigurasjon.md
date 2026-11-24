---
title: 'Story 1.1: Backend-oppsett med helsesjekk og konfigurasjon'
type: 'chore'
created: '2026-11-24'
status: 'done'
baseline_commit: '73f22831cdbc6d4727dde56642e9e441294e8d8e'
route: 'dispatch'
review_loop_iteration: 0
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-1-context.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Det finnes ingen backend ennå. Sensor skal kunne starte backend og kjøre testene med én kommando hver, uten manuelt oppsett og uten hemmeligheter i repoet (NFR-1, NFR-2, AD-9, AD-10, AD-11).

**Approach:** Opprett uv-prosjektet `backend/` etter strukturfrøet i arkitekturen, med FastAPI-app, `GET /api/health`, konfigurasjon via `pydantic-settings` (prefiks `RBE_`) og trygge standardverdier. Legg til pytest og ruff, og tester for helsesjekk og konfigurasjon.

## Boundaries & Constraints

**Always:**
- `pyproject.toml`: `requires-python = ">=3.14"`, `[build-system]` med `requires = ["uv_build>=0.12,<0.13"]` og `build-backend = "uv_build"` (pakken `rbe` installeres editable i `.venv`), `==`-festing: `fastapi[standard]==0.165.0`, `pydantic-settings==2.16.3`, og i `[dependency-groups] dev`: `pytest==9.2.0`, `ruff==0.17.6`. `httpx` til `TestClient` følger med `fastapi[standard]`. Kan `uv lock` ikke løse versjonene: stopp og før avviket i specen og arkitekturen, ikke bytt versjon stille. (Sjekket 2026-11-24: alle løses mot Python 3.14.7.)
- `.python-version` i `backend/` er `3.14`.
- All konfigurasjon leses i `rbe/config.py`. Ingen annen modul i `src/rbe` bruker `os.environ`, `os.environb`, `os.getenv`, `os.getenvb` eller `os.putenv`, verken via `import os` (også med alias) eller `from os import …`.
- Stier regnes ut fra pakkens plassering: `BACKEND_DIR = Path(__file__).resolve().parents[2]`, `REPO_DIR = parents[3]`. Standardverdier: `database_url = f"sqlite:///{(BACKEND_DIR / 'data' / 'rbe.db').as_posix()}"`, `fixture_path = REPO_DIR / "testdata/testfartoy-v1/input.json"`, `.env` i `BACKEND_DIR` (valgfri). Ingen mappe opprettes i denne storyen.
- `session_secret: str | None = None`. Både `None` og tom streng regnes som manglende. Mangler den, lager en `model_validator` på `Settings` en nøkkel med `secrets.token_urlsafe(32)` og logger én WARNING på loggeren `rbe.config`. `get_settings()` har `@lru_cache`, og `create_app()` kaller den, slik at advarselen kommer ved oppstart.
- `create_app()` setter opp logging med `logging.basicConfig(level=logging.INFO)`, ikke `dictConfig`, så eksisterende loggere ikke slås av. `rbe.config` settes aldri til `propagate=False`, så `caplog` ser advarselen uansett hvilken rekkefølge testene kjører i.
- Demobrukerens standardverdier er brukernavn `demo` og passord `demo` (besluttet av Thobias 2026-11-24). De er et kjent demopassord og skal stå i README (NFR-2).
- Testfunksjoner har kravnummeret i navnet, for eksempel `test_nfr1_health_returns_ok` og `test_ad9_random_secret_warns`. Filnavnene er `tests/api/test_health.py` og `tests/test_config.py`.
- Konvensjon for FastAPI-avhengigheter fra nå: `Annotated[…, Depends(…)]`, ikke `Depends()` som standardverdi. Da trengs ikke noe unntak for ruff-regel B008.
- Levering: branch `story/1.1-backend-oppsett`, én PR, 3 commits på norsk med kravnummer, og en oppføring i `docs/ai-log.md`.

**Never:**
- Ingen database, innlogging, seed eller fasitparser (story 1.2–1.4). Ingen SQLAlchemy, pwdlib eller itsdangerous i avhengighetene ennå.
- Ingen Docker og ingen CI. README endres ikke. Det er et bevisst avvik fra felleskravet om README ved ny oppstart: README v1 skrives samlet i story 1.7, når også frontend og innlogging finnes.
- Ikke endre `testdata/`.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Helsesjekk | `GET /api/health` uten cookie | 200, `{"status": "ok"}` | – |
| Ingen `.env` og ingen `RBE_`-variabler | `Settings(_env_file=None)` | Standardverdier, tilfeldig nøkkel, nøyaktig én WARNING fra `rbe.config` | – |
| `RBE_SESSION_SECRET` satt | Miljøvariabel | Verdien brukes, ingen WARNING | – |
| `RBE_SESSION_SECRET=""` | Tom miljøvariabel | Regnes som manglende: tilfeldig nøkkel og én WARNING | – |
| `RBE_DATABASE_URL` satt | Miljøvariabel | Overstyrer standardverdien | – |
| `.env` finnes | Midlertidig fil gitt som `_env_file` | Verdiene i fila brukes | – |
| Annen arbeidsmappe | `chdir` til en mappe med mellomrom i navnet | Samme stier som fra `backend/`, og `fixture_path` finnes | – |

</frozen-after-approval>

## Code Map

- `.gitignore` -- dekker allerede `.venv/`, `__pycache__/`, `.pytest_cache/`, `.ruff_cache/` og `.env` på alle nivåer (`!.env.example`). Mangler `backend/data/`.
- `testdata/testfartoy-v1/input.json` -- fasiten. Bare stien brukes her. Leses ikke.
- Ingen eksisterende backendkode. Strukturfrø: `backend/src/rbe/{main.py,config.py,api/}`, `backend/tests/{api/}`.

## Tasks & Acceptance

**Execution:**
- [x] `backend/pyproject.toml`, `backend/.python-version`, `backend/uv.lock` -- prosjektet `rbe` som over. `[tool.pytest.ini_options]`: `testpaths = ["tests"]`, `addopts = "--import-mode=importlib"`. `[tool.ruff]`: `line-length = 100`, lint `select = ["E", "F", "I", "UP", "B"]`
- [x] `backend/src/rbe/__init__.py`, `backend/src/rbe/api/__init__.py` -- pakker
- [x] `backend/src/rbe/config.py` -- `BACKEND_DIR`, `REPO_DIR`, `Settings` med `database_url`, `fixture_path`, `session_secret`, `demo_username`, `demo_password` og validatoren, og `get_settings()` -- AD-9
- [x] `backend/src/rbe/api/health.py` -- router med `GET /api/health`
- [x] `backend/src/rbe/main.py` -- `create_app()` som setter opp `logging.basicConfig`, kaller `get_settings()` og tar med routeren, og modulnivå `app`
- [x] `backend/.env.example` -- de fem variablene med kommentarer, uten ekte hemmeligheter
- [x] `.gitignore` -- legg til `backend/data/`
- [x] `backend/tests/api/test_health.py` -- helsesjekken via `TestClient`
- [x] `backend/tests/test_config.py` -- alle radene i I/O-matrisen. En autouse-fixture fjerner `RBE_*` (`monkeypatch.delenv(..., raising=False)`) og kaller `get_settings.cache_clear()`. `ast`-sjekken av `src/rbe` har en selvtest på en tekstbit med alle forbudte varianter (`import os as o; o.environ`, `from os import getenv`, `os.environ.get`, `os.environb`), der alle må bli funnet
- [x] `docs/ai-log.md` -- oppføring for story 1.1

**Commit-plan:** (1) uv-prosjekt og konfigurasjon, (2) helsesjekk og app, (3) tester og `.gitignore`. AI-loggen kommer i commit 3 eller i en egen fjerde commit.

**Acceptance Criteria:**
- Given en ren klone med uv, when `uv run fastapi dev src/rbe/main.py` kjøres i `backend/`, then henter uv Python 3.14, og `GET /api/health` svarer 200.
- Given `backend/`, when `uv run pytest`, `uv run ruff check` og `uv run ruff format --check` kjøres, then består alt med 0 funn.
- Given at `backend/.env` og `backend/data/` finnes lokalt, when `git status` kjøres, then er ingen av dem sporet.

## Implementation Notes

- Implementert i commit `5202b6c`, `95fb071` og `29711fa` på `story/1.1-backend-oppsett`. `uv lock` løste alle festede versjoner, og specen trengte ingen endring.
- **Sperre på denne maskinen:** Windows nekter å kjøre kjørbare filer som uv lager. Det gjelder Python i `uv venv` og konsollskriptene `pytest.exe` og `fastapi.exe`, som alle gir os error 5. Uv sin egen Python og Pythons egen `venv` virker. Løsning lokalt:
  - Opprett `backend/.venv` med `"%APPDATA%/uv/python/cpython-3.14.7-windows-x86_64-none/python.exe" -m venv .venv` før `uv sync`.
  - Bruk `uv run python -m pytest` og `uv run python -m fastapi dev src/rbe/main.py`. `uv run ruff …` virker som vanlig.
  - Verifisert slik: 11 tester består, ruff gir 0 funn, og `GET /api/health` gir `{"status":"ok"}` med advarselen i loggen.
- **Ikke prøvd på denne maskinen:** `uv run pytest` og `uv run fastapi dev` slik de står (første og andre akseptansekriterium). Sensorflyten endres ikke. Det må prøves på en maskin uten sperren, senest i story 1.7.
- **To advarsler under `fastapi dev`:** advarselen om tilfeldig nøkkel kommer to ganger, fordi både reloaderen og arbeidsprosessen bygger `Settings`. Hver prosess logger én, som specen sier.

## Spec Change Log

## Review Triage Log

Runde 1 (2026-11-24, lagene blind-hunter, edge-case-hunter og verification-gap). Rute: patch (P), defer (D) eller avvist (A).

| # | Lag | Funn | Vurdering | Begrunnelse | Rute |
|---|---|---|---|---|---|
| 1 | VG | Standardplasseringen av `.env` (`BACKEND_DIR/.env`) testes ikke | medium | Alle testene overstyrer `_env_file`, så om `env_file` endres til `".env"`, består fortsatt alle 11 | P |
| 2 | VG | Advarselen ved oppstart via `create_app()` testes ikke | medium | Fjernes `get_settings()`-kallet, består alle testene | P |
| 3 | VG, BH, ECH | `.env.example` foreslår relative stier for `RBE_FIXTURE_PATH` og `RBE_DATABASE_URL`, som regnes fra arbeidsmappa | medium | `Path` og URL brukes uendret, så eksempelet virker bare fra `backend/` | P (eksempelet krever absolutte stier) |
| 4 | BH, ECH, VG | `test_health` er ikke isolert fra lokal `RBE_*` og cache | low | Bare `test_config` har autouse-fixturen. Retting: flytt fixturen til `tests/conftest.py` | P |
| 5 | BH | `create_app()` kaster resultatet av `get_settings()` | low | Det er med vilje (spec: advarsel ved oppstart), men koden sier det ikke | P (kommentar) |
| 6 | BH | `.gitignore`-blokken deler Python-gruppen | low | Kosmetisk. Retting: flytt | P |
| 7 | BH | Ingen test overstyrer `RBE_FIXTURE_PATH` og demoverdiene fra miljøet | low | Bare `DATABASE_URL` og `SESSION_SECRET` testes | P |
| 8 | ECH | `import os.path` binder `os`, men `ast`-sjekken fanger ikke det | low | `alias.name == "os"` gjelder ikke `os.path` | P |
| 9 | ECH | `ast`-sjekken består uten å sjekke noe hvis `rglob` ikke finner filer | low | Retting: `assert files` | P |
| 10 | ECH | En `RBE_SESSION_SECRET` med bare mellomrom godtas | low | `not self.session_secret` er usann for `" "`. Retting: `.strip()` | P |
| 11 | BH, ECH | `backend/data/` opprettes ikke | medium | Specen utelater mapper i 1.1, og databasen kommer i 1.3 | D |
| 12 | ECH | `fixture_path` sjekkes ikke ved oppstart | low | Seed i 1.3 leser fila | D (sammen med 11) |
| 13 | BH | `app` på modulnivå har bivirkninger ved import | false | Specen krever `app` på modulnivå for `fastapi dev`. Den doble advarselen er dokumentert | A |
| 14 | BH | `session_secret` har fortsatt typen `str \| None` | low | Typen er fastsatt i den låste specen. Story 1.4 kan snevre den inn | A |
| 15 | BH | README er ikke oppdatert | false | Specen utsetter README til 1.7 med begrunnelse | A |
| 16 | BH | Ingen advarsel om standardverdiene for demobrukeren | false | Ikke krevd. NFR-2 sier at demopassordet er kjent | A |
| 17 | BH | Ingen test av prioritet mellom miljø og `.env`, og ingen test av rutene | false | Prioriteten er pydantic-settings sin oppførsel. Rutetesten hører til 1.4 | A |
| 18 | BH, ECH | `getattr(os, …)` og `__import__` fanges ikke | low | Usannsynlig i prosjektet, og en retting gjør sjekken mer komplisert | A |
| 19 | BH | AI-loggen mangler commit-hash og oppfølging av `uv run` | low | Rettes ved avslutningen (orkestratoren) | P (orkestrator) |
| 20 | BH | `uv.lock` er ikke med i diffen | false | Utelatt med vilje fordi fila er generert. Versjonene er sjekket med `uv lock` | A |
| 21 | ECH | URL-tegn (`%`, `#`, `?`) i stien til repoet | low | Repoet har ingen slike tegn, og en retting legger til kompleksitet | A |
| 22 | ECH | Installasjon som ikke er editable | false | Specen krever editable installasjon | A |
| 23 | ECH | Tomt brukernavn eller passord for demobrukeren godtas | low | Usannsynlig, og innloggingen kommer i 1.3–1.4 | A |
| 24 | ECH | Feilstavede `RBE_`-variabler ignoreres uten melding | low | `extra="ignore"` trengs for `.env` med andre nøkler | A |

## Verification

**Commands:**
- `uv run pytest` (i `backend/`) -- expected: alle tester består
- `uv run ruff check` og `uv run ruff format --check` (i `backend/`) -- expected: 0 funn
- `uv run --project backend fastapi dev backend/src/rbe/main.py` fra repo-rota (stien har mellomrom) + `curl -s localhost:8000/api/health` -- expected: `{"status":"ok"}`, og advarselen om tilfeldig nøkkel i loggen. Steget viser at stiene ikke avhenger av arbeidsmappa. Ren klone og Python-oppslaget prøves av det første akseptansekriteriet
