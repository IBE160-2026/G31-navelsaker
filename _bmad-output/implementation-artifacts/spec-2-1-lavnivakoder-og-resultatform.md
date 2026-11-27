---
title: 'Story 2.1: Lavnivåkoder og resultatform'
type: 'feature'
created: '2026-11-27'
status: 'done'
baseline_commit: '69c8ea0b63376a9d831e9b4a3bc74facb1136017'
route: 'dispatch'
review_loop_iteration: 0
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-2-context.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Kjernen har bare inndatatyper. Epic 2 trenger lavnivåkodene (hver vare planlegges én gang, etter alle foreldrene sine) og én resultatform som er lik fasiten, før 2.2–2.4 kan fylle inn tallene (FR-10, AD-2, AD-3).

**Approach:** Legg til frosne resultattyper og inngangsfunksjonen `run_mrp(data) -> MrpResult` i `rbe.mrp`. Den sjekker referansene i inndataene, beregner LLC uten rekursjon, avviser sykler, og gir resten av feltene i riktig form og lengde. Fasittesten for LLC parametriseres fra `expected.json`, slik at 2.2–2.4 bare utvider den.

## Boundaries & Constraints

**Always:**
- **Typer i `rbe/mrp/types.py`** (`frozen=True, slots=True`, samlinger som `tuple`): `PlannedOrder(receipt_week, release_week, quantity)`, `LeadTimeExceedsHorizon(item, lead_time_weeks, horizon_weeks)`, `PastDueRelease(item, quantity, receipt_week, release_week, weeks_past_due, earliest_receipt_week)`, aliaset `MrpException = LeadTimeExceedsHorizon | PastDueRelease`, `ItemResult(id, name, unit, on_hand, low_level_code, gross_requirements, scheduled_receipts, projected_on_hand, net_requirements, planned_order_receipts, planned_order_releases, planned_orders)` og `MrpResult(items: tuple[ItemResult, ...], exceptions: tuple[MrpException, ...])`. Meldingskoden er `type: ClassVar[Literal[...]]` (`"LEAD_TIME_EXCEEDS_HORIZON"` og `"PAST_DUE_RELEASE"`), ikke et felt.
- **Inndatasjekk** (i `run_mrp`, før LLC): like vare-id-er, like (parent, child)-linjer, og en BOM-linje, MPS-linje eller åpen ordre mot en vare som ikke finnes, gir `MrpInputError(ValueError)` som nevner varen eller linjen.
- **LLC i `rbe/mrp/llc.py`:** `low_level_codes(data) -> dict[str, int]` = lengste vei fra en vare uten forelder. Varer utenfor BOM-en får 0. Ingen rekursjon. Sykel gir `MrpInputError` som bare nevner varene i én sykel, i fast rekkefølge med start i minste id.
- **`run_mrp`** sorterer varene på (`low_level_code`, `id`), `planned_orders` på `receipt_week` og meldingene på (`type`, `item`, `receipt_week` der feltet finnes), på ett sted. Ukesarrayene har lengde `data.horizon.weeks` og er nuller, og `planned_orders` og `exceptions` er tomme (2.2–2.4 fyller dem). Ingen tidsstempel.
- **`result_to_dict(result) -> dict`** gir formen i `expected.json` for ett scenario: `{"items": {id: {...}}, "exceptions": [...]}`, med varene satt inn i rekkefølgen (`low_level_code`, `id`). Per vare: fasitfeltene pluss `name`, `unit` og `on_hand`, uten `id` (den er nøkkelen). Per melding: `type`, `item` og tallfeltene. Bare `dict`, `list`, `str` og `int`, ingen tupler. Ingen `json`-import i kjernen.
- **Fasittest:** parameterlista bygges fra `expected.json` med en tabell fra felt til FR (`{"low_level_code": "FR-10"}`) som 2.2–2.4 utvider. Id-er på formen `A-FR-10-PLT-900-low_level_code`. Fasitstien har én kilde i `tests/conftest.py` (AD-4), som også parametriserer via `pytest_generate_tests`.
- Ingen varenummer, uker eller horisont fra fasiten i `src/` (sjekkes i gjennomgangen).

**Never:**
- Ingen netting, bruttobehov, partiregel eller meldingslogikk (2.2–2.4). Ingen database, API eller frontend.
- Ikke endre `testdata/` eller `rbe.fixture`. Ingen nye avhengigheter.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| A–E | `load_input(input.json, s)` | `low_level_code` lik `expected.json` for alle varer, PLT-900 = 3, og varesettet er likt fasiten | – |
| Rekkefølge | Scenario A | `list(d["items"])` = RBE-000, DEK-300, MAS-200, SKR-100, GIR-220, MOT-210, SEK-110, STY-310, PLT-900, PRF-910, VIN-920 | – |
| JSON-form | `d = result_to_dict(run_mrp(A))` | Nøklene per vare = fasitens + `name`, `unit`, `on_hand`; arrayer med lengde 16; `d == json.loads(json.dumps(d))` | – |
| Annen horisont | A med `Horizon(1, 8)` | Arrayer med lengde 8 | – |
| Vare uten BOM-linje | Ekstra vare | LLC 0 | – |
| Dyp kjede | Generert kjede med 3000 varer | LLC for siste vare = 2999 | – |
| Sykel | A + PLT-900 → SEK-110 | – | `MrpInputError` som nevner PLT-900 og SEK-110, ikke PRF-910 |
| Selvsykel | A + PLT-900 → PLT-900 | – | `MrpInputError` som nevner PLT-900 |
| Ukjent vare | BOM-linje (parent eller child), MPS-linje eller åpen ordre mot en vare som ikke finnes | – | `MrpInputError` med varen |
| Duplikater | To like vare-id-er, eller to like (parent, child) | – | `MrpInputError` |
| Uforanderlig | Tilordning til et `ItemResult`-felt | – | `FrozenInstanceError` |
| Determinisme | `run_mrp` to ganger, og med varer og BOM i omvendt rekkefølge | Like resultater | – |

</frozen-after-approval>

## Code Map

- `backend/src/rbe/mrp/types.py` -- inndatatypene fra 1.2. Resultattypene legges til her, og docstringen («Resultattypene kommer i story 2.1») oppdateres.
- `backend/src/rbe/mrp/__init__.py` -- eksportene. Legg til `run_mrp`, `result_to_dict`, `low_level_codes`, `MrpInputError`, `MrpException` og resultattypene.
- `backend/src/rbe/fixture.py` -- `load_input(path, scenario)` for testene. Endres ikke. Den sjekker ikke referansene i basisdataene, så sjekken i `run_mrp` er den eneste.
- `backend/tests/conftest.py` -- `fixture_dir` (linje 34) regner stien. Flytt utregningen til en modulkonstant som både fixturen og `pytest_generate_tests` bruker. Fixturene `clean_env` og `client` endres ikke.
- `backend/tests/mrp/test_core_is_pure.py` -- skanner alle filer i `rbe/mrp` automatisk, og forbyr blant annet `sys` og `json`. Endres ikke.

## Tasks & Acceptance

**Execution:**
- [x] `backend/src/rbe/mrp/types.py` -- resultattypene og `MrpException` -- AD-2
- [x] `backend/src/rbe/mrp/llc.py` -- `MrpInputError`, `low_level_codes` -- FR-10
- [x] `backend/src/rbe/mrp/run.py` -- inndatasjekk, `run_mrp` og `result_to_dict` -- AD-2, AD-3
- [x] `backend/src/rbe/mrp/__init__.py` -- eksportene
- [x] `backend/tests/conftest.py` -- felles fasitsti og `pytest_generate_tests` for fasittestene -- AD-4, AD-10
- [x] `backend/tests/mrp/test_fixture_scenarios.py` -- LLC for A–E × alle varer, og varesettet per scenario -- FR-10
- [x] `backend/tests/mrp/test_llc.py` -- resten av I/O-matrisen -- FR-10, AD-2, AD-3
- [x] Prøv vakten: endre LLC midlertidig til korteste vei, se at PLT-900-testene feiler, og tilbakestill. Før det i Implementation Notes -- SM-C2

**Prosess (tiltak 7–9 fra retrospektiven av epic 1):** 4–5 commits etter CLAUDE.md. I tillegg kommer de to doc-commitene fra main (`cbb059c`, `5c68730`), som PR-beskrivelsen forklarer. Thobias går gjennom PR-en (`bmad-walkthrough`) og skriver én egen observasjon i PR-en før fletting. Claude ber om refleksjonsnotat i sluttoppsummeringen. Tiltak 4 er flyttet til 3.1 (deferred-work.md).

**Acceptance Criteria:**
- Given `backend/`, when `uv run python -m pytest`, `ruff check` og `ruff format --check` kjøres, then består alt med 0 funn, og alle tidligere tester består.
- Given pytest med `-v`, when fasittestene listes, then har hver id scenario, FR-10, vare og felt.

## Implementation Notes

- **Vakten prøvd (SM-C2):** LLC ble midlertidig endret til korteste vei (`min` i stedet for `max` over foreldrene). Da feilet `test_fasit_field[A–E-FR-10-PLT-900-low_level_code]` (5 stk.) og `test_fr10_scenario_a_item_order`. Endringen ble tilbakestilt, og alle tester består igjen.
- **Sykelmeldingen:** varene som står igjen etter Kahn, har alle minst én forelder som også står igjen. `_find_cycle` går derfor oppover fra minste gjenværende id via minste gjenværende forelder til en vare gjentas, snur sykelen til retningen forelder → barn og starter den i minste id (f.eks. «PLT-900 → SEK-110 → PLT-900»). Det gir én sykel i fast rekkefølge uten å nevne varer under sykelen.
- **Sortering på ett sted:** `_ordered` i `run.py` sorterer varer, `planned_orders` og meldinger. Meldinger uten `receipt_week` (E1) får 0 i sorteringsnøkkelen, som bare skiller innen samme `type`.
- **`low_level_codes`** sjekker inndataene selv (`_check_input` i `llc.py`), før LLC. `run_mrp` får sjekken gjennom den, så rekkefølgen «sjekk før LLC» i specen holder. Flyttet fra `run.py` etter gjennomgangen (triage nr. 2).
- **Etter gjennomgangen (`37f552c`):** 195 tester består, og ruff gir 0 funn. Nye tester for sorteringen i `_ordered`, alle seks ukesarrayer, sykel med en vare under, selvsykelens form og `low_level_codes` kalt direkte.
- **Fasittesten:** `conftest.py` har `FIXTURE_DIR`, `expected_scenarios()` (lest én gang), fixturen `expected` og `pytest_generate_tests`, som leser `FIELD_FR` fra testmodulen og lager `fasit_case`. 2.2–2.4 utvider bare `FIELD_FR` i `test_fixture_scenarios.py`. Varesettet testes med id-er som `A-FR-10-varesett`.

## Spec Change Log

## Review Triage Log

Spec-gjennomgang før godkjenning (2026-11-27, én subagent). Alle funn ble rettet i specen før godkjenning: tupler i `result_to_dict` (1), nøkler og `ClassVar` for `type` (2), duplikater (3), ukjente varer i BOM, MPS og åpne ordre før sykelsjekken (4), sykelmeldingen bare med varene i sykelen (5), test av dyp kjede (6), fasitsti fra `conftest.py` etter AD-4 (7), FR-tabell og varesett i fasittesten (8), sortering på ett sted (9), rekkefølgen i dicten (10), commitantallet og prosessen ut av den frosne delen (11), retningslinje og algoritmevalg (12).

Runde 1 av kodegjennomgangen (2026-11-27, lagene blind-hunter (BH), edge-case-hunter (ECH) og verification-gap (VG), mot `0710d01`). Rute: patch (P) eller avvist (A). Ingen funn var `intent_gap` eller `bad_spec`.

| # | Lag | Funn | Vurdering | Begrunnelse | Rute |
|---|---|---|---|---|---|
| 1 | VG, BH | Sorteringen av meldinger og `planned_orders` i `_ordered` testes ikke. Endret eller fjernet sorteringsnøkkel består hele testsettet | medium | `run_mrp` sender alltid tomme lister, og formtesten bygger `MrpResult` direkte. Fasittestene i 2.4 sammenligner som mengde (fasitens README), så de fanger det heller ikke. Brudd på AD-3 ville gitt ulik JSON for like kjøringer | P |
| 2 | ECH, BH | `low_level_codes` er eksportert, men gir `KeyError` for en ukjent vare og slår sammen like id-er når den kalles direkte | medium | Story 4.4 henter LLC til BOM-treet fra kjernen og kan kalle funksjonen direkte. Retting: inndatasjekken flyttes inn i `low_level_codes`, uten nytt eksportert navn | P |
| 3 | ECH, BH | `test_fr10_item_outside_bom_gets_zero` sjekker `items[0]` (RBE-000) i stedet for ZZZ-999 gjennom `run_mrp` | low | Påstanden består uansett hva ZZZ-999 får. Direkte retting: slå opp på id | P |
| 4 | BH | Formtesten for meldinger hopper over fasitens melding nr. 2 (E2 for MOT-210, negativ `release_week`) og bruker skjøre indekser | low | Direkte retting, tatt sammen med nr. 1: sammenlign med hele lista | P |
| 5 | BH | Bare `gross_requirements` sjekkes for nuller og `tuple` | low | Direkte retting: løkke over `WEEK_FIELDS` | P |
| 6 | BH | Ingen test av sykelmeldingen når en vare med lavere id henger under sykelen, og selvsykelen sjekkes ikke på form | medium | Det er grunnen til at `_find_cycle` kutter stien, og ingen test viser at kuttet virker. Retting: to tester | P |
| 7 | ECH | Horisont 0 eller negativ gir tomme arrayer uten feil | low | Horisonten kommer fra fasiten og redigeres ikke av brukeren (FR-8 har ikke horisont). Rettingen legger til en vakt for en tilstand som ikke kan nås | A |
| 8 | ECH, BH | `pytest_generate_tests` gir `AttributeError` hvis `FIELD_FR` mangler, og `KeyError` ved samlingen hvis et felt mangler i fasiten | low | Bare for utviklere, og feilen nevner allerede attributtet eller feltet. Fasiten har alle feltene for alle varer. Rettingen legger til vakter | A |
| 9 | BH | `SCENARIOS` er hardkodet ved siden av scenarioene fra fasiten | low | `test_fasit_covers_all_scenarios` feiler hvis de spriker, så avviket kan ikke gå stille | A |
| 10 | BH | Feilmeldingen for ukjente varer nevner den første i inndatarekkefølgen | low | Feilen er riktig og nevner en ukjent vare. Å samle og sortere alle gir mer kode for en melding om ugyldige data | A |
| 11 | BH | Specen har `status: 'in-review'`, mens sprintstatus bruker `review` | false | Malen for specen har `in-review` som gyldig verdi, og sprintstatus har sitt eget skjema med `review`. Det er to ulike felt | A |
| 12 | VG | B–E gir ingen ny LLC-dekning utover A, fordi LLC er lik i alle scenarioene | false | Ikke en feil. BOM-strukturen er den samme i A–E, og vakten (korteste vei) fanges av PLT-900. LLC-reglene dekkes ellers av testene for kjede og sykel | A |

## Design Notes

Nullene i ukesarrayene er bevisste: formen er kontrakten (AD-2), og 2.2 erstatter dem. Ingen bruker resultatet før 3.1. Anbefalt LLC-metode er en topologisk gjennomgang (Kahn): barn får `max(LLC(forelder) + 1)`, og varer som står igjen, er i eller under en sykel. Søket etter sykelen til feilmeldingen startes fra hver gjenværende vare i id-rekkefølge, siden en vare under sykelen ikke fører tilbake til den.

## Verification

**Commands:**
- `uv run python -m pytest` (i `backend/`) -- expected: alle tester består
- `uv run python -m ruff check` og `uv run python -m ruff format --check` (i `backend/`) -- expected: 0 funn
