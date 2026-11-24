# AI-logg

Kuratert logg over vesentlige KI-prompter og beslutninger under utvikling, til bruk for sporbarhet (jf. sensorveiledningens kriterium "Prosess og KI-styring"). Dekker implementasjonsfasen (kode, tester). Planleggingsfasen (brief, PRD, arkitektur, stories) spores i egne BMAD-artefakter under `_bmad-output/` (bl.a. `.memlog.md`-filer per dokument).

## Når og hvordan logge

Legg til én ny oppføring under **Logg** etter en KI-sesjon som endrer kode, tester eller planleggingsdokumenter på en måte som er verdt å spore — ikke for trivielle rettelser (typo, formatering). Commit loggoppføringen sammen med (eller i samme PR som) endringen den beskriver, slik at git-historikken og loggen følger hverandre. Siden commits allerede får en `Co-Authored-By: Claude`-linje, gir git-loggen (`git log`) i tillegg en automatisk oversikt over hvilke commits som hadde KI-involvering.

**Format per oppføring:**

```
## YYYY-MM-DD — Kort tittel på hva som ble gjort

- **Hvorfor**: Hvilket behov, tilbakemelding eller krav som utløste dette.
- **Prompt(er)**: Kort sammendrag av hva som ble spurt om (ikke nødvendigvis ordrett — nok til å forstå hensikten).
- **Verktøy/modell**: Hvilket KI-verktøy og modell (f.eks. Claude Code, Sonnet 5).
- **Endringer**: Hvilke filer/moduler som ble endret.
- **Verifisering**: Hvordan output ble kvalitetssikret (kjørt mot fasit, test, manuell gjennomlesning, code review).
- **Commit**: Kort hash eller melding for commit(ene) endringen hører til (fylles inn etter commit).
```

## Logg

## 2026-11-24 — Avgrenset v1-omfang i product brief

- **Hvorfor**: Faglærers tilbakemelding (`_bmad-output/.../tilbakemelding-product-brief.md`) påpekte at v1 var for stort for ett semester/én person, at suksesskriteriene ikke var testbare, og at Supabase gjorde appen avhengig av ekstern konto.
- **Prompt(er)**: Oppsummer tilbakemeldingen → anbefal neste steg → skriv ny Omfang-seksjon (v1 = flernivå BOM + MRP for ett testfartøy, trinn 2 = sikkerhetslager) → oppdater resten av briefen til å stemme med det nye omfanget → forenkle BOM i v1 til fast struktur uten alternativregler, og rett emnekode IBE130 → IBE160.
- **Verktøy/modell**: Claude Code (Sonnet 5).
- **Endringer**: `_bmad-output/planning-artifacts/briefs/brief-Red Ball Express-2026-09-16/brief.md` (Sammendrag, Løsningen, Hva gjør dette annerledes, Hvem dette tjener, Suksesskriterier, Omfang, Visjon), `addendum.md` (modul-merking v1/trinn 2/utenfor v1, emnekode).
- **Verifisering**: Manuell gjennomlesning for konsistens mot ny Omfang-seksjon og mot faglærers tilbakemelding, punkt for punkt. Ingen automatisert test — dette er et planleggingsdokument, ikke kode.
- **Commit**: `378d919` — Avgrens v1-omfang i product brief til flernivå BOM + MRP

## 2026-11-24 — Testfartøy med håndregnet MRP-fasit

- **Hvorfor**: Suksesskriteriene i briefen (korrekt BOM-eksplosjon, bestillingsforslag og exception-meldinger, synlig forplantning) krever en konkret, håndregnet fasit som MRP-logikken kan testes mot. Dette sto som åpent punkt etter forrige økt.
- **Prompt(er)**: Lag et testfartøy med fast BOM på tre–fire nivåer (inkl. hovedmotor med lang ledetid) og en enkel MPS. Regn ut en komplett MRP-tabell for hånd (nettobehov, bestillingsforslag med ledetidsoffset, minst én exception). Dokumenter som fasit-fil med format og plassering valgt ut fra repoets struktur, og si fra om uklarheter i briefen.
- **Verktøy/modell**: Claude Code (Opus 5.5).
- **Endringer**: `testdata/testfartoy-v1/` (ny: `README.md` med konvensjoner R1–R10, BOM, MPS og beregning steg for steg for scenario A/B/C; `input.json`; `expected.json`). Lenker lagt til i `README.md` og i Omfang-seksjonen i `brief.md`.
- **Verifisering**: Håndregning vist steg for steg i fasiten. `expected.json` kryssjekket mot et uavhengig engangsskript (Node, ikke committet) som beregner MRP fra `input.json`: alle tre scenarier stemmer, og massebalansen går opp per vare. Skriptet ble selv testet ved å legge inn en bevisst feil i fasiten, som det fanget. Tabellene i README er gjengitt fra `expected.json`, slik at de ikke kan sprike fra JSON-en.
- **Commit**: `94a6c10` — Legg til testfartøy med håndregnet MRP-fasit for v1

## 2026-11-24 — PRD for v1, utvidet fasit (scenario D og E)

- **Hvorfor**: Neste BMAD-steg etter brief og fasit. PRD-en skulle avgjøre de åpne spørsmålene fra fasiten og gjøre akseptansekriteriene testbare mot den.
- **Prompt(er)**: Rett motoreksempelet i briefen → lag PRD med `bmad-prd` (rask vei). Brukeren ba om forslag med begrunnelse til ni beslutninger og godtok dem. Brukeren stilte så oppfølgingsspørsmål: når scenario D skal regnes ut (svar: nå), hvordan BOM kan justeres (variant b: mengde per, ledetid og partiregel, FR-18) og om teknologivalget bør utsettes (ja, til arkitekturen). Videre: hvor mange komponenter MRP-en håndterer (førte til en skalatest i NFR-3) og om 2-sekunderskravet var nødvendig (nei, fjernet). Til slutt avslutning med kvalitetssjekk.
- **Verktøy/modell**: Claude Code (Opus 5.5), BMAD-skill `bmad-prd`.
- **Endringer**: `_bmad-output/planning-artifacts/prds/prd-Red Ball Express-2026-11-24/` (`prd.md` med FR-1–FR-18, NFR-1–7, SM-1–4 og SM-C1–2; `addendum.md`; `.memlog.md` med alle beslutninger). `testdata/testfartoy-v1/` (regel R11, scenario D og E). Motoreksempelet i `brief.md` er rettet.
- **Verifisering**: Scenario D og E er regnet ut for hånd og kryssjekket mot det uavhengige kontrollskriptet (alle fem scenarier stemmer). Kontrollskriptet ble utvidet med R11 og BOM-overstyring. PRD-en er sjekket mot BMADs kvalitetsrubrikk. Det avdekket blant annet at FR-17 ikke definerte når et bestillingsforslag er «det samme» uten pegging, og det er rettet. KI-forslag som ble justert av brukeren: en BOM som bare kunne vises, ble til en BOM som kan justeres, og det faste 2-sekunderskravet ble fjernet.
- **Commit**: `7cb8d9a`, `f50d19f`, `ba85817`, pluss avslutnings-commiten som inneholder denne oppføringen.

## 2026-11-24 — Faste regler for AI-logg, commits og sporbarhet i CLAUDE.md

- **Hvorfor**: Brukeren spurte om logging og sporbarhet skjer automatisk. Det gjorde det bare delvis: sesjonsloggen, Co-Authored-By og BMADs .memlog. AI-logg, commits og FR-referanser avhang av at det sto i hver prompt.
- **Prompt(er)**: «Hva må jeg gjøre for å sørge for at loggføring og sporbarhet blir gjennomført? Skjer det automatisk?» → oversikt over hva som er automatisk og ikke, med fire forslag → brukeren valgte å utvide CLAUDE.md. Forslagene om en Stop-hook og branch/PR per story ble ikke valgt nå.
- **Verktøy/modell**: Claude Code (Opus 5.5).
- **Endringer**: `CLAUDE.md` har fått tre nye seksjoner: AI-logg, Commits og Sporbarhet fra krav til kode.
- **Verifisering**: Manuell gjennomlesning mot sensorveiledningens kriterium 1 (sporbar KI-bruk, commit-historikk, sammenheng mellom plan og kode) og mot PRD-ens NFR-7.
- **Commit**: `1f44523` — Legg regler for AI-logg, commits og sporbarhet i CLAUDE.md

## 2026-11-24 — Arkitektur for v1 og teknologivalg

- **Hvorfor**: Neste BMAD-steg etter PRD-en. Teknologivalget (database, frontend, prosjektstruktur) sto som åpent spørsmål i PRD-en og i `issues.md`, og faglærer hadde anbefalt det enkleste for sensor.
- **Prompt(er)**: Les issues, sesjonslogger, PRD, addendum, memlog, fasit og brief → lag arkitekturen med `bmad-architecture`. Brukeren ba om forslag med kort begrunnelse til åtte konkrete beslutninger (database, frontend, mappestruktur, ren MRP-kjerne og tester, testdata uten kopi, lagring av kjøringer for FR-17, innlogging, verktøy og oppstart med eller uten Docker) og presiserte: «Ikke ta valgene for meg», hold det så enkelt som v1 krever, og si fra om noe i PRD-en er uklart i stedet for å anta. KI-en la fram forslag med alternativer og to uklarheter i PRD-en. Brukeren ba KI-en lese CLAUDE.md på nytt før svaret, og godtok deretter alle forslagene. Den nye regelen der om å føre avvik tilbake i planleggingsdokumentet førte til at presiseringene ble skrevet inn i PRD-en, ikke bare i arkitekturen.
- **Verktøy/modell**: Claude Code (Opus 5.5), BMAD-skill `bmad-architecture`.
- **Endringer**: Ny mappe `_bmad-output/planning-artifacts/architecture/architecture-Red Ball Express-2026-11-24/` med `ARCHITECTURE-SPINE.md` (paradigme, AD-1–AD-11, konvensjoner, stack, strukturfrø, kart fra krav til arkitektur, utsatte beslutninger), `.memlog.md` (alle beslutninger og forkastede alternativer) og `reviews/review-gate.md`. Hovedvalg: SQLite uten migreringer, FastAPI + Vite/React-SPA, fasiten som eneste kilde til testdata, uforanderlige MRP-kjøringer med endringer beregnet i kjernen, sesjonscookie og ingen Docker. PRD: FR-8 (MPS-linjer bare for nivå 0-varen, byggenummer ≥ 1) og FR-17 («Før u1»-kolonnen regnes som celler) presisert, og §9 lukket.
- **Verifisering**: Alle versjoner i stacken ble hentet fra npm og PyPI samme dag, i stedet for fra modellens treningsdata. `lint_spine.py` ga 0 funn. Kvalitetssjekken ble kjørt sekvensielt i økta (ikke som uavhengige subagenter): avstemming mot PRD, addendum, fasit og brief, versjonssjekk, og en kritisk gjennomgang som prøvde å bygge to enheter som følger alle reglene, men likevel ikke passer sammen. Den fant seks hull i KI-ens eget utkast, som ble rettet før status `final`. Blant dem: «tom database» var udefinert, formen på endringsdata for FR-17 manglet, og det var uklart om backend eller frontend lager meldingstekst.
- **Commit**: `e416be1` — Legg til arkitektur for v1 med teknologivalg; `010d7e7` — Presiser FR-8 og FR-17 i PRD etter arkitekturen; pluss commiten som inneholder denne oppføringen.

## 2026-11-24 — Opprydding av åpne punkter etter arkitekturen

- **Hvorfor**: Brukeren ba om å løse de åpne punktene i `issues.md`.
- **Prompt(er)**: «Løs issues». KI-en løste TypeScript-punktet selv. For `technology.md` stoppet KI-en og spurte, fordi fila var lagt inn av en annen person (Bård Pettersen). Brukeren valgte å flytte og merke den i stedet for å flytte den ut av repoet. UX-skissene og branch/PR per story ble bevisst stående åpne etter brukerens valg.
- **Verktøy/modell**: Claude Code (Opus 5.5).
- **Endringer**: Arkitekturens Stack-rad for TypeScript er bekreftet mot `create-vite` 9.3.4 (`react-ts` setter `typescript ~7.0.2`). `technology.md` er flyttet til `_bmad-output/planning-artifacts/referanser/technology-pytagoras.md` med en merknad, og lenken i PRD-addendum er oppdatert.
- **Verifisering**: Malens `package.json` ble lest fra npm-pakken (lastet ned til scratchpad, ikke kjørt). `lint_spine.py` ga 0 funn etter endringen. `grep` bekreftet at ingen andre lenker pekte på den gamle stien.
- **Commit**: `75255cd` — Bekreft TypeScript-versjon i arkitekturens stack mot Vite-malen; `e3e2bd6` — Flytt Pytagoras-dokumentet til referanser og merk det; pluss commiten som inneholder denne oppføringen.

## 2026-11-24 — Regel om påminnelser for skjermbilder og video i CLAUDE.md

- **Hvorfor**: Sensorveiledningen bruker skjermbilder og video i repoet som dokumentasjon av design og funksjonalitet, og som reserve hvis appen ikke lar seg kjøre. Samtidig trekker den for store binærfiler. Brukeren ønsket å bli minnet på dette til riktig tid.
- **Prompt(er)**: «Jeg ønsker en regel som minner meg på å ta skjermbilder/videoer når det er riktig tidspunkt, ref. sensorveiledning.»
- **Verktøy/modell**: Claude Code (Opus 5.5).
- **Endringer**: `CLAUDE.md` har fått seksjonen «Skjermbilder og video». Den angir fem tidspunkter (første gang et skjermbilde virker, UX-skisser, en kjerneflyt som virker fra start til slutt, README, før innlevering), at filene lagres i `docs/media/` med datofilnavn, at videoer skal være små og komprimerte, og at påminnelser som ikke er fulgt opp, føres som åpent punkt.
- **Verifisering**: Manuell gjennomlesning mot sensorveiledningen: kriterium 4 (spor av designarbeid), kriterium 6 (README med skjermbilde), kriterium 7 (ingen store binærfiler) og kapittel 3 (skjermbilder og video som reserve).
- **Commit**: `d2c83cd` — Legg til regel om påminnelser for skjermbilder og video i CLAUDE.md

## 2026-11-24 — UX for v1: design og opplevelse

- **Hvorfor**: Neste BMAD-steg etter arkitekturen. Arkitekturen hadde utsatt visuelt uttrykk, komponentbibliotek og skjermbildenes oppbygging til UX, og skisser av skjermbildene sto som åpent punkt (faglærers tilbakemelding, sensorkriterium 4).
- **Prompt(er)**: `bmad-ux` på coaching-vei. Brukerens utgangspunkt: «rent design, behagelig og profesjonell fargepalett, svært enkelt å finne frem, ikke mange komponenter som kjemper om oppmerksomheten». KI-en viste alternativer som HTML-skisser, og brukeren valgte i hver runde. Eksempler på at brukeren styrte eller rettet KI-forslag:
  - Valgte først designretning A, men byttet til C («mest oversiktlig»).
  - Ba om en logo med symbolikk fra konvoioperasjonen i 1944. Valgte konsept 3, ba om flere varianter og valgte 3c. Valgte fontpar 7 (Manrope), selv om det fjernet serif-preget fra C.
  - Innførte prinsippet «farger skal ha betydning» (rød = varsel, grønn = forbedring). Rettet KI-ens utkast til fargekart: E1 skal være rav, og «noe som er nøytralt trenger ikke farge», i stedet for KI-ens forslag om blått for nøytrale endringer.
  - Valgte at en forverret melding skal vises som én melding («forverret: 9 → 11 uker»). Det avviker fra PRD FR-17 og ble ført tilbake.
  - Krevde en rolig startside som mellomledd for å unngå overstimulering, og at «Kjør MRP» bare vises der det er relevant.
  - Ville ha et ekte fotografi av havet, helst fra Norge, i stedet for KI-ens illustrasjon.
- **Verktøy/modell**: Claude Code (Opus 5.5), BMAD-skill `bmad-ux`. Én web-fetch-subagent for å sjekke lisens på bilder fra Unsplash.
- **Endringer**: Ny mappe `_bmad-output/planning-artifacts/ux-designs/ux-Red Ball Express-2026-11-24/`:
  - `DESIGN.md`: tokens, palett A «Varm skifer» med fast fargebetydning, Manrope og komponenter.
  - `EXPERIENCE.md`: navigasjon med adresser, endringsmarkering med paringsregel, tone, tilstander, tastatur, tilgjengelighet, UJ-1 og UJ-2.
  - `mockups/key-screens.html`, `mockups/logo-3c.svg` og `mockups/favicon.svg`.
  - `imports/` med havbilde fra Stavanger (Oleksii Topolianskyi, Unsplash-lisens, WebP 270 KB) og `KILDER.md`.
  - `.working/` med alle skissene, `reviews/` og `.memlog.md`.

  PRD FR-17 og arkitekturens AD-6 er oppdatert med paringsregelen. Arkitekturen har også fått `@fontsource/manrope` 5.3.0 og `docs/media/`.
- **Verifisering**:
  - Kontrasten for alle tekstpar ble beregnet etter WCAG (minst 4,5:1).
  - Lisensen for bildet ble sjekket på bildesiden. Et Unsplash+-bilde (betalt) ble forkastet.
  - Avstemmingen mot kildene fant at designprinsippet «synlig dataflyt» fra brief-addendumet manglet. Det ble lagt inn.
  - Brukeren valgte en kvalitetssjekk med rubrikk og tilgjengelighet. Den ble kjørt sekvensielt i økta, ikke som uavhengige subagenter. Den fant feil i KI-ens eget utkast: kanten på felt hadde for lav kontrast (1,77:1 mot kravet 3:1), forrige verdi i endrede celler var bare tilgjengelig ved hover, og 13 komponenter manglet visuell spesifikasjon. Alt ble rettet før status `final`.
- **Commit**: `22d7f65`, `5469fad`, `2dbc212`, `e08f920`, `17d50ef`, pluss commiten som inneholder denne oppføringen.

## 2026-11-24 — Skjermbilde av UX, ny medieregel og bildekreditering

- **Hvorfor**: Åpne punkter etter UX-økten: skjermbilde av nøkkelskjermbildene til `docs/media/` og kreditering av fotografen.
- **Prompt(er)**: «Må jeg ta skjermbilder eller kan du gjøre det?» og «Må vi kreditere fotografen?». KI-en svarte at den kan ta skjermbilder med Edge uten vindu, men ikke en naturlig video, og at Unsplash ikke krever kreditering. Brukeren valgte at KI-en tar skjermbildene, at regelen i CLAUDE.md endres tilsvarende, og at krediteringen blir en kort linje i README. Brukeren venter med video til appen kjører.
- **Verktøy/modell**: Claude Code (Opus 5.5). Microsoft Edge headless og Pillow.
- **Endringer**: `docs/media/2026-11-24-ux-nokkelskjermbilder.png` (ny). `CLAUDE.md`: Claude tar skjermbilder selv, brukeren tar video. `README.md`: bildekreditering, og UX er lagt til blant planleggingsdokumentene.
- **Verifisering**: Skjermbildet ble sett over før commit. Fotografi og fonter var lastet inn, alle sider kom med, og bildet er beskåret til innholdet og komprimert til 337 KB.
- **Commit**: `d2045f6`, `0000522`, `094ad9d`, pluss commiten som inneholder denne oppføringen.

## 2026-11-24 — Epics og stories for v1

- **Hvorfor**: Neste BMAD-steg etter PRD, arkitektur og UX. Implementasjonen skal kunne gjøres story for story, med én branch og én pull request per story, og hver FR skal kunne spores til story og test (NFR-7, SM-4).
- **Prompt(er)**: Lag epics og stories med `bmad-create-epics-and-stories`. Brukeren ba om forslag med kort begrunnelse og ville ta valgene selv. Seks punkter skulle avgjøres: inndeling og rekkefølge, størrelse på stories, akseptansekriterier, sporbarhet fra FR til story til test, hvor enkelttestene og dokumentene hører hjemme, og når skjermbilder og video skal tas. Uklarheter skulle meldes og føres tilbake.
- **Verktøy/modell**: Claude Code (Opus 5.5), BMAD-skillene `bmad-create-epics-and-stories` og `bmad-advanced-elicitation` (pre-mortem og gjennomgang av grensetilfeller).
- **Endringer**:
  - `_bmad-output/planning-artifacts/epics.md` (ny): 6 epics og 27 stories, kravoversikt med 22 UX-krav, sporbarhetstabell og medieplan.
  - PRD: FR-8 (unikt byggenummer) og SM-2 (testplanen dekker også UJ-1 og UJ-2).
  - Arkitektur: AD-6 (revisjonsteller `input_revision`), AD-7 og ER-diagrammet.
  - EXPERIENCE.md: en utdatert setning om FR-17 er rettet.
- **Verifisering**:
  - Akseptansekriteriene for FR-17 ble regnet mot `expected.json` før de ble brukt: A→B gir 11 nye og 11 fjernede forslag, A→C 1 og 0, A→E 6 og 4.
  - Et skript sjekket at hver FR og hver UX-DR er dekket av minst én story, og at ingen story viser til en senere story. Det fant én henvisning framover (1.5 → 4.2), som ble rettet.
- **Brukerens styring av KI-forslagene**:
  - Brukeren godtok anbefalingene om rekkefølge (skjelettet først), sammenslåing av BOM og redigering, revisjonsteller og utvidet SM-2.
  - Brukeren påpekte at KI-en skrev forslaget på engelsk selv om prosjektet er satt opp på norsk.
  - Brukeren spurte hvorfor KI-en ikke brukte Python. Den hadde byttet til Node fordi `python` på PATH bare var Store-aliaset, men skulle brukt Python via uv.
  - Pre-mortem fant at story 3.2 var for stor, og den ble delt i to.
  - Gjennomgangen av grensetilfeller avdekket at PRD-en ikke sa noe om duplikate byggenumre. Brukeren valgte å avvise duplikater.
  - KI-en sa først at det var 24 stories. Det riktige tallet med inndelingen brukeren godkjente var 26, og 27 etter delingen.
- **Commit**: `1038d5d`, `144175a`, `e0ab294`, `e0cede3`, pluss commiten som inneholder denne oppføringen.

## 2026-11-24 — Sprintstatus for v1

- **Hvorfor**: Sjekke at planene er klare for implementasjon, og lage sporingsfila for stories før første story bygges.
- **Prompt(er)**: «Fortsett» etter epics og stories. Det startet `bmad-sprint-planning` med full flyt: sjekk av om planene er klare, og deretter generering av statusfila.
- **Verktøy/modell**: Claude Code (Opus 5.5), BMAD-skill `bmad-sprint-planning` (skriptet `sprint_plan.py`).
- **Endringer**: `_bmad-output/implementation-artifacts/sprint-status.yaml` (ny): 6 epics og 27 stories i backlog, og retrospektiver som valgfrie.
- **Verifisering**:
  - Klar-sjekken ga PASS. Krav og beslutninger kan spores fram til stories, ingen story viser til en senere story, og arkitektur- og UX-beslutningene stories bygger på, er skrevet ned.
  - Skriptet validerte fila etter skriving. De tre advarslene gjaldt overskrifter som ikke er epics (dekningskart, epic-liste, sporbarhet), og de ble ignorert med vilje.
  - Skriptet kunne ikke startes via uv sitt skriptmiljø (Windows: «Ingen tilgang»). Det ble kjørt med `uv run --no-project --with ruamel.yaml python`.
- **Commit**: `d6c0931`, pluss commiten som inneholder denne oppføringen.

## 2026-11-24 — Story 1.1: backend-oppsett med helsesjekk og konfigurasjon

- **Hvorfor**: Første story i epic 1. Sensor skal kunne starte backend og kjøre testene med én kommando hver, uten manuelt oppsett og uten hemmeligheter i repoet (NFR-1, NFR-2, AD-9–AD-11).
- **Prompt(er)**: «Les spec-1-1-backend-oppsett-med-helsesjekk-og-konfigurasjon.md og implementer den. Specen er eneste sannhetskilde.» Specen fastsatte blant annet versjoner, stier, at tom `RBE_SESSION_SECRET` regnes som manglende, `basicConfig` i stedet for `dictConfig`, og demobrukeren `demo`/`demo` (Thobias' beslutning).
- **Verktøy/modell**: Claude Code (Opus 5.5), som underagent fra `bmad-build`.
- **Endringer**: Nytt uv-prosjekt `backend/` (`pyproject.toml`, `.python-version`, `uv.lock`, `.env.example`), `src/rbe/config.py`, `src/rbe/main.py`, `src/rbe/api/health.py`, `tests/test_config.py`, `tests/api/test_health.py`. `.gitignore` har fått `backend/data/`.
- **Verifisering**: `uv lock` løste alle festede versjoner mot Python 3.14.7. 11 tester består, og `ruff check` og `ruff format --check` gir 0 funn. AST-sjekken av at bare `config.py` leser miljøet ble prøvd med en forbudt import lagt inn midlertidig, og den feilet som den skulle. Fra repo-rota svarte `GET /api/health` med `{"status":"ok"}`, og advarselen om tilfeldig nøkkel kom i loggen. `git check-ignore` bekreftet at `backend/.env` og `backend/data/` ikke spores. Avvik i kjøringen: på denne maskinen nekter Windows å kjøre `.venv\Scripts\python.exe` (os error 5), så `uv run` feiler. Testene og serveren ble derfor kjørt med uv sin Python 3.14 direkte og `PYTHONPATH` satt til `src` og venv-ens `site-packages`. `uv run …` må prøves på en annen maskin eller etter at sperren er fjernet.
- **Commit**: `5202b6c` — Opprett uv-prosjekt for backend med konfigurasjon (AD-9, NFR-2); `95fb071` — Legg til FastAPI-app med helsesjekk (NFR-1, AD-10); pluss commiten med testene og denne oppføringen.
