# Kvalitetssjekk av arkitekturen (reviewer gate)

2026-11-24. Kjørt sekvensielt i samme økt, ikke som uavhengige subagenter (solo-prosjekt, lav risiko, samme vurdering som for PRD-en). Funnene er rettet i `ARCHITECTURE-SPINE.md` før status ble satt til `final`.

## 1. Lint (`lint_spine.py`)

0 funn.

## 2. Avstemming mot input (PRD, addendum, fasit, brief)

Alle FR-1–FR-18, NFR-1–7 og SM-1–4 finnes i kartet fra krav til arkitektur. NFR-6 er bevisst utsatt til UX-steget. Føringene i addendum (FastAPI/uv, Node-frontend, lokal database) er oppfylt. Ingen stille krav falt ut. To uklarheter i PRD-en ble funnet og avgjort av brukeren (byggenummer og varevalg i MPS-linjer, «Før u1» som celler i FR-17). De er ført tilbake i PRD-en.

## 3. Versjonssjekk

Alle versjoner i Stack ble hentet fra npm og PyPI samme dag (se memlog). Én risiko: Vite-malen `react-ts` kan sette en annen TypeScript-versjon enn siste (7.0.2). Bekreftet etterpå: `create-vite` 9.3.4 setter `typescript ~7.0.2` i `react-ts`-malen.

## 4. Kritisk gjennomgang (to enheter som følger alle AD-er, men likevel ikke passer sammen)

| # | Hull | Rettet i |
| --- | --- | --- |
| 1 | «Databasen er tom» var udefinert. Én enhet kunne sjekke brukertabellen, en annen varetabellen. Etter tilbakestilling (bruker beholdt) ville det gitt ulik oppførsel | AD-5: varetabell og demobruker sjekkes hver for seg |
| 2 | Formen på endringene (FR-17) var udefinert, så API og frontend kunne velge ulik struktur. «Før u1» manglet nøkkel | AD-6: fast struktur, uke 0 = «Før u1» |
| 3 | Det var ikke bestemt hvem som lager meldingstekst, så backend og frontend kunne begge gjøre det | Konvensjon: frontend lager meldingstekst, backend bare valideringsmeldinger |
| 4 | MPS-linjer og åpne ordre har ingen id i fasiten. Endring og sletting (FR-5, FR-7) kunne fått ulike nøkler | Konvensjon: heltalls-id fra databasen |
| 5 | LLC i BOM-treet (FR-4) kunne blitt beregnet i frontend | AD-7: frontend beregner aldri LLC |
| 6 | Visningsfelt ved siden av fasitfeltene var åpne («navn, enhet, …») | AD-2: fast liste `name`, `unit`, `on_hand` |

## 5. Sjekkliste for god arkitektur

- Delepunktene for stories er låst (resultatform, identitet, skriving, innlogging, konfigurasjon, testdata). OK.
- Hver Rule kan håndheves, og to av dem automatisk med test (AD-1 importtest, AD-8 rutetest). OK.
- Ingenting under Utsatt kan få to enheter til å divergere: endepunktstier følger av AD-2/AD-7 og API-konvensjonen. OK.
- Drift og miljø: bare lokalt (AD-11). Øvrig drift er eksplisitt utsatt. OK.
