# Epic 1 Context: Kjørbart skjelett med innlogging og testdata

<!-- Compiled from planning artifacts. Edit freely. Regenerate with compile-epic-context if planning docs change. -->

## Goal

Epicen gir et skjelett som sensor kan klone og kjøre lokalt etter README. Backend (FastAPI) og frontend (Vite + React) starter hver med én kommando, og `uv run pytest` kjører testene. Demobrukeren logger inn og kommer til en rolig startside med fire dører. Testfartøyet (scenario A) er lest inn i databasen direkte fra fasiten, så app og fasit ikke kan sprike. Konfigurasjon, innloggingskrav på alle API-ruter, renhetstesten for MRP-kjernen og arbeidsflyten med én branch og én PR per story kommer på plass her. Alle senere epics bygger på dette.

## Stories

- Story 1.1: Backend-oppsett med helsesjekk og konfigurasjon
- Story 1.2: Kjernens datatyper og fasitparser
- Story 1.3: Database og seed ved tom database
- Story 1.4: Innlogging i backend
- Story 1.5: Frontend-oppsett, designtokens og innloggingsside
- Story 1.6: Menylinje og startside
- Story 1.7: README v1 med oppstart og tester

## Requirements & Constraints

- **Innlogging (FR-1):** én demobruker med brukernavn og passord, og utlogging. Uten innlogging gir alle skjermbilder og data-API-er avvisning (401) eller omdirigering til innlogging. Feil brukernavn og feil passord gir den samme meldingen: «Feil brukernavn eller passord.». Passordet lagres ikke i klartekst.
- **Testdata ved oppstart (FR-2):** en tom database får scenario A og demobrukeren. Databasen skal da inneholde nøyaktig varene, BOM-linjene, MPS-linjene, lagerbeholdningene og de åpne ordrene i `testdata/testfartoy-v1/input.json`: horisont 16, 11 varer, 12 BOM-linjer, 2 MPS-linjer og 2 åpne ordre. Dataene leses fra fasitfila, aldri fra en kopi.
- **Kjørbar lokalt (NFR-1, SM-3):** en ren maskin trenger bare uv og Node 26 LTS. Ingen kontoer, nøkler, Docker eller eksterne tjenester. En fremmed skal få app og tester til å kjøre med bare README, på under 15 minutter. Stien kan ha mellomrom (repoet ligger i en slik mappe).
- **Ingen hemmeligheter (NFR-2):** miljøvariabler og `backend/.env.example` uten ekte verdier. `.env` og `backend/data/` er gitignorert. Demopassordet er kjent og står i README.
- **Tilgjengelighet (NFR-6):** norsk UI i du-form, tastaturbruk, etiketter på alle felt, lesbar kontrast, beregnet på PC.
- **Sporbarhet (NFR-7):** tester og commits viser til FR-nummeret.
- **Felles ferdigkrav:** `uv run pytest`, `uv run ruff check` og `uv run ruff format --check` i `backend/` og `npx biome check` i `frontend/` gir 0 feil. Hver story leveres på branchen `story/<n.m>-<kort-navn>` som én PR med 2–5 commits på norsk i imperativ. Hver økt får en oppføring i `docs/ai-log.md`.

## Technical Decisions

- **Funksjonell kjerne, imperativt skall.** Lagene er `backend/src/rbe/{mrp,db,api}`, `fixture.py`, `config.py` og `main.py`, med testene i `tests/{mrp,api}`. Importene går bare fra api til db/mrp, fra db til fixture/mrp og fra fixture til mrp. `rbe.mrp` importerer aldri noe utenfor seg selv.
- **Ren kjerne (AD-1):** `rbe.mrp` bruker bare standardbiblioteket og egne moduler, uten fil-, nett- eller klokkekall. Inndatatypene er frosne dataklasser med fasitens feltnavn (`item`, `bom`, `qty_per`, `mps`, `hull_no`, `on_hand`, `scheduled_receipts`, `lot_sizing`, `lead_time_weeks`, `source`). `tests/mrp/test_core_is_pure.py` leser importene med `ast` og feiler ved brudd. Testen prøves med en forbudt import som legges inn midlertidig.
- **Fasitparser (AD-4):** `rbe.fixture` er den eneste parseren av fasitformatet. Seed bruker alltid scenario A. Tester bruker A–E: `mps` erstatter hele lista, `on_hand` overstyrer de oppgitte varene, og `bom_qty` overstyrer mengde per på de oppgitte linjene. Et ukjent scenario eller en fil som mangler, gir en tydelig feil. Stien kommer fra `RBE_FIXTURE_PATH`, med repoets fasit som standard, regnet ut fra pakkens plassering. `tests/conftest.py` gir testene stien.
- **Database (AD-5):** SQLite i `backend/data/` (gitignorert), opprettet med `create_all` og uten Alembic. Endres skjemaet, slettes fila. Ved oppstart sjekkes to ting hver for seg: er varetabellen tom, seedes scenario A, og mangler demobrukeren, opprettes den. Eksisterende data seedes aldri på nytt. Tabellene i epic 1 er varer, BOM-linjer, MPS-linjer, åpne ordre, planinnstillinger og brukere. Varenummeret er primærnøkkel for varer, og (forelder, barn) for BOM-linjer. MPS-linjer og åpne ordre får heltalls-id. Alle mengder og uker er heltall.
- **Innlogging (AD-8):** `SessionMiddleware` med signert cookie (httpOnly, SameSite=Lax), `pwdlib` med argon2 og `require_user` på alle `/api`-rutere. De eneste unntakene er `POST /api/auth/login` og `GET /api/health`. Endepunktene er `POST /api/auth/login`, `POST /api/auth/logout` og `GET /api/auth/me`. En rutetest går gjennom `app.routes` og feiler hvis en ny rute mangler `require_user`. `conftest.py` får en innlogget testklient som senere stories bruker. Presisert i 1.4: `require_user` settes på ruterne i `create_app()`, rutene leser brukeren med `CurrentUser`, og rutetesten bruker `iter_route_contexts`. Cookien heter `rbe_session` og varer 8 timer. Svarene er `{"username"}` fra login og me, 204 fra logout, og 401 med `detail` «Feil brukernavn eller passord.» eller «Du er ikke logget inn.».
- **Konfigurasjon (AD-9):** `pydantic-settings` med prefikset `RBE_`. Variablene er `RBE_DATABASE_URL`, `RBE_FIXTURE_PATH`, `RBE_SESSION_SECRET`, `RBE_DEMO_USERNAME` og `RBE_DEMO_PASSWORD`. `.env` er valgfri. Mangler sesjonsnøkkelen, lages en tilfeldig med en advarsel i loggen, og sesjonene overlever da ikke en omstart. Bare `config.py` leser `os.environ`. Standardstiene regnes ut fra pakkens plassering, ikke fra arbeidsmappa.
- **Kjøring (AD-10, AD-11):** uv henter Python 3.14 fra `.python-version`. Backend startes med `uv run fastapi dev src/rbe/main.py` i `backend/`, og frontend med `npm run dev` i `frontend/`. Vite-proxyen sender `/api` videre til backend, så nettleseren ser ett opphav og det trengs ingen CORS. Frontend lages fra Vite-malen `react-ts`. Integrasjonstestene bruker `TestClient` og en midlertidig SQLite-fil.
- **Stack:** versjonene er festet i `pyproject.toml`/`uv.lock` og `package.json`: FastAPI 0.165.0 (`fastapi[standard]`), SQLAlchemy 2.1.9, pydantic-settings 2.16.3, `pwdlib[argon2]` 0.4.2, itsdangerous 2.2.0, pytest 9.2.0, ruff 0.17.6, Vite 8.3.8, React 19.3.1, React Router 8.5.2, TypeScript ~7.0.2, Biome 2.6.8 og @fontsource/manrope 5.3.0.
- **Konvensjoner:** engelske navn i koden og `snake_case` i JSON over API-et. All UI-tekst er norsk. Backend logger med `logging`, aldri med `print`. API-et er REST under `/api` med ressurser i flertall og bindestrek. Feil har FastAPIs `detail`-format.

## UX & Interaction Patterns

- **Designtokens (UX-DR1):** farger, typografi, `rounded` og `spacing` fra frontmatter i DESIGN.md blir CSS-variabler. Det brukes ikke noe komponentbibliotek. Manrope (vekt 400–800) serveres lokalt fra `@fontsource/manrope`. Tall i tabeller er tabulære og høyrejusterte. `accent` (skifer) er den eneste fargen uten betydning. Rød, rav og grønn brukes bare med sin faste betydning, og `brand-red` bare i logoballen. Det er ingen mørk modus.
- **Logo og favicon (UX-DR2):** filene er `mockups/logo-3c.svg` og `mockups/favicon.svg` i UX-mappa. Menylinjen har logoen liggende, og innloggingssiden har den stablet.
- **Innlogging `/logg-inn` (UX-DR5):** et sentrert kort (ca. 320 px) med stablet logo, to felt med etikett og primærknappen «Logg inn» over hele bredden. Knappen viser «Logger inn …» og er deaktivert mens den arbeider. Under står «Demobrukeren står i README». Feil innlogging gir «Feil brukernavn eller passord.» koblet til skjemaet. Hele innloggingen kan gjøres med Tab og Enter. Hvis serveren ikke svarer, vises «Fikk ikke kontakt med serveren. Prøv igjen.» med `aria-live="assertive"`, og det som er skrevet, beholdes. Uinnlogget tilgang til en adresse sender brukeren til `/logg-inn` og tilbake til adressen etter innlogging. Et 401-svar senere sender til innlogging med «Du er logget ut. Logg inn igjen for å fortsette.».
- **Menylinje (UX-DR3):** står øverst på alle sider etter innlogging. Den har logoen (lenke til `/`), lenkene Bestillingsforslag og meldinger (`/forslag`), MRP-tabell (`/mrp`), BOM-tre (`/bom`) og MPS og lager (`/plan`), og «demo · Logg ut» til høyre. Valgt side har tekstfarge og en 2 px strek i aksentfargen. «Logg ut» sender brukeren til `/logg-inn`.
- **Startside `/` (UX-DR4):** havfotoet går over hele bredden (340 px, `alt=""`) og ligger i `imports/hav-stavanger-oleksii-topolianskyi.webp` i UX-mappa. Oppå bildet ligger en lys velkomstflate med «Velkommen» og «Hva vil du gjøre?». Fire dør-kort står i fast rekkefølge (forslag, MRP-tabell, BOM-tre, MPS og lager), og hvert kort er én lenke med tittel, én setning og «Åpne →». Statuslinjen er nøytral og sier «Ingen MRP-kjøring ennå.». Den har aldri antall eller farge. Fotografen Oleksii Topolianskyi (Unsplash) krediteres på siden. Startsiden viser aldri meldinger.
- **Plassholdersider:** `/forslag`, `/mrp`, `/bom` og `/plan` får hver sin H1 og dokumenttittel på formen «… – Red Ball Express». Innholdet kommer i senere epics.
- **Tilgjengelighet (UX-DR21):** målet er WCAG 2.2 AA. «Hopp til innhold» er første element med fokus. Hver side har en unik dokumenttittel, og fokus flyttes til H1 ved sidebytte. Alt som kan få fokus, har en synlig fokusramme i aksentfargen. Klikkmål er minst 24 × 24 px, og dokumentet har `lang="no"`. Ingen funksjon finnes bare ved hover.
- **Layout (UX-DR22):** innholdet er maks 1280 px bredt med 24 px sidemarg. Målbredden er minst 1280 px, og layouten fungerer ned til 1024 px. Mobil er ikke et mål.
- **Media:** Claude tar skjermbildene `docs/media/YYYY-MM-DD-innlogging.png` (1.5) og `docs/media/YYYY-MM-DD-startside.png` (1.6). README bruker skjermbildet av startsiden.

## Cross-Story Dependencies

- 1.1 er grunnlaget: `config.py`, testoppsettet og `main.py`.
- 1.2 trenger konfigurasjonen fra 1.1 for `RBE_FIXTURE_PATH`. Typene og parseren fra 1.2 brukes av seed i 1.3 og av alle fasittester i epic 2.
- 1.3 bruker `rbe.fixture` (1.2) og passordhashing med `pwdlib`. Demobrukeren fra 1.3 trengs i 1.4.
- 1.4 gir `require_user`, rutetesten og den innloggede testklienten som alle senere API-stories bruker.
- 1.5 bygger på innloggings-API-et fra 1.4, og 1.6 bygger på rutingen og innloggingssiden fra 1.5. Statuslinjen om siste kjøring får ekte data i story 3.2, og stegene for innlogging og startside føres inn i `docs/testplan.md` når den opprettes i 3.2.
- 1.7 kommer til slutt: den trenger hele oppstarten og skjermbildet fra 1.6, og prøves fra en ny klone på Windows.
- Epic 4 bygger på databasen fra 1.3: tilbakestilling bruker `rbe.fixture` på samme måte, og planinnstillingene får telleren `input_revision`.
