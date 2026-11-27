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
- **Verifisering**:
  - `uv lock` løste alle festede versjoner mot Python 3.14.7.
  - AST-sjekken av at bare `config.py` leser miljøet ble prøvd med en forbudt import lagt inn midlertidig, og den feilet som den skulle.
  - `GET /api/health` svarte `{"status":"ok"}`, og advarselen om tilfeldig nøkkel kom i loggen.
  - `git check-ignore` bekreftet at `backend/.env` og `backend/data/` ikke spores.
  - **Gjennomgang av specen før godkjenning:** to runder med en subagent ga 15 funn, og alle ble tatt inn etter brukerens valg. Eksempler: `[build-system]` manglet, og `import rbe` ville derfor feilet i testene. En lokal `.env` kunne lekke inn i testene. Logging med `dictConfig` ville slått av loggeren som testene sjekker.
  - **Gjennomgang av koden etterpå:** tre uavhengige lag (blind-hunter, edge-case-hunter, verification-gap) ga 24 funn. 10 ble rettet i `ec068af`, blant annet at standardplasseringen av `.env` og advarselen ved oppstart ikke var testet. 2 er utsatt til story 1.3 i `deferred-work.md`, og 12 ble avvist med begrunnelse i specens triagelogg.
  - Til slutt består 15 tester, og ruff gir 0 funn.
  - **Avvik:** på denne maskinen nekter Windows å kjøre filer som uv lager (`uv venv`, `pytest.exe`, `fastapi.exe`: os error 5). Løsningen var å lage `backend/.venv` med Pythons egen `venv` og bruke `uv run python -m pytest` og `uv run python -m fastapi dev`. `uv run pytest` og `uv run fastapi dev` slik de står i README-flyten, er ikke prøvd ennå. Det må gjøres på en annen maskin senest i story 1.7.
- **Commit**: `5202b6c`, `95fb071`, `29711fa`, `ec068af`, pluss commiten som inneholder denne oppføringen.

## 2026-11-26 — Story 1.2: kjernens datatyper og fasitparser

- **Hvorfor**: Seed (story 1.3) og fasittestene i epic 2 trenger testfartøyets inndata som kjernens egne typer, lest direkte fra `testdata/testfartoy-v1/input.json`, slik at app og fasit ikke kan sprike (FR-2, AD-4). MRP-kjernen skal være ren fra første linje (AD-1, AD-2).
- **Prompt(er)**: «Les spec-1-2-kjernens-datatyper-og-fasitparser.md og implementer den. Specen er eneste sannhetskilde.» Specen fastsatte typene og feltnavnene, reglene for override, hvilke feil som skal gi `FixtureError`, og lista over forbudte importer og kall i `rbe.mrp`.
- **Verktøy/modell**: Claude Code (Opus 5.5), som underagent fra `bmad-build`.
- **Endringer**: `backend/src/rbe/mrp/__init__.py` og `types.py` (nye, frosne inndatatyper), `backend/src/rbe/fixture.py` (ny, `load_input` og `FixtureError`), `backend/tests/conftest.py` (fixturene `fixture_dir` og `input_path`), `backend/tests/test_fixture.py` og `backend/tests/mrp/test_core_is_pure.py` (nye).
- **Verifisering**:
  - 65 tester består (27 nye for parseren, 23 for renhetstesten), og `ruff check` og `ruff format --check` gir 0 funn.
  - Scenario A sammenlignes felt for felt med `input.json`, og B–E sjekkes som «A pluss overstyringen» med `dataclasses.replace`.
  - Renhetstesten ble prøvd med en midlertidig `import pathlib` i `rbe/mrp/types.py`. Den feilet med `{'rbe.mrp.types': ['import pathlib (forbudt)']}`, og linjen ble fjernet før commit.
  - En test skanner `src/rbe` for varenumrene i fasiten og finner ingen.
  - **Utover specen:** parseren avviser også ukjente override-nøkler, feil felttyper, ukjent partiregel eller varetype og scenarioer i ring. Det står i specens Implementation Notes.
  - **Gjennomgang av koden etterpå:** tre uavhengige lag (blind-hunter, edge-case-hunter, verification-gap) ga 12 funn etter sammenslåing. 6 ble rettet i `2329d35`:
    - flere av avvisningene parseren gjorde, var ikke testet, og kunne fjernes uten at noen test feilet
    - et feilstavet `overide` på scenarionivå ga stille en kopi av A
    - renhetsvakten slapp gjennom `builtins`, `importlib`, `__import__`, `eval` og `exec`

    6 ble avvist med begrunnelse i specens triagelogg, blant annet full validering av grunndataene. Den hører til API-et (AD-7) og kjernen (story 2.1).
  - Til slutt består 78 tester, og ruff gir 0 funn.
  - Specen ble godkjent uten egen gjennomgang. Brukeren valgte å beholde den samlet selv om den var på omtrent 2000 tokens.
- **Commit**: `38f2ef1`, `852af8a`, `cdf0bb9`, `2329d35`, pluss commiten som inneholder denne oppføringen.

## 2026-11-26 — Story 1.3: database og seed ved tom database

- **Hvorfor**: Sensor skal møte testfartøyet og demobrukeren uten å legge inn noe selv, og passordet skal ikke lagres i klartekst (FR-2, FR-1, AD-4, AD-5).
- **Prompt(er)**: «Les spec-1-3-database-og-seed-ved-tom-database.md og implementer den. Specen er eneste sannhetskilde.» Specen fastsatte tabellene, rekkefølgen i oppstarten og I/O-matrisen. Brukeren hadde på forhånd besluttet at et endret demopassord skal oppdatere hashen ved oppstart (alternativ b), så databasefila aldri må slettes for å bytte passord.
- **Verktøy/modell**: Claude Code (Opus 5.5), som underagent fra `bmad-build`.
- **Endringer**: `backend/pyproject.toml` og `uv.lock` (`sqlalchemy==2.1.9`, `pwdlib[argon2]==0.4.2`), ny pakke `backend/src/rbe/db/` (`models.py`, `session.py`, `seed.py`, `repository.py`), `backend/src/rbe/main.py` (`lifespan` som kjører oppstarten og legger engine og sessionmaker på `app.state`) og `backend/tests/api/test_seed.py` (ny).
- **Verifisering**:
  - 87 tester består (9 nye), og `ruff check` og `ruff format --check` gir 0 funn. Testene dekker alle radene i I/O-matrisen mot en midlertidig SQLite-fil i en mappe med mellomrom som ikke finnes på forhånd.
  - `read_input` sammenlignes med `load_input(..., "A")` etter at begge er sortert likt. Fasiten har ikke varene og BOM-linjene sortert, mens specen krever at `read_input` sorterer på id og (forelder, barn).
  - Backend ble startet to ganger lokalt (`uv run python -m fastapi run`). Første gang logget den seed av scenario A og opprettelse av demobrukeren, andre gang «Databasen har allerede data» og at demobrukeren finnes. `backend/data/` ble slettet etterpå.
  - SQLite håndhever fremmednøklene (`PRAGMA foreign_keys=ON`). Etter gjennomgangen er dette testet, og orkestratoren har sjekket at testen feiler når pragmaet fjernes.
  - **Gjennomgang av koden etterpå:** tre uavhengige lag ga 17 funn etter sammenslåing.
    - 5 ble rettet i `d6fbc6b`: fremmednøklene var ikke testet, og testene brukte en engine uten pragmaet. Testen for manglende fasit traff mappenavnet i testen i stedet for feilmeldingen. Testene kunne lese en lokal `.env`. Grenen «unchanged» og loggtekstene var ikke testet, og nå brukes `verify_and_update`.
    - 1 er utsatt til story 4.6 i `deferred-work.md`: en gammel databasefil må gi en tydelig melding når skjemaet endres.
    - 11 ble avvist med begrunnelse i specens triagelogg.
  - Til slutt består 89 tester, og ruff gir 0 funn.
  - **Brukerens styring:** KI-en foreslo i specen to måter å håndtere et endret demopassord på. Brukeren spurte hvorfor databasefila måtte slettes med alternativ a), og valgte b) etter forklaringen: hashen synkroniseres ved oppstart. AD-5 i arkitekturen er presisert tilsvarende (`0830903`).
  - Ingen skjermbilder, fordi storyen ikke har noe brukergrensesnitt.
- **Commit**: `0830903` (AD-5), `5bc79c3`, `1746ff5`, `05daff7`, `d6fbc6b`, pluss commiten som inneholder denne oppføringen.

## 2026-11-26 — Story 1.4: innlogging i backend

- **Hvorfor**: Hvem som helst som nådde backend, kunne lese alt API-et ga. Planleggeren skal logge inn og ut med demobrukeren, og alle `/api`-ruter utenom innlogging og helsesjekk skal avvise uinnloggede (FR-1, AD-8).
- **Prompt(er)**: «Les spec-1-4-innlogging-i-backend.md og implementer den. Specen er eneste sannhetskilde.» Specen fastsatte cookien (`rbe_session`, 8 timer, SameSite=Lax), endepunktene, feilmeldingene, dummy-hashen ved ukjent brukernavn og at `require_user` settes på ruterne, ikke på hver rute.
- **Verktøy/modell**: Claude Code (Opus 5.5), som underagent fra `bmad-build`.
- **Endringer**: `backend/pyproject.toml` og `uv.lock` (`itsdangerous==2.2.0`), nye `backend/src/rbe/api/deps.py` (`get_session`, `require_user`, `current_user`) og `api/auth.py` (`public_router` med innlogging, `router` med utlogging og `me`), `backend/src/rbe/main.py` (`SessionMiddleware` og rutere), `backend/tests/conftest.py` (`client`, `logged_in_client`), nye `tests/api/test_auth.py` og `tests/api/test_routes_require_login.py`.
- **Verifisering**:
  - 104 tester består (15 nye), og `ruff check` og `ruff format --check` gir 0 funn. Auth-testene dekker alle radene i I/O-matrisen, blant annet tuklet cookie, slettet bruker og at passordet ikke havner i loggen. At ukjent brukernavn verifiseres mot dummy-hashen, er sjekket med en spion på `verify`.
  - Akseptansekriteriet er prøvd: med `require_user` fjernet midlertidig fra `include_router` i `create_app()` feiler rutetesten og nevner `POST /api/auth/logout` og `GET /api/auth/me`. Endringen ble tilbakestilt etterpå.
  - **To avvik fra den første planen, oppdaget underveis:**
    - FastAPI 0.165 flater ikke ut inkluderte rutere i `app.routes`, men legger inn ett objekt per ruter. Den første rutetesten fant derfor ingen ruter og besto uten å sjekke noe. Det ble oppdaget fordi testen for unntakslista feilet. Rutetesten bruker nå FastAPIs `iter_route_contexts`, som gir hver rute med avhengighetene fra `include_router`.
    - Hvis rutene selv avhenger av `require_user` for å få brukeren, finnes den i avhengighetstreet selv om ruteren mangler den, og akseptansekriteriet kan ikke oppfylles. `require_user` legger derfor brukeren på `request.state`, og rutene leser den med `current_user`, som også avviser med 401 hvis brukeren mangler.
  - **Gjennomgang med tre uavhengige lag** (blind-hunter, edge-case-hunter, verification-gap): 15 funn, hvorav 5 ble rettet og 10 avvist med begrunnelse i specens Review Triage Log.
    - Rettet: en test av at cookien signeres med `RBE_SESSION_SECRET`, en test av at innlogging tømmer en eksisterende sesjon, en test av reserveveien i `current_user`, og `%r` når brukernavnet logges (`56d2387`).
    - AD-8 er presisert i arkitekturen, siden CLAUDE.md krever at avvik føres tilbake (`29d942e`).
    - Avvist blant annet: lengdegrense på passordet, sperre av cookien etter utlogging og begrensning av antall forsøk. Dette er en lokal demoapp med én bruker, og specen holder slikt utenfor.
    - Etter rettelsene består 107 tester.
  - **Brukerens styring:** brukeren godkjente specen uten endringer og valgte å beholde den samlet, selv om den var over anbefalt lengde.
  - Ingen skjermbilder, fordi storyen ikke har noe brukergrensesnitt.
- **Commit**: `eef5a41`, `6970659`, `22912e3`, `29d942e` (AD-8), `56d2387`, pluss commiten som inneholder denne oppdateringen.

## 2026-11-26 — Story 1.5: frontend-oppsett, designtokens og innloggingsside

- **Hvorfor**: Det fantes ingen frontend. Sensor skal åpne appen i nettleseren, bli sendt til innlogging og logge inn med demobrukeren mot API-et fra story 1.4 (FR-1, NFR-6, AD-11, UX-DR1, UX-DR2, UX-DR5, UX-DR20).
- **Prompt(er)**: «Les spec-1-5-frontend-oppsett-designtokens-og-innloggingsside.md og implementer den. Specen er eneste sannhetskilde.» Specen fastsatte de festede versjonene, Biome i stedet for ESLint, proxyen, tokennavnene, oppførselen til klienten ved 401 og nettverksfeil, at adressen brukeren ba om ligger i routerens `state` (ikke i et søkeparameter, for å unngå åpen omdirigering), og alle tekstene og ARIA-attributtene på innloggingssiden.
- **Verktøy/modell**: Claude Code (Opus 5.5), som underagent fra `bmad-build`. Edge uten vindu for skjermbilde og nettlesertest.
- **Endringer**: ny mappe `frontend/` fra `create-vite` 9.4.0 (`react-ts`): `package.json` med nøyaktige versjoner, `biome.json`, `vite.config.ts` (proxy), `index.html` (`lang="no"`, favicon), `src/styles/tokens.css` og `global.css`, `src/components/Logo.tsx`, `src/api/client.ts`, `src/auth/AuthProvider.tsx` (tilstand, `RequireAuth`), `src/pages/LoginPage.tsx` og `SignedInPage.tsx`, `src/App.tsx` og `main.tsx`. Skjermbildet `docs/media/2026-11-26-innlogging.png`.
- **Verifisering**:
  - `npm run build` og `npx biome check` gir 0 feil. Backend har fortsatt 107 tester som består.
  - `curl -i http://localhost:5173/api/health` gir 200 og `{"status":"ok"}` gjennom proxyen.
  - Alle radene i I/O-matrisen er prøvd i Edge uten vindu, styrt over DevTools-protokollen med ekte Tab og Enter. Et innloggingskall ble holdt igjen for å se «Logger inn …», og utløpt sesjon ble laget ved å logge ut i backend uten at frontend visste det. Med backend stoppet svarer Vite-proxyen 502. Steg og utfall står i specens Implementation Notes.
  - **Avvik fra specen:** malen lager ikke lenger ESLint, men oxlint. Det ble fjernet i stedet. Biome fikk `lineEnding: "auto"` etter at testen viste at filer med CRLF, som git sjekker ut med `core.autocrlf=true` på Windows, ga formateringsfeil.
  - Skjermbildet er tatt med Edge uten vindu (1280 × 800), beskåret til kortet og komprimert til 6 kB.
  - **Gjennomgang med tre uavhengige lag** (blind-hunter, edge-case-hunter, verification-gap): 21 funn.
    - Rettet: Vitest 5.1.1 og 8 enhetstester for fetch-klienten (`7d659c7`). Det er prøvd at testen for 504 feiler når sjekken smalnes. I tillegg er manglende hash i denne oppføringen rettet.
    - Utsatt: en automatisk test av flyten for innlogging. Story 1.6 bygger om rutene, og arkitekturen bruker den manuelle testplanen for flyten (`deferred-work.md`).
    - Avvist: 18 funn med begrunnelse i specens Review Triage Log, blant annet mobilbredde, `vite preview` og README, som er story 1.7.
  - **Brukerens styring:** brukeren godkjente specen uten endringer og valgte å beholde den samlet, selv om den var godt over anbefalt lengde (ca. 2 800 tokens). Før storyen ba brukeren KI-en flette PR #4 uten egen gjennomgang. Valget ble gitt eksplisitt, med at det da ikke blir noen menneskelig gjennomgang av PR-en.
- **Commit**: `6f85d01`, `46b4734`, `f8c2c4b` (Biomes linjeskift), `7ae7734` (skjermbilde og AI-logg), `7d659c7` (Vitest), pluss commiten som inneholder denne oppdateringen.

## 2026-11-26 — Story 1.6: menylinje og startside

- **Hvorfor**: Etter innlogging kom man til en foreløpig side uten navigasjon. Planleggeren skal komme til en rolig startside med fire dører og ha menylinjen med utlogging på alle sider (FR-1, UX-DR3, UX-DR4, UX-DR21, UX-DR22).
- **Prompt(er)**: «Les spec-1-6-menylinje-og-startside.md og implementer den. Specen er eneste sannhetskilde.» Specen fastsatte tekstene, rekkefølgen på dørene, at utlogging uten server beholder innloggingen, at 401 på utlogging ikke skal gi meldingen om utløpt sesjon, og at fokus flyttes til H1 ved sidebytte, men ikke ved første lasting.
- **Verktøy/modell**: Claude Code (Opus 5.5), som underagent fra `bmad-build`. Edge uten vindu over DevTools-protokollen for nettlesertest og skjermbilde.
- **Endringer**: `frontend/src/auth/AuthProvider.tsx` (`logout`, notice `signed-out`), nye `components/AppLayout`, `TopNav`, `PageTitle` og `navigation.ts` (med `navigation.test.ts`), `pages/HomePage`, `PlaceholderPage` og `NotFoundPage`, havfotoet i `src/assets/`, rutene i `App.tsx`. `SignedInPage.tsx` er fjernet. Skjermbildet `docs/media/2026-11-26-startside.png`.
- **Verifisering**:
  - `npm run build`, `npx biome check` og `npm run test` (10 tester) gir 0 feil. Backend har fortsatt 107 tester som består, og `ruff` er ren.
  - Alle radene i I/O-matrisen er prøvd i Edge uten vindu med ekte Tab, Enter og museklikk: 32 av 32 sjekker besto, ved 1280 og 1024 px. Utlogging uten server ble laget ved å avvise logout-kallet i nettleseren (`Fetch.failRequest`), og 401 på utlogging ved å logge ut i backend først. Steg og utfall står i specens Implementation Notes.
  - Gjennomgangen fant én feil som ble rettet: « · » mellom brukernavn og «Logg ut» forsvant, fordi flex fjerner mellomrommene i teksten.
  - **Avvik fra specen:** ruteverneren er endret litt. Etter egen utlogging sender den til `/logg-inn` uten adresse (notice `signed-out`). Ellers ville den lagt siden man logget ut fra i `state`, og neste innlogging ville gått dit i stedet for til `/`. Navigasjonen i React Router går i en overgang (`startTransition`), så det var ikke trygt å navigere før brukeren ble satt til `null`.
  - Skjermbildet er tatt med Edge uten vindu (1280 × 800), beskåret til 1280 × 560 og redusert til 256 farger (179 kB). Paletten har tokenfargene med, så logoballen beholder fargen.
  - **Gjennomgang med tre uavhengige lag** (blind-hunter, edge-case-hunter, verification-gap): 11 funn.
    - Rettet (`8c70170`):
      - Etter utlogging husket ikke appen adressen fra en dyp lenke (nå `clearSignedOut()`).
      - Feillinjen etter mislykket utlogging fulgte med til andre sider.
      - Testnavnet viser nå til NFR-6.
      - Nettleserstegene er prøvd på nytt: 38 av 38 sjekker besto.
    - Utsatt: et testmiljø for komponenter (jsdom). Uten det er utlogging, `RequireAuth`, fokus og ruter bare prøvd manuelt (`deferred-work.md`).
    - Avvist: 6 funn med begrunnelse i specens Review Triage Log.
  - **Brukerens styring:** brukeren godkjente specen uten endringer og valgte å beholde den samlet (ca. 2 500 tokens). Før storyen prøvde brukeren innloggingen fra 1.5 selv og fikk «Fikk ikke kontakt med serveren». KI-en fant at backend ikke kjørte, og at den korte `uv run fastapi dev` stoppes av en Windows-sperre på maskinen. Etter at backend ble startet med `python -m`, bekreftet brukeren at innloggingen virket. Deretter ba brukeren KI-en flette PR #5.
- **Commit**: `593e95c` (utlogging, oppsett, menylinje, fokus), `ac5af66` (startside, plassholdere, ukjent adresse), `a27ce44` (skjermbilde og AI-logg), `8c70170` (rettelser etter gjennomgangen), pluss commiten som inneholder denne oppdateringen.

## 2026-11-26 — Vis/skjul passord på innloggingssiden

- **Hvorfor**: Brukeren prøvde innloggingssiden og savnet en måte å se passordet man skriver på (FR-1, UX-DR5, NFR-6).
- **Prompt(er)**: «Det er ikke mulig å trykke på slik at man har valget til å se passordet man skriver inn. Det ønsker jeg».
- **Verktøy/modell**: Claude Code (Opus 5.5), direkte uten `bmad-build`, fordi endringen er liten og avgrenset. Edge uten vindu for skjermbilde.
- **Endringer**:
  - `frontend/src/pages/LoginPage.tsx` og `LoginPage.css`: tekstknappen «Vis passord» / «Skjul passord» (`type="button"`, `aria-controls`) står på samme linje som etiketten «Passord». Den bytter feltet mellom `password` og `text`.
  - KI-en valgte plasseringen ved etiketten og ikke inni feltet, så knappen ikke dekker teksten og den synlige teksten er knappens navn (WCAG 2.5.3).
  - Passordet skjules igjen ved innsending.
  - Skjermbildet `docs/media/2026-11-26-innlogging.png` er oppdatert, og DESIGN.md (`login-card`) beskriver knappen.
- **Verifisering**: `npm run build`, `npx biome check` og `npm run test` (10 tester) gir 0 feil. Skjermbildet fra Edge uten vindu viser knappen til høyre for etiketten.
- **Commit**: commiten med koden og skjermbildet, og commiten med DESIGN.md og denne oppføringen.

## 2026-11-26 — Skjermbilder fra ekte nettleser i stedet for Edge uten vindu

- **Hvorfor**: Brukeren påpekte at skjermbildene tatt med Edge uten vindu ikke ga et riktig bilde av appen («Der ligger skrift utenfor boksene. Det må gjøres i en nettleser i full skjerm utenfor terminal, eller underveis i videoen»).
- **Prompt(er)**: Se over. Det er en rettelse av en KI-praksis som stod i CLAUDE.md.
- **Verktøy/modell**: Claude Code (Opus 5.5). ffmpeg (via `imageio-ffmpeg`) og Pillow.
- **Endringer**:
  - `docs/media/2026-11-26-startside.png` og `2026-11-26-innlogging.png` er tatt på nytt. Bildene er hentet fra brukerens skjermopptak i full skjerm (1902 × 1118): startsiden fra 0:34,5 og innloggingen fra 0:39,5.
  - Nettleserrammen er beskåret bort. Cursoren på startsiden er dekket med bakgrunnsfargen.
  - Bildene er komprimert til 243 kB og 20 kB.
  - CLAUDE.md, under «Skjermbilder og video», sier nå at skjermbilder av appen skal vise den i en ekte nettleser i full skjerm.
- **Verifisering**: Bildene er sjekket visuelt: ingen cursor, ingen nettleserramme og ingen hemmeligheter.
- **Commit**: commiten som inneholder bildene, CLAUDE.md og denne oppføringen.

## 2026-11-26 — Story 1.7: README v1 med oppstart og tester

- **Hvorfor**: README sa ingenting om oppstart, innlogging eller tester. Sensor skal klone repoet og få app og tester til å kjøre med bare README, på under 15 minutter og uten kontoer eller hemmeligheter (NFR-1, NFR-2, SM-3).
- **Prompt(er)**: «Les spec-1-7-readme-v1-med-oppstart-og-tester.md og implementer den. Specen er eneste sannhetskilde.» Specen fastsatte innholdet og rekkefølgen i README, og at README skulle prøves bokstavelig fra en ny klone i en mappe med mellomrom.
- **Verktøy/modell**: Claude Code (Opus 5.5), som underagent fra `bmad-build`. Edge uten vindu over DevTools-protokollen for innloggingen.
- **Endringer**:
  - `README.md` er skrevet om: hva appen gjør, skjermbilde og video, forutsetninger, oppstart i to terminaler, demobrukeren, tester og kvalitetssjekk, feilsøking og lenker til planleggingsdokumentene.
  - ARCHITECTURE-SPINE.md: AD-10 og AD-11 forklarer hvorfor README bruker `uv run python -m …`.
  - Specen har fått steg og utfall fra prøven i Implementation Notes.
- **Verifisering**:
  - Ny klone fra GitHub i en mappe med mellomrom: 107 backendtester består med `uv run python -m pytest`, og ruff gir 0 funn. Frontend har 10 tester som består, `biome` gir 0 funn, og bygget lykkes.
  - Første start av backend opprettet databasen med testfartøyet og demobrukeren, og `demo`/`demo` ga startsiden i Edge uten vindu.
  - Et lite skript fant 0 døde relative lenker i README.
  - **Prøven rettet README to steder:**
    - En klone i scratchpad feilet med «Filename too long» og manglende moduler, fordi stien ble over 260 tegn. README ber nå om en kort sti og forklarer feilen.
    - `uv python install` ble fjernet fra løsningen på os error 5, fordi den bare ga en advarsel.
  - **Avvik:** å stoppe serverne fra økten på 8000 og 5173 ble nektet av tillatelsessystemet. Backend fra klonen ble derfor prøvd på port 8001, og frontend fra klonen fikk port 5175. Raden «Backend kjører ikke» ble ikke prøvd på nytt.
  - **Brukerens styring:** brukeren valgte alternativ B for kommandoene, «den som er best og oppfyller kravene sensor stiller». Det ble `python -m`-formen, og prøven bekreftet valget: `uv run pytest` ga os error 5 i den nye klonen, mens `uv run python -m pytest` virket.
  - **Gjennomgang med tre uavhengige lag** (blind-hunter, edge-case-hunter, verification-gap): 15 funn.
    - Rettet (`f727195`):
      - README beskrev MRP-funksjoner som om de fantes. Den har nå en statusdel, og setningen om beregningstestene er rettet.
      - Det er nye setninger om `.env`, `RBE_SESSION_SECRET` og endret demobruker, og et nytt punkt om opptatt port 8000.
      - Tilbakestillingen nevner nå `RBE_DATABASE_URL`, og rådet om kort sti peker på `C:\dev`.
      - Kommandoene bruker `python -m ruff`, og formuleringen i AD-11 er presisert.
    - Avvist: 6 funn med begrunnelse i specens Review Triage Log. Tidtaking etter SM-3 på en ren maskin hører til story 6.2.
  - **Rettelse fra brukeren underveis:** skjermbildene ble tatt på nytt fra brukerens opptak i ekte nettleser (egen oppføring over).
- **Commit**: `8225c6b` (README v1), `7466eac` (rettelser etter prøven), `f3518eb` (AD-10 og AD-11), `f38907f` (første versjon av denne oppføringen og prøven i specen), `f727195` (rettelser etter gjennomgangen), pluss commiten som inneholder denne oppdateringen.

## 2026-11-27 — Retrospektiv av epic 1 og regel om retrospektiv etter hver epic

- **Hvorfor**: Brukeren spurte om dokumentasjonen holder til en refleksjonsrapport. Ett av svarene var at ingen epic var oppsummert. Brukeren ba om en retrospektiv av det som er gjort, og om at det skal gjøres etter hver epic framover.
- **Prompt(er)**: «Gjør 3. for det vi allerede har gjort og sett det opp slik at vi gjør det fremover også. Sensorveiledning ligger vel allerede inne?»
- **Verktøy/modell**: Claude Code (Opus 5.5) med `bmad-retrospective`, og `bmad-review` med tre underagenter: adversarial, edge-case-hunter og verification-gap. Diffen var `73f2283..24f0d85`, med `backend/` og `frontend/`.
- **Endringer**:
  - [epic-1-retro-2026-11-27.md](../_bmad-output/implementation-artifacts/epic-1-retro-2026-11-27.md) har funn med kilde, prøve av appen, 9 tiltak og vurdering av akseptansen.
  - Sprintstatus: `epic-1-retrospective` er satt til done, og de 9 tiltakene er ført inn med skriptet til skillen.
  - CLAUDE.md har fått seksjonen «Retrospektiv etter hver epic».
- **Verifisering**:
  - 107 backendtester og 10 frontendtester består, og ruff og Biome gir 0 funn.
  - Innloggingsflyten er prøvd fra start til slutt med curl mot en midlertidig backend. Prøven bekreftet at en kopiert cookie fortsatt virker etter utlogging, slik det er godtatt i triageloggen til 1.4. Avveiningen står ikke i AD-8 (tiltak 2).
  - Funnene fra underagentene som tiltakene bygger på, er sjekket mot koden: `get_session` uten `begin()` (`deps.py:13-16`), sesjonsnøkkelen uten krav til lengde (`config.py:35-43`) og innstillingene som leses to ganger (`main.py:21, 36`).
- **Resultat og vurdering**:
  - Gjennomgangen av hele diffen fant 18 nye funn som ingen enkelt story så.
  - Det viktigste er at `get_session` ikke committer, noe som må rettes før første skrivende rute i 3.1. To konfigurasjonsvariabler som README lover, mangler også tester.
  - Prosessfunnene:
    - 63 av 72 commits er fra én dag.
    - PR #4–#6 ble flettet uten menneskelig gjennomgang.
    - Prosessdokumentasjonen har ingen egne refleksjoner.
  - Maskinens vurdering er *rejected*, fordi story 1.7 står i review (PR #7 er ikke flettet). Den blir *accepted-with-open-items* når brukeren fletter PR-en og bekrefter.
  - **Sensorveiledningen:** den ligger i semestermappa utenfor repoet. Den ble flyttet dit med vilje i PRD-økten (kriterium 7). Den sier at refleksjonen vurderes i del 2, som er refleksjonsrapporten og teller 30 %. Veiledningen for del 2 finnes ikke i repoet eller i semestermappa.
- **Oppfølging samme dag**:
  - Prompt: «1. Ja 2. Hva anbefaler du? 3. Ja»
  - PR #7 er flettet (`8784631`). Story 1.7 og epic 1 er satt til done, og vurderingen er endret til *accepted-with-open-items* etter brukerens beslutning (`3506901`).
  - Brukeren godtok forslaget om refleksjonsnotater (tiltak 9). Det er laget [docs/refleksjonsnotater.md](refleksjonsnotater.md) med mal, og CLAUDE.md har fått en regel: Claude ber om to–tre setninger ved slutten av hver økt og fører dem inn ordrett (`ea544c0`).
  - `/docs`: Claude anbefalte å skru den av. Brukeren har ikke bestemt seg ennå, og det gjøres i tiltak 2.
- **Commit**: `d33e523` (retrospektiv og sprintstatus), `b89003f` (regel i CLAUDE.md), `e2ac951` (denne oppføringen), `3506901` og `ea544c0` (oppfølging), pluss commiten som inneholder denne oppdateringen.

## 2026-11-27 — Tiltak 1, 2 og 5 fra retrospektiven av epic 1

- **Hvorfor**: Retrospektiven av epic 1 fant at epics.md brukte utdaterte kommandoer (V5), at `/docs` var åpen uten innlogging og ikke ble sjekket av rutetesten (R4), at avveiningen om kopiert cookie manglet i AD-8 (V6), og at feilsøkingen i README var for snever (R5). Tiltakene skulle gjøres før story 2.1.
- **Prompt(er)**: «Gjør tiltak 1, 2 og 5». Før det spurte brukeren «Hva anbefaler du?» om `/docs`. Claude anbefalte å skru den av, og brukeren sa ikke imot.
- **Verktøy/modell**: Claude Code (Opus 5.5), gjort direkte uten `bmad-build`. Begrunnelse: endringene er små, avgrenset av retrospektiven, og har test.
- **Endringer**:
  - Tiltak 1 (`61e80fb`): epics.md og tabellene i arkitekturen bruker `uv run python -m …`. AD-11 i epics.md forklarer hvorfor.
  - Tiltak 2 (`6cd68d9`):
    - `create_app()` skrur av `/docs`, `/redoc` og `/openapi.json`.
    - Rutetesten har tre nye tester: ingen ruter utenfor `/api/`, dokumentasjonssidene gir 404, og sjekken fanger en ny rute utenfor `/api/`.
    - AD-8 forklarer valget og avveiningen om den tilstandsløse cookien.
  - Tiltak 5 (`fd86f0f`): README forklarer de tre årsakene til «Fikk ikke kontakt med serveren»: backend er ikke startet, backend har stoppet med en feil, eller en annen backend svarer på port 8000.
- **Verifisering**:
  - `uv run python -m pytest` ga 110 tester som består, og ruff ga 0 funn.
  - De tre nye rutetestene feilet når `docs_url`, `redoc_url` og `openapi_url` ble fjernet midlertidig, og besto igjen etter at de ble satt tilbake.
  - Feilmeldingen «Fant ikke fasitfila» i README er sjekket mot `rbe/db/seed.py:37`.
- **Commit**: `61e80fb`, `6cd68d9`, `fd86f0f`, pluss commiten som inneholder denne oppføringen.

## 2026-11-27 — Fast commitmønster per story og læringspunkter i refleksjonsnotatene

- **Hvorfor**: Retrospektiven av epic 1 viste at PR-ene hadde 8–14 commits mot regelen om 2–5 (funn V7). Brukeren spurte hvordan det kan unngås, og ba om at læringspunktene fra retrospektiven føres inn i refleksjonsnotatene.
- **Prompt(er)**:
  - «Du kan skrive dette under refleksjonsnotat om læringspunkter, og skriv det ut med bedre forklaring: …», med brukerens fem stikkord.
  - «Hvordan kan vi unngå at det blir for mange commits igjen?»
  - «Ja, legg det inn i CLAUDE.md. Legg det også til i refleksjonsnotatet som læringspunkt»
- **Verktøy/modell**: Claude Code (Opus 5.5).
- **Endringer**:
  - `docs/refleksjonsnotater.md` har fått seksjonen «Læringspunkter fra retrospektiven av epic 1». Stikkordene er brukerens, og forklaringene er skrevet av Claude og merket som det (`71520af`, `585fee5`).
  - CLAUDE.md: et fast mønster med 4–5 commits per story-PR. Sesjonsloggen committes én gang per story, status `done` tas med i neste spec-commit, og squash merge brukes ikke. epics.md er avstemt (`e9ac439`).
- **Verifisering**: Claude telte commitene i PR #4 for å finne årsaken. Av 11 commits var 3 loggcommits, 1–2 AI-logg, 2 overført fra forrige story og bare rundt 3 kode.
- **Brukerens styring**:
  - Brukeren valgte selv hvilke læringspunkter som skulle med.
  - Brukeren skrev at det å flette uten gjennomgang «førte til at feil ikke ble oppdaget». Claude endret det til «feil gikk videre uten at jeg så dem», fordi det ikke er sikkert at en menneskelig gjennomgang ville funnet `get_session`-feilen. Brukeren ble gjort oppmerksom på endringen.
- **Commit**: `71520af`, `e9ac439`, `585fee5`, pluss dokumentasjonscommiten som inneholder denne oppføringen.

## 2026-11-27 — Story 2.1: lavnivåkoder og resultatform

- **Hvorfor**: Første story i epic 2. Kjernen trengte lavnivåkoder og én resultatform lik fasiten før netting, R11 og meldinger kan bygges i 2.2–2.4 (FR-10, AD-2, AD-3).
- **Prompt(er)**:
  - «Fortsett med story 2.1. Les først CLAUDE.md …, åpne tiltak fra retrospektiven av epic 1 i sprint-status.yaml, og issues.md … Ta inn tiltak som gjelder story 2.1 i specen.»
  - Svarene på sjekkpunktene: «Flytt til 3.1», «Er det trygt å forkorte specen?», «Ja, bruk dem» (subagenter), «Gjennomgå specen», «Så vi bør i utgangspunktet ikke forkorte specen?», «Hva kan du jobbe med imens?» og «Godkjenn og fortsett».
- **Verktøy/modell**: Claude Code (Opus 5.5) med `bmad-build`. Én subagent gikk gjennom specen, én implementerte, og tre gikk gjennom koden (blind-hunter, edge-case-hunter, verification-gap).
- **Endringer**:
  - `backend/src/rbe/mrp/`: resultattypene i `types.py`, `llc.py` med `low_level_codes` (lengste vei uten rekursjon, sjekk av inndata og sykler), og `run.py` med `run_mrp`, `result_to_dict` og sorteringen etter AD-3 på ett sted. Ukesarrayene er nuller til 2.2.
  - `backend/tests/conftest.py`: én kilde til fasitstien (`FIXTURE_DIR`, AD-4) og `pytest_generate_tests`, som lager fasittilfeller fra `expected.json` med en tabell fra felt til FR. 2.2–2.4 utvider bare tabellen.
  - `backend/tests/mrp/test_fixture_scenarios.py` (55 LLC-tilfeller for A–E, id-er som `A-FR-10-PLT-900-low_level_code`) og `test_llc.py` (resten av I/O-matrisen).
  - `_bmad-output/implementation-artifacts/epic-2-context.md` (ny) og specen for 2.1.
- **Verifisering**:
  - `uv run python -m pytest` ga 195 tester som består, og ruff ga 0 funn.
  - Vakten (SM-C2) er prøvd. Med LLC midlertidig regnet som korteste vei feilet de fem PLT-900-tilfellene og testen av rekkefølgen.
  - Spec-gjennomgangen fant 12 svakheter før koden ble skrevet. Det alvorligste var at `result_to_dict` kunne gitt tupler, og `(0, 0) == [0, 0]` er falskt i Python, så alle sammenligningene mot fasiten i 2.2 ville feilet.
  - Kodegjennomgangen gav 12 rader i triageloggen: 6 rettet og 6 avvist med begrunnelse. Viktigst var at sorteringen av meldinger ikke var testet. Testsettet besto med feil sorteringsnøkkel, og fasittestene i 2.4 sammenligner som mengde.
- **Brukerens styring**:
  - Brukeren valgte å flytte tiltak 4 fra retrospektiven (tester for egen `RBE_DEMO_USERNAME` og `RBE_FIXTURE_PATH`) fra 2.1 til 3.1, etter Claudes anbefaling. Det er ført i `deferred-work.md`.
  - Brukeren valgte ikke mellom «behold» og «kort ned» da specen var for lang, men spurte om det var trygt å korte den ned. Claude svarte at feltlistene er kontrakten for de neste storyene. Specen ble ikke kortet ned for å nå en lengde.
  - Brukeren ba om at specen ble gjennomgått før godkjenning, i stedet for å godkjenne direkte. Det fant feilen med tupler før koden ble skrevet.
- **Commit**: `69c8ea0` (spec), `0710d01` (kode med tester), `37f552c` (retting etter gjennomgangen), pluss dokumentasjonscommiten som inneholder denne oppføringen.

## 2026-11-27 — Story 2.2: bruttobehov, netting, partiregel og ledetidsoffset

- **Hvorfor**: Story 2.2 i epic 2. Kjernen ga bare lavnivåkoder, og ukesarrayene var nuller. Planleggeren trenger bruttobehov, nettobehov og bestillingsforslag per vare og uke (FR-10, FR-11, FR-9).
- **Prompt(er)**:
  - «Fortsett med story 2.2. Les CLAUDE.md, åpne tiltak i sprint-status.yaml, issues.md … og punktene fra spec 2.1 i deferred-work.md (særlig uke → indeks og FIELD_FR). Spec-commiten skal også sette 2.1 til done og lukke punktet om min observasjon i issues.md.»
  - Svarene på sjekkpunktene: «Krev first_week = 1», «MrpInputError nå» (uker utenfor horisonten), «Behold hele specen», «Gå gjennom specen» og «Godkjenn og fortsett».
- **Verktøy/modell**: Claude Code (Opus 5.5) med `bmad-build`. Én subagent gikk gjennom specen, én implementerte, og tre gikk gjennom koden (blind-hunter, edge-case-hunter, verification-gap).
- **Endringer**:
  - `backend/src/rbe/mrp/plan.py` (ny): planlegger varene i LLC-rekkefølge etter R2, R3 og R5–R9. Barna leser forelderens `planned_orders`, så R11 kan legges til i 2.3.
  - `backend/src/rbe/mrp/llc.py`: kjernen avviser første uke ≠ 1, MPS-linjer og åpne ordre utenfor horisonten, negativ ledetid, ukjent partiregel og FOQ uten kvantum. `run.py` bruker `plan.py`.
  - `backend/tests/conftest.py`: valgfri `fasit_marks` per fasittilfelle. `tests/mrp/conftest.py` (ny) har `result_for`.
  - `backend/tests/mrp/test_fixture_scenarios.py`: alle åtte feltene for A–E. D er skipped (77 tilfeller) til R11 finnes. Nye `test_plan.py` og `test_properties.py`.
  - AD-2 i `ARCHITECTURE-SPINE.md` og `epic-2-context.md`: første uke er 1, og kjernen avviser de nye inndataene. `deferred-work.md`: punktet om uke → indeks er lukket, og punktet for 4.1 er oppdatert.
- **Verifisering**:
  - `uv run python -m pytest` gir 532 tester som består og 77 skipped. Ruff gir 0 funn.
  - Vakten (SM-C2) er prøvd. Med forfalte frigivelser lagt i uke 1 feilet 9 fasittilfeller (MOT-210, VIN-920 og GIR-220 i C) og tre enhetstester.
  - Undersøkelsen fant at fasiten ikke skiller to av reglene: ingen vare har åpen ordre og bruttobehov i samme uke (R2), og PLT-900 trenger aldri mer enn ett parti (R6). Det er sjekket med skript mot `expected.json`. Begge har nå egne enhetstester. Vakten Claude først foreslo, ville ikke fått noen test til å feile, og ble byttet før godkjenning.
  - Spec-gjennomgangen fant 15 svakheter. Den alvorligste var at Claude hadde regnet sikkerhetslageret feil i matrisen (NB 5 i uke 2 i stedet for 2 i uke 1 og 3 i uke 2).
  - Kodegjennomgangen gav 13 rader: 5 rettet og 8 avvist med begrunnelse. Viktigst var at åpne ordre i uke 0 og to åpne ordre i samme uke ikke var testet.
- **Brukerens styring**:
  - Brukeren pekte selv på uke → indeks og `FIELD_FR` som det viktigste fra 2.1, og valgte at kjernen krever første uke 1 og avviser uker utenfor horisonten.
  - Brukeren ba om gjennomgang av specen før godkjenning, som i 2.1. Den fant regnefeilen i sikkerhetslageret før koden ble skrevet.
  - Claude beholdt `skip` for D, mot subagentens forslag om `xfail`, og la begrunnelsen fram ved sjekkpunktet. Brukeren godkjente specen uten å endre det.
- **Commit**: `6989d94` (spec), `414d436` (kode med tester), `ab22f52` (retting etter gjennomgangen), pluss dokumentasjonscommiten som inneholder denne oppføringen.

## 2026-11-27 — Story 2.3: komponentbehov fra forfalte produksjonsordrer (R11)

- **Hvorfor**: Story 2.3 i epic 2. Uten R11 mistet barna behovet fra forslag med frigivelsesuke < 1, og i scenario D hadde PLT-900 30 i bruttobehov mot 66 i fasiten (FR-12). Thobias sin gjennomgang av PR #12 viste at ingenting ville feilet om skip-regelen for D ble stående, og at bare egenskapen «ingen behov går tapt» fanger tapet mellom forelder og barn.
- **Prompt(er)**:
  - «Fortsett med story 2.3. Les CLAUDE.md, åpne tiltak i sprint-status.yaml, issues.md … og punktene for 2.3 i deferred-work.md (særlig «ingen behov går tapt», skip-regelen for D og FR-12 i id-ene). Spec-commiten skal også sette 2.2 til done og lukke punktet om fletting av PR #12 i issues.md.»
  - Svarene på sjekkpunktene: «Gå gjennom specen» og «Godkjenn og fortsett».
- **Verktøy/modell**: Claude Code (Opus 5.5) med `bmad-build`. Én subagent gikk gjennom specen og regnet R1–R11 uavhengig, én implementerte, og tre gikk gjennom koden (blind-hunter, edge-case-hunter, verification-gap).
- **Endringer**:
  - `backend/src/rbe/mrp/plan.py`: R11 er én linje, `week = max(order.release_week, 1)`. Regelen gjelder alle foreldre uansett `source`, en bevisst utvidelse av «produksjonsvare». `run.py` har oppdatert docstring.
  - `backend/tests/conftest.py`: kroken `fasit_marks` er byttet ut med en valgfri `fasit_fr`, som setter FR-nummeret både i id-en og i `case.fr`.
  - `backend/tests/mrp/test_fixture_scenarios.py`: skip for D er fjernet. De 77 D-tilfellene for feltene fra 2.2 har `D-FR-12-` i id-en, og `low_level_code` beholder FR-10.
  - `backend/tests/mrp/test_properties.py`: ny `test_fr12_no_requirements_are_lost` for A–E. `test_plan.py`: R11 i tre ledd, forelder med forfalt og gyldig forslag (to tilfeller) og kjøpt forelder.
  - AC 3 for story 2.3 i `epics.md` sjekker per vare med MPS, ikke per BOM-linje. FR-12 i PRD-en nevner utvidelsen til kjøpte foreldre. `deferred-work.md`: punktet for 2.3 er lukket.
- **Verifisering**:
  - `uv run python -m pytest` gir 619 tester som består og 0 skipped. Ruff gir 0 funn.
  - Vakten (SM-C2) er prøvd. Med R11 fjernet feilet 40 tester: 36 av 77 D-tilfeller, egenskapen for D og kjedetestene. A, B, C og E besto.
  - Egenskapen slo ut for andre varer enn specen ventet: GIR-220, MOT-210, STY-310, SEK-110 og PLT-900, ikke PRF-910. Den sammenligner med forelderens forslag i samme kjøring, så den finner tapet i leddet rett under den forfalte forelderen. Følgefeilene lenger ned fanges av fasiten for D. Tallene i specen ble rettet.
  - Spec-gjennomgangen regnet R1–R11 i et eget skript og fikk 0 avvik mot `expected.json` for A–E. Den fant 11 svakheter. Den viktigste var at AC 3 i epics («for hver BOM-linje», uten MPS) ikke kan sjekkes slik: PLT-900 har tre foreldre, og RBE-000 har MPS uten foreldre.
  - Kodegjennomgangen gav 8 rader (edge-case-hunter fant ingenting): 4 rettet og 4 avvist med begrunnelse. Viktigst var at ingen test hadde en kjøpt forelder med barn, så utvidelsen av R11 kunne forsvunnet stille.
- **Brukerens styring**:
  - Omfanget kom fra Thobias sin egen gjennomgang av PR #12: egenskapen «ingen behov går tapt», fjerning av skip-regelen og FR-12 i id-ene.
  - Brukeren ba igjen om gjennomgang av specen før godkjenning. Den fant avviket i AC 3 før koden ble skrevet.
  - Claude valgte selv at R11 gjelder alle foreldre og at LLC i D beholder FR-10, og la begge valgene fram ved sjekkpunktet. Brukeren godkjente uten å endre dem.
- **Commit**: `1c7690d` (spec), `51c43c7` (kode med tester), `84fb59e` (retting etter gjennomgangen), pluss dokumentasjonscommiten som inneholder denne oppføringen.

## 2026-11-27 — Gjennomgang av story 2.3 før fletting (bmad-walkthrough)

- **Hvorfor**: Tiltak 7 fra retrospektiven av epic 1: Thobias går selv gjennom PR-en og skriver én egen observasjon før fletting. Gjennomgangen viste at FR-12 i PRD-en og første AC for story 2.3 i `epics.md` fortsatt sa «produksjonsvare», mens kjernen bruker R11 på alle foreldre.
- **Prompt(er)**:
  - «/bmad-walkthrough Gå gjennom story 2.3 (R11, FR-12) … Hjelp meg å forstå og teste endringen selv, så jeg kan skrive én egen observasjon i PR-en før fletting», med fem punkter: R11 med scenario D, utvidelsen til kjøpte foreldre, egenskapen «ingen behov går tapt», `fasit_fr` og avvikene fra planleggingen.
  - «Rett epics.md:444 og første setning i FR-12».
- **Verktøy/modell**: Claude Code (Opus 5.5) med `bmad-walkthrough`, uten subagenter. Mutantene ble kjørt som et pytest-plugin i scratchpad, uten å endre filene i repoet.
- **Endringer**:
  - `prd.md`, FR-12: første setning gjelder nå «en vare med BOM-linjer under seg», og at det også gjelder kjøpte varer, står rett etter. Den doble formuleringen fra rettingen er fjernet.
  - `epics.md`, story 2.3: første AC sier «en vare med BOM-linjer under seg (produksjonsvare eller kjøpt vare)».
- **Verifisering**:
  - `uv run python -m pytest` gir 619 tester som består og 0 skipped. `--collect-only` gir 77 id-er med `D-FR-12-` og 12 med `D-FR-10-` (11 for LLC og 1 for varesettet).
  - Uten R11 feiler 41 tester, ikke 40 som i Implementation Notes: testen for kjøpt forelder kom til i rettingen. Med en vakt som bare tar med `make`-foreldre, feiler bare `test_fr12_r11_purchased_parent_past_due`, så utvidelsen holdes oppe av én test.
  - Egenskapen «ingen behov går tapt» stopper ved første avvik (GIR-220). De fem varene i Implementation Notes ble bekreftet med et eget skript. PRF-910 og VIN-920 slår ikke ut fordi foreldrene deres ikke har forfalte forslag igjen uten R11.
- **Brukerens styring**:
  - Thobias valgte de fem punktene selv, og valgte å rette bare de to stedene i planleggingen. Andre svakheter (egenskapen viser bare første avvik, id-ene er ikke testet, alternativet å avvise kjøpte foreldre med BOM) ble lagt fram uten å bli rettet.
- **Commit**: `9e47420` (retting i PRD og epics), pluss dokumentasjonscommiten som inneholder denne oppføringen.

## 2026-11-27 — Story 2.4: exception-meldinger E1 og E2

- **Hvorfor**: Story 2.4 i epic 2. Kjernen ga alltid en tom `exceptions`-liste, så planleggeren fikk ikke vite om ledetid lengre enn horisonten (FR-13) eller forslag som skulle vært frigitt før uke 1 (FR-14). To punkter fra Thobias sin gjennomgang av PR #11 (egen fasittest for meldingene, eksplisitt sorteringsnøkkel per type) og to vedtak fra gjennomgangen av PR #13 (alle avvik i én assert, krok mot skipped tester) hørte til storyen.
- **Prompt(er)**:
  - «Fortsett med story 2.4. Les CLAUDE.md, åpne tiltak i sprint-status.yaml, issues.md … og punktene for 2.4 i deferred-work.md … Vurder også det åpne punktet fra gjennomgangen av 2.3 … Følg observasjonen min fra PR #13: all gjennomgang, også min egen, skal være ferdig før dokumentasjonscommiten. Spec-commiten skal også sette 2.3 til done og lukke punktene om gjennomgangen og flettingen av PR #13 i issues.md.»
  - Svar på sjekkpunktene: regelen i CLAUDE.md i spec-commiten, Claude pusher og oppretter PR-en, specen beholdes hel over 1600 tokens, «Gjennomgå specen», «Ja, rett alle ti, ta med egenskapstesten», «Godkjenn og fortsett», og rettingen av CLAUDE.md i dokumentasjonscommiten.
  - «Hvor kommer anbefalningen om maks 1600 tokens på spec fra?» Svar: fra `bmad-build` sin SCOPE STANDARD og spec-malen, uten oppgitt kilde, og grensen er ikke et krav.
  - «Start gjennomgangen av PR #14 med bmad-walkthrough» og «Oppsummer hva vi har gjort som er relevant for observasjonene min».
- **Verktøy/modell**: Claude Code (Opus 5.5) med `bmad-build` og `bmad-walkthrough`. Subagenter: én laget epic-2-konteksten på nytt, én gikk gjennom specen og regnet E1 og E2 uavhengig, én implementerte, og tre gikk gjennom koden (blind-hunter, edge-case-hunter, verification-gap).
- **Endringer**:
  - `backend/src/rbe/mrp/exceptions.py` (ny): `find_exceptions` gir E1 per vare med bruttobehov og ledetid > horisont, og E2 per forslag med frigivelsesuke < 1, for alle varer uansett `source`.
  - `backend/src/rbe/mrp/run.py`: `run_mrp` sender meldingene til `_ordered`, og `_exception_key` har en gren per type med `match`. En ukjent type gir `TypeError`.
  - `backend/tests/mrp/test_fixture_scenarios.py`: `test_fasit_exceptions` sammenligner som multimengde per scenario og type (10 tilfeller) og feiler på ukjent type. `test_llc.py`: scenario A, tom MPS, ukjent type og tuple-sjekkene. `test_plan.py`: fire grensetilfeller fasiten ikke har. `test_properties.py`: alle avvik i én assert, og egenskapen `{s}-FR-14-forfalt-forsinkelse`.
  - `backend/tests/conftest.py`: kroker som gjør skip, `skipif`, xfail, XPASS og skip på modulnivå til feil. `tests/test_no_skip.py` prøver alle fem med `pytester` (`-p pytester` i `pyproject.toml`).
  - `CLAUDE.md`: regelen om at all gjennomgang er ferdig før dokumentasjonscommiten, og i dokumentasjonscommiten presisert mot «Push bare når brukeren ber om det» og uten force-push. `epic-2-context.md` er laget på nytt. `deferred-work.md`: avvisning av kjøpte foreldre med BOM ført for 4.1, og de to punktene for 2.4 lukket.
- **Verifisering**:
  - `uv run python -m pytest` gir 646 tester som består og 0 skipped. Ruff gir 0 funn.
  - Vaktprøvene (SM-C2) slår alle ut: `>=` i E1 (1 feil), `<= 1` i E2 (1), feil `earliest_receipt_week` (11), E1 på forslag i stedet for bruttobehov (1) og `pytest.skip` i fasittesten (10 feil, 0 skipped).
  - Spec-gjennomgangen lagde E1 og E2 etter reglene i specen og fikk 0 avvik mot `expected.json` for A–E. Den fant 10 svakheter. To var alvorlige: vaktprøven `<= 1` kunne aldri slå ut fordi ingen forslag hadde frigivelse i uke 1, og raden for ledetid lik horisonten ventet ingen meldinger, mens den gir én E2.
  - Kodegjennomgangen gav 12 rader: 3 rettet (blant annet manglende test for XPASS), 1 avgjort av Thobias (CLAUDE.md strider mot push-regelen og åpnet for force-push), 8 avvist med begrunnelse.
  - Thobias gikk gjennom PR #14 med `bmad-walkthrough` før dokumentasjonscommiten, uten nye rettinger. Observasjonen står i PR-en.
- **Brukerens styring**:
  - Rekkefølgen med gjennomgang før dokumentasjon kom fra Thobias sin observasjon i PR #13, og han valgte at den skulle stå i CLAUDE.md fra spec-commiten.
  - Thobias ba om gjennomgang av specen og godkjente alle ti rettinger, også den valgfrie egenskapstesten.
  - Thobias spurte hvor grensen på 1600 tokens kom fra, i stedet for å ta den for gitt.
  - Da kodegjennomgangen fant at regelen hans strider mot push-regelen, valgte han å rette den i dokumentasjonscommiten, uten ekstra commit.
  - Thobias ba om en oppsummering før han skrev observasjonen. Claude ga fakta som stikkord og ikke ferdige setninger, fordi teksten i PR #13 ble nesten ordrett lik oppsummeringen.
- **Commit**: `f81b899` (spec), `4e90236` og `8549abb` (kode med tester), `443f7ea` (retting etter gjennomgangen), pluss dokumentasjonscommiten som inneholder denne oppføringen.
