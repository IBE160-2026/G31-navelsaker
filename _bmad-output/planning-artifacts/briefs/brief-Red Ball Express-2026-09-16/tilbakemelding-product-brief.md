# Tilbakemelding på product brief

| | |
|---|---|
| **Gruppe** | G31 – G31-navelsaker |
| **Product brief** | `_bmad-output/planning-artifacts/briefs/brief-Red Ball Express-2026-09-16/brief.md` (commit `465bc73`), med `addendum.md` i samme mappe |
| **Tilbakemelding fra** | Faglærer i IBE160 (utarbeidet med KI-støtte) |
| **Dato** | 2026-10-06 |

## Samlet vurdering

- **Bør revideres før dere går videre.** Rett punktene markert «Endre» før dere lager PRD og arkitektur.

**Det som er bra:**

1. Verftscaset er godt valgt og godt begrunnet: dype BOM-strukturer, lange ledetider på importerte komponenter som hovedmotor og væravhengig skrogarbeid gir et faglig interessant planleggingsproblem. Addendumet viser at dere har satt dere inn i markedet og fagstoffet.
2. Prioriteringstabellen med BOM + MRP som kjerne er et klokt grep, og det er ærlig at dere skriver hva systemet ikke er (ikke fullt ERP, ingen regnskap, HR eller CRM).

**De viktigste endringene:**

1. Omfanget er for stort for semesteret. Briefen har alle seks MRP II-modulene i v1, i tillegg til KI-prognoser, Monte Carlo-simulering, værvinduer, flernivå BOM med alternativregler og innlogging. Det tilsvarer hele forslag 4, som er det mest omfattende forslaget på lista, og repoet har ett medlem. Avgrens v1 til BOM + MRP, og flytt resten til senere trinn.
2. Suksesskriteriene kan ikke testes slik de står. «Forplanter seg synlig og korrekt» og «reelt fungerende, ikke attrapper» trenger konkrete eksempler med fasit, for eksempel «nettobehov per uke og komponent stemmer med en håndregnet MRP-tabell for et testfartøy med tre BOM-nivåer». Briefen sier selv at måltall mangler.
3. Avklar hva «AI» betyr i appen og hvordan sensor kan kjøre den. Er prognosen en statistisk modell, maskinlæring eller en språkmodell? Supabase krever en konto. Planlegg en lokal database eller ferdige testdata, slik at appen kan kjøres etter README uten deres tjenester.

## Vanskelighetsgrad og gjennomførbarhet

### Vurdert vanskelighetsgrad

- **Vanskelig**

**Sammenlignbart med:** 4) KI-støttet MRP II (inkl. BOM) – alle modulene 4.1–4.6, med Monte Carlo-simulering og værvinduer i tillegg.

**Begrunnelse:**

| Faktor | Nivå (lav / middels / høy) | Kommentar |
|---|---|---|
| Domenelogikk – hvor mange og hvor kompliserte regler og beregninger må stemme? | Høy | Prognoser, S&OP, MPS, flernivå BOM-eksplosjon, nettobehov, sikkerhetslager, Monte Carlo og scheduling må alle stemme og henge sammen. |
| Datamodell – antall entiteter og relasjoner mellom dem | Høy | Produkt, komponent, BOM-nivåer med alternativer og versjoner, leverandør, ressurs, operasjon, routing, ordre, prognose og plan per periode. |
| Brukere, roller og innlogging | Lav | Én demo-persona med enkel innlogging. |
| KI-funksjonalitet i appen, f.eks. kall til språkmodell, prompts i koden og håndtering av usikre svar | Høy | Prognosemodeller, ledetidsprediksjon og Monte Carlo er krevende å implementere og enda mer krevende å kontrollere. Det er uklart hvilken type KI som menes. |
| Integrasjoner og eksterne tjenester, f.eks. API-er, betaling og e-post | Middels | Supabase som ekstern database. Eventuelle værdata er ikke beskrevet. |
| Sanntid, samtidighet eller flere brukere som påvirker hverandre | Lav | Ikke krav om mange samtidige brukere. |
| Filhåndtering, f.eks. opplasting, PDF-lesing og eksport | Lav | Ikke beskrevet. Realistiske verftsdata må likevel lages og lastes inn. |
| Sikkerhet og personvern | Lav | Fiktive forretningsdata og enkel innlogging. |

**Hva vanskelighetsgraden betyr for dere:**

- _Vanskelig:_ Et vanskelig prosjekt gir større mulighet for toppkarakter, men også større risiko. Definer en minimal versjon som sikkert kan bli ferdig, og legg resten i tydelige trinn etterpå. For dere bør den minimale versjonen være flernivå BOM + MRP for ett testfartøy.

### Gjennomførbarhet med BMAD og Claude Code

Dere skal planlegge med BMAD (product brief → PRD → arkitektur → epics og stories) og implementere med Claude Code. Vurderingen under tar hensyn til at det må være tid til hele denne flyten, og til testing, retting og README til slutt.

| Spørsmål | Vurdering (OK / risiko / stor risiko) | Kommentar |
|---|---|---|
| **Tid og omfang** – kan v1 realistisk bli ferdig og stabil i løpet av semesteret, med tid til flere iterasjoner? | Stor risiko | Seks moduler pluss tre KI-/usikkerhetsfunksjoner er langt mer enn én person rekker gjennom hele BMAD-flyten med testing. Ingen PRD eller arkitektur ennå. |
| **BMAD-flyten** – er briefen konkret nok til at PRD, arkitektur og stories kan lages uten store hull, og blir det overkommelig mange stories? | Stor risiko | Modulspesifikasjonen i addendumet er kopiert fra forslagslista og er ikke tilpasset verftscaset. Det vil gi svært mange stories med uklare akseptansekriterier. |
| **Egnet for Claude Code** – bruker løsningen en vanlig, godt dokumentert teknologistakk som Claude Code håndterer godt, eller krever den nisjeteknologi, spesialmaskinvare eller mye manuell konfigurasjon? | Risiko | FastAPI og en JavaScript-frontend er godt egnet. Supabase gir ekstra oppsett og avhengighet av en ekstern konto. SQLite eller lokal PostgreSQL er enklere. |
| **Kontroll på KI-ens arbeid** – kan gruppen selv avgjøre om koden gjør det riktige? Krever domenet kunnskap gruppen ikke har, f.eks. avanserte beregninger eller fagregler, så er det vanskelig å kvalitetssikre. | Stor risiko | MRP kan kontrolleres med håndregnede tabeller. Prognosemodeller, Monte Carlo-sikkerhetslager og værvinduer er derimot svært vanskelige å kontrollere for riktighet. |
| **Testbarhet** – finnes det tydelige regler og forventede resultater som tester kan skrives mot? | Risiko | BOM-eksplosjon og nettobehov er godt testbare. De øvrige kriteriene har ingen forventede resultater ennå. |
| **Kjørbar for sensor** – kan appen kjøres lokalt etter README, uten gruppens nøkler, betalte kontoer eller egen infrastruktur? | Risiko | Supabase krever konto og nøkler. Planlegg lokal database med seed-data. |
| **Avhengigheter og kostnader** – krever løsningen betalte API-er, f.eks. språkmodeller, og finnes det en plan for kostnad, testmodus eller mock-data? | Risiko | Supabase har gratisnivå, men krever konto. Det er uklart om KI-delen bruker eksterne API-er. Beskriv dette. |

**Konklusjon om gjennomførbarhet:**

- **Lite realistisk uten vesentlige endringer.** Se forslagene under.

**Forslag til justering av omfang eller vanskelighetsgrad:**

1. Gjør v1 til **flernivå BOM + MRP for ett testfartøy**: produktstruktur med tre–fire nivåer, MPS som input, nettobehov per uke, bestillingsforslag med ledetidsoffset og exception-meldinger (for eksempel når hovedmotoren har lengre ledetid enn horisonten). Dette er fortsatt et krevende prosjekt, og det er fullt testbart med fasittabeller.
2. Legg til én avgrenset usikkerhetsfunksjon i trinn 2, for eksempel sikkerhetslagerformelen fra addendumet for de viktigste importkomponentene. Flytt prognoser, S&OP, scheduling, Monte Carlo og værvinduer til «Ute» eller visjonen.

## Hvorfor product brief er viktig for mappen

Product brief er utgangspunktet for PRD, arkitektur, stories og til slutt koden. Del 1 av mappen vurderes blant annet på om sensor kan følge en sporbar vei fra plan til ferdig app. Den vurderes også på om appen gjør det dere har beskrevet, om den er testet, om den er godt designet, og om den kan kjøres etter README. Et uklart, for stort eller for lite brief gjør alt dette vanskeligere senere. Det er mye enklere å rette nå enn sent i semesteret.

## 1. Gjennomgang av briefens deler

| Del av brief | Status | Kommentar |
|---|---|---|
| Executive Summary – er det klart hva appen er, og hvilket problem den løser? | Juster | Klart hva systemet er, men sammendraget omtaler emnet som IBE130. Rett til IBE160, og si tydelig hva v1 skal levere. |
| The Problem – er problemet konkret, med reelle situasjoner og brukere? | OK | De tre problemene (dype BOM-er, usikre ledetider, væravhengighet) er konkrete og godt forklart. |
| The Solution – beskriver løsningen brukeropplevelsen, ikke bare teknologi? | Endre | Løsningen er en liste over moduler og teknikker. Beskriv hva planleggeren gjør i appen, steg for steg, for eksempel «legger inn MPS, ser nettobehov per uke, får varsel om at hovedmotoren må bestilles i uke 3». |
| What Makes This Different – er vurderingen ærlig og realistisk? | Juster | Ærlig om at teknikkene er etablerte. Men «AI inne i planleggingslogikken» og «værvinduer» er det dere har minst mulighet til å levere og kontrollere. |
| Who This Serves – er primærbrukerne tydelige, og vet vi hva de trenger? | Juster | Produksjonsplanleggeren ved verftet er en god primærbruker. Beskriv hvilke beslutninger personen tar i en vanlig uke, slik at designet kan bygges rundt dem. |
| Success Criteria – kan kriteriene faktisk sjekkes eller testes? | Endre | Kriteriene er kvalitative. Legg til konkrete kriterier med fasit for BOM-eksplosjon, nettobehov og exception-meldinger. |
| Scope – er det klart hva som er med i første versjon, og hva som ikke er det? | Endre | «Alle seks moduler» i v1 er for stort. Del i v1 (BOM + MRP), trinn 2 og «Ute». |
| Vision – henger visjonen sammen med resten uten å blåse opp omfanget? | OK | Nøktern og ærlig om at prosjektet er en demonstrasjon av prinsipp. |

## 2. Utgangspunkt for del 1 av mappen

Punktene følger kriteriene i sensorveiledningen for del 1. Vektene i parentes viser hvor mye hvert kriterium teller i del 1.

| Kriterium i del 1 | Hva briefen bør legge til rette for | Status | Kommentar |
|---|---|---|---|
| **1. Prosess og KI-styring** (30 %) | Brief som er presis nok til at PRD og stories kan bygges direkte på den, slik at krav kan spores fra brief til kode. | Endre | Med seks moduler blir sporbarheten fra brief til kode vanskelig. En avgrenset v1 gir PRD og stories som faktisk kan følges til kode. |
| **2. Funksjonalitet og omfang** (20 %) | Realistisk omfang for gruppen og semesteret: en tydelig kjerneflyt som kan bli ferdig og stabil, og nok innhold til å vise reell funksjonalitet. | Endre | Risiko for mange halvferdige moduler. BOM + MRP alene gir nok reell funksjonalitet. |
| **3. Kvalitetssikring og testing** (15 %) | Suksesskriterier og funksjoner som er konkrete nok til å bli testtilfeller. | Endre | Lag et testfartøy med håndregnet MRP-tabell som fasit. Uten dette kan dere ikke vise at Claude Codes beregninger stemmer. |
| **4. Design og brukeropplevelse** (10 %) | Tydelige brukere og brukssituasjoner som designet kan bygges rundt, gjerne med de viktigste skjermbildene eller flytene skissert. | Juster | Designprinsippet om synlig dataflyt i addendumet er godt. Skisser de to–tre viktigste skjermbildene (BOM-tre, MRP-tabell, varselliste). |
| **5. Kodekvalitet og arkitektur** (10 %) | Teknologivalg som er begrunnet og ikke mer komplekse enn appen trenger. | Juster | Tre deler (FastAPI, Node-frontend, Supabase) er mye for én person. Vurder en enklere stakk med lokal database. |
| **6. README og kjørbarhet** (10 %) | Løsning som andre kan kjøre lokalt uten betalte kontoer, og uten tilgang til gruppens egne tjenester og nøkler. | Juster | Supabase gjør kjøring avhengig av konto og nøkler. Planlegg lokal kjøring med seed-data. |
| **7. Ryddighet i repoet** (5 %) | En plan for hvor hemmeligheter, testdata og dokumentasjon skal ligge. | Juster | Planlegg `.env.example`, en mappe for verftstestdata og at Supabase-nøkler aldri committes. |

## 3. Neste steg for gruppen

1. Skriv om Scope: v1 = flernivå BOM + MRP for ett testfartøy, trinn 2 = sikkerhetslager for importkomponenter, resten under «Ute» eller visjonen.
2. Lag et konkret testfartøy med tre–fire BOM-nivåer og en håndregnet MRP-tabell, og skriv suksesskriteriene om til «resultatet stemmer med fasit».
3. Bestem databaseløsning og hva «AI» betyr i v1, og beskriv hvordan sensor kan kjøre appen lokalt uten deres kontoer. Gå deretter videre til PRD.

Oppdater product brief i repoet når dere har gjort endringene, slik at historikken viser hvordan planen utviklet seg. Det er en del av prosessen sensor ser etter.
