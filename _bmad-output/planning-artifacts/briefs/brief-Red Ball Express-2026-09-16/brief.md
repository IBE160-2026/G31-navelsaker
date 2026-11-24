---
title: Red Ball Express
status: final
created: 2026-09-16
updated: 2026-09-16
---

# Product Brief: Red Ball Express

## Sammendrag

Red Ball Express er, i v1, et BOM + MRP-system — kjernen i produksjonsplanleggingen i et MRP II/ERP-system, ikke et fullt ERP — bygget som eksamensprosjekt i IBE160 (Programmering med KI, logistikkstudiet). Systemet demonstrerer, med ett testfartøy fra en fiktiv verftsbedrift som case, hvordan en flernivå produktstruktur (BOM) brytes ned til korrekte nettobehov, bestillingsforslag og exception-meldinger per uke og komponent (MRP) — og hvordan en endring (f.eks. endret hovedplan eller forsinket leveranse) forplanter seg synlig gjennom BOM-strukturen til oppdaterte behov.

Verftsproduksjon er et krevende, men lærerikt case for produksjonsplanlegging fordi det kombinerer dype, flernivå produktstrukturer og lange, usikre ledetider på importerte nøkkelkomponenter (f.eks. hovedmotor) — se Problemet for hvorfor dagens store ERP-/MRP-verktøy dekker dette dårlig. Den fulle visjonen inkluderer også væravhengig produksjon, etterspørselsprognoser og usikkerhetsmodellering (se Visjon), men dette er utenfor v1.

Prosjektet er ikke kommersielt. Målet er en fungerende, testbar v1 innen semesterslutt som viser faglig presisjon i BOM-eksplosjon og nettobehovsberegning, verifisert mot en håndregnet fasit for testfartøyet — ikke bredde for breddens skyld.

## Problemet

Produksjonsplanlegging i verftsindustrien er komplekst av tre grunner:

1. **Dype, flernivå produktstrukturer (BOM).** Et spesialfartøy består av tusenvis av komponenter organisert i flere nivåer, med alternativregler og versjonering. Feil eller upresise strukturer forplanter seg videre til feil i komponentbehov og produksjonsplan.
2. **Lange og usikre ledetider på importerte komponenter.** Nøkkelkomponenter som hovedmotor importeres ofte med lang og uforutsigbar leveringstid. Én forsinket kritisk komponent kan kaskadere gjennom hele byggesekvensen, fordi skrog- og utrustningsarbeid ofte er sekvensielt avhengig.
3. **Væravhengig produksjon.** Skrogarbeid utendørs er begrenset av værvinduer (bølgehøyde, vind), en usikkerhetskilde som ikke finnes i innendørs diskret produksjon og som tradisjonelle MRP-systemer ikke modellerer eksplisitt.

Bransjen løser i dag dette med generalist-ERP-systemer tilpasset engineer-to-order-produksjon (SAP S/4HANA PP, IFS Cloud, Infor CloudSuite/SyteLine) eller maritime MRO-verktøy, med begrenset offentlig dokumentert AI-støttet usikkerhetshåndtering i selve planleggingskjernen (se addendum for markedsgrunnlag). Konsekvensen er planer som ofte er statiske i møte med usikkerhet planleggeren i praksis må håndtere manuelt.

## Løsningen

Red Ball Express v1 implementerer kjernen i MRP II-kjeden — Bill of Materials (BOM) og Material Requirements Planning (MRP) — som en sammenhengende flyt der planleggeren jobber slik:

1. Planleggeren legger inn eller justerer hovedproduksjonsplanen (MPS) for testfartøyet — hvilke enheter som skal være ferdige i hvilken uke.
2. Planleggeren åpner produktstrukturen (BOM) for fartøyet og ser komponentene brutt ned i tre–fire nivåer, med mengder per komponent (fast struktur i v1, uten alternative komponenter).
3. Systemet kjører MRP-eksplosjonen: beregner nettobehov per uke og komponent basert på MPS, BOM, lagerstatus og ledetider, og genererer bestillingsforslag med ledetidsoffset.
4. Planleggeren ser en liste over exception-meldinger — for eksempel at hovedmotoren til byggenr. 2 skulle vært bestilt for 9 uker siden, fordi ledetiden (20 uker) er lengre enn planleggingshorisonten (16 uker) — og kan justere MPS eller BOM og se at nettobehovet oppdateres på nytt.

Full spesifikasjon av data inn/data ut/beslutningspunkter for BOM og MRP, fra fagets oppgavetekst, ligger i addendum. Spesifikasjonen av de fire modulene utenfor v1 (Demand Management, S&OP, Operations Scheduling) ligger også i addendum, som kildegrunnlag for en eventuell videreføring etter v1 (se Visjon).

**Teknisk grunnlag**: FastAPI/Python-backend (uv), Node.js-frontend, lokal database (SQLite eller lokal PostgreSQL) med seed-data for testfartøyet, slik at systemet kan kjøres etter README uten eksterne kontoer eller nøkler. Enkel innlogging (brukernavn/passord) er inkludert siden dataene regnes som forretningskritiske i domenet, uten krav om mange samtidige brukere.

## Hva gjør dette annerledes

- **BOM og MRP testet mot en håndregnet fasit.** Riktigheten dokumenteres med et konkret testfartøy der nettobehov, bestillingsforslag og exception-meldinger er verifisert opp mot en manuelt beregnet MRP-tabell — ikke bare visuelt plausible tall.
- **Synlig dataflyt gjennom BOM-strukturen.** En endring i MPS eller lagerstatus forplanter seg synlig gjennom BOM-nivåene til oppdaterte nettobehov, slik at sammenhengen i planleggingslogikken er eksplisitt, ikke skjult i en svart boks.
- **Ærlig om hva det ikke er.** Dette er verken et fullt ERP-system eller en fullverdig MRP II-kjede i v1 — etterspørselsprognoser, S&OP, scheduling, væravhengighet og Monte Carlo-basert usikkerhetsmodellering er bevisst utelatt fra v1 og beskrevet som visjon, ikke levert funksjonalitet.

Fortrinnet i v1 er ikke teknologisk unikt — BOM-eksplosjon og MRP-nettobehovsberegning er veletablert teori (se addendum) — men presisjonen og testbarheten i implementasjonen, demonstrert mot et konkret, håndregnet eksempel.

## Hvem dette tjener

**Primær**: En fiktiv produksjonsplanlegger ved verftsbedriften — demo-persona som i en vanlig uke tar beslutninger om: når en komponent må bestilles ut fra ledetiden (f.eks. hovedmotor), hvilken partistørrelse som skal bestilles, og hvordan man reagerer når en exception-melding varsler om en forsinkelse som påvirker byggesekvensen. Systemet støtter disse beslutningene ved å gjøre nettobehov og konsekvensen av endringer synlige, ikke ved å ta beslutningen for planleggeren.

## Suksesskriterier

- **Korrekt BOM-eksplosjon**: for testfartøyet (tre–fire BOM-nivåer) stemmer systemets beregnede nettobehov per uke og komponent med en håndregnet MRP-tabell (fasit) for samme fartøy.
- **Korrekte bestillingsforslag og exception-meldinger**: bestillingsforslag med ledetidsoffset og exception-meldinger (f.eks. hovedmotor med ledetid lengre enn horisonten) stemmer med fasiten.
- **Synlig forplantning**: en endring i MPS eller lagerstatus for testfartøyet gir en synlig og korrekt oppdatering av nettobehov og exception-meldinger i brukergrensesnittet.
- **Kjørbar uten eksterne tjenester**: systemet kan settes opp og kjøres lokalt etter README, med seed-data for testfartøyet, uten kontoer eller nøkler til eksterne tjenester.
- **Demonstrerbar innen semesterslutt**: BOM+MRP-kjeden for testfartøyet kan vises fram som en sammenhengende, testet demo.

## Omfang

**Inn (v1, demonstrasjonsklar — enklest mulige variant som fortsatt er reelt testbar):**
- Flernivå BOM (tre–fire nivåer) for ett testfartøy, fast struktur uten alternative komponenter.
- MRP: nettobehovsberegning per uke og komponent, bestillingsforslag med ledetidsoffset, exception-meldinger (f.eks. når hovedmotoren har lengre ledetid enn planleggingshorisonten).
- Enkel MPS som input til MRP — en manuelt satt hovedproduksjonsplan for testfartøyet, ikke en egen S&OP-modul.
- Et konkret testfartøy med håndregnet MRP-tabell som fasit, til bruk i test og demo (se `testdata/testfartoy-v1/`).
- Enkel innlogging (brukernavn/passord) for demoformål.
- Lokal database med seed-data for testfartøyet, slik at systemet kan kjøres etter README uten eksterne kontoer eller nøkler.

**Trinn 2 og videre (bygges på kun hvis det er hensiktsmessig etter at v1 er stabil og testet):**
- Alternativregler i BOM (velge mellom erstattbare komponenter/leverandører for en BOM-linje).
- Sikkerhetslager-beregning (probabilistisk formel, jf. addendum) for de viktigste importerte komponentene, f.eks. hovedmotor.

**Ute (eksplisitt utenfor scope — flyttet til visjonen):**
- Demand Management / AI-støttet etterspørselsprognose
- Sales & Operations Planning (S&OP) som egen modul
- Monte Carlo-simulering
- Værvinduer / væravhengig planlegging
- Operations Scheduling (detaljert produksjonskjøreplan)
- Regnskap/økonomi
- HR/lønn
- CRM/salg
- Fullverdig innkjøpsmodul
- Leverandørportal-integrasjon
- Generisk datamodell for andre produksjonsbedrifter (kan vurderes senere, ikke et v1-mål)
- Støtte for mange samtidige brukere eller produksjonsherding utover demoformål

## Visjon

v1 beviser at BOM-eksplosjon og MRP-nettobehovsberegning kan gjøres riktig og testbart for et verftscase med dype produktstrukturer og usikre ledetider. Lykkes v1, er den naturlige videreføringen (ikke en del av eksamensleveransen med mindre tiden tillater det):

- **Trinn 2**: alternativregler i BOM (erstattbare komponenter), deretter sikkerhetslager-beregning for de viktigste importkomponentene (f.eks. hovedmotor) — bygges på kun hvis det er hensiktsmessig etter at v1 er stabil og testet.
- **Videre visjon**: en full MRP II-kjede med AI-støttet etterspørselsprognose, S&OP, forenklet operations scheduling, væravhengig planlegging (værvinduer) og Monte Carlo-basert usikkerhetsmodellering — slik den opprinnelige briefen skisserte. Full spesifikasjon av disse modulene ligger i addendum som kildegrunnlag hvis prosjektet videreføres, sammen med en eventuell generisk datamodell for andre diskrete produksjonsbedrifter.

Som eksamensprosjekt er ambisjonen ikke kommersialisering, men et system som beviser sin egen påstand innenfor det avgrensede omfanget: at dyp, korrekt BOM/MRP-logikk kan demonstreres og testes for et krevende verftscase. Det forblir en demonstrasjon av prinsipp, ikke et produkt under videre utvikling etter innlevering, med mindre annet besluttes.
