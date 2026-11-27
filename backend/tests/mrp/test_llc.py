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
    MrpException,
    MrpInput,
    MrpInputError,
    MrpResult,
    PastDueRelease,
    PlannedOrder,
    ScheduledReceipt,
    low_level_codes,
    result_to_dict,
    run_mrp,
)
from rbe.mrp.run import WEEK_FIELDS, _ordered

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


def test_ad2_other_horizon_gives_other_array_length(scenario_a: MrpInput) -> None:
    d = result_to_dict(run_mrp(replace(scenario_a, horizon=Horizon(1, 20))))
    for values in d["items"].values():
        for name in WEEK_FIELDS:
            assert len(values[name]) == 20, name


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
    by_id = {item.id: item for item in run_mrp(data).items}
    assert by_id["ZZZ-999"].low_level_code == 0


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
    with pytest.raises(MrpInputError, match="PLT-900 → PLT-900"):
        run_mrp(_with_bom(scenario_a, ("PLT-900", "PLT-900")))


def test_fr10_cycle_message_skips_smaller_item_below_cycle() -> None:
    items = tuple(_item(i) for i in ("A", "B", "C"))
    bom = tuple(BomLine(p, c, 1) for p, c in (("B", "C"), ("C", "B"), ("C", "A")))
    with pytest.raises(MrpInputError) as info:
        run_mrp(MrpInput(Horizon(1, 4), items, bom, (), ()))
    message = str(info.value)
    assert "B → C → B" in message
    assert "A →" not in message and "→ A" not in message


def test_fr10_low_level_codes_checks_input_directly(scenario_a: MrpInput) -> None:
    with pytest.raises(MrpInputError, match="XXX-6"):
        low_level_codes(_with_bom(scenario_a, ("SEK-110", "XXX-6")))
    with pytest.raises(MrpInputError, match=scenario_a.items[0].id):
        low_level_codes(replace(scenario_a, items=(*scenario_a.items, scenario_a.items[0])))


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


def test_ad2_exceptions_empty_until_story_2_4(scenario_a: MrpInput) -> None:
    result = run_mrp(scenario_a)
    assert result.exceptions == ()
    for item in result.items:
        assert isinstance(item.planned_orders, tuple), item.id
        for name in WEEK_FIELDS:
            assert isinstance(getattr(item, name), tuple), (item.id, name)


def _fasit_exceptions(expected: dict[str, Any]) -> list[MrpException]:
    """Meldingene i scenario A fra fasiten, bygd som kjernens typer."""
    out: list[MrpException] = []
    for raw in expected["A"]["exceptions"]:
        fields = {key: value for key, value in raw.items() if key != "type"}
        if raw["type"] == LeadTimeExceedsHorizon.type:
            out.append(LeadTimeExceedsHorizon(**fields))
        else:
            out.append(PastDueRelease(**fields))
    return out


def test_ad2_exception_dict_matches_fasit_form(expected: dict[str, Any]) -> None:
    exceptions = tuple(_fasit_exceptions(expected))
    d = result_to_dict(MrpResult(items=(), exceptions=exceptions))
    assert d["exceptions"] == expected["A"]["exceptions"]
    e1_keys = ["type", "item", "lead_time_weeks", "horizon_weeks"]
    e2_keys = [
        "type",
        "item",
        "quantity",
        "receipt_week",
        "release_week",
        "weeks_past_due",
        "earliest_receipt_week",
    ]
    assert [list(e) for e in d["exceptions"]] == [e1_keys, e2_keys, e2_keys]


def test_ad3_ordered_sorts_items_orders_and_exceptions(
    scenario_a: MrpInput, expected: dict[str, Any]
) -> None:
    fasit = _fasit_exceptions(expected)
    extra = PastDueRelease("MOT-210", 1, 4, -16, 17, 21)
    shuffled = [fasit[2], extra, fasit[1], fasit[0]]
    template = run_mrp(scenario_a).items
    orders = (PlannedOrder(16, 14, 1), PlannedOrder(12, 10, 1), PlannedOrder(5, 3, 2))
    items = [replace(item, planned_orders=orders) for item in template[::-1]]

    result = _ordered(items, shuffled)

    assert [(e.type, e.item, getattr(e, "receipt_week", None)) for e in result.exceptions] == [
        ("LEAD_TIME_EXCEEDS_HORIZON", "MOT-210", None),
        ("PAST_DUE_RELEASE", "MOT-210", 4),
        ("PAST_DUE_RELEASE", "MOT-210", 12),
        ("PAST_DUE_RELEASE", "VIN-920", 6),
    ]
    assert [item.id for item in result.items] == [item.id for item in template]
    for item in result.items:
        assert [order.receipt_week for order in item.planned_orders] == [5, 12, 16]
