"""Lavnivåkoder, inndatasjekk og resultatform (FR-10, AD-2, AD-3), scenario A som grunnlag."""

import json
from dataclasses import FrozenInstanceError, replace
from pathlib import Path
from typing import Any

import pytest

from rbe.fixture import load_input
from rbe.mrp import (
    BomLine,
    Horizon,
    Item,
    LeadTimeExceedsHorizon,
    LotSizing,
    MpsLine,
    MrpInput,
    MrpInputError,
    MrpResult,
    PastDueRelease,
    ScheduledReceipt,
    low_level_codes,
    result_to_dict,
    run_mrp,
)

EXTRA_KEYS = {"name", "unit", "on_hand"}


@pytest.fixture(scope="module")
def scenario_a(input_path: Path) -> MrpInput:
    return load_input(input_path, "A")


def _item(item_id: str) -> Item:
    return Item(
        id=item_id,
        name=item_id,
        source="purchase",
        unit="stk",
        lead_time_weeks=1,
        on_hand=0,
        safety_stock=0,
        lot_sizing=LotSizing(rule="L4L"),
    )


def _with_bom(data: MrpInput, *lines: tuple[str, str]) -> MrpInput:
    return replace(data, bom=(*data.bom, *(BomLine(p, c, 1) for p, c in lines)))


def test_fr10_scenario_a_item_order(scenario_a: MrpInput) -> None:
    assert list(result_to_dict(run_mrp(scenario_a))["items"]) == [
        "RBE-000",
        "DEK-300",
        "MAS-200",
        "SKR-100",
        "GIR-220",
        "MOT-210",
        "SEK-110",
        "STY-310",
        "PLT-900",
        "PRF-910",
        "VIN-920",
    ]


def test_ad2_json_shape_matches_fasit(scenario_a: MrpInput, expected: dict[str, Any]) -> None:
    d = result_to_dict(run_mrp(scenario_a))
    assert set(d) == {"items", "exceptions"}
    weeks = scenario_a.horizon.weeks
    for item_id, values in d["items"].items():
        assert set(values) == set(expected["A"]["items"][item_id]) | EXTRA_KEYS, item_id
        for field, value in values.items():
            if isinstance(value, list) and field != "planned_orders":
                assert len(value) == weeks, (item_id, field)
    assert d == json.loads(json.dumps(d))


def test_ad2_result_dict_has_only_json_types(scenario_a: MrpInput) -> None:
    def walk(value: Any) -> None:
        if isinstance(value, dict):
            for key, inner in value.items():
                assert type(key) is str
                walk(inner)
        elif isinstance(value, list):
            for inner in value:
                walk(inner)
        else:
            assert type(value) in (str, int), type(value)

    walk(result_to_dict(run_mrp(scenario_a)))


def test_ad2_other_horizon_gives_shorter_arrays(scenario_a: MrpInput) -> None:
    d = result_to_dict(run_mrp(replace(scenario_a, horizon=Horizon(1, 8))))
    for values in d["items"].values():
        assert len(values["gross_requirements"]) == 8
        assert len(values["planned_order_releases"]) == 8


def test_ad2_extra_fields_come_from_input(scenario_a: MrpInput) -> None:
    d = result_to_dict(run_mrp(scenario_a))
    for item in scenario_a.items:
        values = d["items"][item.id]
        assert (values["name"], values["unit"], values["on_hand"]) == (
            item.name,
            item.unit,
            item.on_hand,
        )


def test_fr10_item_outside_bom_gets_zero(scenario_a: MrpInput) -> None:
    data = replace(scenario_a, items=(*scenario_a.items, _item("ZZZ-999")))
    assert low_level_codes(data)["ZZZ-999"] == 0
    assert run_mrp(data).items[0].low_level_code == 0


def test_fr10_deep_chain_without_recursion() -> None:
    ids = [f"V{i:05d}" for i in range(3000)]
    data = MrpInput(
        horizon=Horizon(1, 4),
        items=tuple(_item(i) for i in ids),
        bom=tuple(BomLine(p, c, 1) for p, c in zip(ids, ids[1:], strict=False)),
        mps=(),
        scheduled_receipts=(),
    )
    assert low_level_codes(data)[ids[-1]] == 2999
    assert run_mrp(data).items[-1].low_level_code == 2999


def test_fr10_cycle_names_only_cycle_items(scenario_a: MrpInput) -> None:
    with pytest.raises(MrpInputError) as info:
        run_mrp(_with_bom(scenario_a, ("PLT-900", "SEK-110")))
    message = str(info.value)
    assert "PLT-900" in message and "SEK-110" in message
    assert "PRF-910" not in message
    assert "PLT-900 → SEK-110 → PLT-900" in message


def test_fr10_self_cycle(scenario_a: MrpInput) -> None:
    with pytest.raises(MrpInputError, match="PLT-900"):
        run_mrp(_with_bom(scenario_a, ("PLT-900", "PLT-900")))


def test_fr10_cycle_message_is_fixed_and_starts_with_smallest_id() -> None:
    items = tuple(_item(i) for i in ("A", "B", "C", "D"))
    bom = (("D", "A"), ("C", "B"), ("A", "C"), ("B", "D"))
    data = MrpInput(Horizon(1, 4), items, tuple(BomLine(p, c, 1) for p, c in bom), (), ())
    reversed_data = replace(data, items=items[::-1], bom=data.bom[::-1])
    for variant in (data, reversed_data):
        with pytest.raises(MrpInputError) as info:
            run_mrp(variant)
        assert "A → C → B → D → A" in str(info.value)


@pytest.mark.parametrize(
    ("change", "named"),
    [
        (lambda d: _with_bom(d, ("XXX-1", "PLT-900")), "XXX-1"),
        (lambda d: _with_bom(d, ("SEK-110", "XXX-2")), "XXX-2"),
        (lambda d: replace(d, mps=(*d.mps, MpsLine("XXX-3", 5, 1, 9))), "XXX-3"),
        (
            lambda d: replace(
                d, scheduled_receipts=(*d.scheduled_receipts, ScheduledReceipt("XXX-4", 3, 1))
            ),
            "XXX-4",
        ),
    ],
    ids=["bom-parent", "bom-child", "mps", "scheduled-receipt"],
)
def test_ad2_unknown_item_is_rejected(scenario_a: MrpInput, change: Any, named: str) -> None:
    with pytest.raises(MrpInputError, match=named):
        run_mrp(change(scenario_a))


def test_ad2_unknown_item_is_found_before_cycle(scenario_a: MrpInput) -> None:
    data = _with_bom(scenario_a, ("PLT-900", "SEK-110"), ("PLT-900", "XXX-5"))
    with pytest.raises(MrpInputError, match="XXX-5"):
        run_mrp(data)


def test_ad2_duplicate_item_is_rejected(scenario_a: MrpInput) -> None:
    data = replace(scenario_a, items=(*scenario_a.items, scenario_a.items[0]))
    with pytest.raises(MrpInputError, match=scenario_a.items[0].id):
        run_mrp(data)


def test_ad2_duplicate_bom_line_is_rejected(scenario_a: MrpInput) -> None:
    line = scenario_a.bom[0]
    with pytest.raises(MrpInputError, match=line.child):
        run_mrp(replace(scenario_a, bom=(*scenario_a.bom, line)))


def test_ad2_item_result_is_frozen(scenario_a: MrpInput) -> None:
    item = run_mrp(scenario_a).items[0]
    with pytest.raises(FrozenInstanceError):
        item.low_level_code = 5  # type: ignore[misc]


def test_ad2_week_arrays_are_zero_and_lists_empty(scenario_a: MrpInput) -> None:
    result = run_mrp(scenario_a)
    assert result.exceptions == ()
    for item in result.items:
        assert item.planned_orders == ()
        assert set(item.gross_requirements) == {0}
        assert isinstance(item.gross_requirements, tuple)


def test_ad3_deterministic_and_independent_of_input_order(scenario_a: MrpInput) -> None:
    reversed_a = replace(scenario_a, items=scenario_a.items[::-1], bom=scenario_a.bom[::-1])
    first = run_mrp(scenario_a)
    assert run_mrp(scenario_a) == first
    assert run_mrp(reversed_a) == first
    assert result_to_dict(run_mrp(reversed_a)) == result_to_dict(first)


def test_ad2_exception_dict_matches_fasit_form(expected: dict[str, Any]) -> None:
    exceptions = (
        LeadTimeExceedsHorizon("MOT-210", 20, 16),
        PastDueRelease("VIN-920", 1, 6, 0, 1, 7),
    )
    d = result_to_dict(MrpResult(items=(), exceptions=exceptions))
    fasit = expected["A"]["exceptions"]
    assert d["exceptions"] == [fasit[0], fasit[2]]
    assert [list(e) for e in d["exceptions"]] == [
        ["type", "item", "lead_time_weeks", "horizon_weeks"],
        [
            "type",
            "item",
            "quantity",
            "receipt_week",
            "release_week",
            "weeks_past_due",
            "earliest_receipt_week",
        ],
    ]
