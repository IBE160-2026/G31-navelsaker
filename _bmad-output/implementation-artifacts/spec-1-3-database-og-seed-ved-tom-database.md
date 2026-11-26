---
title: 'Story 1.3: Database og seed ved tom database'
type: 'feature'
created: '2026-11-26'
status: 'done'
baseline_commit: '08309039b2bec24ea656c83b4683673359080049'
route: 'dispatch'
review_loop_iteration: 0
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-1-context.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Når appen starter første gang, er databasen tom. Sensor skal møte testfartøyet uten å legge inn noe selv, og demobrukeren skal finnes med et passord som ikke er lagret i klartekst (FR-2, FR-1, AD-4, AD-5).

**Approach:** Legg til SQLite via SQLAlchemy i `rbe.db`. Ved oppstart av appen opprettes tabellene med `create_all`. Er varetabellen tom, lastes scenario A inn via `rbe.fixture` i én transaksjon. Mangler demobrukeren, opprettes den med en argon2-hash. En lesefunksjon gir inndataene tilbake som `MrpInput`.

## Boundaries & Constraints

**Always:**
- Avhengigheter med `==`: `sqlalchemy==2.1.9` og `pwdlib[argon2]==0.4.2`. Stopp og før avviket hvis `uv lock` ikke klarer å løse dem.
- `rbe/db/` har `models.py` (SQLAlchemy 2-deklarativ), `session.py` (engine og sessionmaker fra `database_url`), `seed.py` og `repository.py`. `rbe.db` kan importere `rbe.fixture`, `rbe.mrp` og `rbe.config`, men ikke `rbe.api`.
- Tabeller (AD-5):
  - `items`: `id` er varenummeret og primærnøkkel, pluss `name`, `source`, `unit`, `lead_time_weeks`, `on_hand`, `safety_stock`, `lot_rule` og `lot_quantity` (kan være tom).
  - `bom_lines`: (`parent`, `child`) er primærnøkkel, begge med fremmednøkkel til varer, pluss `qty_per`.
  - `mps_lines`: heltalls-id, `item` (fremmednøkkel), `week`, `quantity` og `hull_no`, som er unik (FR-8).
  - `scheduled_receipts`: heltalls-id, `item` (fremmednøkkel), `week`, `quantity` og `note`.
  - `planning_settings`: én rad med `first_week` og `horizon_weeks`.
  - `users`: heltalls-id, `username` (unik) og `password_hash`.
  - Alle mengder og uker er heltall. `input_revision` kommer i story 4.6, ikke nå.
- Seed lagrer alle feltene i `MrpInput` (også `source`, `unit`, `safety_stock`, `note` og `first_week`), slik at `repository.read_input(session)` gir tilbake det samme som `load_input(fixture_path, "A")`.
- `read_input` sorterer deterministisk: varer på `id`, BOM-linjer på (`parent`, `child`), MPS-linjer og åpne ordre på `id`.
- Oppstart skjer i en FastAPI-`lifespan` i `create_app()`, ikke ved import. Rekkefølge:
  1. Opprett mappa til SQLite-fila hvis den mangler.
  2. Sjekk at `fixture_path` finnes. Mangler den, stopper oppstarten med en `FixtureError` som nevner stien, også når databasen allerede er seedet (fra `deferred-work.md`).
  3. Kjør `create_all`.
  4. Seed hvis varetabellen er tom.
  5. Sørg for demobrukeren: mangler en bruker med `demo_username`, opprettes den. Finnes den, men `pwdlib` godkjenner ikke `demo_password` mot hashen, oppdateres hashen (besluttet av Thobias 2026-11-26, alternativ b). Passordet i konfigurasjonen gjelder da alltid, og databasefila trenger aldri slettes for å bytte demopassord. Andre brukere røres ikke.

  Seed og demobruker sjekkes og skrives i hver sin transaksjon, og ett av punktene logges med `logging`.
- Engine og sessionmaker legges på `app.state`, så senere stories kan hente dem.
- Testfunksjoner har kravnummeret i navnet, for eksempel `test_fr2_seed_matches_fixture`.

**Never:**
- Ingen Alembic eller migrering. Endres skjemaet, slettes fila (AD-5).
- Ingen innlogging, ruter eller API for data (story 1.4 og senere).
- Ingen kopi av fasitdata i koden. Seed leser alltid via `rbe.fixture`.
- Ikke endre `testdata/`.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Tom database | Ingen fil, og mappa finnes ikke | Mappa og fila opprettes, alle tabellene finnes, `read_input` == scenario A, og demobrukeren finnes | – |
| Omstart | Seedet database med endret `on_hand` | Ingenting seedes på nytt, og endringen beholdes. Fortsatt én demobruker | – |
| Bare brukeren mangler | Varer finnes, `users` er tom | Bare demobrukeren opprettes. Inndataene er urørt | – |
| Endret demopassord | Seedet database, så `RBE_DEMO_PASSWORD=nytt` og ny oppstart | Hashen er oppdatert: `nytt` godkjennes, `demo` avvises. Fortsatt én demobruker, og inndataene er urørt | – |
| Passord | Etter seed | `password_hash` begynner med `$argon2`, er ikke `demo`, og `pwdlib` godkjenner `demo` mot hashen | – |
| Fasiten mangler | `RBE_FIXTURE_PATH` peker på en fil som ikke finnes, med tom eller seedet database | Appen starter ikke | `FixtureError` med stien |
| Sti med mellomrom | `RBE_DATABASE_URL` til `tmp/mappe med mellomrom/rbe.db` | Fungerer som tom database | – |

</frozen-after-approval>

## Code Map

- `backend/src/rbe/config.py` -- `Settings.database_url` (standard `sqlite:///…/backend/data/rbe.db`), `fixture_path`, `demo_username` og `demo_password`, og `get_settings()`. Skal ikke endres.
- `backend/src/rbe/fixture.py` -- `load_input(path, scenario)` og `FixtureError`. Gjenbrukes til seed og til sjekken av stien.
- `backend/src/rbe/mrp/types.py` -- `MrpInput` og de andre typene. `read_input` bygger disse.
- `backend/src/rbe/main.py` -- `create_app()` med `basicConfig` og `get_settings()`. Utvides med `lifespan`. Helsesjekken skal virke uten database (`TestClient` uten `with` kjører ikke `lifespan`).
- `backend/tests/conftest.py` -- `clean_env`, `fixture_dir` og `input_path`. Kan få en fixture som lager en midlertidig databasesti.
- `backend/tests/mrp/test_core_is_pure.py` -- skal fortsatt bestå. `rbe.db` er forbudt i kjernen.

## Tasks & Acceptance

**Execution:**
- [x] `backend/pyproject.toml`, `backend/uv.lock` -- legg til `sqlalchemy==2.1.9` og `pwdlib[argon2]==0.4.2`
- [x] `backend/src/rbe/db/__init__.py`, `models.py` og `session.py` -- tabellene, og `make_engine(url)` som oppretter mappa til SQLite-fila
- [x] `backend/src/rbe/db/seed.py` -- `check_fixture(path)`, `seed_if_empty(session, data)`, `ensure_demo_user(session, settings)` og `startup(engine, settings)`
- [x] `backend/src/rbe/db/repository.py` -- `read_input(session) -> MrpInput`
- [x] `backend/src/rbe/main.py` -- `lifespan` som kjører `startup` og legger engine og sessionmaker på `app.state`
- [x] `backend/tests/api/test_seed.py` -- alle radene i I/O-matrisen, med `with TestClient(create_app())` og `RBE_DATABASE_URL` mot en midlertidig fil (`monkeypatch.setenv` og `get_settings.cache_clear()`)
- [x] `docs/ai-log.md` -- oppføring for story 1.3

**Commit-plan:** (1) avhengigheter og tabeller, (2) seed, demobruker og oppstart med tester (FR-2, FR-1), (3) AI-logg.

**Acceptance Criteria:**
- Given `backend/`, when testene, `ruff check` og `ruff format --check` kjøres, then består alt med 0 funn.
- Given at backend startes lokalt to ganger, when databasefila finnes etter første gang, then seedes den ikke på nytt, og loggen sier at databasen allerede har data.

## Implementation Notes

- Implementert i `5bc79c3` (avhengigheter og tabeller), `1746ff5` (seed, demobruker, oppstart og tester) og `05daff7` (AI-logg). `uv add` løste versjonene uten avvik.
- **Sortering:** `input.json` har ikke varene og BOM-linjene sortert. `read_input` sorterer som specen krever, så testen sorterer `load_input(..., "A")` på samme måte før de sammenlignes. Innholdet er det samme, bare rekkefølgen er normalisert.
- **Fasiten leses ved hver oppstart:** `startup` kjører `load_input` også når databasen allerede er seedet. Dermed stopper også en ødelagt fasit oppstarten, ikke bare en fil som mangler. Det er i tråd med at manglende fasit skal stoppe oppstarten. Tilbakestilling (4.3) trenger uansett en gyldig fasit.
- `make_engine` slår på `PRAGMA foreign_keys=ON` for SQLite, så fremmednøklene faktisk håndheves.
- To oppstarter lokalt med `uv run python -m fastapi run` ga riktig logg første og andre gang. `backend/data/` ble slettet etterpå.

- **Etter gjennomgangen (`d6fbc6b`):**
  - Testene bruker `make_engine`, og en ny test viser at fremmednøklene håndheves. Testen feiler når pragma-lytteren fjernes, og det er prøvd av orkestratoren.
  - Testen for manglende fasit treffer nå selve feilmeldingen.
  - `test_seed.py` leser ikke en lokal `.env`.
  - `ensure_demo_user` bruker `verify_and_update`, og alle tre utfallene er testet med loggtekst.
  - Endringen av skjema mot en gammel databasefil er utsatt til 4.6 i `deferred-work.md`.
  - 89 tester består.

## Spec Change Log

## Review Triage Log

Runde 1 (2026-11-26, lagene blind-hunter (BH), edge-case-hunter (ECH) og verification-gap (VG)). Rute: patch (P), defer (D) eller avvist (A).

| # | Lag | Funn | Vurdering | Begrunnelse | Rute |
|---|---|---|---|---|---|
| 1 | VG, BH | At fremmednøklene håndheves, testes ikke, og `_session` i testene lager en egen engine uten pragmaet | medium | Fjernes `event.listen`, består alle testene likevel, og dokumentasjonen sier at fremmednøklene håndheves | P |
| 2 | BH, ECH | `match="finnes ikke"` treffer mappenavnet i testen | medium | Testen består uansett hvilken melding som kommer | P |
| 3 | VG | `test_seed.py` kan lese en lokal `backend/.env` | medium | `clean_env` fjerner bare variablene i miljøet. Demobrukeren og fasitstien kan da komme fra fila | P (autouse i modulen) |
| 4 | BH, ECH | Grenen «unchanged», loggmeldingene og `verify_and_update` testes ikke | low | Det er billig å teste med `caplog`, og `verify_and_update` er en direkte utskifting | P |
| 5 | BH | `_enable_foreign_keys` mangler typer, og `make_sessionmaker` mangler docstring | low | Kosmetisk, men en direkte retting | P |
| 6 | BH | AI-loggen nevner ikke hvorfor det ikke er skjermbilde, og hva som ikke er committet | low | Rettes ved avslutningen | P (orkestrator) |
| 7 | BH | `create_all` legger ikke til nye kolonner i en database som allerede finnes | medium | Det rammer først når skjemaet endres (`input_revision` i 4.6). Da får en gammel lokal fil en uklar feil i stedet for en melding om å slette den | D (4.6) |
| 8 | ECH | En ødelagt hash gir `UnknownHashError` | low | Hashen skrives bare av appen. Usannsynlig | A |
| 9 | ECH | En fasit som bryter databaseregler, gir rå `IntegrityError` | low | Fasiten er validert av parseren og fasittestene | A |
| 10 | BH, ECH | Flere workere kan seede samtidig | low | Lokal kjøring med én prosess (AD-11) | A |
| 11 | BH, ECH | Mangler `planning_settings` gir `NoResultFound`, og `merge` brukes i stedet for `add` | low | Raden skrives i samme transaksjon som varene. `merge` er ufarlig | A |
| 12 | BH, ECH | `read_input` stoler på databasen (`cast`, ingen CHECK) | low | Valideringen av skrivinger kommer i API-et (AD-7, 4.1 og 4.5) | A |
| 13 | BH | MPS sorteres på id, ikke på (uke, byggenummer) | false | Specen har valgt id. Kjernen sorterer det den trenger selv (AD-3) | A |
| 14 | BH | Antallene er hardkodet i testen | false | Det er tallene fra akseptansekriteriene i storyen. Hele innholdet sammenlignes dessuten med fasiten | A |
| 15 | ECH | SQLite i minnet (`:memory:`) | false | Støttes ikke og brukes ikke | A |
| 16 | ECH | Tomt brukernavn eller passord for demobrukeren | low | Samme vurdering som i 1.1 | A |
| 17 | BH, ECH | Fasiten leses ved hver oppstart, og `check_fixture` er overflødig | false | Det er med vilje og dokumentert i Implementation Notes. `check_fixture` gir en tydeligere melding | A |

## Verification

**Commands:**
- `uv run pytest` (i `backend/`) -- expected: alle tester består. **På denne maskinen:** bruk `uv run python -m pytest` (Windows-sperre, se spec 1.1)
- `uv run ruff check` og `uv run ruff format --check` (i `backend/`) -- expected: 0 funn
- `uv run python -m fastapi dev src/rbe/main.py` to ganger (i `backend/`) -- expected: første gang logges seed av scenario A og opprettelse av demobrukeren, andre gang ikke. Slett `backend/data/rbe.db` etterpå
