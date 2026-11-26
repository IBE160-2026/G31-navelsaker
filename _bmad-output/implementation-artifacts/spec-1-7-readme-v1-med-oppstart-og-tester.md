---
title: 'Story 1.7: README v1 med oppstart og tester'
type: 'chore'
created: '2026-11-26'
status: 'in-progress'
baseline_commit: 'd6de94ae2c08579b2984f2e24111c66d32e801c6'
route: 'dispatch'
review_loop_iteration: 0
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-1-context.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** README sier i dag ingenting om hvordan appen startes, logges inn i eller testes. Sensor skal klone repoet og få app og tester til å kjøre med bare README, på under 15 minutter, uten kontoer eller hemmeligheter (NFR-1, NFR-2, SM-3).

**Approach:** Skriv README v1 på norsk med hva appen gjør, skjermbilde og video, forutsetninger, oppstart av backend og frontend i hver sin terminal, demobrukeren, testkommandoene, feilsøking og lenker til planleggingsdokumentene. Prøv README steg for steg fra en ny klone i en mappe med mellomrom på Windows, og rett README der den ikke stemmer.

## Boundaries & Constraints

**Always:**
- README er skrevet for sensor, som ikke kjenner prosjektet. Den er kort og har kommandoer i kodeblokker, og alt står i den rekkefølgen det gjøres.
- **Innhold, i denne rekkefølgen:**
  1. Tittel og 2–3 setninger om hva appen gjør (MRP for skipsbygging med testfartøyet).
  2. Skjermbildet `docs/media/2026-11-26-startside.png` og en lenke til videoen `docs/media/2026-11-26-innlogging-og-meny.mp4`.
  3. Forutsetninger: Git, uv og Node 26 LTS, med lenker til installasjon. Det trengs ingen kontoer, nøkler eller Docker.
  4. Oppstart:
     - `git clone` og `cd`.
     - Terminal 1 i `backend/` starter backend (port 8000). Første start oppretter databasen og legger inn testfartøyet.
     - Terminal 2 i `frontend/`: `npm install` og `npm run dev`.
     - Åpne http://localhost:5173.
  5. Innlogging: brukernavn `demo` og passord `demo`. Det kan endres med `RBE_DEMO_USERNAME` og `RBE_DEMO_PASSWORD`, og `backend/.env.example` lister alle variablene. Dette er det kjente demopassordet og ingen hemmelighet.
  6. Tester og kvalitetssjekk:
     - Backend: tester og `uv run ruff check` / `uv run ruff format --check`.
     - Frontend: `npm run test`, `npx biome check` og `npm run build`.
     - Testene leser fasiten i `testdata/testfartoy-v1/`.
  7. Feilsøking:
     - «Fikk ikke kontakt med serveren. Prøv igjen.» betyr at backend ikke kjører.
     - Er port 5173 opptatt, velger Vite en annen port, og da gjelder den adressen.
     - Databasen tilbakestilles ved å slette `backend/data/rbe.db`.
  8. Lenker til brief, PRD, arkitektur, UX (DESIGN.md og EXPERIENCE.md), epics og sprintstatus, fasiten og AI-loggen.
  9. Medlemmer og bildekreditering beholdes fra dagens README.
- Ingen ekte hemmeligheter i README eller i skjermbildet.
- **Prøvd fra en ny klone:** `git clone` fra GitHub (`main`, etter at denne branchen er flettet, eller fra denne branchen) til en mappe med mellomrom i scratchpad. Følg README bokstavelig. Backend og frontend starter, innloggingen virker i Edge uten vindu, og testene består. Alt som måtte gjøres annerledes enn README sier, rettes i README. Steg og utfall føres i Implementation Notes. Kjører det allerede servere på 8000 eller 5173 fra økten, stoppes de først.
- **Beslutning om kommandoene** (Thobias 2026-11-26: «den som er best og oppfyller kravene sensor stiller», alternativ B):
  - Hovedkommandoene i README er `uv run python -m pytest` og `uv run python -m fastapi dev src/rbe/main.py`, fordi de virker både med og uten Windows-sperren på konsollskriptene fra uv (os error 5, spec 1.1). En setning sier at `uv run pytest` gir det samme på en maskin uten sperren.
  - Feilsøkingsdelen forklarer hva man gjør ved os error 5 på selve Python i `.venv`: lag `.venv` med Pythons egen `venv` før `uv sync`.
  - Avviket fra ordlyden i AD-10, AD-11 og epics.md føres tilbake i arkitekturen.
  - Det åpne punktet fra story 1.1 lukkes når prøven fra en ny klone har bestått.

**Never:**
- Ingen endring i appkoden.
- Ingen oppstartsskript, Docker eller Makefile. README er inngangen (AD-11).
- Ingen kopi av innholdet i planleggingsdokumentene. README lenker til dem.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Ny klone | Tom mappe med mellomrom i navnet, uv og Node installert | Backend og frontend starter etter README, og `demo`/`demo` gir startsiden | – |
| Første start | Ingen `backend/data/` | Mappa og databasen opprettes, og testfartøyet legges inn | – |
| Tester | Ny klone | Backend- og frontendtestene består med kommandoene i README | – |
| Backend kjører ikke | Bare frontend startet | Innloggingen viser serverfeilen. README forklarer hvorfor | – |

</frozen-after-approval>

## Code Map

- `README.md` -- dagens innhold: tittel, kort beskrivelse, lenker, medlemmer og bildekreditering. Skrives om.
- `backend/.env.example` -- variablene med standardverdier. Lenkes til, og kopieres ikke.
- `backend/src/rbe/config.py` -- standard database `backend/data/rbe.db` og demobruker `demo`/`demo`.
- `frontend/package.json` -- skriptene `dev`, `build`, `check` og `test`.
- `frontend/vite.config.ts` -- proxyen til `127.0.0.1:8000`, så backend må kjøre på port 8000.
- `docs/media/` -- `2026-11-26-startside.png`, `2026-11-26-innlogging.png` og `2026-11-26-innlogging-og-meny.mp4`.
- Dokumentene det lenkes til:
  - `_bmad-output/planning-artifacts/briefs/brief-Red Ball Express-2026-09-16/brief.md`
  - `prds/prd-Red Ball Express-2026-11-24/prd.md`
  - `architecture/architecture-Red Ball Express-2026-11-24/ARCHITECTURE-SPINE.md`
  - `ux-designs/ux-Red Ball Express-2026-11-24/DESIGN.md` og `EXPERIENCE.md`
  - `epics.md`
  - `_bmad-output/implementation-artifacts/sprint-status.yaml`
  - `testdata/testfartoy-v1/README.md`
  - `docs/ai-log.md`
  
  Mellomrom i stiene må kodes som `%20` i Markdown-lenker.
- `_bmad-output/implementation-artifacts/spec-1-1-backend-oppsett-med-helsesjekk-og-konfigurasjon.md` linje 84–88 -- løsningen for sperren.

## Tasks & Acceptance

**Execution:**
- [x] `README.md` -- skriv om etter innholdslista
- [x] Ny klone i scratchpad -- prøv README bokstavelig. Rett README, og før steg og utfall i Implementation Notes
- [x] `_bmad-output/planning-artifacts/architecture/architecture-Red Ball Express-2026-11-24/ARCHITECTURE-SPINE.md` -- AD-10 og AD-11: før inn `python -m`-formen som anbefalt kommando i README, og hvorfor
- [x] `docs/ai-log.md` -- oppføring for story 1.7

**Commit-plan:** (1) README v1 (NFR-1, NFR-2, SM-3), (2) rettelser etter prøven fra ny klone, hvis noen, (3) AI-logg.

**Acceptance Criteria:**
- Given README, when en som ikke kjenner prosjektet leser den, then finner de alt i innholdslista, minst ett skjermbilde, og ingen ekte hemmeligheter.
- Given at alle relative lenker og bildestier i README sjekkes mot filene i repoet, then peker alle på filer som finnes.

## Verification

**Commands:**
- Prøven fra ny klone (se Always) -- expected: backend og frontend starter, innloggingen virker, og testene består
- Et lite skript som sjekker at hver relativ lenke i README finnes på disk -- expected: 0 døde lenker

## Implementation Notes

- README skrevet i `8225c6b`, rettet etter prøven i `7466eac`. AD-10 og AD-11 er presisert i `f3518eb`.
- **Klonekilde:** branchen er ikke pushet (push bare når brukeren ber om det), så prøven klonet `main` fra GitHub (`288e2a3`). `git diff --stat origin/main HEAD` viser at koden er den samme. Forskjellen er README, dokumentasjon og skjermbilder. Kommandoene ble fulgt fra README på denne branchen.
- **Stopp av servere fra økten:** det kjørte backend på 8000 og Vite på 5173 og 5174 fra `C:\HiM\…\Red Ball Express`. Å stoppe dem ble nektet av tillatelsessystemet. Prøven er derfor gjort med to avvik: backend fra klonen ble startet med `--port 8001`, og Vite fra klonen fikk port 5175 og sendte `/api` til backend på 8000 fra repoet (samme kode).
- **Steg og utfall:**
  1. `git clone` til scratchpad (`…\scratchpad\ny klone\`) feilet med «Filename too long», fordi scratchpad-stien alene er ca. 150 tegn. Med `core.longpaths` lyktes klonen, men `uv run python -m pytest` ga os error 5 (sperren), og etter løsningen fra Feilsøking manglet en fil i `.venv` (`ModuleNotFoundError: _pytest.assertion._compare_mapping`) og `ensurepip` feilet, begge på grunn av grensen på 260 tegn. En kortere mappe i scratchpad (`k 1`) ga også «Filename too long» ved checkout. **Rettet i README:** kort sti anbefales ved klonen, og feilen står under Feilsøking.
  2. Ny klone i `%LOCALAPPDATA%\Temp\rbe proeve\G31-navelsaker` (kort sti med mellomrom). `uv run python -m pytest` i `backend/`: uv hentet miljøet, og 107 tester besto. Her var Python i `.venv` ikke sperret, men `uv run pytest` ga `Failed to spawn: pytest … os error 5`. Det bekrefter valget av `python -m`-formen. `uv run ruff check` ga «All checks passed!», og `uv run ruff format --check` «23 files already formatted».
  3. `uv run python -m fastapi dev src/rbe/main.py --port 8001`: `backend/data/` og `rbe.db` ble opprettet, loggen sa «Tom database: la inn scenario A …» og «Opprettet demobrukeren», og advarselen om sesjonsnøkkelen kom. Tabellene hadde 11 varer, 12 BOM-linjer, 2 MPS-linjer, 2 åpne ordre, 1 planinnstilling og 1 bruker. `GET /api/health` ga `{"status":"ok"}`, innlogging med `demo`/`demo` ga `{"username":"demo"}`, og `GET /api/auth/me` uten cookie ga 401.
  4. `npm install` (0 sårbarheter), `npm run test` (10 tester består), `npx biome check` (29 filer, 0 funn) og `npm run build` (bygget) i `frontend/`.
  5. `npm run dev`: Vite skrev «Port 5173 is in use, trying another one…» og valgte 5175, som Feilsøking sier. Edge uten vindu over DevTools-protokollen: `/` sendte til `/logg-inn`, `demo`/`demo` og Enter ga startsiden med dokumenttittelen «Velkommen – Red Ball Express», menylinjen og dørene.
  6. Løsningen på os error 5 fra Feilsøking (slett `.venv`, `& (uv python find --no-project 3.14) -m venv .venv`, `uv sync`) er kjørt i en egen klone (`klone 2`): `uv sync` godtok miljøet, og 107 tester besto. `uv python install` ble fjernet fra løsningen, fordi Python allerede er hentet når feilen oppstår, og kommandoen bare ga en advarsel om `python3.14.exe` i `~/.local/bin`.
- **Ikke prøvd i denne prøven:** raden «Backend kjører ikke» (krever at backend på 8000 stoppes). Meldingen ble prøvd i story 1.5 og 1.6. `uv run fastapi dev` uten `python -m` er ikke prøvd, men `uv run pytest` viser at sperren på konsollskriptene gjelder her.
- **Lenkesjekk:** et lite skript i scratchpad fant 13 relative lenker og bildestier i README, og 0 døde.
- Det åpne punktet fra story 1.1 (`uv run pytest` og `uv run fastapi dev` ikke prøvd) lukkes: prøven fra en ny klone besto med kommandoene i README, og den korte formen er bevisst ikke hovedkommando lenger (AD-11).

## Spec Change Log

## Review Triage Log
