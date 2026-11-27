---
title: 'Story 2.2: Bruttobehov, netting, partiregel og ledetidsoffset'
type: 'feature'
created: '2026-11-27'
status: 'ready-for-dev'
route: 'dispatch'
review_loop_iteration: 0
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-2-context.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** `run_mrp` gir bare lavnivåkoder, og alle ukesarrayer er nuller. Planleggeren trenger bruttobehov, nettobehov og bestillingsforslag per vare og uke for å vite når hver vare må bestilles eller startes (FR-10, FR-11, FR-9).

**Approach:** Planlegg varene i LLC-rekkefølge etter R2, R3 og R5–R9 i fasiten, og fyll de seks ukesarrayene og `planned_orders` i formen fra 2.1. Fasittesten utvides med feltene for A, B, C og E, og en ny `test_properties.py` sjekker massebalanse, determinisme og at horisonten leses fra inndataene.

## Boundaries & Constraints

**Always:**
- **Uke → indeks (Thobias sitt valg 2026-11-27):** kjernen krever `horizon.first_week == 1` og gir ellers `MrpInputError`. Indeks = uke − 1, og en frigivelse er forfalt når uka er < 1 (R1, R9, FR-8). Docstringen til `Horizon` sier det.
- **Uker utenfor horisonten (Thobias sitt valg 2026-11-27):** en MPS-linje eller åpen ordre med uke < 1 eller > `horizon.weeks` gir `MrpInputError` som nevner varen og uka. Sjekken ligger i `_check_input`. API-et i 4.1 avviser det samme (FR-8).
- **Andre inndatasjekker i `_check_input`:** ledetid < 0, en partiregel som ikke er L4L eller FOQ, og FOQ uten kvantum ≥ 1 gir `MrpInputError` som nevner varen. Mengde per < 1 og negative mengder i MPS og åpne ordre krasjer ikke beregningen og avvises av API-et i 4.1 (FR-8), ikke av kjernen.
- **Beregning i ny modul `rbe/mrp/plan.py`**, kalt fra `run_mrp`. Varene behandles i rekkefølgen (`low_level_code`, `id`), så alle foreldre er ferdige før barnet. BOM-linjene indekseres per barn én gang, så kjøretiden er lineær i antall linjer (dyp kjede med 3000 varer, skalatesten i 2.5).
- **Bruttobehov (R3):** sum av varens MPS-linjer per uke, pluss for hver BOM-linje der varen er barn: forelderens forslag i `planned_orders` med `release_week` ≥ 1, `quantity` × `qty_per` i frigivelsesuka. Barna leser forslagene, ikke arrayen, så 2.3 kan legge til R11 for `release_week` < 1 uten ny struktur. To MPS-linjer i samme uke summeres.
- **Netting (R2, R5, R7):** `on_hand` gjelder før uke 1. Åpne ordre summeres per uke og dekker behov samme uke. NB = max(0, BB + SS − (BL forrige + ÅO)) med varens `safety_stock`, BL = BL forrige + ÅO + PM − BB.
- **Partiregel (R6):** L4L gir PM = NB. FOQ med Q gir minste multiplum av Q som er ≥ NB.
- **Forslag (R8, R9):** ett `PlannedOrder` per uke med PM > 0, med `release_week` = mottaksuke − ledetid. Frigivelser før første planuke står bare i `planned_orders`, ikke i `planned_order_releases`. MRP flytter aldri åpne ordre (R10).
- **Fasittesten:** `FIELD_FR` utvides med `gross_requirements` (FR-10) og de fem andre feltene og `planned_orders` (FR-11). Tilfellene for scenario D på de sju nye feltene (ikke `low_level_code`) får `skip` med grunnen «R11 (FR-12) kommer i story 2.3», så de synes i utdataene: nøyaktig 77 (11 varer × 7 felt). `pytest_generate_tests` henter en valgfri modulfunksjon med `getattr(metafunc.module, "fasit_marks", None)` og lager `pytest.param(case, id=..., marks=...)` med samme id-format som før. 2.3 fjerner skip-regelen og gir D-tilfellene FR-12 i id-en (epics, story 2.3).
- **`test_properties.py`:** massebalanse per vare for A, B, C og E (on_hand + ΣÅO + ΣPM − ΣBB = BL i siste uke), determinisme (to kjøringer, og varer, BOM, MPS og åpne ordre i omvendt rekkefølge; `test_ad3_deterministic_and_independent_of_input_order` flyttes hit fra `test_llc.py` og utvides), og horisont fra inndataene. Massebalansen går nesten opp per definisjon når BL regnes med R7, så den er med for AC-en i epics. SM-C2 bæres av enhetstestene for R2 og R6 og av vakten.
- Ingen varenummer, uker eller horisont fra fasiten i `src/`.

**Never:**
- Ingen R11: barnas behov fra frigivelser før uke 1 går foreløpig tapt, og det er grunnen til at D venter (2.3). Ingen meldinger E1/E2 (2.4). Ingen database, API eller frontend.
- Ikke endre `testdata/`, `rbe.fixture` eller resultattypene. Ingen nye avhengigheter.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| A, B, C, E | `load_input(input.json, s)` | Alle seks ukesarrayer og `planned_orders` lik `expected.json` for alle varer | – |
| D | Scenario D | Fasittilfellene for 2.2-feltene står som skipped med grunnen | – |
| FOQ (AC i epics) | Scenario A, PLT-900 | NB 2 i uke 6, PM 25, `planned_orders` har mengde 25 (dekkes også av fasittesten) | – |
| Forfalt (R9) | Scenario A, MOT-210 | `planned_orders` har (12, −8, 1), og `planned_order_releases` er bare nuller | – |
| Samme uke | A med byggenr. 1 og 2 i uke 12 | BB for RBE-000 uke 12 = 2, og SKR-100 får 2 i uka RBE-000 frigis | – |
| Lengre horisont | A med `Horizon(1, 20)` | Arrayer med lengde 20. Uke 1–16 lik fasiten for A, uke 17–20 er 0, og BL holder siste verdi | – |
| Åpen ordre samme uke (R2) | Én vare, on_hand 0, ÅO 5 og BB 5 i uke 3 | NB 0 i uke 3, ingen forslag | – |
| FOQ flere partier (R6) | FOQ 25, on_hand 0, BB 60 i uke 4 | PM 75 i uke 4, BL 15 | – |
| Sikkerhetslager (R5) | Én vare, SS 2, on_hand 0, BB 3 i uke 2 | NB = PM = 2 i uke 1 og 3 i uke 2, BL = 2 fra uke 1 | – |
| Ugyldig vare | FOQ uten kvantum eller med 0, regel «POQ», eller ledetid −1 | – | `MrpInputError` som nevner varen |
| Annen første uke | A med `Horizon(2, 16)` | – | `MrpInputError` |
| Uke utenfor | MPS-linje i uke 0 eller 17, eller åpen ordre i uke 17, med horisont 16 | – | `MrpInputError` med varen og uka |

</frozen-after-approval>

## Code Map

- `backend/src/rbe/mrp/run.py` -- `run_mrp` (bygger `ItemResult` med nuller) og `_ordered` (eneste sortering, AD-3). `run_mrp` skal få arrayene og forslagene fra `plan.py`. `result_to_dict` og `WEEK_FIELDS` endres ikke.
- `backend/src/rbe/mrp/llc.py` -- `low_level_codes` og `_check_input` (kalles fra `low_level_codes`). Nye sjekker (første uke, uker utenfor horisonten, ledetid, partiregel og FOQ-kvantum) legges i `_check_input`, så `low_level_codes` og `run_mrp` får dem begge. Docstringen til `MrpInputError` utvides.
- `backend/src/rbe/mrp/types.py` -- `LotSizing(rule, quantity)`, `Item.safety_stock`, `Horizon(first_week, weeks)`, `PlannedOrder`. Bare docstringen til `Horizon` endres (første uke er alltid 1).
- `backend/src/rbe/mrp/__init__.py` -- eksportene. Ingen nye offentlige navn er nødvendige.
- `backend/tests/conftest.py` -- `fasit_cases` og `pytest_generate_tests` (linje 57–76). Legg til en valgfri modulfunksjon (f.eks. `fasit_marks(case)`) som gir marks per tilfelle, og bruk `pytest.param(..., marks=...)`.
- `backend/tests/mrp/test_fixture_scenarios.py` -- `FIELD_FR` (linje 17) utvides. Fixturen `result_for` flyttes til en ny `tests/mrp/conftest.py`, så `test_properties.py` kan bruke den (`--import-mode=importlib` gjør import mellom testmoduler skjør).
- `backend/tests/mrp/test_llc.py` -- `test_ad2_week_arrays_are_zero_and_lists_empty` blir en test av at `exceptions == ()` (til 2.4). `test_ad2_other_horizon_gives_shorter_arrays` bruker `Horizon(1, 20)`, fordi A med 8 uker har MPS i uke 12 og 16, som nå gir `MrpInputError`. `test_ad3_deterministic_and_independent_of_input_order` flyttes til `test_properties.py`. Seed, repository og `rbe.fixture` gir alle `first_week` 1, og ingen API-test kaller `run_mrp`, så de nye sjekkene bryter ikke noe annet.
- `testdata/testfartoy-v1/README.md` §1 og §5–§11 -- reglene og håndregningen. Fasiten er autoritativ.

## Tasks & Acceptance

**Execution:**
- [ ] `backend/src/rbe/mrp/plan.py` -- bruttobehov, netting, partiregel og ledetidsoffset per vare i LLC-rekkefølge -- FR-10, FR-11
- [ ] `backend/src/rbe/mrp/llc.py` -- nye inndatasjekker i `_check_input` -- FR-11, FR-8
- [ ] `backend/src/rbe/mrp/run.py` -- bruk `plan.py`, oppdater docstringen -- FR-9, AD-2
- [ ] `backend/tests/conftest.py` -- valgfri `fasit_marks` per fasittilfelle -- AD-10
- [ ] `backend/tests/mrp/conftest.py` -- `result_for` flyttet hit -- AD-10
- [ ] `backend/tests/mrp/test_fixture_scenarios.py` -- utvid `FIELD_FR`, skip for D -- FR-10, FR-11
- [ ] `backend/tests/mrp/test_properties.py` -- massebalanse, determinisme, horisont fra inndata -- FR-9, SM-C2
- [ ] `backend/tests/mrp/test_plan.py` -- resten av I/O-matrisen (FOQ, R9, samme uke, R2, FOQ flere partier, sikkerhetslager, ugyldig vare, første uke, uker utenfor horisonten) -- FR-10, FR-11
- [ ] `backend/tests/mrp/test_llc.py` -- skriv om og flytt testene som Code Map nevner
- [ ] Prøv vakten: legg midlertidig forfalte frigivelser i uke 1 i `planned_order_releases` (brudd på R9), se at fasittilfellene for MOT-210 og VIN-920 (A, B, C, E) og GIR-220 (C) og R9-testen feiler, tilbakestill og før det i Implementation Notes -- SM-C2

**Prosess (tiltak 7–9 fra retrospektiven av epic 1):** 4–5 commits etter CLAUDE.md. Spec-commiten setter også 2.1 til `done` i sprintstatus og lukker punktet om Thobias sin observasjon i issues.md (observasjonen står i PR #11). Thobias går gjennom PR-en (`bmad-walkthrough`) og skriver én egen observasjon før fletting. Claude ber om refleksjonsnotat i sluttoppsummeringen. Dokumentasjonscommiten lukker punktet om uke → indeks i `deferred-work.md` og fører inn i punktet for 4.1 at kjernen nå avviser første uke ≠ 1, uker utenfor horisonten, negativ ledetid og ukjent partiregel.

**Acceptance Criteria:**
- Given `backend/`, when `uv run python -m pytest`, `ruff check` og `ruff format --check` kjøres, then består alt med 0 funn, og nøyaktig 77 tester er skipped (D × 11 varer × 7 felt).
- Given pytest med `-v`, when fasittestene listes, then har hver id scenario, FR-10 eller FR-11, vare og felt (f.eks. `B-FR-11-PLT-900-planned_orders`).

## Implementation Notes

## Spec Change Log

## Review Triage Log

Spec-gjennomgang før godkjenning (2026-11-27, én subagent). Den regnet reglene uavhengig og fikk 0 avvik mot `expected.json` for A, B, C og E. For D avviker 36 av 77 tilfeller uten R11. 15 funn, rettet i specen før godkjenning:
- Sikkerhetslager-raden var regnet feil. R5 gir NB 2 allerede i uke 1, ikke 5 i uke 2 (1, high).
- 2.3 må også gi D FR-12 i id-en (2).
- Negativ ledetid og ukjent partiregel ga krasj eller stille L4L. De avvises nå, mens mengde per og negative mengder venter til 4.1 (3, 4).
- BOM-linjene indekseres per barn (5), og `result_for` flyttes til `tests/mrp/conftest.py` (6).
- Skip-mekanismen er presisert med `getattr`, id og 77 skipped (7). Skip er beholdt framfor `xfail`, med begrunnelse (8).
- GIR-220 (C) er med i vakten (9), og FOQ-raden er merket som AC fra epics (10).
- Determinismetesten flyttes i stedet for å dupliseres (11), og massebalansens svakhet står i specen (12).
- Omskrivingen av `test_llc.py` er konkretisert (13). `deferred-work.md` oppdateres i dokumentasjonscommiten (14).
- Barna leser forelderens `planned_orders`, så 2.3 kan legge til R11 uten ny struktur (15).

## Design Notes

Én funksjon per vare holder beregningen lesbar: bygg BB, gå uke for uke med BL, NB, PM, og lag forslagene til slutt. Forslagene legges i et oppslag per vare-id som barna leser fra. Med L4L og BB 0 blir alt null, så varer utenfor BOM-en uten MPS krever ingen særbehandling. Fasiten skiller ikke to regler: ingen vare har åpen ordre og bruttobehov i samme uke (R2), og ingen FOQ-vare har NB over 25 (R6, ett parti er alltid nok). En kjerne som bryter dem, består fasittestene, så de dekkes av egne enhetstester (samme mønster som Thobias sin observasjon om PLT-900 i PR #11). Skip for D er valgt framfor å utelate tilfellene, så sensor ser i pytest-utdataene at D venter på 2.3. `xfail(strict=False)` ble vurdert: 41 av 77 D-tilfeller stemmer allerede uten R11, men et blandet resultat av XPASS og XFAIL sier lite før R11 finnes, og skip gir et fast antall i AC-en.

## Verification

**Commands:**
- `uv run python -m pytest` (i `backend/`) -- expected: alle tester består, 77 skipped
- `uv run python -m ruff check` og `uv run python -m ruff format --check` (i `backend/`) -- expected: 0 funn
