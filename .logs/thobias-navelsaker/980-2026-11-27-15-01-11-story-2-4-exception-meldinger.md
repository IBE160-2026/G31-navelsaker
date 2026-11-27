# Story 2.4: Exception-meldinger E1 og E2

## 2026-11-27 kl. 15:01 — Thobias Navelsaker

### Oppgave
Fortsette med story 2.4 (FR-13, FR-14): kjernen skal gi exception-meldingene E1 (ledetid lengre enn horisont) og E2 (forfalt frigivelse). Omfanget omfatter punktene for 2.4 i `deferred-work.md` fra gjennomgangen av PR #11 (egen fasittest for meldingene som usortert mengde, eksplisitt sorteringsnøkkel per type) og vedtakene fra gjennomgangen av PR #13. Thobias sin observasjon fra PR #13 skulle følges: all gjennomgang, også hans egen, er ferdig før dokumentasjonscommiten. Spec-commiten skulle sette 2.3 til done og lukke punktene om gjennomgangen og flettingen av PR #13.

### Plan
- `bmad-build`: epic-2-konteksten laget på nytt (PRD og epics var endret i 2.3), spec med gjennomgang før godkjenning, implementasjon i en subagent og kodegjennomgang med tre lag.
- Specen: [spec-2-4-exception-meldinger-e1-og-e2.md](../../_bmad-output/implementation-artifacts/spec-2-4-exception-meldinger-e1-og-e2.md).
- Ny rekkefølge: spec, kode, kodegjennomgang og retting, push og PR, Thobias sin `bmad-walkthrough` og observasjon, og til sist dokumentasjonscommiten. Branchen er `story/2.4-exception-meldinger`, PR #14.

### Resultat
- **Fra 2.3, som ikke var logget:** branchen for 2.3 ble pushet og PR #13 opprettet, og PR #13 ble flettet med merge-commit `b7f2e00`. Refleksjonsnotatet om gjennomgangen av PR #13 og loggseksjonen kl. 14:21 i [981-…-story-2-3](981-2026-11-27-13-23-32-story-2-3-r11-forfalte-ordre.md) ble committet i spec-commiten for 2.4, så det ikke ble en egen commit på `main`.
- **Spec (`f81b899`):**
  - 2.3 satt til done og 2.4 til in-progress.
  - De tre punktene for 2.3 lukket i issues.md: gjennomgangen, flettingen og vedtakene.
  - Regelen om gjennomgang før dokumentasjon skrevet inn i CLAUDE.md.
  - Avvisning av kjøpte foreldre med BOM ført for 4.1 i `deferred-work.md`.
  - Thobias valgte å beholde specen hel, selv om den er over 1600 tokens. Han spurte hvor grensen kommer fra. Den kommer fra `bmad-build` og har ingen oppgitt kilde.
- **Spec-gjennomgang:** E1 og E2 regnet etter reglene i specen ga 0 avvik mot fasiten for A–E. Gjennomgangen fant 10 svakheter, og alle ble rettet før koden. To var alvorlige:
  - En vaktprøve (`<= 1` i E2) kunne ikke slå ut.
  - Raden for ledetid lik horisonten hadde feil forventning.
- **Kode (`4e90236`, `8549abb`):**
  - `rbe/mrp/exceptions.py` med `find_exceptions`.
  - `_exception_key` per type i `run.py`.
  - Fasittest for meldingene som multimengde (10 tilfeller), grensetester, egenskap for E2-feltene og alle avvik i én assert.
  - Kroker som gjør alle skip og xfail til feil, prøvd med `pytester`.
- **Retting (`443f7ea`):** 12 rader fra kodegjennomgangen.
  - 3 rettet: XPASS-test, ukjent type i fasittesten og minst én E2 i egenskapen.
  - 1 avgjort av Thobias: CLAUDE.md-regelen strider mot push-regelen og åpnet for force-push. Den er rettet i dokumentasjonscommiten.
  - 8 avvist med begrunnelse.
- **Push og PR:** branchen pushet, og [PR #14](https://github.com/IBE160-2026/G31-navelsaker/pull/14) opprettet.
- **Thobias sin gjennomgang:** `bmad-walkthrough` av PR #14 ga ingen nye rettinger. Observasjonen står ordrett i PR-en. Thobias ba først om en oppsummering, og Claude ga fakta som stikkord, ikke ferdige setninger.
- **Verifisering:** 646 tester består, 0 er skipped, og ruff gir 0 funn. Alle fem vaktprøvene slår ut.
- **Dokumentasjon:** AI-logg, denne loggen, specen satt til `done` med triagelogg, sprintstatus `review`, de to punktene for 2.4 lukket i `deferred-work.md` og CLAUDE.md presisert (push og ingen force-push). Refleksjonsnotatet er ført ordrett i `docs/refleksjonsnotater.md`, med samme tekst som observasjonen i PR #14, slik Thobias valgte.

### Åpne punkter
- Flett PR #14 og sett 2.4 til done i spec-commiten for 2.5.
