# Story 1.4: innlogging i backend

## 2026-11-26 kl. 11:58 — Thobias Navelsaker

### Oppgave
Fortsette med story 1.4: demobrukeren skal kunne logge inn og ut med signert sesjonscookie, og alle `/api`-ruter utenom innlogging og helsesjekk skal gi 401 uten innlogging (FR-1, AD-8).

### Plan
- `bmad-build` på branchen `story/1.4-innlogging-i-backend`. Planlagt ut fra epic-1-konteksten og specen for 1.3.
- Spec: [spec-1-4-innlogging-i-backend.md](../../_bmad-output/implementation-artifacts/spec-1-4-innlogging-i-backend.md). Brukeren godkjente den uten endringer og valgte å beholde den samlet (ca. 2 000 tokens).
- Arbeidsfordeling:
  - En subagent implementerte.
  - Tre uavhengige lag gikk gjennom koden: blind-hunter, edge-case-hunter og verification-gap.
  - Funnene som skulle rettes, ble sendt tilbake til implementeringsagenten.

### Resultat
- **Kode** (`eef5a41`):
  - Ny avhengighet: `itsdangerous==2.2.0`.
  - `rbe/api/deps.py` med `get_session`, `require_user` og `CurrentUser`.
  - `rbe/api/auth.py` med login, logout (204) og me.
  - `SessionMiddleware` i `main.py`. Cookien heter `rbe_session`, er httpOnly og SameSite=Lax og varer 8 timer.
  - `require_user` settes på ruterne i `create_app()`.
- **Tester** (`6970659`, `56d2387`):
  - Testklientene `client` og `logged_in_client` i `conftest.py`.
  - `test_auth.py` dekker hele I/O-matrisen, sesjonsnøkkelen fra konfigurasjonen og at innlogging tømmer sesjonen.
  - Rutetesten `test_routes_require_login.py` sjekker både avhengighetstreet og 401 for hver rute. En egen test viser at den finner en åpen rute.
- **Avvik ført tilbake:** FastAPI 0.165 flater ikke ut inkluderte rutere, så rutetesten bruker `iter_route_contexts`. Rutene leser brukeren med `CurrentUser`, ikke med `require_user`. Begge deler er presisert i AD-8 i arkitekturen (`29d942e`).
- **Gjennomgang:** 15 funn. 5 ble rettet, og 10 ble avvist med begrunnelse i triageloggen i specen. Ingenting ble utsatt.
- **Verifisering:** 107 tester består, og `ruff check` og `ruff format --check` gir 0 funn. Akseptansekriteriet er prøvd: uten `require_user` feiler rutetesten og nevner begge rutene.
- **Status:** AI-logg, spec og sprintstatus (1.4 → review) ligger i `2be743c`. Ingen skjermbilder, fordi storyen ikke har noe brukergrensesnitt. Branchen ble pushet til origin etter at brukeren ba om det. Ingen PR er laget ennå.

### Åpne punkter
- Ingen.
