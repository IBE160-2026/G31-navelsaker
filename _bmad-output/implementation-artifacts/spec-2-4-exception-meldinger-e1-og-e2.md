---
title: 'Story 2.4: Exception-meldinger E1 og E2'
type: 'feature'
created: '2026-11-27'
baseline_commit: 'b7f2e00c3e05e9be3a17cd855c12ab592875d245'
status: 'done'
route: 'dispatch'
review_loop_iteration: 0
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-2-context.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Kjernen gir alltid en tom `exceptions`-liste. Planleggeren får derfor ikke vite at MOT-210 har lengre ledetid enn horisonten, eller at forslag skulle vært frigitt før uke 1 (FR-13, FR-14). Fasiten har 3–10 meldinger per scenario som ingen test sjekker.

**Approach:** Lag E1 og E2 fra planene i kjernen, sorter dem med en eksplisitt nøkkel per type, og sammenlign dem med `expected.json` som usortert mengde per scenario. Ta samtidig med de to vedtakene fra gjennomgangen av 2.3 som gjelder testene: alle avvik i én assert i «ingen behov går tapt», og en krok som får kjøringen til å feile når en test står som skipped.

## Boundaries & Constraints

**Always:**
- **E1 (FR-13):** én `LeadTimeExceedsHorizon` per vare med `sum(gross_requirements) > 0` og `lead_time_weeks > horizon.weeks`. Ledetid lik horisonten gir ingen E1.
- **E2 (FR-14):** én `PastDueRelease` per forslag i `planned_orders` med `release_week < 1`, for alle varer uansett `source`: `quantity`, `receipt_week`, `release_week`, `weeks_past_due = 1 − release_week`, `earliest_receipt_week = 1 + lead_time_weeks`.
- Meldingene lages i en ny modul `rbe/mrp/exceptions.py` (`find_exceptions(data, plans)`), og `run_mrp` sender dem til `_ordered`. Ingen tekst i kjernen (AD-2).
- **Sorteringsnøkkel per type (AD-3):** `_ordered` bruker en funksjon med `match` på klassen: E1 gir (`type`, `item`, 0) og E2 (`type`, `item`, `receipt_week`). En ukjent type gir `TypeError`, ikke en stille standardverdi. `getattr(e, "receipt_week", 0)` fjernes.
- **Fasittest i `test_fixture_scenarios.py`:** per scenario A–E og per type, sammenlign meldingene fra `result_to_dict` med `expected.json` som multimengde (`Counter` over meldingene som sorterte nøkkel/verdi-par). Id-er `A-FR-13-meldinger` (E1) og `A-FR-14-meldinger` (E2), 10 tilfeller. Feilmeldingen viser hva som mangler og hva som er for mye.
- **Enhetstester i `test_llc.py`:** scenario A gir nøyaktig E1 for MOT-210 (20, 16), E2 for MOT-210 (1, u12, u−8, 9, u21) og E2 for VIN-920 (FR-13, FR-14). A med tom MPS (`replace(data, mps=())`) gir ingen meldinger. Ukjent meldingstype i `_ordered` gir `TypeError`. `test_ad2_exceptions_empty_until_story_2_4` erstattes, men tuple-sjekkene i den beholdes i en egen test (`test_ad2_result_collections_are_tuples`). `test_ad3_ordered_sorts_items_orders_and_exceptions` står uendret.
- **Enhetstester i `test_plan.py`** (én vare med `_item(lead_time=…)` og `_single`, horisont 16 der ikke annet står): radene for grensene i matrisen, dvs. frigivelse i nøyaktig uke 1, ledetid lik horisonten og ledetid lengre enn horisonten med og uten bruttobehov.
- **Egenskap i `test_properties.py`, A–E:** for hver E2 er `earliest_receipt_week − receipt_week = weeks_past_due` og `release_week = 1 − weeks_past_due`. Test-id `{s}-FR-14-forfalt-forsinkelse`.
- **Vedtak 1 fra 2.3:** `test_fr12_no_requirements_are_lost` samler alle varer som avviker i en dict `{vare: (faktisk, forventet)}` og har én `assert avvik == {}`.
- **Vedtak 2 fra 2.3:** kroker i `backend/tests/conftest.py` gjør alle skip og xfail til feil, med grunnen i feilmeldingen: `pytest_runtest_makereport` (wrapper) for skip i test og oppsett, og `pytest_collectreport` for skip på modulnivå. Kroken testes med `pytester` (`-p pytester` i `addopts`). Den indre kjøringen laster ikke `tests/conftest.py`, så testen kopierer den inn med `pytester.makeconftest(<sti>.read_text(encoding="utf-8"))`. Fire tilfeller: `pytest.skip`, `skipif`, `xfail` og `pytest.skip(..., allow_module_level=True)`. Hvert gir failed eller error og 0 skipped.
- Ingen varenummer, uker eller horisont fra fasiten i `src/`.
- **Vedtak (Thobias, 2026-11-27): gjennomgang før dokumentasjon.** All gjennomgang, også Thobias sin egen, er ferdig før dokumentasjonscommiten. Regelen skrives inn i commit-mønsteret i CLAUDE.md i spec-commiten. Rekkefølgen: kode, kodegjennomgang og retting, så pusher Claude branchen og oppretter PR-en, så går Thobias gjennom den (`bmad-walkthrough`) og skriver observasjonen i PR-en, og til sist kommer dokumentasjonscommiten, som Claude pusher.
- **Vedtak: lengden.** Specen er på om lag 2600 tokens, over målet på 1600. Thobias valgte å beholde den hel.

**Never:**
- Ingen meldingstekst, database, API eller frontend (epic 3). Ingen meldinger for åpne ordre (R10).
- Ikke endre `testdata/`, `rbe.fixture`, resultattypene eller beregningen i `plan.py`. Ingen nye avhengigheter.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| A–E | `load_input(input.json, s)` | `exceptions` lik fasiten som multimengde per type (3, 3, 4, 10, 3 meldinger) | – |
| D | Scenario D | 1 E1 (MOT-210) og 9 E2, blant dem MOT-210 med 20 uker forfalt | – |
| Tom MPS | A med `mps=()` | Ingen meldinger | – |
| Frigivelse i uke 1 | Én vare, LT 2, H 6, MPS 1 i uke 3 | Forslag med frigivelse i uke 1, ingen E2 | – |
| Ledetid = horisont | Én vare, LT 16, H 16, MPS 1 i uke 16 | Ingen E1, nøyaktig én E2 (1, u16, u0, 1 uke forfalt, tidligst u17) | – |
| LT > H, behov dekket av lager | Én vare, LT 20, H 16, lager 1, MPS 1 i uke 5 | 1 E1 (20, 16), ingen E2 | – |
| LT > H uten behov | Én vare, LT 20, H 16, ingen MPS | Ingen meldinger | – |
| Ukjent type | `_ordered` med et objekt som ikke er E1/E2 | – | `TypeError` |
| Skip i alle former | `pytest.skip`, `skipif`, `xfail` og skip på modulnivå under `pytester` | Hver gir failed eller error, 0 skipped | – |

</frozen-after-approval>

## Code Map

- `backend/src/rbe/mrp/run.py` -- `run_mrp` sender i dag `[]` til `_ordered`. `_ordered` har `getattr(e, "receipt_week", 0)`. Modul-docstringen sier «Meldingene er foreløpig tomme (story 2.4)».
- `backend/src/rbe/mrp/plan.py` -- `ItemPlan` har `gross_requirements` og `planned_orders`. `plan_items(data, codes)` gir `dict[vare, ItemPlan]`. Endres ikke.
- `backend/src/rbe/mrp/types.py` -- `LeadTimeExceedsHorizon`, `PastDueRelease` og `MrpException` finnes med fasitens feltnavn og `type` som `ClassVar`. `_exception_to_dict` i `run.py` gir fasitens form. Endres ikke.
- `backend/tests/mrp/test_core_is_pure.py` -- sjekker alle moduler i `rbe/mrp/`, så den nye modulen dekkes uten endring.
- `backend/tests/mrp/test_fixture_scenarios.py` -- `SCENARIOS`, `result_for`, docstringen («Story 2.4 utvider tabellen …») skrives om, fordi meldingene får en egen test.
- `backend/tests/mrp/test_llc.py` -- `test_ad2_exceptions_empty_until_story_2_4` (linje 223) erstattes, og tuple-sjekkene i den flyttes til en egen test. `_fasit_exceptions` gjenbrukes. `test_ad3_ordered_sorts_items_orders_and_exceptions` består med nøkkelen per type og endres ikke. `test_ad2_exception_dict_matches_fasit_form` sjekker allerede at meldingene bare har fasitens nøkler. `_item` her har bare `item_id` og LT 1, så testene med én vare hører hjemme i `test_plan.py`.
- `backend/tests/mrp/test_plan.py` -- hjelperne `_item(lead_time=…)` og `_single(..., weeks=…)` passer for testene med én vare.
- `backend/tests/mrp/test_properties.py` -- `test_fr12_no_requirements_are_lost` (vedtak 1).
- `backend/tests/conftest.py` -- kroken for skipped (vedtak 2). `backend/pyproject.toml` -- `addopts`.
- `testdata/testfartoy-v1/README.md` -- tabellen over exception-typer (E1, E2) og §7 og meldingene for B–D. Fasiten er autoritativ.

## Tasks & Acceptance

**Execution:**
- [x] `backend/src/rbe/mrp/exceptions.py` -- `find_exceptions` med E1 og E2 -- FR-13, FR-14
- [x] `backend/src/rbe/mrp/run.py` -- kall `find_exceptions`, eksplisitt nøkkel per type, docstring -- FR-13, FR-14, AD-3
- [x] `backend/tests/mrp/test_fixture_scenarios.py` -- fasittest for meldingene per scenario og type, docstring -- FR-13, FR-14
- [x] `backend/tests/mrp/test_llc.py` -- scenario A, tom MPS, ukjent type og tuple-sjekkene -- FR-13, FR-14, AD-2, AD-3
- [x] `backend/tests/mrp/test_plan.py` -- grensene for én vare fra matrisen -- FR-13, FR-14
- [x] `backend/tests/mrp/test_properties.py` -- alle avvik i én assert, og egenskapen for E2-feltene -- FR-12, FR-14
- [x] `backend/tests/conftest.py`, `backend/pyproject.toml` og `backend/tests/test_no_skip.py` -- skip i alle former gir feil -- SM-1
- [x] Prøv vaktene: (1) `>=` i stedet for `>` i E1, (2) `<= 1` i stedet for `< 1` i E2, (3) `earliest_receipt_week = receipt_week + 1`, (4) E1 på varer med forslag i stedet for bruttobehov, (5) `pytest.skip` i en fasittest. Se at noe feiler hver gang, tilbakestill og før tallene i Implementation Notes -- SM-C2

**Prosess:** 4–5 commits etter CLAUDE.md på `story/2.4-exception-meldinger`. Spec-commiten tar med regelen om gjennomgang før dokumentasjon i CLAUDE.md, epic-2-context.md (laget på nytt), setter 2.3 til `done` og 2.4 til `in-progress`, lukker de tre punktene for 2.3 i issues.md (gjennomgang, fletting og vedtakene), legger punktet om kjøpte foreldre med BOM for 4.1 i deferred-work.md og tar med refleksjonsnotatet og loggseksjonen for 2.3 som ikke er committet. Dokumentasjonscommiten markerer de to punktene for 2.4 i deferred-work.md som løst.

**Acceptance Criteria:**
- Given `backend/`, when `uv run python -m pytest`, `ruff check` og `ruff format --check` kjøres, then består alt med 0 funn og 0 skipped.
- Given pytest med `-v`, when meldingstestene listes, then finnes `{s}-FR-13-meldinger` og `{s}-FR-14-meldinger` for A–E.
- Given scenario A, when `result_to_dict(run_mrp(...))` gir meldingene, then har hver melding bare fasitens nøkler (`type`, `item` og tallfeltene), ingen tekst (AD-2).
- Given radene i I/O-matrisen, when enhetstestene kjøres, then har hver rad minst én test som gir utfallet i matrisen.

## Implementation Notes

- `find_exceptions` bruker `horizon.first_week` (alltid 1) i stedet for tallet 1, så ingen uke er hardkodet i kjernen.
- Kroken importerer `pytest.TestReport` og `pytest.CollectReport` fra det offentlige API-et. `pytest_collectreport` har `tryfirst=True`, ellers rekker terminalrapporten å telle skip på modulnivå som skipped før kroken endrer rapporten. For xfail fjernes `wasxfail`, så rapporten ikke vises som xfailed.
- Resultat: 645 tester består, 0 skipped. `ruff check` og `ruff format --check` gir 0 funn.
- Vaktprøver (hver tilbakestilt etterpå):
  1. `>=` i stedet for `>` i E1: 1 feiler (ledetid lik horisonten).
  2. `<= 1` i stedet for `< 1` i E2: 1 feiler (frigivelse i uke 1).
  3. `earliest_receipt_week = receipt_week + 1`: 11 feiler (fasittestene for E2 i A–E, enhetstesten for scenario A og egenskapen i A–E). Testen for ledetid lik horisonten fanger det ikke, fordi 16 + 1 = 1 + 16.
  4. E1 på varer med forslag i stedet for bruttobehov: 1 feiler (behov dekket av lager).
  5. `pytest.skip` i fasittesten for meldingene: 10 feiler (alle 10 tilfellene, ingen skipped).

## Spec Change Log

## Review Triage Log

Spec-gjennomgang før godkjenning (2026-11-27, én subagent). Den lagde E1 og E2 etter reglene i specen fra planene for A–E og fikk 0 avvik mot `expected.json` som multimengde (3, 3, 4, 10, 3). Vilkåret om bruttobehov slår aldri ut i fasiten, og fasitlista er ikke sortert etter AD-3 i C og D. 10 funn, alle rettet i specen etter Thobias sitt ja:
- Vaktprøve 2 (`<= 1`) kunne ikke slå ut, fordi ingen forslag har frigivelse i uke 1. Ny rad og test (1, high).
- Raden «Ledetid = horisont» ga én E2, ikke ingen meldinger (2, high).
- Vilkåret om bruttobehov for E1 var ikke testet. Ny rad med behov dekket av lager, og vaktprøve 4 (3, medium).
- Kroken fanget ikke `skipif` (blir error) eller skip på modulnivå. `pytest_collectreport` og fire tilfeller i testen (4, medium).
- Tuple-sjekkene i testen som erstattes, beholdes (5, medium).
- `pytester` virker med `-p pytester`. Den indre kjøringen trenger `makeconftest` (6, low). Fil per test (7), sorteringstesten uendret (8), to nye AK (9), egenskap for E2-feltene (10), alle low.

Runde 1 av kodegjennomgangen (2026-11-27, lagene blind-hunter (BH), edge-case-hunter (ECH) og verification-gap (VG), mot `b7f2e00`, uten specen i diffen). Rute: patch (P), utsatt til Thobias (U) eller avvist (A). Ingen funn var `intent_gap` eller `bad_spec`.

| # | Lag | Funn | Vurdering | Begrunnelse | Rute |
|---|---|---|---|---|---|
| 1 | VG, BH | xfail som består (XPASS) er ikke testet. En krok som bare ser på `report.skipped`, består alle fire tilfellene | medium | Grenen for `wasxfail` på en bestått rapport er uprøvd, og XPASS teller som grønt | P |
| 2 | ECH, BH | `test_fasit_exceptions` filtrerer på `kind`, så en melding med ukjent type sees ikke | low | `_ordered` gir `TypeError` for ukjente klasser, men en ny type i fasiten ville forsvunnet stille. Én assert | P |
| 3 | ECH, BH | `test_fr14_past_due_fields_agree` består uten E2 | low | Fasittestene fanger en tom liste, men egenskapen skal stå på egne ben (SM-C2). Én assert | P |
| 4 | BH | Ny regel i CLAUDE.md strider mot «Push bare når brukeren ber om det», og «rettinger inn i rettingscommiten» etter push krever force-push | medium | Begge deler stemmer. Rettingen endrer CLAUDE.md, så Thobias avgjorde den: rettes i dokumentasjonscommiten (ja til rekkefølgen i specen er bestilling om push, og rettinger etter push kommer i ny commit) | U |
| 5 | BH | CLAUDE.md-endringen er utenfor storyen og burde hatt egen commit | false | Thobias valgte spec-commiten (vedtak i specen). AI-loggen kommer i dokumentasjonscommiten | A |
| 6 | BH | `test_no_skip.py` har ingen kontroll av at vanlige tester består | false | En krok som gjorde alle tester til feil, ville felt de 645 andre testene i samme kjøring | A |
| 7 | BH | Testen for scenario A har fasitverdiene skrevet inn | low | AC 2 i epics krever nettopp disse verdiene, og fasittesten leser `expected.json`. Rekkefølgen er dekket av `test_ad3_ordered_…` | A |
| 8 | BH | Kroken erstatter tracebacken for xfail som feiler | low | xfail er forbudt, og tracebacken kommer når markøren fjernes. Å beholde den krever en gren for `longrepr` | A |
| 9 | BH | Kopien av hele conftest i `test_no_skip.py` burde vært en egen plugin | low | `makeconftest` er valgt i specen etter spec-gjennomgangen, og det virker | A |
| 10 | BH | Refleksjonsnotatet om PR #13 lenker ikke til sesjonsloggen | false | Overskriften for story 2.3 lenker til `981-…`, der seksjonen kl. 14:21 står. Merknaden er Thobias sin godkjente tekst | A |
| 11 | BH | E1 er ikke testet med behov bare fra forelder eller fra R11 | false | MOT-210 har bare avhengig behov i fasiten, og i D bare fra R11 i uke 1. Fasittestene for E1 dekker begge | A |
| 12 | BH | Assert-meldingen i «ingen behov går tapt» mangler scenarioet, og `avvik` er norsk | low | Test-id-en har scenarioet, og navnet `avvik` står i vedtaket | A |

## Design Notes

E1 og E2 sammenlignes hver for seg, så id-en kan oppgi ett FR-nummer, og en feil i E1 ikke skjuler seg i en liste med ti E2. Multimengde og ikke mengde, fordi to like E2 for samme vare og uke ellers ville telle som én. E2 lages for alle varer med forfalte forslag, også kjøpte (MOT-210, VIN-920), som i fasiten. Nøkkelen 0 for E1 holder fordi det er høyst én E1 per vare.

Kroken gjør skipped til failed i stedet for å endre sluttstatusen, så den feilende testen og grunnen står i rapporten. xfail regnes med, fordi den også skjuler en test som ikke sjekker noe.

## Verification

**Commands:**
- `uv run python -m pytest` (i `backend/`) -- expected: alle tester består, 0 skipped
- `uv run python -m ruff check` og `uv run python -m ruff format --check` (i `backend/`) -- expected: 0 funn
