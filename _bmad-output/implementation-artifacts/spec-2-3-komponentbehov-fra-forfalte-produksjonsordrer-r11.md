---
title: 'Story 2.3: Komponentbehov fra forfalte produksjonsordrer (R11)'
type: 'feature'
created: '2026-11-27'
baseline_commit: 'b61dc1177871a0e26bf55467b85e66d24e7bed57'
status: 'in-progress'
route: 'dispatch'
review_loop_iteration: 0
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-2-context.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Når en forelder får et forslag med frigivelsesuke < 1, mister barna behovet fra det forslaget. I scenario D har PLT-900 bare 30 i bruttobehov mot 66 i fasiten, så en plan som ikke rekker, gir for lite komponentbehov uten at noe sier fra (FR-12).

**Approach:** Legg barnas bruttobehov fra forfalte forslag i uke 1 (R11), slik at regelen virker i alle ledd nedover. Fjern skip-regelen for D, gi D-tilfellene FR-12 i test-id-en og legg til egenskapen «ingen behov går tapt» for A–E.

## Boundaries & Constraints

**Always:**
- **R11 i `plan_items`:** et forslag med `release_week` < 1 gir barnet `quantity` × `qty_per` i uke 1 (indeks 0). Forslag med `release_week` ≥ 1 går som før i frigivelsesuka. Barna leser fortsatt forelderens `planned_orders`. `planned_order_releases` endres ikke (R9): forfalte frigivelser står bare i `planned_orders`.
- **Gjelder alle foreldre, uansett `source`:** en vare med BOM-linjer under seg produseres. Fasiten har ingen kjøpte foreldre. Å hoppe over kjøpte foreldre ville la behov gå tapt, det FR-12 skal hindre. Dette er en bevisst utvidelse av «produksjonsvare» i R11, og den står i docstringen til `plan.py` og i Design Notes.
- **Fasittesten:** `fasit_marks` og `R11_SKIP` fjernes fra `test_fixture_scenarios.py`, og kroken for `fasit_marks` i `tests/conftest.py` fjernes, siden ingen bruker den. I stedet kan modulen ha `fasit_fr(scenario, field, fr)`, som `pytest_generate_tests` bruker til FR-nummeret, både i id-en og i `case.fr` (`case._replace(fr=...)`). For D gir den FR-12 på de sju feltene fra 2.2 (f.eks. `D-FR-12-PLT-900-gross_requirements`). `low_level_code` beholder FR-10 også i D, fordi R11 ikke påvirker LLC. 0 tester skipped.
- **«Ingen behov går tapt» i `test_properties.py`, A–E:** for hver vare er sum av `gross_requirements` = sum av varens MPS + Σ over BOM-linjene der varen er barn av Σ `quantity` i forelderens `planned_orders` × `qty_per`. MPS og BOM leses fra inndataene (`load_input`), forslagene fra resultatet. Test-id `{s}-FR-12-ingen-tapte-behov`. Massebalansen beholdes uendret. **Avvik fra AC 3 i epics:** epics sier «for hver BOM-linje» og nevner ikke MPS. Det kan ikke sjekkes per linje, fordi en vare med flere foreldre (PLT-900) har ett samlet bruttobehov, og RBE-000 har MPS og ingen foreldre. AC-en i `epics.md` skrives om til formen per vare.
- **Enhetstester i `test_plan.py`:** `_item` får en `source`-parameter. Kjede X → Y → Z (alle `make`, L4L, ledetid 2, lager 0, mengde per 2) med `MpsLine("X", 1, 1, 1)`: alle tre frigis i uke −1, Y får BB 2 og Z BB 4 i uke 1, og `planned_order_releases` er null for alle tre. Blandet forelder P → C (P `make`, L4L, ledetid 1, mengde per 2): MPS 1 i uke 1 og 1 i uke 4 gir P frigivelser i uke 0 og 3, og C får BB 2 i uke 1 og 2 i uke 3. MPS 1 i uke 1 og 1 i uke 2 gir frigivelser i uke 0 og 1, og C får BB 4 i uke 1 (forfalt og gyldig summeres).
- Ingen varenummer, uker eller horisont fra fasiten i `src/`.

**Never:**
- Ingen meldinger E1/E2 (2.4). Ingen database, API eller frontend.
- Ikke endre `testdata/`, `rbe.fixture` eller resultattypene. Ingen nye avhengigheter.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| D (AC i epics) | `load_input(input.json, "D")` | Alle felt for alle varer lik `expected.json` for D, id-er med D og FR-12 | – |
| D, PLT-900 | Scenario D | Sum av BB 66 (18 + 4 + 8 = 30 i uke 1 for byggenr. 1), som i A | – |
| A, B, C, E | Uendret | Fasittilfellene består som før | – |
| Kjede i tre ledd | X → Y → Z, MPS 1 i uke 1, LT 2, mengde per 2 | Alle frigis i uke −1. Y: BB 2 i uke 1. Z: BB 4 i uke 1. `planned_order_releases` er null for alle tre | – |
| Blandet forelder | P (LT 1) → C (mengde per 2), MPS 1 i uke 1 og 4 | P frigis i uke 0 og 3. C: BB 2 i uke 1 og 2 i uke 3 | – |
| Forfalt og gyldig i uke 1 | Som over, MPS 1 i uke 1 og 2 | P frigis i uke 0 og 1. C: BB 4 i uke 1 | – |
| Ingen tapte behov | A–E | Sum av BB = MPS + Σ foreldrenes forslag × mengde per, for hver vare | – |

</frozen-after-approval>

## Code Map

- `backend/src/rbe/mrp/plan.py` -- `plan_items`, løkka over `lines_by_child` (vakten `if order.release_week >= 1`). R11 er én linje her: uka blir `max(order.release_week, 1)`. Docstringen i modulen og punktet om bruttobehov (R3) får R11. `_plan_item` og `_lot_size` endres ikke.
- `backend/src/rbe/mrp/run.py` -- docstringen til `run_mrp` sier «R11 kommer i 2.3». Skriv om.
- `backend/tests/conftest.py` -- `pytest_generate_tests` (henter `fasit_marks` med `getattr`). Bytt til en valgfri `fasit_fr`, og oppdater både modul-docstringen og docstringen til funksjonen. Bare `test_fixture_scenarios.py` bruker `fasit_case`. `docs/ai-log.md` nevner `fasit_marks` som historikk og endres ikke.
- `backend/tests/mrp/test_fixture_scenarios.py` -- `FIELD_FR`, `R11_SKIP`, `fasit_marks`, modul-docstringen («Story 2.3–2.4 utvider …»).
- `backend/tests/mrp/test_properties.py` -- modul-docstringen (få med FR-12) og docstringen til `test_fr11_mass_balance_per_item` (viser til 2.3) oppdateres. Ny test for «ingen behov går tapt» ved siden av. `input_path`-fixturen finnes i `tests/conftest.py`.
- `backend/tests/mrp/test_plan.py` -- hjelperne `_item` (lager `source="purchase"`) og `_single` (én vare uten BOM). Kjedetestene trenger egen `MrpInput` med `BomLine(parent, child, qty_per)`. `MpsLine` tar `hull_no` som fjerde argument.
- `_bmad-output/planning-artifacts/epics.md` -- AC 3 i story 2.3 («for hver BOM-linje»).
- `testdata/testfartoy-v1/README.md` §10 -- gangen i D og kontrollen av R11 (PLT-900 66, PRF-910 70). Fasiten er autoritativ.

## Tasks & Acceptance

**Execution:**
- [ ] `backend/src/rbe/mrp/plan.py` -- R11: forfalte forslag gir barna behov i uke 1, med docstring om at det gjelder alle foreldre -- FR-12
- [ ] `backend/src/rbe/mrp/run.py` -- docstringen til `run_mrp` får R11 -- FR-12
- [ ] `backend/tests/conftest.py` -- erstatt kroken `fasit_marks` med `fasit_fr` -- AD-10
- [ ] `backend/tests/mrp/test_fixture_scenarios.py` -- fjern skip, FR-12 for D -- FR-12
- [ ] `backend/tests/mrp/test_properties.py` -- «ingen behov går tapt» for A–E, docstringene -- FR-12, SM-C2
- [ ] `backend/tests/mrp/test_plan.py` -- `source` i `_item`, kjede i tre ledd og blandet forelder (to tilfeller) -- FR-12
- [ ] `_bmad-output/planning-artifacts/epics.md` -- AC 3 i story 2.3 per vare, med MPS -- sporbarhet
- [ ] Prøv vakten: sett tilbake `if order.release_week >= 1`, se at D-tilfellene (spec-gjennomgangen regnet 36 av 77), egenskapen for D (PLT-900 30 mot 66, PRF-910 30 mot 70) og kjedetestene feiler, tilbakestill og før tallene i Implementation Notes -- SM-C2

**Prosess (tiltak 7–9 fra retrospektiven av epic 1):** 4–5 commits etter CLAUDE.md på branchen `story/2.3-r11-forfalte-ordre`. Spec-commiten setter også 2.2 til `done` og 2.3 til `in-progress` i sprintstatus og lukker punktet om fletting av PR #12 i issues.md. Thobias går gjennom PR-en (`bmad-walkthrough`) og skriver én egen observasjon før fletting. Claude ber om refleksjonsnotat i sluttoppsummeringen. Dokumentasjonscommiten markerer punktet for 2.3 i `deferred-work.md` som løst.

**Acceptance Criteria:**
- Given `backend/`, when `uv run python -m pytest`, `ruff check` og `ruff format --check` kjøres, then består alt med 0 funn og 0 skipped.
- Given pytest med `-v`, when fasittestene for D listes, then har de 77 tilfellene for feltene fra 2.2 id-er med `D-FR-12-`, og de 11 for `low_level_code` har `D-FR-10-`.

## Implementation Notes

## Spec Change Log

## Review Triage Log

Spec-gjennomgang før godkjenning (2026-11-27, én subagent). Den regnet R1–R11 uavhengig og fikk 0 avvik mot `expected.json` for A–E på alle felt. Egenskapen holder for A–E i fasiten, og kjeden X → Y → Z stemmer. 11 funn, alle low eller medium, rettet i specen før godkjenning:
- Egenskapen avviker fra AC 3 i epics («for hver BOM-linje», uten MPS). Avviket står nå i specen, og AC-en i epics skrives om (1, medium).
- Egenskapen gir bare signal i D og sjekker ikke uka. Står i Design Notes (2, medium).
- `fasit_fr` gjelder både id-en og `case.fr` (3). Docstringene i `conftest.py`, `run.py` og `test_properties.py` er gjort til faste oppgaver (4–6).
- `_item` får `source` (7). Blandet forelder har konkrete inndata og et tilfelle der forfalt og gyldig summeres i uke 1 (8). `MpsLine` og `BomLine` er nevnt i Code Map (9).
- Utvidelsen til alle foreldre står som bevisst avvik (10). Vaktprøven har tall som kan sjekkes (11).

## Design Notes

R11 er en endring på én linje, fordi 2.2 lot barna lese forelderens `planned_orders` i stedet for `planned_order_releases`. Egenskapen «ingen behov går tapt» er den eneste testen som fanger tapt behov mellom forelder og barn: massebalansen gjelder hver vare for seg og går opp også uten R11. Egenskapen bruker inndataene og forslagene, ikke `planned_order_releases`, så den er uavhengig av R9. I A, B, C og E har ingen forelder med barn forfalte forslag (MOT-210 i A er kjøpt og har ingen barn), så egenskapen gir bare signal i D, og den sjekker summer, ikke uka. At behovet havner i uke 1, dekkes av fasiten for D og av kjedetestene. FR-12 i id-en gjelder bare feltene R11 kan påvirke. Å gi LLC i D FR-12 ville si at testen viser noe den ikke viser.

R11 i fasiten sier «produksjonsvare». Kjernen bruker regelen på alle foreldre, fordi en kjøpt vare med barn ellers ville miste behov. Resultatet for fasiten blir det samme.

## Verification

**Commands:**
- `uv run python -m pytest` (i `backend/`) -- expected: alle tester består, 0 skipped
- `uv run python -m ruff check` og `uv run python -m ruff format --check` (i `backend/`) -- expected: 0 funn
