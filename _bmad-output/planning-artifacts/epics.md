---
stepsCompleted: [1, 2, 3, 4]
inputDocuments:
  - prds/prd-Red Ball Express-2026-11-24/prd.md
  - prds/prd-Red Ball Express-2026-11-24/addendum.md
  - prds/prd-Red Ball Express-2026-11-24/.memlog.md
  - architecture/architecture-Red Ball Express-2026-11-24/ARCHITECTURE-SPINE.md
  - architecture/architecture-Red Ball Express-2026-11-24/.memlog.md
  - ux-designs/ux-Red Ball Express-2026-11-24/DESIGN.md
  - ux-designs/ux-Red Ball Express-2026-11-24/EXPERIENCE.md
  - ux-designs/ux-Red Ball Express-2026-11-24/mockups/key-screens.html
  - ../../testdata/testfartoy-v1/README.md
---

# Red Ball Express v1 – epics og stories

## Oversikt

Dette dokumentet bryter kravene i PRD-en, arkitekturen og UX-spinene ned i epics og stories for v1. Kravnummerene (FR-n, NFR-n, SM-n) er de faste nummerene fra [PRD-en](prds/prd-Red%20Ball%20Express-2026-11-24/prd.md). AD-n viser til [arkitekturen](architecture/architecture-Red%20Ball%20Express-2026-11-24/ARCHITECTURE-SPINE.md). Scenario A–E og reglene R1–R11 viser til [fasiten](../../testdata/testfartoy-v1/README.md).

## Kravoversikt

### Funksjonelle krav

- **FR-1** Logge inn og ut: demobrukeren logger inn med brukernavn og passord og kan logge ut. Uten innlogging gir alle skjermbilder og API-kall med data avvisning eller omdirigering. Feil brukernavn og feil passord gir samme melding. Passord lagres ikke i klartekst.
- **FR-2** Testdata ved oppstart: tom database får scenario A fra `testdata/testfartoy-v1/input.json` og demobrukeren. Databasen inneholder da nøyaktig dataene i `input.json`, og de leses fra fasitfila, ikke fra en kopi.
- **FR-3** Tilbakestille til testdata: erstatter MPS, lagerbeholdning, åpne ordre, mengde per, ledetider og partiregler med scenario A og sletter MRP-kjøringer, etter bekreftelse. En kjøring rett etterpå gir scenario A i `expected.json`.
- **FR-4** Vise BOM-treet: alle nivåer og alle 12 BOM-linjer, også når en vare har flere foreldre (PLT-900 under SEK-110, STY-310 og DEK-300). Hver node viser varenummer, navn, mengde per, type og ledetid, og lavnivåkoden kan ses.
- **FR-5** Redigere MPS: legge til, endre (uke, antall) og slette MPS-linjer.
- **FR-6** Redigere lagerbeholdning for hver vare.
- **FR-7** Redigere åpne ordre: legge til, endre (uke, antall) og slette.
- **FR-8** Validere inndata: uke i horisonten (1–16), antall ≥ 1, lager ≥ 0, MPS bare for nivå 0-varen, byggenummer ≥ 1 og unikt i hovedplanen, mengde per ≥ 1, ledetid ≥ 0, FOQ-kvantum ≥ 1, alle som heltall. Ugyldig verdi gir feilmelding ved feltet, og databasen er uendret.
- **FR-9** Kjøre MRP: knappen «Kjør MRP» starter en kjøring som lagres. Kjøringen bruker inndataene slik de er lagret når knappen trykkes. To kjøringer på samme inndata gir identisk resultat.
- **FR-10** BOM-eksplosjon med lavnivåkoder: `gross_requirements` og `low_level_code` stemmer med `expected.json` for scenario A, B, C og E.
- **FR-11** Netting, partiregel og ledetidsoffset: `scheduled_receipts`, `projected_on_hand`, `net_requirements`, `planned_order_receipts`, `planned_order_releases` og `planned_orders` stemmer med `expected.json` for A, B, C og E, sammenlignet på hele ukesarrayer. Forfalte forslag beholder beregnet frigivelsesuke ≤ 0.
- **FR-12** Komponentbehov fra forfalte produksjonsordrer (R11): barnas bruttobehov legges i uke 1, i alle ledd nedover. Alle felt stemmer for scenario D, og ingen bruttobehov går tapt.
- **FR-13** Ledetid lengre enn horisont (E1): én melding per vare med bruttobehov i horisonten og ledetid > horisont.
- **FR-14** Forfalt bestilling (E2): én melding per bestillingsforslag med frigivelsesuke < 1, med antall, mottaksuke, frigivelsesuke, uker forfalt og tidligste mottaksuke. Meldingene (FR-13, FR-14) stemmer med `exceptions` for A–E som usortert mengde. Teksten er på norsk og testes ikke ordrett.
- **FR-15** MRP-tabell per vare: de seks radene per uke i horisonten, med lagerbeholdning og forfalte frigivelser i en egen kolonne før uke 1.
- **FR-16** Liste over bestillingsforslag (vare, type, antall, frigivelsesuke, mottaksuke) sortert på frigivelsesuke, og alle exception-meldinger. Forfalte forslag er tydelig merket.
- **FR-17** Markere endringer siden forrige kjøring: nye og fjernede forslag, nye, forverrede, forbedrede og løste meldinger (paret på type og vare), og endrede celler, også i «Før u1». Akseptansekriterier for A, B, C og E. Første kjøring har ingen markeringer.
- **FR-18** Justere BOM-linjer og varedata: mengde per på eksisterende BOM-linjer, og ledetid og partiregel (L4L eller FOQ med kvantum) på eksisterende varer.

### Ikke-funksjonelle krav

- **NFR-1** Kjørbar lokalt etter README på en ren maskin, uten kontoer, nøkler eller eksterne tjenester.
- **NFR-2** Ingen hemmeligheter i repoet: miljøvariabler og `.env.example` uten ekte verdier. Demopassordet står i README.
- **NFR-3** Testbar beregningskjerne uten database og brukergrensesnitt, direkte mot `input.json` og `expected.json`, med én testkommando. Automatisk skalatest med generert BOM (~500 varer, 10 nivåer, felles komponent på flere nivåer): fullfører, riktig LLC og massebalanse for alle varer. Ingen tidskrav.
- **NFR-4** En MRP-kjøring for testfartøyet viser resultatet uten merkbar ventetid.
- **NFR-5** Ugyldig input, gjentatte kjøringer og tilbakestilling midt i bruk gir ikke krasj eller inkonsistente data.
- **NFR-6** Lesbar kontrast, kan brukes med tastatur, etiketter på alle skjemafelt, norsk UI, beregnet på PC.
- **NFR-7** Stories og automatiske tester viser til FR-nummer, og beregningstestene viser til scenario i fasiten.

### Suksessmål som binder stories

- **SM-1** Alle automatiske beregningstester mot scenario A–E består (FR-10 til FR-14).
- **SM-2** Manuell testplan for scenario A, B, C og E er gjennomført uten avvik og dokumentert i repoet (FR-15 til FR-18).
- **SM-3** En person som ikke kjenner prosjektet, får appen og testene til å kjøre bare med README, på under 15 minutter (NFR-1, NFR-3).
- **SM-4** Hver FR er dekket av minst én story og minst én test, automatisk eller manuell (NFR-7).
- **SM-C2** Testene skal ikke kunne bestås av kode som er skreddersydd for testfartøyet.

### Tilleggskrav fra arkitekturen

- **Ingen ferdig startmal for hele prosjektet.** Backend settes opp som uv-prosjekt etter strukturfrøet (`backend/src/rbe/{mrp,db,api}`, `fixture.py`, `config.py`, `main.py`, `tests/{mrp,api}`). Frontend lages fra Vite-malen `react-ts` (create-vite 9.3.4). Begge oppsettene hører til første epic.
- **AD-1** `rbe.mrp` importerer bare standardbiblioteket og egne moduler. Importtesten `tests/mrp/test_core_is_pure.py` leser importene med `ast`. Inndata og resultat er frosne dataklasser.
- **AD-2** Kjernens resultat har samme form og feltnavn som ett scenario i `expected.json`, pluss `name`, `unit` og `on_hand` per vare. Lagret kjøring og API-svar bruker samme form. Meldinger er `type` + tallfelt, ikke tekst.
- **AD-3** Deterministisk rekkefølge: varer på (`low_level_code`, `id`), forslag på `receipt_week`, meldinger på (`type`, `item`, `receipt_week`).
- **AD-4** `rbe.fixture` er eneste parser av fasitformatet, brukt av seed (scenario A) og tester (A–E via `override`). Stien kommer fra `RBE_FIXTURE_PATH`, med repoets fasit som standard.
- **AD-5** SQLite i `backend/data/` (gitignorert), `create_all` uten Alembic. Seed når varetabellen er tom, og demobruker når den mangler, sjekket hver for seg. Tilbakestilling i én transaksjon som beholder demobrukeren.
- **AD-6** `mrp_run(id, created_at, result_json)` er uforanderlig. Endringer mellom siste og nest siste kjøring beregnes av en ren funksjon i `rbe.mrp` med returformen `{planned_orders: {added, removed}, exceptions: {added, resolved, paired}, cells}`. Testes automatisk for A→B, A→C og A→E.
- **AD-7** Alle skrivinger går via backend og lagres i én transaksjon eller avvises. Uke valideres mot lagret horisont. Feil i FastAPIs 422-format med norske meldinger, og frontend viser dem ved feltet `loc` peker på. Frontend regner aldri MRP eller LLC.
- **AD-8** Signert sesjonscookie (`SessionMiddleware`, httpOnly, SameSite=Lax), `pwdlib` argon2, `require_user` på alle `/api`-ruter unntatt `POST /api/auth/login` og `GET /api/health`. En test går gjennom `app.routes`.
- **AD-9** Konfigurasjon med `pydantic-settings` og prefikset `RBE_`. `backend/.env.example` lister variablene. Mangler sesjonsnøkkel, lages en tilfeldig med advarsel. Ingen annen kode leser `os.environ`.
- **AD-10** `uv run python -m pytest` i `backend/` kjører alle backendtester. Fasittestene er parametrisert over scenario × vare × felt, og test-id-en oppgir scenario og FR. Integrasjonstester bruker `TestClient` og en midlertidig SQLite-fil.
- **AD-11** Forutsetninger: uv og Node 26 LTS. Backend med `uv run python -m fastapi dev src/rbe/main.py`, frontend med `npm run dev`, og Vite-proxy for `/api`. Ingen Docker. Kommandoene bruker `python -m`-formen fordi den virker også der Windows sperrer konsollskriptene uv lager (os error 5), presisert i story 1.7 og i retrospektiven av epic 1.
- **Konvensjoner:** engelske navn i kode etter fasitens feltnavn, norsk UI-tekst. Meldingsteksten lages i frontend. REST under `/api` med ressurser i flertall og bindestrek. `created_at` i UTC, vist i lokal tid. `logging`, ikke `print`. Ruff og Biome.
- **Stack:** versjonene i arkitekturens Stack-tabell (Python 3.14, FastAPI 0.165.0, SQLAlchemy 2.1.9, React 19.3.1, Vite 8.3.8, React Router 8.5.2, Biome 2.6.8, @fontsource/manrope 5.3.0 osv.).

### Prosessrammer fra CLAUDE.md

- Hver story bygges på egen branch og leveres som én pull request (åpent punkt i `.logs/thobias-navelsaker/issues.md`). Små commits med én sak hver, på norsk i imperativ, med FR-nummer.
- Beregningstester leser fasiten direkte og oppgir scenario. Fasiten endres bare bevisst.
- Skjermbilde når et skjermbilde eller en brukerflyt virker for første gang. Video (tas av brukeren) når en kjerneflyt virker fra start til slutt, og før innlevering. Lagres i `docs/media/YYYY-MM-DD-<hva>.png|.mp4`. README skal ha minst ett skjermbilde.
- AI-logg i `docs/ai-log.md` etter hver økt som endrer kode eller tester.

### UX-krav

- **UX-DR1** Designtokens: fargene, typografien, `rounded` og `spacing` fra frontmatter i DESIGN.md som CSS-variabler. Manrope fra `@fontsource/manrope` med vektene 400–800, servert lokalt. Tabulære, høyrejusterte tall i alle tabeller.
- **UX-DR2** Logo 3c liggende i menylinjen og stablet på innloggingssiden, og favicon (`mockups/logo-3c.svg`, `mockups/favicon.svg`).
- **UX-DR3** Menylinje på alle sider etter innlogging: logo (til startsiden), fire tekstlenker (Bestillingsforslag og meldinger, MRP-tabell, BOM-tre, MPS og lager), «demo · Logg ut». Valgt side markert med strek i aksentfarge.
- **UX-DR4** Startside `/`: havfoto over hele bredden (340 px, `alt=""`), velkomstflate med «Velkommen» og «Hva vil du gjøre?», fire dør-kort i fast rekkefølge der hele kortet er én lenke, nøytral statuslinje om siste kjøring uten antall og farge, og kreditering av fotografen. Ingen meldinger eller antall.
- **UX-DR5** Innloggingsside `/logg-inn`: kort med stablet logo, to felt med etikett, primærknapp over hele bredden, «Logger inn …» mens den arbeider, hjelpeteksten «Demobrukeren står i README» og samme feilmelding for feil brukernavn og feil passord.
- **UX-DR6** Knapper: primær (høyst én per område), sekundær og fare. «Kjør MRP» står på Bestillingsforslag og meldinger, MRP-tabell, MPS og lager og i linjen om ikke-kjørte endringer. Ved trykk: «Kjører …» og deaktivert. Etterpå blir brukeren på siden, innholdet oppdateres, og «MRP er kjørt kl. …» vises. Hopper aldri automatisk til meldingene.
- **UX-DR7** Meldingsseksjon: «Meldinger (N)» med «Skjul/Vis», åpen når siden åpnes, rekkefølge røde, rav, grønne. Meldingskort med 4 px kant og merkelapp i meldingens farge. Teksten lages i frontend fra `type`, tallfelt og varenavn, i du-form uten utropstegn. Varenavn er lenker til MRP-tabellen.
- **UX-DR8** Forslagstabell: sortert på frigivelsesuke (forfalte først) og så varenummer. Kolonner: endring, vare, type, antall, frigivelse, mottak. Forfalte forslag har merkelappen «u−10 forfalt». Nye forslag har «ny». Fjernede forslag ligger bak «Vis N forslag som er borte siden forrige kjøring», dempet og gjennomstreket med «borte».
- **UX-DR9** Vareliste på `/mrp/:vare`: gruppert etter lavnivåkode (Nivå 0–3), sortert på varenummer, søkefelt som filtrerer på nummer og navn. Valgt vare er markert, og adressen endres. Piltast opp/ned flytter valget. `/mrp` åpner RBE-000. Tilstandene «Ingen varer passer søket.» og «Fant ikke varen XYZ.».
- **UX-DR10** MRP-tabell: overskrift med vare, type, ledetid, partiregel og LLC. Seks rader, kolonnene «Før u1» og uke 1–16. Nuller vises tomme, unntatt i beregnet lager. Forfalte frigivelser summeres i «Før u1», som har `surface-muted`. Ekte `<table>` med `<th scope>`, i et rulleområde med `tabindex="0"`, `role="region"` og etikett.
- **UX-DR11** Endrede celler: vekt 800 med prikket understrek, uten farge, verktøytips «Forrige kjøring: 8», skjult tekst for skjermleser («24, endret fra 0») og avkrysningsboksen «Vis verdier fra forrige kjøring» som viser «24 ← 0».
- **UX-DR12** BOM-tre: alle 12 linjer, varer med flere foreldre under hver forelder. Noder kan foldes, og alt er utfoldet ved start. Node: varenummer, navn, «× mengde per», type, ledetid og LLC. `role="tree"`/`treeitem`, `aria-expanded`, piltaster. Klikk eller Enter åpner redigeringspanelet.
- **UX-DR13** Redigeringspanel: valgt vare og «Valgt under …», fieldset «Denne BOM-linjen» (mengde per) og «Varedata» (ledetid, partiregel L4L/FOQ, kvantum bare ved FOQ) med teksten «gjelder alle N steder varen brukes». «Lagre» og «Avbryt», Esc avbryter, lenken «Vis MRP-tabell». Fokus til første felt ved åpning og tilbake til noden ved lukking.
- **UX-DR14** Radredigering i MPS og lager: tre tabeller under hverandre (hovedplan, åpne ordre, lagerbeholdning), maks ca. 820 px, ingen faner. «Endre» gjør én rad om gangen til felt. Enter lagrer, Esc avbryter, fokus tilbake til «Endre». «Slett» med innebygd bekreftelse i raden og fokus på «Nei». «+ Legg til …» gir en tom rad i redigeringsmodus. Tomme tilstander for hovedplan og åpne ordre.
- **UX-DR15** Felt med validering: feilmeldingen fra backend (422 `loc`) står under feltet, med rød kant, `aria-invalid` og `aria-describedby`. Fokus til første felt med feil. Ingenting lagres.
- **UX-DR16** Linje om ikke-kjørte endringer på BOM-tre og MPS og lager: «Du har N endringer som ikke er tatt med i MRP ennå.» med en liten «Kjør MRP», uten farge, som forsvinner etter kjøring. Resultatsidene viser da statuslinjen «Inndata er endret etter siste kjøring.»
- **UX-DR17** Bekreftelseslinjer: grønn «✓ Lagret.» og «✓ Testdata er lastet inn på nytt.» som forsvinner etter 5 sekunder. Nøytral «MRP er kjørt kl. …» blir stående. `aria-live="polite"`.
- **UX-DR18** Bekreftelsesdialog for tilbakestilling: forklarer hva som går tapt, «Avbryt» har fokus, «Tilbakestill» er rød, Esc avbryter, fokus holdes i dialogen og går tilbake til knappen.
- **UX-DR19** Fargebetydning og endringsvisning: rød for E2, forverret og valideringsfeil, rav for E1, grønn for forbedret, løst og bekreftelser. Nøytrale endringer uten farge. Tekstene «▲ Forverret: 9 → 11 uker», «▼ Forbedret: 11 → 9 uker», «Endret», «Endret: ledetid 20 → 22 uker», «ny» og «Løst: …». Ingen betydning formidles bare med farge.
- **UX-DR20** Felles tilstander: «Ingen MRP-kjøring ennå. Trykk Kjør MRP for å beregne.», «Ingen meldinger fra siste kjøring.», «Ingen bestillingsforslag fra siste kjøring.», «Henter …» i dempet tekst, rød feillinje «Fikk ikke kontakt med serveren. Prøv igjen.» (`aria-live="assertive"`) som beholder skjemadata, «Kjøring feilet» som beholder forrige resultat, og 401 som sender til innlogging med «Du er logget ut. Logg inn igjen for å fortsette.» og tilbake til siden etterpå.
- **UX-DR21** Tilgjengelighet: WCAG 2.2 AA, «Hopp til innhold» som første fokuselement, unik dokumenttittel per side («MRP-tabell: PLT-900 – Red Ball Express»), fokus til H1 ved sidebytte, synlig fokusramme i aksentfarge, klikkmål ≥ 24 × 24 px, `lang="no"`, ingen funksjon bare ved hover, ingen dra-og-slipp.
- **UX-DR22** Layout: menylinje øverst, innhold maks 1280 px, målbredde ≥ 1280 px, fungerer ned til 1024 px med sidelengs rulling i MRP-tabellen. Ingen mobil og ingen mørk modus.

### Dekning fra FR til epic

| FR | Epic | Kort |
| --- | --- | --- |
| FR-1 | 1 | Innlogging og utlogging |
| FR-2 | 1 | Testdata fra fasiten ved oppstart |
| FR-3 | 4 | Tilbakestille til testdata |
| FR-4 | 4 | BOM-tre |
| FR-5 | 4 | Redigere MPS |
| FR-6 | 4 | Redigere lagerbeholdning |
| FR-7 | 4 | Redigere åpne ordre |
| FR-8 | 4 | Validering (MPS, lager, åpne ordre og BOM-data) |
| FR-9 | 3 | Kjøre og lagre MRP |
| FR-10 | 2 | BOM-eksplosjon og lavnivåkoder |
| FR-11 | 2 | Netting, partiregel og ledetidsoffset |
| FR-12 | 2 | Forfalte produksjonsordrer (R11) |
| FR-13 | 2 (beregning), 3 (visning) | E1 ledetid lengre enn horisont |
| FR-14 | 2 (beregning), 3 (visning) | E2 forfalt bestilling |
| FR-15 | 3 | MRP-tabell per vare |
| FR-16 | 3 | Bestillingsforslag og meldinger |
| FR-17 | 5 | Endringer siden forrige kjøring |
| FR-18 | 4 | Justere mengde per, ledetid og partiregel |

NFR-1 og SM-3: epic 1 (README v1) og 6 (prøvd på ren maskin). NFR-2: epic 1. NFR-3, SM-1 og SM-C2: epic 2. NFR-4: epic 3. NFR-5: epic 3 og 4. NFR-6: alle stories med skjermbilder. NFR-7 og SM-4: alle stories, sjekket i epic 6. SM-2: testplanen opprettes i epic 3, utvides i 4 og 5 og gjennomføres i 6.

## Epic-liste

### Epic 1: Kjørbart skjelett med innlogging og testdata

Sensor eller planleggeren starter appen etter README, logger inn med demobrukeren og kommer til startsiden. Testfartøyet er lastet inn fra fasiten. Backend, frontend, konfigurasjon, testkommando og arbeidsflyten med branch og PR er på plass.
**FR:** FR-1, FR-2. **Også:** NFR-1, NFR-2, AD-1 (importtest), AD-4, AD-5, AD-8 (rutetest), AD-9, AD-11, UX-DR1–5, UX-DR21–22.

### Epic 2: Riktig MRP-beregning

Den rene kjernen beregner lavnivåkoder, bruttobehov, netting, partiregler, ledetidsoffset, R11 og exception-meldingene. Sensor kan kjøre `uv run python -m pytest` og se at alle felt stemmer med fasiten for scenario A–E, og at skalatesten viser at logikken er generell.
**FR:** FR-10, FR-11, FR-12, FR-13, FR-14. **Også:** NFR-3, SM-1, SM-C2, AD-1, AD-2, AD-3, AD-10.

### Epic 3: Kjør MRP og se resultatet

Planleggeren trykker «Kjør MRP» og ser bestillingsforslag, meldinger og MRP-tabellen for hver vare. Kjøringen lagres som et uforanderlig øyeblikksbilde. Den manuelle testplanen opprettes her.
**FR:** FR-9, FR-15, FR-16 (og visning av FR-13, FR-14). **Også:** NFR-4, AD-6 (lagring), UX-DR6–10, UX-DR20.

### Epic 4: Endre inndata og tilbakestille

Planleggeren ser BOM-treet, endrer MPS, lagerbeholdning, åpne ordre, mengde per, ledetid og partiregel med validering, ser hvor mange endringer som ikke er kjørt, og kan tilbakestille til testdata.
**FR:** FR-3, FR-4, FR-5, FR-6, FR-7, FR-8, FR-18. **Også:** NFR-5, AD-5, AD-7, UX-DR12–18.

### Epic 5: Se hva som endret seg

Etter en ny kjøring ser planleggeren nye og fjernede bestillingsforslag, forverrede, forbedrede og løste meldinger, og endrede celler i MRP-tabellen. Sammenligningen er en ren funksjon i kjernen, testet for A→B, A→C og A→E. UJ-1 virker fra start til slutt.
**FR:** FR-17. **Også:** AD-6 (sammenligning), UX-DR11, UX-DR19.

### Epic 6: Klar for sensor

Den manuelle testplanen er gjennomført og dokumentert, sporbarheten fra FR til story til test er sjekket, README er prøvd på en ren maskin, og skjermbilder og demovideo er oppdatert.
**FR:** ingen nye. **Også:** SM-2, SM-3, SM-4, NFR-1, NFR-7.

### Beslutninger fra nedbrytingen (2026-11-24, Thobias)

- Skjelettet først, så kjernen. Oppsettsfeil og README kommer tidlig, og branch og PR brukes fra første story.
- BOM-tre og BOM-justering inngår i epic 4, fordi de bruker samme mønster for API, validering og ikke-kjørte endringer.
- Sammenligningen av kjøringer (FR-17, AD-6) er første story i epic 5, slik at epicen leverer hele FR-17.
- Ikke-kjørte endringer telles med en revisjonsteller: `input_revision` i `planning_settings` økes ved hver lagring, og hver `mrp_run` lagrer revisjonen den ble kjørt på. Ført tilbake i AD-6.
- Den manuelle testplanen dekker også UJ-2 (FR-1, FR-4, FR-8 i grensesnittet). Ført tilbake i PRD SM-2.
- Én story er én branch og én PR, med 2–5 commits. Stories kan bygges i rekkefølge uten å vente på senere stories.
- Etter pre-mortem og gjennomgang av grensetilfeller: story 3.2 er delt i to (forslag og meldinger), testplanstegene gjennomføres per PR, stier regnes ut fra pakkens plassering, og 4.6 er den eneste storyen som kan kuttes. Grensene for uke, sletting av hele hovedplanen, to byggenumre i samme uke, bytte fra FOQ til L4L og E1 ved endret ledetid er lagt til i akseptansekriteriene.
- Byggenummeret er unikt i hovedplanen, og duplikat avvises (FR-8). Ført tilbake i PRD FR-8.
- Sluttvalidering: NFR-4 har fått et akseptansekriterium i 3.1, `POST /api/reset` er merket som et bevisst endepunkt for en handling, og henvisningen framover fra 1.5 til testplanen er fjernet.

## Felles for alle stories

Dette gjelder hver story i tillegg til egne akseptansekriterier, så det ikke gjentas:

- Storyen bygges på egen branch (`story/<n.m>-<kort-navn>`) og leveres som én pull request med 2–5 commits. Commit-meldingene er på norsk i imperativ og viser til FR-nummeret.
- `uv run python -m pytest`, `uv run python -m ruff check` og `uv run python -m ruff format --check` i `backend/` og `npx biome check` i `frontend/` gir 0 feil.
- Nye API-ruter har `require_user`, og rutetesten (AD-8) består uten nye unntak.
- Automatiske tester har FR-nummeret og eventuelt scenarioet i navnet eller test-id-en (NFR-7).
- Stories med skjermbilder følger EXPERIENCE.md og DESIGN.md: norsk tekst i du-form, fargene bare med sin faste betydning, tastaturbruk, synlig fokus, etiketter på felt, dokumenttittel og fokus til H1 ved sidebytte (NFR-6, UX-DR19, UX-DR21). Fra og med story 3.2 legges stegene for skjermbildet til i `docs/testplan.md`.
- Storyens egne steg i testplanen gjennomføres før PR-en flettes, og resultatet står i PR-beskrivelsen. Story 6.1 er da en hel gjennomkjøring, ikke den første.
- Står det **Media** i storyen, tar Claude skjermbildet eller minner brukeren om videoen etter regelen i CLAUDE.md.
- `docs/ai-log.md` får en oppføring, og README oppdateres hvis oppstart, forutsetninger eller testkommando endres.

## Epic 1: Kjørbart skjelett med innlogging og testdata

Sensor eller planleggeren starter appen etter README, logger inn med demobrukeren og kommer til startsiden. Testfartøyet er lastet inn fra fasiten.

### Story 1.1: Backend-oppsett med helsesjekk og konfigurasjon

Som sensor
vil jeg kunne starte backend og kjøre testene med én kommando hver,
slik at jeg kan prøve appen uten manuelt oppsett.

**Krav:** NFR-1, NFR-2, AD-9, AD-10, AD-11. **Tester:** `tests/api/test_health.py`, `tests/test_config.py`.

**Akseptansekriterier:**

**Gitt** en ren klone med uv installert
**Når** jeg kjører `uv run python -m fastapi dev src/rbe/main.py` i `backend/`
**Så** henter uv Python 3.14 fra `.python-version`, og `GET /api/health` svarer 200 uten innlogging
**Og** avhengighetene er festet i `pyproject.toml` og `uv.lock` med versjonene i arkitekturens Stack

**Gitt** `backend/`
**Når** jeg kjører `uv run python -m pytest`
**Så** kjører og består helsesjekktesten og konfigurasjonstesten

**Gitt** at det ikke finnes noen `.env`
**Når** appen starter
**Så** brukes standardverdiene for alle `RBE_`-variabler, og mangler `RBE_SESSION_SECRET`, lages en tilfeldig nøkkel og en advarsel logges (AD-9)
**Og** `backend/.env.example` lister `RBE_DATABASE_URL`, `RBE_FIXTURE_PATH`, `RBE_SESSION_SECRET`, `RBE_DEMO_USERNAME` og `RBE_DEMO_PASSWORD` uten ekte hemmeligheter
**Og** `.env` og `backend/data/` er gitignorert, og ingen kode utenfor `config.py` leser `os.environ` (NFR-2)
**Og** standardstien til databasen regnes ut fra pakkens plassering, ikke fra arbeidsmappa, og backend er prøvd startet fra en mappe med mellomrom i stien

### Story 1.2: Kjernens datatyper og fasitparser

Som sensor
vil jeg at testdataene leses direkte fra fasitfila,
slik at app og fasit ikke kan sprike.

**Krav:** FR-2, AD-1, AD-2, AD-4. **Tester:** `tests/test_fixture.py`, `tests/mrp/test_core_is_pure.py`.

**Akseptansekriterier:**

**Gitt** `testdata/testfartoy-v1/input.json`
**Når** `rbe.fixture` laster scenario A
**Så** får jeg kjernens frosne inndatatyper med horisont 16, 11 varer, 12 BOM-linjer, 2 MPS-linjer, lagerbeholdning per vare og 2 åpne ordre, med fasitens feltnavn

**Gitt** scenario B, C, D eller E
**Når** `rbe.fixture` laster scenarioet
**Så** brukes `override` fra fasiten: B gir byggenr. 2 i uke 14, C gir lager 0 for GIR-220, D gir byggenr. 1 i uke 4, og E gir mengde per 5 på SKR-100 → SEK-110
**Og** et ukjent scenario eller en fil som ikke finnes, gir en tydelig feil
**Og** standardverdien for `RBE_FIXTURE_PATH` regnes ut fra pakkens plassering og virker når repoet ligger i en mappe med mellomrom i stien

**Gitt** pakken `src/rbe/mrp/` med modulen for datatyper
**Når** `tests/mrp/test_core_is_pure.py` leser importene i alle modulene med `ast`
**Så** feiler testen hvis en modul importerer noe annet enn standardbiblioteket og `rbe.mrp` selv (AD-1), og det er sjekket ved å legge inn en forbudt import midlertidig
**Og** `tests/conftest.py` gir stien til `testdata/testfartoy-v1/`, og det finnes ingen kopi av `input.json` i koden (AD-4)

### Story 1.3: Database og seed ved tom database

Som sensor
vil jeg at testfartøyet er lagt inn når appen starter første gang,
slik at jeg kan bruke appen uten å legge inn noe selv.

**Krav:** FR-2, FR-1 (passordhash), AD-4, AD-5. **Tester:** `tests/api/test_seed.py`.

**Akseptansekriterier:**

**Gitt** at databasefila ikke finnes
**Når** backend starter
**Så** opprettes tabellene for varer, BOM-linjer, MPS-linjer, åpne ordre, planinnstillinger (horisont) og brukere med `create_all`, og scenario A lastes inn via `rbe.fixture`
**Og** databasen inneholder nøyaktig dataene i `input.json`, sjekket tabell for tabell mot det `rbe.fixture` leser (FR-2)

**Gitt** en database som allerede er seedet og endret
**Når** backend starter på nytt
**Så** seedes ingenting på nytt, og endringene beholdes

**Gitt** at varetabellen har data, men demobrukeren mangler
**Når** backend starter
**Så** opprettes bare demobrukeren (de to sjekkes hver for seg, AD-5)
**Og** passordet er lagret som argon2-hash med `pwdlib`, ikke i klartekst (FR-1)

### Story 1.4: Innlogging i backend

Som planlegger
vil jeg logge inn og ut med brukernavn og passord,
slik at forretningskritiske data er beskyttet.

**Krav:** FR-1, AD-8. **Tester:** `tests/api/test_auth.py`, `tests/api/test_routes_require_login.py`.

**Akseptansekriterier:**

**Gitt** demobrukeren
**Når** jeg sender `POST /api/auth/login` med riktig brukernavn og passord
**Så** får jeg 200 og en signert sesjonscookie (httpOnly, SameSite=Lax), og `GET /api/auth/me` gir brukernavnet

**Gitt** feil brukernavn eller feil passord
**Når** jeg logger inn
**Så** får jeg 401 med den samme meldingen «Feil brukernavn eller passord.» i begge tilfeller (FR-1)

**Gitt** at jeg er innlogget
**Når** jeg sender `POST /api/auth/logout`
**Så** gir `GET /api/auth/me` 401 etterpå

**Gitt** alle ruter i `app.routes`
**Når** rutetesten kaller hver rute uten innlogging
**Så** gir alle `/api`-ruter 401, unntatt `POST /api/auth/login` og `GET /api/health`
**Og** testen feiler hvis en ny rute mangler `require_user`, og `conftest.py` har en innlogget testklient som senere tester kan bruke

### Story 1.5: Frontend-oppsett, designtokens og innloggingsside

Som sensor
vil jeg logge inn i nettleseren med demobrukeren,
slik at jeg kommer inn i appen.

**Krav:** FR-1, NFR-6, AD-11, UX-DR1, UX-DR2, UX-DR5, UX-DR20. **Tester:** manuell gjennomgang i PR-en. Stegene føres i testplanen når den opprettes i story 3.2. **Media:** skjermbilde `docs/media/YYYY-MM-DD-innlogging.png`.

**Akseptansekriterier:**

**Gitt** Node 26 LTS og `npm install` i `frontend/` (fra Vite-malen `react-ts`)
**Når** jeg kjører `npm run dev` mens backend kjører
**Så** serveres appen av Vite, og `/api` sendes videre til backend, så nettleseren ser ett opphav (AD-11)

**Gitt** tokenene i frontmatter i DESIGN.md
**Når** appen lastes
**Så** finnes fargene, typografien, `rounded` og `spacing` som CSS-variabler, Manrope lastes lokalt fra `@fontsource/manrope`, favicon og logo er på plass, og dokumentet har `lang="no"` (UX-DR1, UX-DR2)

**Gitt** at jeg ikke er innlogget
**Når** jeg åpner en hvilken som helst adresse i appen
**Så** sendes jeg til `/logg-inn`, og etter innlogging kommer jeg tilbake til adressen jeg ba om
**Og** et 401-svar fra API-et senere sender meg til innlogging med «Du er logget ut. Logg inn igjen for å fortsette.» (UX-DR20)

**Gitt** innloggingssiden
**Når** jeg logger inn
**Så** følger kortet UX-DR5: stablet logo, to felt med etikett, «Logger inn …» og deaktivert knapp mens den arbeider, og hjelpeteksten «Demobrukeren står i README»
**Og** feil brukernavn eller passord gir «Feil brukernavn eller passord.» koblet til skjemaet, og hele innloggingen kan gjøres med Tab og Enter
**Og** svarer ikke serveren, vises «Fikk ikke kontakt med serveren. Prøv igjen.», og det som er skrevet i feltene, beholdes

### Story 1.6: Menylinje og startside

Som planlegger
vil jeg komme til en rolig startside med fire dører,
slik at jeg selv velger hvor jeg går og ikke møter varsler med en gang.

**Krav:** UX-DR3, UX-DR4, UX-DR21, UX-DR22. **Tester:** manuell gjennomgang i PR-en. Stegene føres i testplanen når den opprettes i story 3.2. **Media:** skjermbilde `docs/media/YYYY-MM-DD-startside.png`.

**Akseptansekriterier:**

**Gitt** at jeg er innlogget
**Når** jeg åpner `/`
**Så** ser jeg havfotoet over hele bredden (`alt=""`), velkomstflaten med «Velkommen» og «Hva vil du gjøre?», og fire dør-kort i rekkefølgen forslag, MRP-tabell, BOM-tre, MPS og lager, der hele kortet er én lenke
**Og** statuslinjen viser «Ingen MRP-kjøring ennå.», og fotografen er kreditert på siden

**Gitt** hvilken som helst side etter innlogging
**Når** siden vises
**Så** har den menylinjen fra UX-DR3 med logo (til startsiden), de fire skjermbildene, «demo · Logg ut» og den valgte siden markert
**Og** «Logg ut» logger meg ut og sender meg til `/logg-inn`

**Gitt** de fire adressene `/forslag`, `/mrp`, `/bom` og `/plan`
**Når** jeg åpner dem
**Så** har hver side sin H1 og sin dokumenttittel («… – Red Ball Express»), og innholdet fylles inn av senere stories
**Og** «Hopp til innhold» er første element med fokus, og fokus flyttes til H1 ved sidebytte (UX-DR21)

### Story 1.7: README v1 med oppstart og tester

Som sensor
vil jeg ha en README som forteller hvordan jeg starter appen og kjører testene,
slik at jeg kommer i gang uten å kjenne prosjektet.

**Krav:** NFR-1, NFR-2, SM-3. **Tester:** gjennomgang fra en ny klone. **Media:** README får skjermbildet av startsiden fra story 1.6.

**Akseptansekriterier:**

**Gitt** README
**Når** sensor leser den
**Så** står det hva appen gjør, forutsetningene (uv og Node 26 LTS), oppstart av backend og frontend i hver sin terminal, demobrukeren med demopassordet, testkommandoen og lenker til PRD, arkitektur, UX, fasiten og AI-loggen
**Og** README har minst ett skjermbilde, og ingen ekte hemmeligheter

**Gitt** en ny klone av repoet i en tom mappe
**Når** jeg følger README steg for steg på Windows
**Så** starter backend og frontend, jeg kan logge inn, og `uv run python -m pytest` består
**Og** avvik mellom README og det som faktisk måtte gjøres, er rettet i README

## Epic 2: Riktig MRP-beregning

Den rene kjernen beregner lavnivåkoder, bruttobehov, netting, partiregler, ledetidsoffset, R11 og exception-meldinger. Sensor kan kjøre `uv run python -m pytest` og se at alle felt stemmer med fasiten for scenario A–E.

### Story 2.1: Lavnivåkoder og resultatform

Som sensor
vil jeg at hver vare får riktig lavnivåkode,
slik at hver vare planlegges én gang, etter alle foreldrene sine.

**Krav:** FR-10 (LLC), AD-2, AD-3. **Tester:** `tests/mrp/test_fixture_scenarios.py` (LLC-delen).

**Akseptansekriterier:**

**Gitt** scenario A–E fra fasiten
**Når** kjernen beregner lavnivåkoder
**Så** stemmer `low_level_code` for alle varer med `expected.json`, med test-id som oppgir scenario, FR-10, vare og felt (for eksempel `A-FR-10-PLT-900-low_level_code`)
**Og** PLT-900 får LLC 3 selv om den også forekommer på nivå 2

**Gitt** resultatet fra kjernens inngangsfunksjon
**Når** det gjøres om til JSON
**Så** har det formen fra AD-2: per vare fasitens felt pluss `name`, `unit` og `on_hand`, og en `exceptions`-liste
**Og** varene er sortert på (`low_level_code`, `id`), og resultatet er frosne dataklasser uten tidsstempel (AD-3)

**Gitt** en BOM med en sykel (bygget i testen)
**Når** kjernen beregner lavnivåkoder
**Så** gir den en tydelig feil i stedet for å henge

### Story 2.2: Bruttobehov, netting, partiregel og ledetidsoffset

Som planlegger
vil jeg få riktige bruttobehov, nettobehov og bestillingsforslag for hver vare og uke,
slik at jeg vet når hver vare må bestilles eller startes.

**Krav:** FR-10, FR-11, FR-9 (determinisme i kjernen), SM-1, SM-C2. **Tester:** `tests/mrp/test_fixture_scenarios.py`, `tests/mrp/test_properties.py`.

**Akseptansekriterier:**

**Gitt** scenario A, B, C og E
**Når** kjernen kjører
**Så** stemmer `gross_requirements`, `scheduled_receipts`, `projected_on_hand`, `net_requirements`, `planned_order_receipts`, `planned_order_releases` og `planned_orders` for alle varer med `expected.json`
**Og** sammenligningen gjøres på hele ukesarrayer, parametrisert over scenario × vare × felt med scenario og FR-10/FR-11 i test-id-en

**Gitt** scenario A
**Når** kjernen kjører
**Så** blir PLT-900 bestilt i partier på 25 selv om nettobehovet er 2 (FOQ, R6)
**Og** forslaget for MOT-210 står i `planned_orders` med `release_week` −8, men ikke i `planned_order_releases` (R9)

**Gitt** scenario A, B, C og E
**Når** egenskapstesten sjekker hver vare
**Så** går massebalansen opp: lager før uke 1 + åpne ordre + planlagte mottak − bruttobehov = beregnet lager i siste uke
**Og** to kjøringer på samme inndata gir identisk resultat, og horisonten leses fra inndataene, ikke fra en konstant (SM-C2)

**Gitt** to MPS-linjer i samme uke (bygget i testen: byggenr. 1 og 2 i uke 12)
**Når** kjernen kjører
**Så** er bruttobehovet for RBE-000 i uke 12 lik 2, og behovene forplanter seg summert nedover

### Story 2.3: Komponentbehov fra forfalte produksjonsordrer (R11)

Som sensor
vil jeg at en plan som ikke rekker, ikke mister komponentbehov,
slik at appen gir et forsiktig og synlig resultat også for urealistiske planer.

**Krav:** FR-12, R11. **Tester:** `tests/mrp/test_fixture_scenarios.py` (scenario D), `tests/mrp/test_properties.py`.

**Akseptansekriterier:**

**Gitt** scenario D (byggenr. 1 i uke 4)
**Når** kjernen kjører
**Så** stemmer alle felt for alle varer, også `planned_orders`, med `expected.json` for D, med test-id som oppgir D og FR-12

**Gitt** en produksjonsvare med bestillingsforslag med frigivelsesuke før uke 1
**Når** kjernen beregner barnas bruttobehov
**Så** legges behovet (antall × mengde per) i uke 1, i alle ledd nedover

**Gitt** scenario A–E
**Når** egenskapstesten sjekker hver BOM-linje
**Så** er summen av barnets bruttobehov lik summen av foreldrenes bestillingsforslag × mengde per (ingen behov går tapt)

### Story 2.4: Exception-meldinger E1 og E2

Som planlegger
vil jeg få varsel om varer med for lang ledetid og bestillinger som er for sent ute,
slik at jeg ser problemene før de rammer byggingen.

**Krav:** FR-13, FR-14. **Tester:** `tests/mrp/test_fixture_scenarios.py` (exceptions).

**Akseptansekriterier:**

**Gitt** scenario A–E
**Når** kjernen kjører
**Så** stemmer `exceptions` med `expected.json`, sammenlignet som usortert mengde på `type`, `item` og tallfeltene, med test-id som oppgir scenario og FR-13/FR-14

**Gitt** scenario A
**Når** kjernen kjører
**Så** gir MOT-210 én E1 (ledetid 20, horisont 16) og én E2 (mottak u12, frigivelse u−8, 9 uker forfalt, tidligst mottak u21), og VIN-920 én E2

**Gitt** scenario A med tom MPS (bygget i testen)
**Når** kjernen kjører
**Så** gis ingen E1, fordi ingen vare har bruttobehov i horisonten
**Og** meldingene har bare `type` og tallfelt, ingen tekst, og er sortert på (`type`, `item`, `receipt_week`) (AD-2, AD-3)

### Story 2.5: Skalatest med generert BOM

Som sensor
vil jeg se at beregningen fungerer for en stor, generert produktstruktur,
slik at jeg vet at logikken er generell og ikke tilpasset testfartøyet.

**Krav:** NFR-3, SM-C2. **Tester:** `tests/mrp/test_scale.py`, `tests/mrp/scale_generator.py`.

**Akseptansekriterier:**

**Gitt** en generator med fast seed som lager rundt 500 varer på 10 nivåer, der en felles komponent forekommer på flere nivåer, med blandet L4L og FOQ, ulike ledetider, lagerbeholdning og åpne ordre
**Når** kjernen kjører på den genererte strukturen
**Så** fullfører beregningen uten feil
**Og** LLC for alle varer stemmer med en uavhengig beregning av lengste vei i testen
**Og** massebalansen og regelen om at ingen behov går tapt holder for alle varer

**Gitt** den samme genererte strukturen
**Når** kjernen kjører to ganger
**Så** er resultatene identiske
**Og** testen har ikke noe tidskrav og kjøres med `uv run python -m pytest`

## Epic 3: Kjør MRP og se resultatet

Planleggeren trykker «Kjør MRP» og ser bestillingsforslag, meldinger og MRP-tabellen for hver vare. Kjøringen lagres som et uforanderlig øyeblikksbilde.

### Story 3.1: Kjør MRP og lagre kjøringen

Som planlegger
vil jeg starte en MRP-kjøring og få resultatet lagret,
slik at det kan vises og sammenlignes med neste kjøring.

**Krav:** FR-9, NFR-4, NFR-5, AD-2, AD-6 (lagring). **Tester:** `tests/api/test_mrp_run.py`.

**Akseptansekriterier:**

**Gitt** en seedet database
**Når** jeg sender `POST /api/mrp-runs`
**Så** leses alle inndata i én transaksjon, kjernen kjøres, og resultatet lagres som én rad i tabellen `mrp_run(id, created_at, result_json)`, som opprettes i denne storyen
**Og** resultatet stemmer med `expected.json` for scenario A for alle varer og meldinger

**Gitt** at det finnes kjøringer
**Når** jeg sender `GET /api/mrp-runs/latest`
**Så** får jeg siste kjøring i formen fra AD-2, med `created_at` i UTC ISO 8601
**Og** uten kjøringer får jeg et svar som frontend kan vise som «Ingen MRP-kjøring ennå»

**Gitt** samme inndata
**Når** jeg kjører MRP to ganger
**Så** er `result_json` identisk (FR-9)
**Og** en endring som er lagret i databasen før kjøringen, er med i resultatet, og det finnes ingen API for å endre eller slette en kjøring
**Og** en kjøring på scenario A viser resultatet uten merkbar ventetid, og tiden noteres i testplanen i story 6.1 (NFR-4)

### Story 3.2: Kjør MRP og bestillingsforslag

Som planlegger
vil jeg trykke «Kjør MRP» og se alle bestillingsforslag fra siste kjøring,
slik at jeg ser hva som må bestilles eller startes, og når.

**Krav:** FR-16, FR-9 (knappen), UX-DR6, UX-DR8, UX-DR20. **Tester:** testplan scenario A.

**Akseptansekriterier:**

**Gitt** at det ikke finnes noen kjøring
**Når** jeg åpner `/forslag`
**Så** ser jeg «Ingen MRP-kjøring ennå. Trykk Kjør MRP for å beregne.» med knappen

**Gitt** at jeg trykker «Kjør MRP»
**Når** kjøringen pågår og blir ferdig
**Så** viser knappen «Kjører …» og er deaktivert, og etterpå blir jeg på siden, innholdet oppdateres, og «MRP er kjørt kl. HH:MM.» meldes med `aria-live="polite"`
**Og** feiler kjøringen, vises feillinjen, knappen blir aktiv igjen, og forrige resultat beholdes

**Gitt** en kjøring på scenario A
**Når** siden vises
**Så** viser forslagstabellen 19 forslag sortert på frigivelsesuke og så varenummer, med kolonnene endring, vare, type («Innkjøp» eller «Produksjon»), antall, frigivelse og mottak
**Og** forfalte forslag har den røde merkelappen «u−8 forfalt» eller «u0 forfalt» med tekst, ikke bare farge, og varenavnene er lenker til `/mrp/:vare`
**Og** «Ingen bestillingsforslag fra siste kjøring.» og «Henter …» vises når det passer

**Gitt** startsiden
**Når** det finnes en kjøring
**Så** viser statuslinjen tidspunktet for siste kjøring, uten antall og uten farge
**Og** `docs/testplan.md` er opprettet med kolonnene steg, FR, forventet og resultat, og har stegene for scenario A på denne siden og for innlogging og startside i UJ-2 (story 1.5 og 1.6)

### Story 3.3: Meldinger med norsk tekst

Som planlegger
vil jeg se exception-meldingene fra siste kjøring som korte norske setninger,
slik at jeg forstår hva som er for sent, og hva det betyr for byggingen.

**Krav:** FR-13 og FR-14 (visning), FR-16, UX-DR7, UX-DR19, UX-DR20. **Tester:** testplan scenario A og C. **Media:** skjermbilde `docs/media/YYYY-MM-DD-forslag-og-meldinger.png` (hele siden).

**Akseptansekriterier:**

**Gitt** en kjøring på scenario A
**Når** jeg åpner `/forslag`
**Så** står «Meldinger (3)» over forslagene, åpen når siden åpnes, med «Skjul/Vis»
**Og** de to røde E2-meldingene (MOT-210 og VIN-920) står før den rav E1-meldingen (MOT-210), hver i sitt meldingskort med merkelapp i tekst («Forfalt», «Obs»)

**Gitt** en E2-melding
**Når** teksten lages i frontend fra `type`, tallfeltene og varenavnet
**Så** er den i du-form uten utropstegn, for eksempel «Hovedmotor (MOT-210) skulle vært bestilt for 9 uker siden. Bestilles den nå, kommer den tidligst i uke 21.»
**Og** E1 gir en tilsvarende setning med ledetid og horisont, og varenavnet er en lenke til `/mrp/:vare`

**Gitt** en kjøring uten meldinger
**Når** siden vises
**Så** står «Ingen meldinger fra siste kjøring.» i nøytral tekst
**Og** stegene for meldingene i scenario A og C er lagt til i testplanen

### Story 3.4: MRP-tabell per vare

Som planlegger
vil jeg velge en vare og se MRP-tabellen for hele horisonten,
slik at jeg forstår hvordan behov, lager og forslag henger sammen.

**Krav:** FR-15, UX-DR6, UX-DR9, UX-DR10, UX-DR22. **Tester:** testplan scenario A. **Media:** skjermbilde `docs/media/YYYY-MM-DD-mrp-tabell.png`.

**Akseptansekriterier:**

**Gitt** en kjøring på scenario A
**Når** jeg åpner `/mrp/PLT-900`
**Så** viser tabellen overskriften med vare, type, ledetid, partiregel (FOQ 25) og LLC, de seks radene og kolonnene «Før u1» og uke 1–16, med de samme tallene som tabellen for PLT-900 i fasiten
**Og** nuller vises som tomme celler, unntatt i beregnet lager, og «Før u1» viser lagerbeholdningen 20 i raden for beregnet lager

**Gitt** MOT-210 i scenario A
**Når** jeg åpner tabellen
**Så** viser «Før u1» den forfalte frigivelsen i raden for planlagt frigivelse

**Gitt** varelisten
**Når** jeg bruker den
**Så** er varene gruppert på nivå 0–3 og sortert på varenummer, søkefeltet filtrerer på nummer og navn, piltast opp og ned flytter valget, og adressen og dokumenttittelen («MRP-tabell: PLT-900 – Red Ball Express») følger valget
**Og** `/mrp` åpner RBE-000, «Ingen varer passer søket.» og «Fant ikke varen XYZ.» vises når det passer, og uten kjøring vises den tomme tilstanden med «Kjør MRP»

**Gitt** tabellen
**Når** jeg bruker tastatur eller skjermleser
**Så** er den en ekte `<table>` med `<th scope>` i et rulleområde med `tabindex="0"`, `role="region"` og etikett, og den ruller sideveis inne i seg selv ned til 1024 px bredde
**Og** varenavnene i story 3.2 og 3.3 lenker hit, og stegene for scenario A er lagt til i testplanen

## Epic 4: Endre inndata og tilbakestille

Planleggeren ser BOM-treet, endrer MPS, lagerbeholdning, åpne ordre, mengde per, ledetid og partiregel med validering, ser hvor mange endringer som ikke er kjørt, og kan tilbakestille til testdata.

### Story 4.1: API for MPS, åpne ordre og lagerbeholdning med validering

Som planlegger
vil jeg at endringer i MPS, åpne ordre og lager valideres og lagres trygt,
slik at ugyldige verdier aldri havner i beregningen.

**Krav:** FR-5, FR-6, FR-7, FR-8, NFR-5, AD-7. **Tester:** `tests/api/test_mps.py`, `tests/api/test_scheduled_receipts.py`, `tests/api/test_on_hand.py`, `tests/api/test_validation.py`.

**Akseptansekriterier:**

**Gitt** at jeg er innlogget
**Når** jeg bruker `/api/mps-lines` og `/api/scheduled-receipts` (liste, legge til, endre, slette) og endrer `on_hand` på `/api/items/{id}`
**Så** lagres hver gyldig endring i én transaksjon, og neste lesing viser den

**Gitt** en ugyldig verdi etter FR-8 (uke utenfor horisonten, antall 0, lager −1, byggenummer 0, byggenummer som allerede finnes, MPS-linje for en vare som ikke er nivå 0, desimaltall eller tekst)
**Når** jeg sender endringen
**Så** får jeg 422 i FastAPIs format med `loc` på feltet og en norsk melding, for eksempel «Lagerbeholdningen kan ikke være negativ.» eller «Uke må være mellom 1 og 16.»
**Og** databasen er uendret, sjekket før og etter i testen

**Gitt** grensene for uke
**Når** jeg lagrer en MPS-linje eller åpen ordre i uke 1 og i siste uke i horisonten, og i uke 0 og uka etter horisonten
**Så** godtas uke 1 og siste uke, og uke 0 og uka etter horisonten avvises

**Gitt** en MPS-linje med et byggenummer som allerede finnes i hovedplanen
**Når** jeg lagrer den, som ny linje eller ved å endre en annen linje
**Så** får jeg 422 med «Byggenr. 2 finnes allerede.» ved feltet, og databasen er uendret (FR-8)

**Gitt** at jeg sletter alle MPS-linjene
**Når** jeg kjører MRP
**Så** gir kjøringen ingen bestillingsforslag og ingen meldinger, uten feil

**Gitt** en lagret horisont på 12 uker (satt i testen)
**Når** jeg legger inn en MPS-linje i uke 14
**Så** avvises den, fordi uka valideres mot den lagrede horisonten og ikke mot 16

**Gitt** en seedet database
**Når** jeg flytter byggenr. 2 til uke 14 via API-et og kjører MRP
**Så** stemmer resultatet med `expected.json` for scenario B
**Og** setter jeg lager for GIR-220 til 0 fra scenario A og kjører MRP, stemmer resultatet med scenario C

### Story 4.2: Skjermbildet MPS og lager

Som planlegger
vil jeg endre hovedplan, åpne ordre og lagerbeholdning direkte i tabellene,
slik at jeg raskt kan prøve en ny plan.

**Krav:** FR-5, FR-6, FR-7, FR-8, UX-DR6, UX-DR14, UX-DR15, UX-DR17. **Tester:** testplan scenario B og C, UJ-1 og UJ-2. **Media:** skjermbilde `docs/media/YYYY-MM-DD-mps-og-lager.png`.

**Akseptansekriterier:**

**Gitt** `/plan`
**Når** siden vises
**Så** står hovedplan, åpne ordre og lagerbeholdning under hverandre (maks ca. 820 px, ingen faner), med «Kjør MRP» øverst

**Gitt** en rad
**Når** jeg trykker «Endre», endrer verdien og trykker Enter
**Så** lagres endringen, «✓ Lagret.» vises i grønt i 5 sekunder, raden går tilbake til visning, og fokus går tilbake til «Endre»
**Og** bare én rad kan redigeres om gangen, og Esc avbryter uten å lagre

**Gitt** en ugyldig verdi
**Når** jeg lagrer
**Så** vises meldingen fra backend under feltet `loc` peker på, feltet får rød kant, `aria-invalid` og `aria-describedby`, fokus flyttes til feltet, og ingenting lagres (FR-8)

**Gitt** «Slett» på en rad
**Når** jeg trykker
**Så** vises en bekreftelse i raden («Slette byggenr. 2? Ja / Nei») med fokus på «Nei»
**Og** «+ Legg til byggenummer» og «+ Legg til åpen ordre» gir en tom rad i redigeringsmodus, og tom hovedplan og ingen åpne ordre viser tekstene fra EXPERIENCE.md

**Gitt** testplanen
**Når** storyen er ferdig
**Så** har den stegene for scenario B og C og trinnene i UJ-1 og UJ-2 som handler om denne siden, også at −1 i lagerbeholdning gir feilmelding

### Story 4.3: Tilbakestill til testdata

Som sensor
vil jeg kunne tilbakestille alt til testdataene,
slik at jeg kan eksperimentere fritt uten å ødelegge noe.

**Krav:** FR-3, NFR-5, AD-5, UX-DR17, UX-DR18. **Tester:** `tests/api/test_reset.py`, testplan UJ-2. **Media:** skjermbilde `docs/media/YYYY-MM-DD-tilbakestill-dialog.png`.

**Akseptansekriterier:**

**Gitt** endrede inndata og flere kjøringer
**Når** jeg sender `POST /api/reset` (et bevisst endepunkt for en handling, ikke en ressurs i flertall)
**Så** slettes alle inndata og kjøringer, og scenario A lastes inn på nytt via `rbe.fixture` i én transaksjon, mens demobrukeren beholdes
**Og** databasen er da lik `input.json`, og en ny kjøring gir scenario A i `expected.json`

**Gitt** at innlastingen feiler midt i tilbakestillingen (simulert i testen)
**Når** tilbakestillingen avbrytes
**Så** er databasen uendret fra før tilbakestillingen (NFR-5)

**Gitt** knappen «Tilbakestill til testdata …» (sekundær) på `/plan`
**Når** jeg trykker den
**Så** åpnes en dialog som forklarer hva som går tapt, med fokus på «Avbryt», rød «Tilbakestill», Esc som avbryter og fokus som holdes i dialogen og går tilbake til knappen
**Og** etter bekreftelse vises «✓ Testdata er lastet inn på nytt.», og resultatsidene viser «Ingen MRP-kjøring ennå»

### Story 4.4: BOM-tre

Som planlegger
vil jeg se produktstrukturen til testfartøyet som et tre,
slik at jeg forstår hvilke varer som inngår, og hvor.

**Krav:** FR-4, AD-7 (LLC fra backend), UX-DR12. **Tester:** `tests/api/test_bom.py`, testplan UJ-2.

**Akseptansekriterier:**

**Gitt** en seedet database
**Når** jeg sender `GET /api/bom`
**Så** får jeg alle 12 BOM-linjene og varedata med lavnivåkoden beregnet av `rbe.mrp`, ikke i frontend

**Gitt** `/bom`
**Når** siden vises
**Så** er hele treet utfoldet, og hver node viser varenummer, navn, «× mengde per», type, ledetid og LLC (FR-4)
**Og** PLT-900 vises under SEK-110, STY-310 og DEK-300

**Gitt** treet
**Når** jeg bruker tastatur
**Så** har det `role="tree"`, `treeitem` og `aria-expanded`, piltastene flytter mellom noder og folder inn og ut, og valgt node er markert
**Og** stegene i UJ-2 for BOM-treet er lagt til i testplanen

### Story 4.5: Justere mengde per, ledetid og partiregel

Som planlegger
vil jeg justere mengde per, ledetid og partiregel i BOM-treet,
slik at jeg kan se hva en endring i strukturen gjør med planen.

**Krav:** FR-18, FR-8, AD-7, UX-DR13, UX-DR15. **Tester:** `tests/api/test_bom_edit.py`, testplan scenario E. **Media:** skjermbilde `docs/media/YYYY-MM-DD-bom-tre.png` (treet med panelet åpent).

**Akseptansekriterier:**

**Gitt** at jeg er innlogget
**Når** jeg endrer mengde per på en BOM-linje, eller ledetid og partiregel (L4L, eller FOQ med kvantum) på en vare
**Så** lagres gyldige endringer i én transaksjon
**Og** mengde per 0, ledetid −1, FOQ uten kvantum eller med kvantum 0, og en ukjent regel gir 422 med norsk melding ved feltet, og databasen er uendret

**Gitt** scenario A
**Når** jeg setter mengde per for SKR-100 → SEK-110 til 5 via API-et og kjører MRP
**Så** stemmer resultatet med `expected.json` for scenario E

**Gitt** en vare med FOQ
**Når** jeg bytter til L4L og lagrer
**Så** fjernes kvantumet fra varen, og ved FOQ kreves det igjen
**Og** ledetid 0 godtas og gir frigivelse i samme uke som mottak

**Gitt** scenario A
**Når** jeg setter ledetiden for GIR-220 til 17 via API-et og kjører MRP
**Så** får GIR-220 en E1-melding (ledetid 17, horisont 16), som viser at E1 ikke er knyttet til MOT-210 (SM-C2)

**Gitt** en node i treet
**Når** jeg klikker eller trykker Enter
**Så** åpnes redigeringspanelet med varen og «Valgt under …», feltgruppene «Denne BOM-linjen» og «Varedata», teksten «gjelder alle N steder varen brukes», kvantum bare ved FOQ og lenken «Vis MRP-tabell»
**Og** fokus går til første felt, «Lagre» og «Avbryt» (eller Esc) gir fokus tilbake til noden, og stegene for scenario E er lagt til i testplanen

### Story 4.6: Linje om ikke-kjørte endringer

Som planlegger
vil jeg se hvor mange endringer som ikke er tatt med i MRP ennå,
slik at jeg vet om resultatet jeg ser, er utdatert.

**Krav:** UX-DR16, AD-6 (revisjonsteller). **Tester:** `tests/api/test_pending_changes.py`, testplan UJ-1. **Kan kuttes:** dette er den eneste storyen i v1 som ikke dekker en FR eller et SM. Tar tiden slutt, kuttes den, og avviket føres tilbake i EXPERIENCE.md.

**Akseptansekriterier:**

**Gitt** `input_revision` i planinnstillingene og en kolonne for revisjon i `mrp_run`
**Når** en gyldig endring lagres (MPS, åpne ordre, lager, BOM-linje eller varedata)
**Så** øker telleren i samme transaksjon som endringen, og en kjøring lagrer revisjonen den ble kjørt på
**Og** en avvist endring øker ikke telleren, og tilbakestilling setter den til 0

**Gitt** to lagrede endringer etter siste kjøring
**Når** frontend henter status
**Så** er antallet ikke-kjørte endringer 2, og etter en ny kjøring er det 0
**Og** uten noen kjøring er antallet lik antall lagrede endringer siden tilbakestillingen

**Gitt** ikke-kjørte endringer
**Når** jeg står på `/bom` eller `/plan`
**Så** vises «Du har 2 endringer som ikke er tatt med i MRP ennå.» («1 endring» i entall) med en liten «Kjør MRP», uten farge
**Og** linjen forsvinner etter kjøring, og resultatsidene viser i mellomtiden statuslinjen «Inndata er endret etter siste kjøring.»

## Epic 5: Se hva som endret seg

Etter en ny kjøring ser planleggeren nye og fjernede bestillingsforslag, forverrede, forbedrede og løste meldinger, og endrede celler i MRP-tabellen. UJ-1 virker fra start til slutt.

### Story 5.1: Sammenligning av kjøringer i kjernen

Som planlegger
vil jeg at systemet finner nøyaktig hva som endret seg mellom to kjøringer,
slik at markeringene alltid er riktige.

**Krav:** FR-17, AD-1, AD-6. **Tester:** `tests/mrp/test_compare.py`.

**Akseptansekriterier:**

**Gitt** resultatene for scenario A og B fra `expected.json`
**Når** den rene funksjonen i `rbe.mrp` sammenligner A (forrige) med B (siste)
**Så** returnerer den formen fra AD-6, med 11 nye og 11 fjernede bestillingsforslag, alle for byggenr. 2
**Og** E2 for MOT-210 er paret som `worsened` fra 9 til 11 uker, mens E2 for VIN-920 og E1 for MOT-210 er uendret og ikke er med

**Gitt** A → C
**Når** kjøringene sammenlignes
**Så** er bare GIR-220 endret: ett nytt forslag (1 stk, mottak u8, frigivelse u0), én ny E2, og endrede celler bare for GIR-220, også i uke 0 («Før u1»)

**Gitt** A → E
**Når** kjøringene sammenlignes
**Så** er det 6 nye og 4 fjernede forslag, bare for SEK-110, PLT-900 og PRF-910, og plateordren med mottak i uke 9 er ikke med
**Og** meldingene er uendret, og endrede celler gjelder bare de tre varene

**Gitt** B → A, en endret ledetid for MOT-210 og to meldinger av samme type for samme vare (bygget i testen)
**Når** kjøringene sammenlignes
**Så** er E2 for MOT-210 `improved`, E1 med ny ledetid er `changed`, meldingene pares i rekkefølge etter `receipt_week`, og meldinger uten par er `added` eller `resolved`
**Og** uten forrige kjøring er alle listene tomme, og de forventede settene leses fra `expected.json` i testen, ikke fra en kopi

### Story 5.2: Markering i bestillingsforslag og meldinger

Som planlegger
vil jeg se hvilke forslag og meldinger som er nye, borte, forverret eller forbedret,
slik at jeg ser konsekvensen av endringen min uten å sammenligne selv.

**Krav:** FR-17, AD-6, UX-DR8, UX-DR19. **Tester:** `tests/api/test_mrp_run.py` (endringer), testplan scenario B, C og E. **Media:** skjermbilde `docs/media/YYYY-MM-DD-endringer-forslag.png` etter scenario B. Påminnelse om video av UJ-2: `docs/media/YYYY-MM-DD-uj2-sensor.mp4`.

**Akseptansekriterier:**

**Gitt** to kjøringer
**Når** jeg sender `GET /api/mrp-runs/latest`
**Så** inneholder svaret endringene fra sammenligningen mellom siste og nest siste kjøring, uendret ved siden av resultatet (AD-6)

**Gitt** scenario B etter A
**Når** jeg åpner `/forslag`
**Så** er hovedmotoren øverst i rødt med «▲ Forverret: 9 → 11 uker», forslagene for byggenr. 2 har «ny», og forslagene for byggenr. 1 er umerket
**Og** «Vis 11 forslag som er borte siden forrige kjøring» viser de fjernede forslagene dempet og gjennomstreket med «borte»

**Gitt** scenario C etter A
**Når** jeg åpner `/forslag`
**Så** har E2 for GIR-220 merkelappen «ny», og ingen andre varer er markert

**Gitt** en forbedret, endret eller løst melding
**Når** den vises
**Så** står forbedret i grønt («▼ Forbedret: 11 → 9 uker»), endret uten egen farge («Endret», «Endret: ledetid 20 → 22 uker»), og løste meldinger i grønt under meldingene («Løst: …»), i rekkefølgen røde, rav og grønne
**Og** første kjøring etter tilbakestilling viser ingen markeringer, og stegene for B, C og E er lagt til i testplanen

### Story 5.3: Markering av endrede celler i MRP-tabellen

Som planlegger
vil jeg se hvilke tall i MRP-tabellen som endret seg siden forrige kjøring,
slik at jeg kan følge forplantningen gjennom strukturen.

**Krav:** FR-17, UX-DR11. **Tester:** testplan scenario B, C og E. **Media:** skjermbilde `docs/media/YYYY-MM-DD-endrede-celler.png`. Påminnelse om video av UJ-1: `docs/media/YYYY-MM-DD-uj1-framskynd-byggenr2.mp4`.

**Akseptansekriterier:**

**Gitt** scenario B etter A
**Når** jeg åpner `/mrp/PLT-900`
**Så** er de endrede cellene uthevet med prikket understrek, uten farge, og verktøytipset viser «Forrige kjøring: …»
**Og** skjermleseren får en skjult tekst for hver endret celle, for eksempel «24, endret fra 0»

**Gitt** scenario C etter A
**Når** jeg åpner `/mrp/GIR-220`
**Så** er også cellene i «Før u1» markert (lager 1 → 0 og forfalt frigivelse), og andre varer har ingen markerte celler

**Gitt** avkrysningsboksen «Vis verdier fra forrige kjøring»
**Når** jeg slår den på med tastatur eller mus
**Så** vises endrede celler som «24 ← 0», med forrige verdi i dempet tekst
**Og** UJ-1 kan gjennomføres fra start til slutt, og stegene er lagt til i testplanen

## Epic 6: Klar for sensor

Den manuelle testplanen er gjennomført og dokumentert, sporbarheten er sjekket, README er prøvd på en ren maskin, og skjermbilder og demovideo er oppdatert.

### Story 6.1: Gjennomføre testplanen og sjekke sporbarheten

Som sensor
vil jeg se at appen er testet mot fasiten, og at hvert krav kan spores til kode og test,
slik at jeg kan etterprøve kvaliteten.

**Krav:** SM-1, SM-2, SM-4, NFR-6, NFR-7. **Tester:** `docs/testplan.md`, `uv run python -m pytest`.

**Akseptansekriterier:**

**Gitt** `docs/testplan.md` med stegene for scenario A, B, C og E og UJ-1 og UJ-2
**Når** testplanen gjennomføres fra en nylig tilbakestilt app
**Så** er resultatet for hvert steg ført inn med dato og commit, uten avvik, eller med avvik som er rettet og testet på nytt (SM-2)
**Og** en tastaturgjennomgang av alle sidene og en sjekk av fargebetydningen er ført i testplanen (NFR-6)

**Gitt** `uv run python -m pytest`
**Når** testene kjøres
**Så** består alle, også fasittestene for A–E og skalatesten, og sammendraget er ført i testplanen (SM-1)

**Gitt** tabellen fra FR til story og test (sist i dette dokumentet)
**Når** den sjekkes mot repoet
**Så** finnes hver testfil og hvert steg i testplanen som tabellen viser til, og hver FR-1–FR-18 har minst én story og én test (SM-4)
**Og** den oppdaterte tabellen ligger i `docs/sporbarhet.md`, med lenke fra README

### Story 6.2: README for sensor, prøvd på ren maskin

Som sensor
vil jeg få appen og testene til å kjøre bare ved å følge README,
slik at jeg kan vurdere appen selv om jeg ikke kjenner prosjektet.

**Krav:** SM-3, NFR-1, NFR-2. **Tester:** gjennomføring på ren maskin, ført i testplanen. **Media:** oppdaterte skjermbilder av alle skjermbildene i `docs/media/`. Påminnelse om én demovideo av hele kjerneflyten (under 2 minutter, under 10 MB): `docs/media/YYYY-MM-DD-demo-kjerneflyt.mp4`.

**Akseptansekriterier:**

**Gitt** README
**Når** sensor leser den
**Så** beskriver den appen med skjermbilder, forutsetninger og versjoner, oppstart, demobrukeren, tester, testplanen, sporbarheten, AI-loggen, mappestrukturen, avgrensningen av v1 og bildekrediteringen

**Gitt** en maskin eller Windows-bruker uten prosjektet installert, med bare uv og Node 26 LTS
**Når** en person følger README fra kloning til innlogging og grønne tester
**Så** tar det under 15 minutter, og tid og eventuelle hindringer er ført i testplanen (SM-3)
**Og** hindringer er rettet i README

**Gitt** `docs/media/`
**Når** innleveringen klargjøres
**Så** finnes oppdaterte skjermbilder av innlogging, startside og de fire skjermbildene, beskåret og komprimert, uten hemmeligheter
**Og** demovideoen er lagt inn, eller lenket til hvis den er for stor

## Sporbarhet fra FR til story og test

| FR | Story | Automatisk test | Manuell test (`docs/testplan.md`) |
| --- | --- | --- | --- |
| FR-1 | 1.3, 1.4, 1.5 | `tests/api/test_auth.py`, `tests/api/test_routes_require_login.py`, `tests/api/test_seed.py` (hash) | UJ-2 innlogging |
| FR-2 | 1.2, 1.3 | `tests/test_fixture.py`, `tests/api/test_seed.py` | – |
| FR-3 | 4.3 | `tests/api/test_reset.py` | UJ-2 tilbakestilling |
| FR-4 | 4.4 | `tests/api/test_bom.py` | UJ-2 BOM-tre |
| FR-5 | 4.1, 4.2 | `tests/api/test_mps.py` | Scenario B, UJ-1 |
| FR-6 | 4.1, 4.2 | `tests/api/test_on_hand.py` | Scenario C, UJ-2 |
| FR-7 | 4.1, 4.2 | `tests/api/test_scheduled_receipts.py` | MPS og lager |
| FR-8 | 4.1, 4.2, 4.5 | `tests/api/test_validation.py` (også unikt byggenummer), `tests/api/test_bom_edit.py` | UJ-1 feil uke, UJ-2 negativt lager |
| FR-9 | 2.2, 3.1, 3.2 | `tests/api/test_mrp_run.py`, `tests/mrp/test_properties.py` | Scenario A |
| FR-10 | 2.1, 2.2 | `tests/mrp/test_fixture_scenarios.py` (A, B, C, E) | – |
| FR-11 | 2.2 | `tests/mrp/test_fixture_scenarios.py` (A, B, C, E), `tests/mrp/test_properties.py` | – |
| FR-12 | 2.3 | `tests/mrp/test_fixture_scenarios.py` (D), `tests/mrp/test_properties.py` | UJ-2 byggenr. 1 i uke 4 |
| FR-13 | 2.4, 3.3 | `tests/mrp/test_fixture_scenarios.py` (A–E) | Scenario A |
| FR-14 | 2.4, 3.3 | `tests/mrp/test_fixture_scenarios.py` (A–E) | Scenario A, C |
| FR-15 | 3.4, 5.3 | – | Scenario A, B, C, E |
| FR-16 | 3.2, 3.3, 5.2 | – | Scenario A, B |
| FR-17 | 5.1, 5.2, 5.3 | `tests/mrp/test_compare.py` (A→B, A→C, A→E), `tests/api/test_mrp_run.py` | Scenario B, C, E |
| FR-18 | 4.5 | `tests/api/test_bom_edit.py` (scenario E) | Scenario E |

Alle FR har minst én story og minst én test. FR-15 og FR-16 har bare manuelle tester, fordi frontendtester er utsatt i arkitekturen. SM-4 godtar det.

**Plassering av de enkelte testene og dokumentene:** skalatesten (NFR-3) ligger i story 2.5, importtesten (AD-1) i 1.2 og rutetesten (AD-8) i 1.4. Sammenligningen av kjøringer (FR-17, AD-6) ligger i 5.1. Den manuelle testplanen (SM-2) opprettes i 3.2 og gjennomføres i 6.1. README (SM-3) skrives i 1.7 og ferdigstilles i 6.2.

## Skjermbilder og video

| Story | Skjermbilde (Claude) | Video (brukeren) |
| --- | --- | --- |
| 1.5 | Innloggingsside | – |
| 1.6 | Startside (brukes i README i 1.7) | – |
| 3.3 | Bestillingsforslag og meldinger (hele siden) | – |
| 3.4 | MRP-tabell | – |
| 4.2 | MPS og lager | – |
| 4.3 | Bekreftelsesdialog for tilbakestilling | – |
| 4.5 | BOM-tre med redigeringspanel | – |
| 5.2 | Endringer i forslag og meldinger etter scenario B | UJ-2 fra start til slutt |
| 5.3 | Endrede celler i MRP-tabellen | UJ-1 fra start til slutt |
| 6.2 | Oppdaterte skjermbilder av alt | Demovideo av hele kjerneflyten |
