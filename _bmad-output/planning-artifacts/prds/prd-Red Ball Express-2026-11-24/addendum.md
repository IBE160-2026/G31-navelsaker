# Addendum til PRD: Red Ball Express v1

Materiale som hører til arkitekturen eller forklarer valg i PRD-en, men som ikke er krav.

## Tekniske føringer fra briefen (til arkitekturen)

Briefen beskriver dette tekniske grunnlaget. Arkitekturen tar endelig stilling:

- Backend i Python med FastAPI, pakkehåndtering med uv.
- Frontend i Node.js-økosystemet.
- Lokal database, SQLite eller lokal PostgreSQL, med testdata fra `testdata/testfartoy-v1/input.json`. Faglærer pekte på at tre separate deler er mye for én person, og at SQLite er det enkleste å kjøre for sensor.
- [technology.md](../../architecture/technology.md) beskriver et annet prosjekt (Pytagoras) og kan bare brukes som inspirasjon, ikke som føring.

NFR-3 (testbar beregningskjerne) betyr i praksis at MRP-logikken bør ligge som rene funksjoner uten avhengighet til database eller web-rammeverk.

## Alternativer som ble vurdert og forkastet

| Valg i PRD-en | Alternativ | Hvorfor forkastet |
|---|---|---|
| Bare E1 og E2 som exception-typer | Også framskynd/utsett/kanseller for åpne ordre | Krever regler for hvilken åpen ordre som skal flyttes, og gir mer logikk som er vanskeligere å verifisere. Flyttet til trinn 2. |
| Barnas behov fra forfalte produksjonsordrer legges i uke 1 | Forkaste behovet, eller stoppe kjøringen med feil | Å forkaste skjuler et reelt behov. Å stoppe gir en app som feiler når sensor prøver uventet bruk. Uke 1 er forsiktig og synlig. |
| Justering av mengde per, ledetid og partiregel (FR-18) | Bare visning av BOM | Briefen lover at planleggeren kan justere BOM. Justering av eksisterende linjer koster lite, fordi MRP-logikken allerede er generell, og gir en sterk demo av forplantning (scenario E). |
| Strukturen er fast i v1 | Full redigering (legge til og fjerne varer og BOM-linjer) | Krever sjekk av sykler, varer i bruk og et mer komplisert BOM-tre i skjermbildet. Flyttet til trinn 2. |
| «Kjør MRP»-knapp med endringsmarkering | Automatisk omberegning ved hver endring | En eksplisitt kjøring gir et tydelig før/etter å sammenligne, noe som gjør forplantningen lettere å vise og teste. |
| Ingen KI i appen | KI-basert forklaring av meldinger eller prognoser | Faglærer ba om avklaring av hva «AI» betyr i appen. Det er vanskelig å kontrollere at det er riktig, og det krever eksterne API-er med nøkler. |
