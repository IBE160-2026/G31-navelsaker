---
title: 'Story 2.1: Lavnivåkoder og resultatform'
type: 'feature'
created: '2026-11-27'
status: 'in-progress'
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
- [ ] `backend/src/rbe/mrp/types.py` -- resultattypene og `MrpException` -- AD-2
- [ ] `backend/src/rbe/mrp/llc.py` -- `MrpInputError`, `low_level_codes` -- FR-10
- [ ] `backend/src/rbe/mrp/run.py` -- inndatasjekk, `run_mrp` og `result_to_dict` -- AD-2, AD-3
- [ ] `backend/src/rbe/mrp/__init__.py` -- eksportene
- [ ] `backend/tests/conftest.py` -- felles fasitsti og `pytest_generate_tests` for fasittestene -- AD-4, AD-10
- [ ] `backend/tests/mrp/test_fixture_scenarios.py` -- LLC for A–E × alle varer, og varesettet per scenario -- FR-10
- [ ] `backend/tests/mrp/test_llc.py` -- resten av I/O-matrisen -- FR-10, AD-2, AD-3
- [ ] Prøv vakten: endre LLC midlertidig til korteste vei, se at PLT-900-testene feiler, og tilbakestill. Før det i Implementation Notes -- SM-C2

**Prosess (tiltak 7–9 fra retrospektiven av epic 1):** 4–5 commits etter CLAUDE.md. I tillegg kommer de to doc-commitene fra main (`cbb059c`, `5c68730`), som PR-beskrivelsen forklarer. Thobias går gjennom PR-en (`bmad-walkthrough`) og skriver én egen observasjon i PR-en før fletting. Claude ber om refleksjonsnotat i sluttoppsummeringen. Tiltak 4 er flyttet til 3.1 (deferred-work.md).

**Acceptance Criteria:**
- Given `backend/`, when `uv run python -m pytest`, `ruff check` og `ruff format --check` kjøres, then består alt med 0 funn, og alle tidligere tester består.
- Given pytest med `-v`, when fasittestene listes, then har hver id scenario, FR-10, vare og felt.

## Implementation Notes

## Spec Change Log

## Review Triage Log

Spec-gjennomgang før godkjenning (2026-11-27, én subagent). Alle funn ble rettet i specen før godkjenning: tupler i `result_to_dict` (1), nøkler og `ClassVar` for `type` (2), duplikater (3), ukjente varer i BOM, MPS og åpne ordre før sykelsjekken (4), sykelmeldingen bare med varene i sykelen (5), test av dyp kjede (6), fasitsti fra `conftest.py` etter AD-4 (7), FR-tabell og varesett i fasittesten (8), sortering på ett sted (9), rekkefølgen i dicten (10), commitantallet og prosessen ut av den frosne delen (11), retningslinje og algoritmevalg (12).

## Design Notes

Nullene i ukesarrayene er bevisste: formen er kontrakten (AD-2), og 2.2 erstatter dem. Ingen bruker resultatet før 3.1. Anbefalt LLC-metode er en topologisk gjennomgang (Kahn): barn får `max(LLC(forelder) + 1)`, og varer som står igjen, er i eller under en sykel. Søket etter sykelen til feilmeldingen startes fra hver gjenværende vare i id-rekkefølge, siden en vare under sykelen ikke fører tilbake til den.

## Verification

**Commands:**
- `uv run python -m pytest` (i `backend/`) -- expected: alle tester består
- `uv run python -m ruff check` og `uv run python -m ruff format --check` (i `backend/`) -- expected: 0 funn
