---
title: Red Ball Express v1 — PRD
status: final
created: 2026-11-24
updated: 2026-11-24
---

# PRD: Red Ball Express v1

## 0. Om dokumentet

Denne PRD-en beskriver hva v1 av Red Ball Express skal gjøre: flernivå BOM og MRP for ett testfartøy. Den bygger på [product brief](../../briefs/brief-Red%20Ball%20Express-2026-09-16/brief.md) med [addendum](../../briefs/brief-Red%20Ball%20Express-2026-09-16/addendum.md), [faglærers tilbakemelding](../../briefs/brief-Red%20Ball%20Express-2026-09-16/tilbakemelding-product-brief.md) og den håndregnede fasiten i [testdata/testfartoy-v1/](../../../../testdata/testfartoy-v1/README.md). Fasiten gjentas ikke her. PRD-en viser til den.

Dokumentet er skrevet for den som lager arkitektur, epics og stories, og for faglærer og sensor som skal kunne spore krav til kode. Begrepene i §3 brukes konsekvent. Krav har faste nummer (FR-n, NFR-n, SM-n), slik at stories og tester kan vise til dem. Antakelser er merket `[ASSUMPTION]` og samlet i §10. Teknologivalg står i [arkitekturen](../../architecture/architecture-Red%20Ball%20Express-2026-11-24/ARCHITECTURE-SPINE.md). Føringer fra briefen er samlet i [addendum.md](addendum.md).

## 1. Visjon

Red Ball Express v1 viser at BOM-eksplosjon og MRP kan gjøres riktig og etterprøvbart for et verftscase med dype produktstrukturer og lange ledetider. En produksjonsplanlegger legger inn hovedplanen for et testfartøy. Systemet bryter den ned gjennom produktstrukturen til nettobehov, bestillingsforslag og exception-meldinger per uke og vare.

Det som skiller v1 fra en vanlig skoleoppgave, er at resultatet ikke bare skal se plausibelt ut. Det skal stemme tall for tall med en håndregnet fasit, og det skal være synlig hvordan en endring i planen forplanter seg gjennom strukturen. Systemet gjør konsekvensene av en beslutning tydelige, men tar ikke beslutningen for planleggeren.

v1 er bevisst smal: ett testfartøy, fast BOM og ingen KI i selve appen. Alt annet fra den opprinnelige visjonen (prognoser, S&OP, scheduling, værvinduer, Monte Carlo) står i briefens visjonsseksjon.

## 2. Målbruker

### 2.1 Jobber som skal gjøres

- Vite **når** en vare må bestilles eller produksjonen startes for at et fartøy skal bli ferdig i planlagt uke.
- Se **hvilke** innkjøp som allerede er for sent ute, og hvor mye forsinkelse de gir.
- Forstå **konsekvensen** av en endring (framskyndet leveranse, feil lagerbeholdning) før den blir et problem i byggingen.
- (Sensor og faglærer) Kunne **etterprøve** at beregningene er riktige, og prøve appen fritt uten å ødelegge noe.

### 2.2 Ikke-brukere i v1

- Innkjøpere, ledere og andre roller. Det finnes bare én rolle.
- Verft med flere fartøystyper eller varianter. v1 har én fast BOM.

### 2.3 Brukerreiser

**UJ-1. Ingrid framskynder byggenr. 2 og ser hva det koster.**
Ingrid Solheim er produksjonsplanlegger ved verftet. Salg melder at kunden vil ha byggenr. 2 i uke 14 i stedet for uke 16. Ingrid logger inn og åpner MPS-skjermbildet. Ingrid flytter leveransen for byggenr. 2 fra uke 16 til uke 14 og trykker «Kjør MRP». Bestillingsforslagene og meldingene som endret seg, er markert. Giret må nå bestilles i uke 2 i stedet for uke 4. Hovedmotoren er 11 uker forsinket i stedet for 9. I MRP-tabellen for stålplater ser Ingrid at behovet fra seksjonene og fra styrehuset nå havner i samme uke. Nå er alt klart for å ringe motorleverandøren: verftet trenger motoren 2 uker tidligere enn før. *(Tilsvarer scenario B i fasiten.)*

**UJ-2. Sensor prøver appen etter README.**
Sensor følger README, starter appen lokalt og logger inn med demobrukeren. Testfartøyet er allerede lagt inn. Sensor åpner BOM-treet og ser de fire nivåene. Så setter sensor lagerbeholdningen for giret til 0 og kjører MRP. En ny melding om forfalt bestilling for giret dukker opp og er markert som ny. Sensor prøver å sette en negativ lagerbeholdning og får en forståelig feilmelding. Til slutt flytter sensor byggenr. 1 til uke 4. MRP-en melder at flere produksjonsordrer er forfalt, uten å krasje. Sensor trykker «Tilbakestill til testdata» og er tilbake i utgangspunktet. *(Tilsvarer scenario C og D i fasiten.)*

## 3. Ordliste

Begrepene brukes slik i hele PRD-en og i senere dokumenter. Engelske navn i parentes er feltnavnene i fasitens JSON.

- **Vare** (`item`) — alt som inngår i strukturen, fra komplett fartøy til enkeltdel. Er enten en *produksjonsvare* (`make`) eller en *innkjøpsvare* (`purchase`).
- **Testfartøy** — fartøystypen RBE-000 med fast BOM, slik fasiten definerer den.
- **Byggenummer** — ett konkret fartøy av testfartøystypen. MPS-en har to.
- **BOM** — produktstrukturen: et sett **BOM-linjer** (forelder, barn, **mengde per**).
- **Nivå** — en vares plass i BOM-treet (0 = fartøyet). **Lavnivåkode** (LLC) er det dypeste nivået varen forekommer på.
- **MPS** — hovedproduksjonsplanen: en liste **MPS-linjer** (vare, uke, antall, byggenummer).
- **Horisont** — planleggingsperioden, uke 1–16. Uke 1 er første planuke, ikke kalenderuke.
- **Lagerbeholdning** (`on_hand`) — beholdning ved start av uke 1.
- **Åpen ordre** (`scheduled_receipt`) — en ordre som allerede er bestilt, med antall og mottaksuke.
- **Ledetid** — antall hele uker fra bestilling eller produksjonsstart til varen er tilgjengelig.
- **Partiregel** — L4L (bestill nøyaktig nettobehovet) eller FOQ (bestill i multipler av et fast kvantum).
- **Bruttobehov, nettobehov, beregnet lager** — radene i MRP-tabellen, definert i fasitens regler R3, R5 og R7.
- **Bestillingsforslag** (`planned_order`) — en planlagt ordre med antall, **mottaksuke** og **frigivelsesuke**. For innkjøpsvarer er det et forslag til innkjøpsordre, for produksjonsvarer et forslag til produksjonsordre.
- **MRP-kjøring** — én beregning av MRP-tabeller, bestillingsforslag og exception-meldinger fra gjeldende data.
- **Exception-melding** (`exception`) — et varsel fra en MRP-kjøring. I v1 finnes to typer: **ledetid lengre enn horisont** (E1) og **forfalt bestilling** (E2).
- **Fasit** — `testdata/testfartoy-v1/`: inndata, forventet resultat og regnereglene R1–R11.
- **Scenario** — en navngitt variant av inndata i fasiten (A basis, B MPS-endring, C lagerendring, D forfalte produksjonsordrer, E BOM-endring).
- **Testdata** — fasitens inndata (scenario A) lastet inn i appens database.
- **Demobruker** — den ene brukerkontoen i v1, med innlogging oppgitt i README.

## 4. Funksjoner

### 4.1 Innlogging

**Beskrivelse:** Appen krever innlogging med brukernavn og passord. Det finnes én demobruker, opprettet sammen med testdataene. Innloggingen er der fordi dataene regnes som forretningskritiske i domenet. Den er ikke laget for mange brukere eller roller.

#### FR-1: Logge inn og ut
Demobrukeren kan logge inn med brukernavn og passord og logge ut. Realiserer UJ-1, UJ-2.

**Konsekvenser (testbare):**
- Uten innlogging gir alle skjermbilder og API-kall med data avvisning eller omdirigering til innlogging.
- Feil brukernavn eller passord gir en feilmelding som ikke røper hvilket av dem som var feil.
- Passord lagres ikke i klartekst.

### 4.2 Testdata og tilbakestilling

**Beskrivelse:** Appen starter med testfartøyet ferdig lagt inn, slik at sensor kan bruke den uten å legge inn noe selv. Planleggeren kan når som helst tilbakestille til testdataene.

#### FR-2: Testdata ved oppstart
Når databasen er tom, lastes testdataene fra `testdata/testfartoy-v1/input.json` (scenario A) og demobrukeren opprettes. Realiserer UJ-2.

**Konsekvenser (testbare):**
- Etter første oppstart inneholder databasen nøyaktig varene, BOM-linjene, MPS-linjene, lagerbeholdningene og de åpne ordrene i `input.json`.
- Testdataene leses fra fasitfila, ikke fra en egen kopi, slik at fasit og app ikke kan sprike.

#### FR-3: Tilbakestille til testdata
Planleggeren kan trykke «Tilbakestill til testdata». Det erstatter MPS, lagerbeholdning, åpne ordre, mengde per, ledetider og partiregler med verdiene i scenario A og sletter tidligere MRP-kjøringer. Realiserer UJ-2.

**Konsekvenser (testbare):**
- Appen ber om bekreftelse før tilbakestilling.
- En MRP-kjøring rett etter tilbakestilling gir resultatet for scenario A i `expected.json`.

### 4.3 BOM-visning

**Beskrivelse:** Planleggeren ser produktstrukturen for testfartøyet som et tre. Selve strukturen (hvilke varer og BOM-linjer som finnes) er fast i v1, men mengde per, ledetid og partiregel kan justeres (FR-18).

#### FR-4: Vise BOM-treet
Planleggeren kan se BOM-treet for testfartøyet med alle nivåer. Realiserer UJ-2.

**Konsekvenser (testbare):**
- Hver node viser varenummer, navn, mengde per forelder, type (produksjon/innkjøp) og ledetid.
- Alle 12 BOM-linjene i testdataene vises, også når samme vare har flere foreldre (PLT-900 vises under SEK-110, STY-310 og DEK-300).
- Planleggeren kan se lavnivåkoden for hver vare.

**Utenfor:** å legge til eller fjerne varer og BOM-linjer (trinn 2, se §7.2).

### 4.4 MPS, lagerbeholdning, åpne ordre og BOM-justering

**Beskrivelse:** Planleggeren endrer inndataene som MRP-en beregner fra. Endringer slår ikke inn i resultatene før neste MRP-kjøring.

#### FR-5: Redigere MPS
Planleggeren kan legge til, endre (uke, antall) og slette MPS-linjer for testfartøyet. Realiserer UJ-1.

#### FR-6: Redigere lagerbeholdning
Planleggeren kan endre lagerbeholdningen for hver vare. Realiserer UJ-2.

#### FR-7: Redigere åpne ordre
Planleggeren kan legge til, endre (uke, antall) og slette åpne ordre.

#### FR-18: Justere BOM-linjer og varedata
Planleggeren kan endre mengde per på eksisterende BOM-linjer, og ledetid og partiregel (L4L eller FOQ med kvantum) på eksisterende varer. Realiserer briefens «justere MPS eller BOM».

#### FR-8: Validere inndata
Systemet avviser ugyldige verdier med en forståelig feilmelding i skjemaet og lagrer ingenting av endringen. Realiserer UJ-2.

**Konsekvenser (testbare, gjelder FR-5 til FR-8 og FR-18):**
- Uke må være et heltall i horisonten (1–16). Antall i MPS-linjer og åpne ordre må være et heltall ≥ 1. Lagerbeholdning må være et heltall ≥ 0.
- En MPS-linje kan bare gjelde testfartøyet (nivå 0-varen). Byggenummer må være et heltall ≥ 1.
- Mengde per må være et heltall ≥ 1. Ledetid må være et heltall ≥ 0. FOQ-kvantum må være et heltall ≥ 1.
- Ugyldig verdi gir feilmelding ved feltet. Databasen er uendret.
- Gyldige endringer lagres og vises ved neste visning av skjermbildet.

### 4.5 MRP-beregning

**Beskrivelse:** En MRP-kjøring beregner MRP-tabeller og bestillingsforslag for alle varer fra gjeldende MPS, BOM, lagerbeholdning, åpne ordre, ledetider og partiregler. Reglene er fasitens R1–R11 ([fasit §1](../../../../testdata/testfartoy-v1/README.md#1-beregningskonvensjoner)). R11 tilsvarer FR-12. Beregningen er deterministisk: samme inndata gir alltid samme resultat. Sikkerhetslager er 0 i v1.

#### FR-9: Kjøre MRP
Planleggeren kan starte en MRP-kjøring med knappen «Kjør MRP». Resultatet lagres, slik at det kan sammenlignes med neste kjøring (FR-17). Realiserer UJ-1, UJ-2.

**Konsekvenser (testbare):**
- To kjøringer på samme inndata gir identisk resultat.
- En kjøring bruker inndataene slik de er lagret i det øyeblikket knappen trykkes.

#### FR-10: BOM-eksplosjon med lavnivåkoder
Systemet beregner bruttobehov per vare og uke: fra MPS for nivå 0, og fra foreldrenes frigivelser × mengde per for øvrige varer. Hver vare planlegges én gang, etter alle foreldrene sine (lavnivåkode).

**Konsekvenser (testbare):**
- `gross_requirements` og `low_level_code` for alle varer stemmer med `expected.json` for scenario A, B, C og E.

#### FR-11: Netting, partiregel og ledetidsoffset
Systemet beregner beregnet lager, nettobehov og bestillingsforslag per vare og uke, med varens partiregel. Frigivelsesuka er mottaksuka minus ledetiden.

**Konsekvenser (testbare):**
- `scheduled_receipts`, `projected_on_hand`, `net_requirements`, `planned_order_receipts`, `planned_order_releases` og `planned_orders` for alle varer stemmer med `expected.json` for scenario A, B, C og E. Sammenligningen gjøres på hele ukesarrayer.
- Bestillingsforslag med frigivelsesuke før uke 1 beholdes med beregnet (negativ eller null) frigivelsesuke.

#### FR-12: Komponentbehov fra forfalte produksjonsordrer
Når en produksjonsvare får et bestillingsforslag med frigivelsesuke før uke 1, legges barnas bruttobehov fra det forslaget i uke 1. Forslaget gir en melding om forfalt bestilling (FR-14). Regelen gjelder i alle ledd nedover. Realiserer UJ-2.

**Konsekvenser (testbare):**
- Alle felt stemmer med `expected.json` for scenario D (byggenr. 1 framskyndet til uke 4), regel R11 i fasiten.
- Ingen bruttobehov går tapt: summen av barnets bruttobehov er lik summen av foreldrenes bestillingsforslag × mengde per.

### 4.6 Exception-meldinger

**Beskrivelse:** En MRP-kjøring gir exception-meldinger som varsler planleggeren. Meldingene foreslår ikke endringer og flytter verken ordre eller MPS.

#### FR-13: Ledetid lengre enn horisont (E1)
Systemet gir én melding per vare som har bruttobehov i horisonten og ledetid lengre enn horisonten.

#### FR-14: Forfalt bestilling (E2)
Systemet gir én melding per bestillingsforslag med frigivelsesuke før uke 1. Meldingen oppgir antall, mottaksuke, beregnet frigivelsesuke, antall uker forfalt og tidligste mulige mottaksuke hvis det bestilles nå.

**Konsekvenser (testbare, FR-13 og FR-14):**
- Meldingene stemmer med `exceptions` i `expected.json` for scenario A–E, sammenlignet som usortert mengde på type, vare og tallfelt.
- Meldingsteksten er på norsk og nevner vare (nummer og navn) og uker. Teksten testes ikke ordrett.

### 4.7 Resultatvisning og forplantning

**Beskrivelse:** Planleggeren ser resultatet av siste MRP-kjøring i tre visninger, og ser hva som endret seg siden forrige kjøring. Dette er hvordan «synlig forplantning» fra briefen oppfylles.

#### FR-15: MRP-tabell per vare
Planleggeren kan velge en vare og se MRP-tabellen for horisonten: bruttobehov, åpne ordre, beregnet lager, nettobehov, planlagt mottak og planlagt frigivelse per uke, med lagerbeholdning og forfalte frigivelser i en egen kolonne før uke 1. Realiserer UJ-1.

#### FR-16: Liste over bestillingsforslag og exception-meldinger
Planleggeren kan se alle bestillingsforslag (vare, type, antall, frigivelsesuke, mottaksuke), sortert på frigivelsesuke, og alle exception-meldinger. Forfalte bestillingsforslag er tydelig merket. Realiserer UJ-1, UJ-2.

#### FR-17: Markere endringer siden forrige kjøring
Etter en MRP-kjøring markeres det som er endret siden forrige kjøring: nye og fjernede bestillingsforslag, nye, forverrede, forbedrede og løste exception-meldinger, og endrede celler i MRP-tabellen, også i kolonnen før uke 1 (lagerbeholdning og forfalte frigivelser). Et bestillingsforslag regnes som det samme når vare, antall, mottaksuke og frigivelsesuke er like. Ellers vises det som nytt, og det gamle som fjernet. Exception-meldinger med samme type og vare i begge kjøringene pares og vises som én melding. Har en vare flere meldinger av samme type, pares de i rekkefølge etter mottaksuke. For E2 avgjør antall uker forfalt om meldingen er forverret (flere uker) eller forbedret (færre uker). Meldinger uten par er nye eller løste. Detaljer og visning: [EXPERIENCE.md](../../ux-designs/ux-Red%20Ball%20Express-2026-11-24/EXPERIENCE.md). Realiserer UJ-1, UJ-2.

**Konsekvenser (testbare, FR-15 til FR-17), verifiseres med manuell testplan:**
- Etter tilbakestilling og kjøring (scenario A) viser visningene tallene i fasitens tabeller.
- Når byggenr. 2 flyttes til uke 14 og MRP kjøres (scenario B), er alle bestillingsforslag for byggenr. 2 markert som nye (og de gamle som fjernet), mens forslagene for byggenr. 1 ikke er markert. Meldingen for hovedmotoren er markert som forverret fra 9 til 11 uker forfalt.
- Når lagerbeholdningen for GIR-220 settes til 0 og MRP kjøres fra scenario A (scenario C), er meldingen om forfalt bestilling for GIR-220 markert som ny. Ingen andre varer har endringer.
- Når mengde per for SKR-100 → SEK-110 settes til 5 og MRP kjøres fra scenario A (scenario E), er de endrede bestillingsforslagene for SEK-110, PLT-900 og PRF-910 markert som nye og de gamle som fjernet (blant annet en tredje plateordre med mottak i uke 12). Plateordren med mottak i uke 9 er uendret og ikke markert. Ingen andre varer har endringer.
- Første kjøring etter tilbakestilling har ingen forrige kjøring å sammenligne med, og viser ingen markeringer.

## 5. Tverrgående krav (NFR)

- **NFR-1 Kjørbar lokalt:** appen kan installeres og startes etter README på en ren maskin, uten kontoer, nøkler eller nettilgang til eksterne tjenester (utover å laste ned avhengigheter). Forutsetninger og versjoner står i README.
- **NFR-2 Ingen hemmeligheter i repoet:** konfigurasjon leses fra miljøvariabler med en `.env.example` uten ekte verdier. Demobrukerens passord er et kjent demopassord, dokumentert i README.
- **NFR-3 Testbar beregningskjerne:** MRP-beregningen kan kjøres og testes uten database og brukergrensesnitt, direkte mot `input.json` og `expected.json`. Testene kjøres med én kommando som står i README. I tillegg finnes en automatisk skalatest med en generert BOM på rundt 500 varer og 10 nivåer, der en felles komponent forekommer på flere nivåer. Testen sjekker at beregningen fullfører, at lavnivåkodene er riktige og at massebalansen (lager før uke 1 + åpne ordre + planlagte mottak − bruttobehov = beregnet lager i uke 16) går opp for alle varer. Testen har ikke noe tidskrav. Den skal vise at logikken er generell og ikke tilpasset testfartøyet (jf. SM-C2).
- **NFR-4 Respons:** en MRP-kjøring for testfartøyet viser resultatet uten merkbar ventetid.
- **NFR-5 Stabilitet:** ugyldig input, gjentatte kjøringer og tilbakestilling midt i bruk gir ikke krasj eller inkonsistente data.
- **NFR-6 Tilgjengelighet:** skjermbildene har lesbar kontrast, kan brukes med tastatur og har etiketter på alle skjemafelt. Brukergrensesnittet er på norsk. Skjermbildene er beregnet på PC-skjerm. Mobil er ikke et mål i v1.
- **NFR-7 Sporbarhet:** stories og automatiske tester viser til FR-nummerene i denne PRD-en, og beregningstestene viser til scenario i fasiten.

## 6. Ikke-mål

- **Ingen KI-funksjoner i appen.** KI brukes i utviklingsprosessen (dokumentert i `docs/ai-log.md`), ikke i produktet.
- Ikke et ERP-system, og ikke en full MRP II-kjede: ingen prognoser, S&OP, scheduling, kapasitetsplanlegging, væravhengighet eller Monte Carlo.
- Ingen endring av BOM-strukturen (legge til eller fjerne varer og BOM-linjer), ingen alternative komponenter og ingen versjonering av BOM.
- Ingen meldinger om å framskynde, utsette eller kansellere åpne ordre. MRP flytter aldri ordre selv.
- Ingen pegging (sporing av behov tilbake til byggenummer) og ingen leverandørvalg.
- Ingen innkjøpsmodul: bestillingsforslag blir ikke til faktiske ordre i appen.
- Ingen flere brukere, roller eller samtidig bruk utover demoformål.

## 7. MVP-omfang

### 7.1 Inn

- Innlogging med én demobruker (FR-1).
- Testdata fra fasiten ved oppstart, og tilbakestilling (FR-2, FR-3).
- BOM-tre for testfartøyet (FR-4).
- Redigering av MPS, lagerbeholdning og åpne ordre, og justering av mengde per, ledetid og partiregel, med validering (FR-5 til FR-8, FR-18).
- MRP-kjøring med BOM-eksplosjon, netting, partiregler, ledetidsoffset og forfalte produksjonsordrer (FR-9 til FR-12).
- Exception-meldingene E1 og E2 (FR-13, FR-14).
- MRP-tabell, liste over forslag og meldinger, og markering av endringer (FR-15 til FR-17).

### 7.2 Ute av v1

- **Trinn 2** (bare hvis v1 er stabil og testet): full redigering av BOM-strukturen, alternativregler i BOM, sikkerhetslager for importkomponenter, meldinger om å framskynde eller utsette åpne ordre.
- **Visjon:** alt som står under «Ute» i briefen.

## 8. Suksessmål

**Primære**
- **SM-1 Riktig beregning:** alle automatiske beregningstester mot scenario A–E i fasiten består. Mål: 100 %. Validerer FR-10 til FR-14.
- **SM-2 Synlig forplantning:** den manuelle testplanen for scenario A, B, C og E gjennomføres uten avvik og dokumenteres i repoet. Validerer FR-15 til FR-18.
- **SM-3 Kjørbar for sensor:** en person som ikke kjenner prosjektet, får appen og testene til å kjøre bare ved å følge README, på under 15 minutter. Validerer NFR-1, NFR-3.

**Sekundære**
- **SM-4 Sporbarhet:** hver FR er dekket av minst én story og minst én test (automatisk eller manuell). Validerer NFR-7.

**Mot-mål (skal ikke optimeres)**
- **SM-C1 Antall funksjoner og skjermbilder** — mer funksjonalitet er ikke et mål før SM-1 til SM-3 er nådd. Motvekt til fristelsen å begynne på trinn 2.
- **SM-C2 Tilpasning til fasiten** — testene skal ikke kunne bestås av kode som er skreddersydd for testfartøyet (hardkodede varer eller uker). Motvekt til SM-1. Scenario D, skalatesten i NFR-3 og egenskapssjekker (som massebalanse) brukes for å avsløre dette.

## 9. Åpne spørsmål

Ingen. Teknologivalget (database, frontend-rammeverk, prosjektstruktur) er avgjort i [arkitekturen](../../architecture/architecture-Red%20Ball%20Express-2026-11-24/ARCHITECTURE-SPINE.md) 2026-11-24.

## 10. Antakelser

Ingen gjenstående antakelser. Fasitens regler R1–R11 og scenario A–E er bekreftet.
