# Epic 2 Context: Riktig MRP-beregning

<!-- Compiled from planning artifacts. Edit freely. Regenerate with compile-epic-context if planning docs change. -->

## Goal

Epicen gir den rene MRP-kjernen i `rbe.mrp`: lavnivåkoder, bruttobehov, netting, partiregler, ledetidsoffset, komponentbehov fra forfalte produksjonsordrer (R11) og exception-meldingene E1 og E2. Sensor kjører `uv run python -m pytest` i `backend/` og ser at alle felt for alle varer stemmer med den håndregnede fasiten for scenario A–E, og at en skalatest med generert BOM viser at logikken er generell. Ingen database, API eller skjermbilder hører til epicen. Epic 3 kaller kjernen fra «Kjør MRP» og lagrer resultatet uendret.

## Stories

- Story 2.1: Lavnivåkoder og resultatform
- Story 2.2: Bruttobehov, netting, partiregel og ledetidsoffset
- Story 2.3: Komponentbehov fra forfalte produksjonsordrer (R11)
- Story 2.4: Exception-meldinger E1 og E2
- Story 2.5: Skalatest med generert BOM

## Requirements & Constraints

- **Lavnivåkoder (FR-10):** LLC er det dypeste nivået en vare forekommer på, og hver vare planlegges én gang, etter alle foreldrene sine. PLT-900 står på nivå 2 og 3 og får LLC 3.
- **Bruttobehov (FR-10, R3):** nivå 0 får behov fra MPS. Andre varer får summen over foreldrene av foreldrenes planlagte frigivelser i uka × mengde per.
- **Netting og partiregel (FR-11, R2, R5–R8):** startlager gjelder ved start av uke 1, og åpne ordre kommer inn ved starten av uka og kan dekke behov samme uke. NB = max(0, BB + SS − (BL forrige uke + ÅO)), med SS = 0 i v1. L4L gir PM = NB. FOQ med kvantum Q gir minste multiplum av Q som er ≥ NB. BL = BL forrige + ÅO + PM − BB. Frigivelse = mottaksuke − ledetid.
- **Forfalte frigivelser (R9):** et forslag med frigivelsesuke < 1 beholder den beregnede uka i `planned_orders`, men kommer ikke med i `planned_order_releases`. MRP flytter aldri mottaksuka eller åpne ordre (R10).
- **R11 (FR-12):** får en produksjonsvare et forslag med frigivelsesuke < 1, legges barnas bruttobehov fra forslaget (antall × mengde per) i uke 1, i alle ledd nedover. Ingen behov går tapt (scenario D).
- **Meldinger (FR-13, FR-14):** E1 `LEAD_TIME_EXCEEDS_HORIZON` én gang per vare med bruttobehov i horisonten og ledetid > horisont, med `lead_time_weeks` og `horizon_weeks`. E2 `PAST_DUE_RELEASE` én per forslag med frigivelsesuke < 1, med `quantity`, `receipt_week`, `release_week`, `weeks_past_due` = 1 − frigivelsesuke og `earliest_receipt_week` = 1 + ledetid. Kjernen lager ingen tekst.
- **Testbar kjerne (NFR-3, SM-1):** testene leser `testdata/testfartoy-v1/input.json` og `expected.json` direkte, sammenligner hele ukesarrayer per scenario × vare × felt, og sammenligner `exceptions` som usortert mengde. Test-id-en oppgir scenario og FR-nummer.
- **Ikke skreddersydd (SM-C2):** ingen varenummer, uker eller horisont hardkodet i kjernen. Horisonten leses fra inndataene. Egenskapstester (massebalanse, ingen tapte behov, determinisme) og skalatesten (~500 varer, 10 nivåer, felles komponent på flere nivåer, fast seed, uten tidskrav) skal avsløre tilpasning.
- **Determinisme (FR-9):** to kjøringer på samme inndata gir identisk resultat.

## Technical Decisions

- **Ren kjerne (AD-1):** `rbe.mrp` importerer bare standardbiblioteket og egne moduler, uten fil-, nett-, klokke- eller tilfeldighetskall, og ikke `json`, `logging` eller `rbe.fixture`. `tests/mrp/test_core_is_pure.py` håndhever det for alle filer i pakken. Inn- og utdata er frosne dataklasser (`frozen=True, slots=True`), og samlinger er `tuple`.
- **Inndata finnes:** `MrpInput(horizon, items, bom, mps, scheduled_receipts)` med `Item`, `BomLine`, `MpsLine`, `ScheduledReceipt`, `LotSizing` og `Horizon` i `rbe/mrp/types.py`. Testene får inndata for A–E fra `rbe.fixture.load_input(path, scenario)`.
- **Resultatform (AD-2):** samme struktur og feltnavn som ett scenario i `expected.json`. Per vare: `low_level_code`, ukesarrayene `gross_requirements`, `scheduled_receipts`, `projected_on_hand`, `net_requirements`, `planned_order_receipts` og `planned_order_releases` (lengde = horisont, indeks 0 = uke 1), og `planned_orders` med `receipt_week`, `release_week` og `quantity`. I tillegg `name`, `unit` og `on_hand` (startlager). En `exceptions`-liste med fasitens `type`-koder og tallfelt. Lagret kjøring og API-svar i epic 3 bruker samme form uten å endre navn. Første planuke er alltid 1, og kjernen avviser første uke ≠ 1, MPS-linjer og åpne ordre utenfor horisonten, negativ ledetid, ukjent partiregel og FOQ uten kvantum med `MrpInputError` (AD-2, presisert i 2.2).
- **Rekkefølge (AD-3):** varer på (`low_level_code`, `id`), `planned_orders` på `receipt_week`, meldinger på (`type`, `item`, `receipt_week` der feltet finnes). Ingen tidsstempel eller hash-rekkefølge.
- **Tester (AD-10):** `uv run python -m pytest` i `backend/`. Fasittestene ligger i `tests/mrp/test_fixture_scenarios.py`, egenskapstestene i `tests/mrp/test_properties.py`, og skalatesten i `tests/mrp/test_scale.py` med generatoren i `tests/mrp/scale_generator.py`. Pytest kjører med `--import-mode=importlib`.
- **Konvensjoner:** engelske navn etter fasitens feltnavn, heltall overalt og ingen flyttall. Uker er heltall med uke 1 som første planuke. Ruff med linjelengde 100.

## Cross-Story Dependencies

- 2.1 gir lavnivåkodene, resultattypene og kjernens inngangsfunksjon. 2.2–2.4 fyller resten av feltene i den samme formen.
- 2.2 bygger på LLC-rekkefølgen fra 2.1. 2.3 (R11) endrer hvordan barnas bruttobehov regnes i 2.2. 2.4 bruker forslagene fra 2.2 og 2.3.
- 2.5 bruker hele kjernen og trenger en uavhengig LLC-beregning i testen.
- Epic 3 (3.1) kaller kjernen og lagrer resultatet som JSON. Epic 4 (BOM-treet, 4.4) henter LLC fra kjernen. Epic 5 (5.1) sammenligner to resultater i den samme formen.
