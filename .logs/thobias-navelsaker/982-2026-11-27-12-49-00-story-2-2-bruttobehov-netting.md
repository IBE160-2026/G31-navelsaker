# Story 2.2: bruttobehov, netting, partiregel og ledetidsoffset

## 2026-11-27 kl. 12:49 — Thobias Navelsaker

### Oppgave
Fortsette med story 2.2 i epic 2: bruttobehov, netting, partiregel og ledetidsoffset (FR-10, FR-11, FR-9). Før det skulle CLAUDE.md, åpne tiltak, issues.md og punktene fra spec 2.1 i deferred-work.md leses, særlig uke → indeks og `FIELD_FR`. Spec-commiten skulle sette 2.1 til done og lukke punktet om Thobias sin observasjon.

### Plan
- `bmad-build` med specen [spec-2-2-bruttobehov-netting-partiregel-og-ledetidsoffset.md](../../_bmad-output/implementation-artifacts/spec-2-2-bruttobehov-netting-partiregel-og-ledetidsoffset.md) og [epic-2-context.md](../../_bmad-output/implementation-artifacts/epic-2-context.md).
- Thobias valgte at kjernen krever første uke 1 og avviser uker utenfor horisonten. Scenario D er skipped til R11 kommer i 2.3.
- Branchen `story/2.2-bruttobehov-netting` er laget fra main etter flettingen av PR #11.
- En subagent gikk gjennom specen før godkjenning, én implementerte, og tre gikk gjennom koden.

### Resultat
- **Spec (`6989d94`):** specen, sprintstatus (2.1 `done`, 2.2 `in-progress`) og punktet om Thobias sin observasjon lukket i issues.md (observasjonen står i PR #11). Spec-gjennomgangen fant 15 svakheter, blant annet en regnefeil i sikkerhetslageret, og alle ble rettet før godkjenning.
- **Kode (`414d436`):** `rbe/mrp/plan.py` (ny), nye inndatasjekker i `llc.py`, og `run.py` bruker planen. Testene ligger i `test_fixture_scenarios.py` (alle åtte feltene), `test_plan.py` og `test_properties.py`.
- **Retting (`ab22f52`):** kodegjennomgangen gav 13 rader. Av dem ble 5 rettet: tester for åpen ordre i uke 0 og to åpne ordre i samme uke, `WEEK_FIELDS` importert, ett oppslag per vare i `run_mrp`, og en presisering i AD-2. De 8 andre er avvist med begrunnelse i specen.
- **Verifisering:** 532 tester består, og 77 er skipped (D × 11 varer × 7 felt). Ruff gir 0 funn. Vakten (forfalte frigivelser i uke 1) fikk 9 fasittilfeller og tre enhetstester til å feile.
- Fasiten skiller ikke R2 (åpen ordre samme uke) og R6 (flere FOQ-partier), så begge har egne enhetstester.
- AI-loggen har fått oppføringen «Story 2.2: bruttobehov, netting, partiregel og ledetidsoffset». `deferred-work.md` er oppdatert. Specen er `done`, og sprintstatus for 2.2 er `review`.
- Ingen skjermbilder eller video, fordi storyen ikke har brukergrensesnitt.

### Åpne punkter
- Thobias går gjennom PR-en for 2.2 (`bmad-walkthrough`) og skriver én egen observasjon før fletting (tiltak 7).
- Refleksjonsnotat for økten om story 2.2 venter på Thobias sine egne ord.

## 2026-11-27 kl. 13:05 — Thobias Navelsaker

### Oppgave
Føre inn refleksjonsnotatet for story 2.2 etter Thobias sine stikkord, skrevet bedre, og si fra om noe var feil.

### Plan
- Sammenligne stikkordene med det som faktisk skjedde i økten, og rette det som ikke stemte.

### Resultat
- Notatet er ført inn i `docs/refleksjonsnotater.md`, formulert av Claude, med stikkordene ordrett i parentes.
- Tre punkter i stikkordene ble rettet og forklart for Thobias:
  - Thobias fant uke → indeks selv, i gjennomgangen av PR #11.
  - Begge feilene i specen ble funnet av KI: vakten i Claudes egenkontroll, og sikkerhetslageret i spec-gjennomgangen.
  - Kodegjennomgangen fant to manglende tester etter at koden var skrevet.

### Åpne punkter
- Thobias går gjennom PR-en for 2.2 (`bmad-walkthrough`) og skriver én egen observasjon før fletting (står allerede i issues.md).

## 2026-11-27 kl. 13:10 — Thobias Navelsaker

### Oppgave
Pushe branchen og lage PR for story 2.2.

### Plan
- Push `story/2.2-bruttobehov-netting` og PR mot `main` med beskrivelse og en tom seksjon for Thobias sin gjennomgang.

### Resultat
- Branchen er pushet med fem commits (`6989d94`, `414d436`, `ab22f52`, `e6dabe5`, `779d1d4`).
- PR #12: https://github.com/IBE160-2026/G31-navelsaker/pull/12.

### Åpne punkter
- Thobias går gjennom PR #12 (`bmad-walkthrough`) og skriver én egen observasjon før fletting (står allerede i issues.md).

## 2026-11-27 kl. 13:30 — Thobias Navelsaker

### Oppgave
Gå gjennom PR #12 med `bmad-walkthrough`, grave i unntakene for scenario D, og rette det gjennomgangen fant.

### Plan
- Walkthrough i fire steg: orientering, gjennomgang per tema, risikosteder og graving i unntakene for D.
- Rette funnet i PR-en og føre resten for 2.3 i `deferred-work.md`.

### Resultat
- Gjennomgangen viste at begrunnelsen for å holde D utenfor massebalansetesten ikke holdt. Massebalansen gjelder hver vare for seg og går opp i D uten R11. D er tatt med i `tests/mrp/test_properties.py`, og docstringen er rettet. 533 tester består (77 skipped), og ruff gir 0 funn.
- Ingenting tvinger 2.3 til å fjerne skip-regelen. Uten R11 er summen av bruttobehov for PLT-900 i D 30, mot 66 i fasiten. Egenskapen «ingen behov går tapt», fjerning av skip-regelen og FR-12 i D-id-ene er ført i `deferred-work.md` for 2.3.
- Funnet er Thobias sin observasjon i PR #12, formulert av Claude og godkjent av Thobias.

### Åpne punkter
- Flett PR #12 (merge-commit, ikke squash) og sett 2.2 til `done` i spec-commiten for 2.3.
