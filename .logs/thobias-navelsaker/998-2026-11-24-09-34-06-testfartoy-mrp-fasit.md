# Testfartøy MRP-fasit

## 2026-11-24 kl. 09:34 — Thobias Navelsaker

### Oppgave
Lage et konkret testfartøy for v1 (flernivå BOM + MRP) som fasit for suksesskriteriene i briefen. Det skulle inneholde fast BOM på tre–fire nivåer med hovedmotor som importkomponent med lang ledetid, en enkel MPS, en håndregnet MRP-tabell (nettobehov, bestillingsforslag med ledetidsoffset, exception-meldinger) og etterprøvbar beregning. Format og plassering skulle velges ut fra repoets struktur. Etterpå: oppdatere AI-loggen, committe, og si fra om uklarheter i briefen.

### Plan
- Lese forrige sesjonslogg, issues.md, brief.md (Omfang, Suksesskriterier) og addendum.md.
- Velge plassering `testdata/testfartoy-v1/` i rota (data som skal leses av kode, ikke et BMAD-planleggingsdokument) og formatet README.md (håndregning) + input.json (inndata/seed) + expected.json (testorakel).
- Designe fartøyet: 11 varer, BOM nivå 0–3, felles stålplate på nivå 2 og 3 (tester LLC), lager på mellomnivå, åpne ordre, én FOQ-vare, hovedmotor med LT 20 mot horisont 16, og to byggenumre i MPS.
- Definere beregningskonvensjoner (R1–R10) og exception-typer (E1 ledetid > horisont, E2 forfalt frigivelse), som briefen ikke spesifiserer.
- Regne scenario A (basis), B (byggenr. 2 framskyndet 16 → 14) og C (GIR-220-lager 1 → 0) for hånd.
- Kryssjekke mot et uavhengig engangsskript i scratchpad (ikke committet), og gjengi tabellene i README fra expected.json.

### Resultat
- `testdata/testfartoy-v1/README.md`, `input.json` og `expected.json` opprettet. Lenker lagt til i rot-`README.md` og i Omfang-seksjonen i `brief.md`. Commit `94a6c10`.
- `docs/ai-log.md`: ny oppføring for økten. Commit `b740df3`.
- Fasitens innhold: 19 bestillingsforslag i A. Exception-meldinger i A: E1 MOT-210, E2 MOT-210 (frigivelse u−8, 9 uker forfalt) og E2 VIN-920 (u0, 1 uke). B gir MOT-210 11 uker forfalt og flytter alle ordre for byggenr. 2 to uker fram. C gir en ny E2 på GIR-220.
- Verifisering: expected.json stemmer med uavhengig beregning i alle tre scenarier, og massebalansen går opp per vare. Kontrollskriptet ble testet med en bevisst feil (fanget). Ikke pushet.
- Lukket åpent punkt fra forrige økt: «testfartøy med håndregnet MRP-tabell (fasit) er ikke laget ennå».

### Åpne punkter
- Briefens eksempel «hovedmotoren må bestilles i uke 3 fordi ledetiden er lengre enn planleggingshorisonten» (Løsningen pkt. 4) er logisk inkonsistent. Med LT > horisont havner frigivelsen før uke 1. Bør omformuleres (se fasit, Avklaringer pkt. 1).
- PRD må bekrefte eller justere fasitens antakelser: «ett testfartøy» = én fartøystype med to byggenumre, horisont 16 uker, L4L + FOQ, og tidsbøttekonvensjonene R1–R10.
- PRD må avgjøre om exception-meldinger for åpne ordre (framskynd/utsett/kanseller) hører til v1, og hvordan barn av forfalte produksjonsordrer skal behandles. Begge er udefinert i fasiten.
