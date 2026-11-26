"""FR-2, AD-4: fasitparseren leser testfartøyet direkte fra ``testdata/testfartoy-v1/input.json``.

Scenarioene A–E testes mot fasitfila. B–E skal være like A bortsett fra overstyringen.
"""

import copy
import dataclasses
import json
import shutil
from pathlib import Path
from typing import Any

import pytest

from rbe.config import BACKEND_DIR, Settings
from rbe.fixture import FixtureError, load_input
from rbe.mrp.types import BomLine, LotSizing, MpsLine, MrpInput

SRC_DIR = BACKEND_DIR / "src" / "rbe"


@pytest.fixture(scope="module")
def raw(input_path: Path) -> dict[str, Any]:
    return json.loads(input_path.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def scenario_a(input_path: Path) -> MrpInput:
    return load_input(input_path, "A")


def _write(tmp_path: Path, data: Any) -> Path:
    path = tmp_path / "mappe med mellomrom" / "input.json"
    path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    return path


def _item(data: MrpInput, item_id: str):
    return next(item for item in data.items if item.id == item_id)


# --- Scenario A -----------------------------------------------------------------------------


def test_fr2_scenario_a_counts(scenario_a: MrpInput) -> None:
    """Scenario A: horisont 16, 11 varer, 12 BOM-linjer, 2 MPS-linjer og 2 åpne ordre."""
    assert (scenario_a.horizon.first_week, scenario_a.horizon.weeks) == (1, 16)
    assert len(scenario_a.items) == 11
    assert len(scenario_a.bom) == 12
    assert [(line.week, line.hull_no) for line in scenario_a.mps] == [(12, 1), (16, 2)]
    assert len(scenario_a.scheduled_receipts) == 2
    assert _item(scenario_a, "PLT-900").lot_sizing == LotSizing(rule="FOQ", quantity=25)


def test_fr2_scenario_a_matches_fixture_exactly(scenario_a: MrpInput, raw: dict) -> None:
    """Scenario A: hvert felt i hver vare, BOM-linje, MPS-linje og åpen ordre er som i fasiten."""
    assert dataclasses.asdict(scenario_a.horizon) == raw["horizon"]
    for item, item_raw in zip(scenario_a.items, raw["items"], strict=True):
        as_dict = dataclasses.asdict(item)
        if as_dict["lot_sizing"]["quantity"] is None:
            del as_dict["lot_sizing"]["quantity"]
        assert as_dict == item_raw
    assert [dataclasses.asdict(line) for line in scenario_a.bom] == raw["bom"]
    assert [dataclasses.asdict(line) for line in scenario_a.mps] == raw["mps"]
    assert [dataclasses.asdict(r) for r in scenario_a.scheduled_receipts] == raw[
        "scheduled_receipts"
    ]


def test_fr2_collections_are_tuples(scenario_a: MrpInput) -> None:
    for collection in (
        scenario_a.items,
        scenario_a.bom,
        scenario_a.mps,
        scenario_a.scheduled_receipts,
    ):
        assert isinstance(collection, tuple)


def test_fr2_default_scenario_is_a(input_path: Path, scenario_a: MrpInput) -> None:
    assert load_input(input_path) == scenario_a


# --- Scenario B–E ---------------------------------------------------------------------------


def test_fr2_scenario_b_moves_hull_2_to_week_14(input_path: Path, scenario_a: MrpInput) -> None:
    """Scenario B: byggenr. 2 i uke 14, resten som A."""
    b = load_input(input_path, "B")
    expected_mps = (MpsLine("RBE-000", 12, 1, 1), MpsLine("RBE-000", 14, 1, 2))
    assert b.mps == expected_mps
    assert b == dataclasses.replace(scenario_a, mps=expected_mps)


def test_fr2_scenario_c_gir_220_on_hand_zero(input_path: Path, scenario_a: MrpInput) -> None:
    """Scenario C: GIR-220 har on_hand 0, resten som A."""
    c = load_input(input_path, "C")
    assert _item(scenario_a, "GIR-220").on_hand == 1
    assert _item(c, "GIR-220").on_hand == 0
    expected_items = tuple(
        dataclasses.replace(item, on_hand=0) if item.id == "GIR-220" else item
        for item in scenario_a.items
    )
    assert c == dataclasses.replace(scenario_a, items=expected_items)


def test_fr2_scenario_d_moves_hull_1_to_week_4(input_path: Path, scenario_a: MrpInput) -> None:
    """Scenario D: byggenr. 1 i uke 4, resten som A."""
    d = load_input(input_path, "D")
    expected_mps = (MpsLine("RBE-000", 4, 1, 1), MpsLine("RBE-000", 16, 1, 2))
    assert d.mps == expected_mps
    assert d == dataclasses.replace(scenario_a, mps=expected_mps)


def test_fr2_scenario_e_sek_110_qty_per_five(input_path: Path, scenario_a: MrpInput) -> None:
    """Scenario E: SKR-100 → SEK-110 har qty_per 5, resten som A."""
    e = load_input(input_path, "E")
    expected_bom = tuple(
        BomLine(line.parent, line.child, 5)
        if (line.parent, line.child) == ("SKR-100", "SEK-110")
        else line
        for line in scenario_a.bom
    )
    assert BomLine("SKR-100", "SEK-110", 4) in scenario_a.bom
    assert BomLine("SKR-100", "SEK-110", 5) in e.bom
    assert e == dataclasses.replace(scenario_a, bom=expected_bom)


def test_fr2_base_is_resolved_recursively(tmp_path: Path, raw: dict, input_path: Path) -> None:
    data = copy.deepcopy(raw)
    data["scenarios"]["F"] = {"base": "B", "override": {"on_hand": {"GIR-220": 0}}}
    f = load_input(_write(tmp_path, data), "F")
    b = load_input(input_path, "B")
    assert f.mps == b.mps
    assert _item(f, "GIR-220").on_hand == 0


def test_fr2_scenario_cycle_fails(tmp_path: Path, raw: dict) -> None:
    data = copy.deepcopy(raw)
    data["scenarios"]["F"] = {"base": "G", "override": {}}
    data["scenarios"]["G"] = {"base": "F", "override": {}}
    with pytest.raises(FixtureError, match="ring"):
        load_input(_write(tmp_path, data), "F")


def test_fr2_missing_note_defaults_to_empty(tmp_path: Path, raw: dict) -> None:
    data = copy.deepcopy(raw)
    del data["scheduled_receipts"][1]["note"]
    assert load_input(_write(tmp_path, data)).scheduled_receipts[1].note == ""


# --- Feil -----------------------------------------------------------------------------------


def test_fr2_unknown_scenario_lists_known(input_path: Path) -> None:
    with pytest.raises(FixtureError) as info:
        load_input(input_path, "X")
    message = str(info.value)
    assert "«X»" in message
    assert "A, B, C, D, E" in message


def test_fr2_missing_file_names_path(tmp_path: Path) -> None:
    missing = tmp_path / "mappe med mellomrom" / "finnes-ikke.json"
    with pytest.raises(FixtureError) as info:
        load_input(missing)
    assert str(missing) in str(info.value)


def _drop_item_name(data: dict) -> None:
    del data["items"][0]["name"]


def _drop_bom(data: dict) -> None:
    del data["bom"]


def _foq_without_quantity(data: dict) -> None:
    for item in data["items"]:
        if item["lot_sizing"]["rule"] == "FOQ":
            del item["lot_sizing"]["quantity"]


def _on_hand_unknown_item(data: dict) -> None:
    data["scenarios"]["C"]["override"]["on_hand"] = {"FINNES-IKKE": 0}


def _bom_qty_unknown_line(data: dict) -> None:
    data["scenarios"]["E"]["override"]["bom_qty"] = [
        {"parent": "SKR-100", "child": "PLT-900", "qty_per": 5}
    ]


def _mps_unknown_item(data: dict) -> None:
    data["scenarios"]["B"]["override"]["mps"][0]["item"] = "FINNES-IKKE"


def _unknown_override_key(data: dict) -> None:
    data["scenarios"]["B"]["override"]["ledetid"] = {}


def _non_int_quantity(data: dict) -> None:
    data["bom"][0]["qty_per"] = "1"


def _bool_quantity(data: dict) -> None:
    data["bom"][0]["qty_per"] = True


def _unknown_lot_rule(data: dict) -> None:
    data["items"][0]["lot_sizing"]["rule"] = "POQ"


def _unknown_source(data: dict) -> None:
    data["items"][0]["source"] = "buy"


def _foq_zero_quantity(data: dict) -> None:
    for item in data["items"]:
        if item["lot_sizing"]["rule"] == "FOQ":
            item["lot_sizing"]["quantity"] = 0


def _l4l_with_quantity(data: dict) -> None:
    data["items"][0]["lot_sizing"] = {"rule": "L4L", "quantity": 5}


def _override_without_base(data: dict) -> None:
    del data["scenarios"]["B"]["base"]


def _override_not_object(data: dict) -> None:
    data["scenarios"]["B"]["override"] = []


def _bom_qty_not_list(data: dict) -> None:
    data["scenarios"]["E"]["override"]["bom_qty"] = {"parent": "SKR-100"}


def _unknown_scenario_key(data: dict) -> None:
    data["scenarios"]["C"]["overide"] = data["scenarios"]["C"].pop("override")


@pytest.mark.parametrize(
    ("mutate", "scenario", "expected"),
    [
        (_drop_item_name, "A", "«name»"),
        (_drop_bom, "A", "«bom»"),
        (_foq_without_quantity, "A", "FOQ"),
        (_on_hand_unknown_item, "C", "FINNES-IKKE"),
        (_bom_qty_unknown_line, "E", "SKR-100 → PLT-900"),
        (_mps_unknown_item, "B", "FINNES-IKKE"),
        (_unknown_override_key, "B", "ledetid"),
        (_non_int_quantity, "A", "heltall"),
        (_bool_quantity, "A", "heltall"),
        (_unknown_lot_rule, "A", "POQ"),
        (_unknown_source, "A", "buy"),
        (_foq_zero_quantity, "A", "større enn 0"),
        (_l4l_with_quantity, "A", "L4L"),
        (_override_without_base, "B", "ingen «base»"),
        (_override_not_object, "B", "«override»"),
        (_bom_qty_not_list, "E", "«bom_qty»"),
        (_unknown_scenario_key, "C", "overide"),
    ],
)
def test_fr2_invalid_content_fails(
    tmp_path: Path, raw: dict, mutate, scenario: str, expected: str
) -> None:
    data = copy.deepcopy(raw)
    mutate(data)
    path = _write(tmp_path, data)
    with pytest.raises(FixtureError) as info:
        load_input(path, scenario)
    assert expected in str(info.value)
    assert str(path) in str(info.value)


def test_fr2_invalid_json_fails(tmp_path: Path) -> None:
    path = tmp_path / "mappe med mellomrom" / "input.json"
    path.parent.mkdir()
    path.write_text("{ ikke json", encoding="utf-8")
    with pytest.raises(FixtureError, match="ugyldig JSON") as info:
        load_input(path)
    assert str(path) in str(info.value)


def test_fr2_fixture_error_is_value_error() -> None:
    assert issubclass(FixtureError, ValueError)


# --- Sti og uforanderlighet -----------------------------------------------------------------


def test_fr2_default_settings_path_loads_scenario_a(scenario_a: MrpInput) -> None:
    """Standardstien i konfigurasjonen peker på fasiten og laster scenario A."""
    assert load_input(Settings(_env_file=None).fixture_path) == scenario_a


def test_fr2_path_with_spaces(tmp_path: Path, input_path: Path, scenario_a: MrpInput) -> None:
    target = tmp_path / "mappe med mellomrom og æøå" / "input.json"
    target.parent.mkdir()
    shutil.copyfile(input_path, target)
    assert load_input(target) == scenario_a


def test_ad2_types_are_frozen(scenario_a: MrpInput) -> None:
    with pytest.raises(dataclasses.FrozenInstanceError):
        scenario_a.items[0].on_hand = 99  # type: ignore[misc]
    with pytest.raises(dataclasses.FrozenInstanceError):
        scenario_a.horizon = None  # type: ignore[misc]


# --- Ingen kopi av fasiten i appkoden -------------------------------------------------------


def test_fr2_no_fixture_item_ids_in_src(raw: dict) -> None:
    """Varenumrene fra fasiten skal ikke stå i appkoden. Dataene leses alltid fra fila."""
    ids = [item["id"] for item in raw["items"]]
    files = list(SRC_DIR.rglob("*.py"))
    assert ids and files
    hits = {
        str(path.relative_to(SRC_DIR)): found
        for path in files
        if (found := [i for i in ids if i in path.read_text(encoding="utf-8")])
    }
    assert hits == {}
