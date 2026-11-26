---
title: 'Story 1.2: Kjernens datatyper og fasitparser'
type: 'feature'
created: '2026-11-26'
status: 'done'
baseline_commit: '811d115fe2ba615fdecd6d02bc1cb9da5a85a785'
route: 'dispatch'
review_loop_iteration: 0
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-1-context.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Seed (story 1.3) og fasittestene (epic 2) trenger testfartøyets inndata som kjernens egne typer, lest direkte fra `testdata/testfartoy-v1/input.json`, slik at app og fasit ikke kan sprike (FR-2, AD-4). MRP-kjernen må dessuten holdes ren fra første linje (AD-1).

**Approach:** Opprett pakken `rbe.mrp` med frosne inndatatyper (AD-2), og `rbe.fixture` som eneste parser av fasitformatet, med scenario A–E via `override`. Legg til en `ast`-basert renhetstest for `rbe.mrp` og en testfixture med stien til fasiten.

## Boundaries & Constraints

**Always:**
- `rbe/mrp/types.py` har frosne dataklasser (`@dataclass(frozen=True, slots=True)`) med fasitens feltnavn: `LotSizing(rule, quantity)` (`rule` er `"L4L"` eller `"FOQ"`, og `quantity` er `int | None`), `Item(id, name, source, unit, lead_time_weeks, on_hand, safety_stock, lot_sizing)`, `BomLine(parent, child, qty_per)`, `MpsLine(item, week, quantity, hull_no)`, `ScheduledReceipt(item, week, quantity, note)` (`note` har standardverdien `""`), `Horizon(first_week, weeks)` og `MrpInput(horizon, items, bom, mps, scheduled_receipts)`. Samlinger er `tuple` i fasitens rekkefølge. Bare inndatatyper. Resultattypene kommer i story 2.1.
- `rbe/fixture.py` har `load_input(path: Path, scenario: str = "A") -> MrpInput` og `FixtureError(ValueError)`. Parseren tar stien som argument og leser ikke konfigurasjonen. Seed (1.3) sender `get_settings().fixture_path`.
- Regler for override (fra fasitens README): `mps` erstatter hele lista, `on_hand` (vare → antall) overstyrer de oppgitte varene, og `bom_qty` (liste med parent, child og qty_per) overstyrer mengde per på de oppgitte linjene. `base` løses rekursivt. A har ingen override.
- `FixtureError` med en norsk melding som nevner stien eller scenarioet, når: fila ikke finnes, JSON-en er ugyldig, et felt mangler, scenarioet er ukjent (meldingen lister de kjente), en override peker på en vare eller BOM-linje som ikke finnes, eller FOQ mangler `quantity`.
- `rbe.mrp` importerer bare standardbiblioteket og `rbe.mrp` selv (også relativt). Disse er forbudt, også om de er i standardbiblioteket: `rbe.db`, `rbe.api`, `rbe.fixture`, `rbe.config`, `fastapi`, `sqlalchemy`, `pydantic`, `pydantic_settings`, `os`, `pathlib`, `io`, `sys`, `socket`, `http`, `urllib`, `subprocess`, `shutil`, `tempfile`, `sqlite3`, `time`, `datetime`, `random`, `logging` og `json`. Kallene `open`, `print` og `input` er også forbudt.
- Testfunksjoner har kravnummeret i navnet, for eksempel `test_fr2_scenario_a_counts` og `test_ad1_core_is_pure`.

**Never:**
- Ingen kopi av innholdet i `input.json` i `src/` (ingen varenummer eller tall fra fasiten i appkoden).
- Ingen database, seed eller MRP-beregning. Ingen nye avhengigheter i `pyproject.toml`.
- Ikke endre `testdata/`.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| A | `input.json`, `"A"` | Horisont (1, 16), 11 varer, 12 BOM-linjer, 2 MPS-linjer (uke 12 og 16), 2 åpne ordre, PLT-900 med FOQ 25 | – |
| B | `"B"` | Byggenr. 2 i uke 14, resten som A | – |
| C | `"C"` | GIR-220 har `on_hand` 0, resten som A | – |
| D | `"D"` | Byggenr. 1 i uke 4, resten som A | – |
| E | `"E"` | SKR-100 → SEK-110 har `qty_per` 5, resten som A | – |
| Ukjent scenario | `"X"` | – | `FixtureError` som lister A–E |
| Fila finnes ikke | Sti til en fil som ikke finnes | – | `FixtureError` med stien |
| Ugyldig innhold | Midlertidig fil med ugyldig JSON, manglende felt, override til ukjent vare eller linje, eller FOQ uten `quantity` | – | `FixtureError` |
| Standardsti | `Settings(_env_file=None).fixture_path`, repoet i en sti med mellomrom | Laster scenario A | – |
| Uforanderlig | Tilordning til et felt | – | `FrozenInstanceError` |

</frozen-after-approval>

## Code Map

- `backend/src/rbe/config.py` -- `REPO_DIR` og `Settings.fixture_path` (standard `REPO_DIR/testdata/testfartoy-v1/input.json`) finnes fra 1.1. Gjenbrukes i testen av standardstien. Skal ikke endres.
- `backend/tests/conftest.py` -- autouse-fixturen `clean_env` fra 1.1. Utvides med fixturen for fasitstien. Fixturen `clean_env` skal ikke endres.
- `backend/tests/test_config.py` -- har `_env_access` (`ast`-mønster) fra 1.1. Kan brukes som forbilde, men skal ikke importeres inn i den nye testen.
- `testdata/testfartoy-v1/input.json` og `README.md` -- formatet og reglene for override. Skal leses, ikke endres.

## Tasks & Acceptance

**Execution:**
- [x] `backend/src/rbe/mrp/__init__.py` og `backend/src/rbe/mrp/types.py` -- inndatatypene over -- AD-1, AD-2
- [x] `backend/src/rbe/fixture.py` -- `FixtureError` og `load_input` med override og feilene over -- AD-4
- [x] `backend/tests/conftest.py` -- session-fixturen `fixture_dir` (`Path(__file__).resolve().parents[2] / "testdata" / "testfartoy-v1"`) og `input_path` (`fixture_dir / "input.json"`) -- AD-4
- [x] `backend/tests/test_fixture.py` -- alle radene i I/O-matrisen, pluss en test som skanner `src/rbe` for varenumrene i fasiten (`RBE-000`, `PLT-900` osv., lest fra `input.json`) og forventer null treff -- FR-2, AD-4
- [x] `backend/tests/mrp/test_core_is_pure.py` -- `ast`-sjekk av alle `.py` i `src/rbe/mrp` (lista er ikke tom). Selvtest på tekstbiter: en tillatt (`from dataclasses import dataclass`, `from .types import Item`, `from rbe.mrp.types import Item`) og en forbudt for hver kategori (`import sqlalchemy`, `from rbe.db import x`, `import pathlib`, `from datetime import date`, `open("f")`) -- AD-1
- [x] Prøv vakten: legg inn `import pathlib` i `rbe/mrp/types.py` midlertidig, se at testen feiler, og fjern linjen. Før det i Implementation Notes -- AD-1
- [x] `docs/ai-log.md` -- oppføring for story 1.2

**Commit-plan:** (1) datatyper og renhetstest (AD-1, AD-2), (2) fasitparser med tester (FR-2, AD-4), (3) AI-logg.

**Acceptance Criteria:**
- Given `backend/`, when testene, `ruff check` og `ruff format --check` kjøres, then består alt med 0 funn.
- Given `src/rbe/mrp/`, when en modul importerer noe forbudt, then feiler `test_ad1_core_is_pure` med modulnavnet og importen.

## Implementation Notes

- **Vakten er prøvd (AD-1):** `import pathlib` ble lagt inn midlertidig etter `from dataclasses import dataclass` i `rbe/mrp/types.py`. `test_ad1_core_is_pure` feilet med `MRP-kjernen er ikke ren: {'rbe.mrp.types': ['import pathlib (forbudt)']}`. Linjen ble fjernet, og testen besto igjen. Den midlertidige endringen ble aldri committet.
- **Renhetstesten** godtar standardbiblioteket (`sys.stdlib_module_names`) minus de forbudte modulene, og `rbe.mrp` både absolutt og relativt. Relative importer løses mot pakken fila ligger i, så `from .. import config` fra `rbe.mrp` blir `rbe.config` og avvises. Alt annet under `rbe` og alle tredjepartspakker avvises.
- **Utover specen, men innenfor intensjonen:** parseren avviser også ukjente nøkler i `override`, MPS i en override for en vare som ikke finnes, felt som har feil type (heltall, tekst), ukjent `rule` eller `source`, FOQ med `quantity` ≤ 0, `override` uten `base`, og scenarioer som peker på hverandre i ring. Alle gir `FixtureError` med stien.
- **Tester:** 27 nye i `test_fixture.py` (alle radene i I/O-matrisen, rekursiv `base`, ring, standardverdien for `note`, og at ingen varenummer fra fasiten står i `src/rbe`) og 23 i `tests/mrp/test_core_is_pure.py` (selvtester for tillatte og forbudte tekstbiter, og selve sjekken).

- **Etter gjennomgangen (`2329d35`):**
  - Parseren avviser også ukjente nøkler på scenarionivå (bare `description`, `base` og `override` er lov) og L4L med `quantity`.
  - `source` og `rule` er typet som `Source` og `LotRule`.
  - Renhetsvakten forbyr også `builtins`, `importlib` og en del stdlib-moduler med I/O (blant andre `glob`, `pickle`, `ssl`, `asyncio`, `threading`, `uuid`, `secrets` og `calendar`), og kallene `__import__`, `eval`, `exec`, `compile` og `breakpoint`.
  - 78 tester består.

## Spec Change Log

## Review Triage Log

Runde 1 (2026-11-26, lagene blind-hunter (BH), edge-case-hunter (ECH) og verification-gap (VG)). Rute: patch (P) eller avvist (A).

| # | Lag | Funn | Vurdering | Begrunnelse | Rute |
|---|---|---|---|---|---|
| 1 | VG, BH | Avvisning av ukjent `rule` eller `source`, FOQ med `quantity` ≤ 0, `override` uten `base`, `bool` som heltall, og `bom_qty` eller `override` som har feil type, testes ikke | medium | Ingen mutasjon i `test_fr2_invalid_content_fails` treffer disse grenene. Valideringen kan fjernes, og alle testene består likevel | P |
| 2 | BH, ECH | Ukjente nøkler på scenarionivå (for eksempel `overide`) ignoreres | medium | `_resolve` leser bare `base` og `override`, så et feilskrevet scenario blir en kopi av A uten feilmelding | P |
| 3 | BH, ECH, VG | Renhetsvakten slipper gjennom `builtins`, `importlib`, `__import__`, `eval`, `exec`, `compile` og andre stdlib-moduler med I/O | medium | Svartelisten mangler disse, og `builtins.open()` fanges ikke. Retting: utvid listene. Et bytte til hviteliste avvises, fordi specen har valgt svarteliste | P |
| 4 | ECH, BH | L4L med `quantity` godtas | low | Fasiten har ingen slik vare, men et skrivefeil (L4L i stedet for FOQ) ville gått gjennom stille. Retting: én feil | P |
| 5 | BH | `_Reader.choice` gir tilbake `Any`, ikke `Literal` | low | `Literal`-typene i `types.py` får ingen effekt for typesjekk. Retting: `cast` | P |
| 6 | BH | Docstringen i `test_fr2_default_settings_path_loads_scenario_a` hevder at testen dekker mellomrom | low | Det stemmer bare på denne maskinen. Mellomrom dekkes av `test_fr2_path_with_spaces` | P |
| 7 | BH, ECH | Grunndataene sjekkes ikke for referanser, duplikater, BOM-sykler eller verdiområder (negative verdier, uker utenfor horisonten) | low | Fasiten endres bare bevisst og kontrolleres av fasittestene. Valideringen av brukerdata hører til API-et (AD-7), og sykelsjekken til kjernen (story 2.1). Rettingen ville lagt mange vakter til parseren | A |
| 8 | ECH | Samme linje står to ganger i `bom_qty` | low | Usannsynlig, og rettingen legger til en vakt | A |
| 9 | ECH | `RecursionError` ved dypt nøstet JSON | false | Fasitfila er flat. Ikke en realistisk inngang | A |
| 10 | BH | `MrpInput` mangler scenariobeskrivelse og fasitnavn | false | Ikke krevd. Kjernetypene skal bare ha det beregningen trenger | A |
| 11 | BH | Stiene utledes på tre måter | false | Det er med vilje: AD-4 sier at testene finner fasiten via `conftest.py`, uavhengig av appens konfigurasjon. `test_fr2_default_settings_path_loads_scenario_a` fanger sprik | A |
| 12 | BH | Specen er ikke med i diffen, og AI-loggen mangler eksempler på brukerstyring | false | Specen committes av orkestratoren ved avslutningen. Brukeren rettet ingen KI-forslag i denne storyen | A |

## Verification

**Commands:**
- `uv run pytest` (i `backend/`) -- expected: alle tester består. **På denne maskinen:** Windows sperrer konsollskript som uv lager (os error 5), så bruk `uv run python -m pytest`. `backend/.venv` er allerede laget med Pythons egen `venv` (se Implementation Notes i spec 1.1)
- `uv run ruff check` og `uv run ruff format --check` (i `backend/`) -- expected: 0 funn
