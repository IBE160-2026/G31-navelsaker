---
title: Red Ball Express
status: final
created: 2026-09-16
updated: 2026-09-16
---

# Product Brief: Red Ball Express

## Sammendrag

Red Ball Express er et AI-støttet MRP II-system — produksjonsplanleggingskjernen i et ERP-system, ikke et fullt ERP — bygget som eksamensprosjekt i IBE130 (Programmering med KI, logistikkstudiet). Systemet demonstrerer, med en verftsbedrift som bygger mindre spesialfartøy (f.eks. servicefartøy til havvind) som case, hvordan data flyter sammenhengende gjennom hele planleggingskjeden: fra etterspørselsprognose, via S&OP og MPS, ned til produktstruktur (BOM), komponentbehov (MRP) og detaljert produksjonsscheduling.

Verftsproduksjon er et krevende, men lærerikt case for produksjonsplanlegging fordi det kombinerer dype, flernivå produktstrukturer, lange og usikre ledetider på importerte nøkkelkomponenter (f.eks. hovedmotor), og væravhengig utendørs produksjon (skrogarbeid) — se Problemet for hvorfor dagens store ERP-/MRP-verktøy dekker dette dårlig.

Prosjektet er ikke kommersielt. Målet er en fungerende, demonstrerbar helhet innen semesterslutt som viser faglig presisjon i produksjonsplanleggingslogikken og reell dataflyt mellom modulene — ikke bredde for breddens skyld.

## Problemet

Produksjonsplanlegging i verftsindustrien er komplekst av tre grunner:

1. **Dype, flernivå produktstrukturer (BOM).** Et spesialfartøy består av tusenvis av komponenter organisert i flere nivåer, med alternativregler og versjonering. Feil eller upresise strukturer forplanter seg videre til feil i komponentbehov og produksjonsplan.
2. **Lange og usikre ledetider på importerte komponenter.** Nøkkelkomponenter som hovedmotor importeres ofte med lang og uforutsigbar leveringstid. Én forsinket kritisk komponent kan kaskadere gjennom hele byggesekvensen, fordi skrog- og utrustningsarbeid ofte er sekvensielt avhengig.
3. **Væravhengig produksjon.** Skrogarbeid utendørs er begrenset av værvinduer (bølgehøyde, vind), en usikkerhetskilde som ikke finnes i innendørs diskret produksjon og som tradisjonelle MRP-systemer ikke modellerer eksplisitt.

Bransjen løser i dag dette med generalist-ERP-systemer tilpasset engineer-to-order-produksjon (SAP S/4HANA PP, IFS Cloud, Infor CloudSuite/SyteLine) eller maritime MRO-verktøy, med begrenset offentlig dokumentert AI-støttet usikkerhetshåndtering i selve planleggingskjernen (se addendum for markedsgrunnlag). Konsekvensen er planer som ofte er statiske i møte med usikkerhet planleggeren i praksis må håndtere manuelt.

## Løsningen

Red Ball Express implementerer de seks klassiske MRP II-modulene — Demand Management, S&OP, MPS, BOM, MRP og Operations Scheduling — som en sammenhengende kjede der en endring ett sted forplanter seg gjennom hele kjeden. AI brukes ikke som pynt på toppen, men som beslutningsstøtte inne i kjeden, med dybde prioritert slik:

| Prioritet | Fokusområde | Rolle i systemet |
|---|---|---|
| 1 | **BOM + MRP** | Kjernen — bygges dypest. Flernivå produktstruktur og nøyaktig nettobehovsberegning er fundamentet alt annet planlegger mot. |
| 2 | **AI-støttet etterspørselsprognose** | Prognosemodeller for Demand Management-modulen, med scenarioer (optimistisk/pessimistisk/normal). |
| 3 | **Usikkerhetsmodellering** | Ledetidsusikkerhet fra underleverandører og produksjonsusikkerhet; sikkerhetslager-beregning og Monte Carlo-simulering. Dette er systemets tydeligste differensiator — nærmeste faglige presedens er fersk forskning på ML-basert ledetidsprediksjon for verft (se addendum). |
| 4 | **S&OP og MPS** | Forenklet, men fungerende — aggregert plan og ukentlig hovedplan kobler prognose til detaljplan. |
| 5 | **Operations Scheduling** | Forenklet detaljplanlegging — jobbrekkefølge og varsler om forsinkelser. |

Full spesifikasjon av data inn/data ut/beslutningspunkter per modul, fra fagets oppgavetekst, ligger i addendum.

Datamodellen designes generisk nok til å kunne brukes av andre diskrete produksjonsbedrifter, selv om selve demoen er verftsspesifikk — dette tvinger fram ryddige abstraksjoner (produkt, ressurs, operasjon, leverandør) fremfor verftsspesifikke snarveier.

**Teknisk grunnlag**: FastAPI/Python-backend (uv), Node.js-frontend, Supabase (PostgreSQL). Innlogging kreves siden dataene regnes som forretningskritiske og konkurransesensitive i domenet — for demoformål er enkel brukernavn/passord-autentisering tilstrekkelig, uten krav om mange samtidige brukere.

## Hva gjør dette annerledes

- **AI inne i planleggingslogikken, ikke rundt den.** Prognoser, ledetidsprediksjon og Monte Carlo-basert sikkerhetslager er integrert i selve beslutningspunktene i MRP-kjeden, ikke et separat analyseverktøy ved siden av.
- **Værvinduer som eksplisitt usikkerhetsakse.** Skrogarbeidets væravhengighet modelleres direkte i planleggingen, ikke bare som en implisitt buffer slik tradisjonelle MRP-systemer håndterer den.
- **Ærlig om hva det ikke er.** Dette er ikke et fullt ERP-system — regnskap, HR, CRM, fullverdig innkjøp og leverandørportaler er bevisst utelatt for å gå i dybden der det faglig teller mest.
- **Generisk datamodell, verftsspesifikk demo.** Domenemodellen er ikke låst til skipsbygging, selv om casen er det.

Fortrinnet er ikke teknologisk unikt — sikkerhetslager og Monte Carlo er etablerte teknikker (se addendum) — men dybden og sammenhengen i hvordan de er integrert gjennom hele planleggingskjeden, i et domene de store verktøyene ikke adresserer med samme AI-fokus.

## Hvem dette tjener

**Primær**: En fiktiv produksjonsplanlegger ved verftsbedriften — demo-persona som viser hvordan systemet støtter beslutninger om bestillingstidspunkt, partistørrelse, prioritering ved kapasitetsmangel og håndtering av forsinkelser.

## Suksesskriterier

- **End-to-end sammenheng**: en endring i én modul (f.eks. endret prognose, forsinket leveranse) forplanter seg synlig og korrekt gjennom hele kjeden fram til produksjonsscheduling.
- **Modul-dybde følger prioritering**: BOM+MRP er den grundigst utbygde og mest robuste delen av systemet; S&OP/MPS/Scheduling er enklere, men reelt fungerende — ikke attrapper.
- **AI leverer synlig beslutningsstøtte**: prognoser, ledetidsprediksjon og Monte Carlo-baserte sikkerhetslagerforslag er koblet til konkrete beslutningspunkter (ikke bare visualisert isolert).
- **Demonstrerbar innen semesterslutt**: systemet kan kjøres og vises fram som en sammenhengende demo med realistiske verftsdata.
- [ANTAKELSE] Konkrete måltall (f.eks. prognosenøyaktighet, andel korrekt genererte bestillingsforslag) er ikke satt ennå — bør defineres i PRD når modellvalg er gjort.

## Omfang

**Inn (v1, demonstrasjonsklar):**
- Alle seks moduler i minst forenklet, fungerende form, med data inn/ut/beslutningspunkter som spesifisert i addendum.
- AI-støttet etterspørselsprognose med scenarioer.
- Usikkerhetsmodellering: sikkerhetslager-beregning og Monte Carlo-simulering for ledetids- og produksjonsusikkerhet.
- Flernivå BOM med alternativregler.
- Innlogging (brukernavn/passord).
- Generisk datamodell som i prinsippet støtter andre diskrete produksjonsbedrifter.

**Ute (eksplisitt utenfor scope):**
- Regnskap/økonomi
- HR/lønn
- CRM/salg
- Fullverdig innkjøpsmodul
- Leverandørportal-integrasjon
- Støtte for mange samtidige brukere eller produksjonsherding utover demoformål

## Visjon

Som eksamensprosjekt er ambisjonen ikke kommersialisering, men et system som selv beviser sin egen påstand: at AI kan gi reell beslutningsstøtte gjennom en hel produksjonsplanleggingskjede i et domene (verft) preget av dyp BOM-kompleksitet og sammensatt usikkerhet. Lykkes den generiske datamodellen, demonstrerer prosjektet i forlengelsen et mønster som kunne bæres videre til andre diskrete, prosjektbaserte produksjonsbedrifter — men det forblir en demonstrasjon av prinsipp, ikke et produkt under videre utvikling etter innlevering, med mindre annet besluttes.
