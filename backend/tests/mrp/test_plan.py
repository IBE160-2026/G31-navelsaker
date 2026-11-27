"""Bruttobehov, netting, partiregel, ledetidsoffset og R11 (FR-10–FR-12) utenfor fasittabellen.

Fasiten skiller ikke alle reglene: ingen vare har åpen ordre og bruttobehov i samme uke (R2),
ingen FOQ-vare trenger mer enn ett parti (R6), og R11 vises bare i to ledd i D. Testene her
dekker dem med små inndata.
"""

from collections.abc import Callable
from dataclasses import replace
from pathlib import Path
from typing import Literal

import pytest

from rbe.fixture import load_input
from rbe.mrp import (
    BomLine,
    Horizon,
    Item,
    ItemResult,
    LotSizing,
    MpsLine,
    MrpInput,
    MrpInputError,
    PlannedOrder,
    ScheduledReceipt,
    run_mrp,
)


@pytest.fixture(scope="module")
def scenario_a(input_path: Path) -> MrpInput:
    return load_input(input_path, "A")


def _by_id(data: MrpInput) -> dict[str, ItemResult]:
    return {item.id: item for item in run_mrp(data).items}


def _item(
    item_id: str = "X-1",
    *,
    lead_time: int = 1,
    on_hand: int = 0,
    safety_stock: int = 0,
    lot_sizing: LotSizing | None = None,
    source: Literal["make", "purchase"] = "purchase",
) -> Item:
    return Item(
        id=item_id,
        name=item_id,
        source=source,
        unit="stk",
        lead_time_weeks=lead_time,
        on_hand=on_hand,
        safety_stock=safety_stock,
        lot_sizing=lot_sizing or LotSizing(rule="L4L"),
    )


def _single(
    item: Item,
    mps: tuple[tuple[int, int], ...],
    receipts: tuple[tuple[int, int], ...] = (),
    weeks: int = 6,
) -> MrpInput:
    """Én vare uten BOM, med MPS og åpne ordre som (uke, antall)."""
    return MrpInput(
        horizon=Horizon(1, weeks),
        items=(item,),
        bom=(),
        mps=tuple(MpsLine(item.id, week, qty, n) for n, (week, qty) in enumerate(mps, 1)),
        scheduled_receipts=tuple(ScheduledReceipt(item.id, week, qty) for week, qty in receipts),
    )


def test_fr11_foq_scenario_a_plt_900(scenario_a: MrpInput) -> None:
    plt = _by_id(scenario_a)["PLT-900"]
    assert plt.net_requirements[6 - 1] == 2
    assert plt.planned_order_receipts[6 - 1] == 25
    assert PlannedOrder(receipt_week=6, release_week=3, quantity=25) in plt.planned_orders


def test_fr11_r9_past_due_release_only_in_planned_orders(scenario_a: MrpInput) -> None:
    mot = _by_id(scenario_a)["MOT-210"]
    assert PlannedOrder(receipt_week=12, release_week=-8, quantity=1) in mot.planned_orders
    assert mot.planned_order_releases == (0,) * scenario_a.horizon.weeks


def test_fr10_two_mps_lines_same_week_are_summed(scenario_a: MrpInput) -> None:
    mps = tuple(replace(line, week=12) for line in scenario_a.mps)
    assert len(mps) == 2
    by_id = _by_id(replace(scenario_a, mps=mps))
    rbe = by_id["RBE-000"]
    assert rbe.gross_requirements[12 - 1] == 2
    release = 12 - 2
    assert rbe.planned_order_releases[release - 1] == 2
    assert by_id["SKR-100"].gross_requirements[release - 1] == 2


def test_fr11_r2_scheduled_receipt_covers_same_week() -> None:
    result = run_mrp(_single(_item(), mps=((3, 5),), receipts=((3, 5),))).items[0]
    assert result.net_requirements[3 - 1] == 0
    assert result.planned_orders == ()
    assert result.projected_on_hand == (0,) * 6


def test_fr11_r2_two_scheduled_receipts_same_week_are_summed() -> None:
    data = _single(_item(), mps=((3, 10),), receipts=((3, 4), (3, 6)))
    result = run_mrp(data).items[0]
    assert result.scheduled_receipts[3 - 1] == 10
    assert result.net_requirements[3 - 1] == 0
    assert result.planned_orders == ()


@pytest.mark.parametrize(
    ("need", "receipt"),
    [(60, 75), (25, 25), (26, 50), (1, 25)],
    ids=["FR-11-FOQ-60", "FR-11-FOQ-25", "FR-11-FOQ-26", "FR-11-FOQ-1"],
)
def test_fr11_r6_foq_gives_smallest_multiple(need: int, receipt: int) -> None:
    item = _item(lot_sizing=LotSizing(rule="FOQ", quantity=25))
    result = run_mrp(_single(item, mps=((4, need),))).items[0]
    assert result.net_requirements[4 - 1] == need
    assert result.planned_order_receipts[4 - 1] == receipt
    assert result.projected_on_hand[4 - 1] == receipt - need
    assert result.planned_orders == (PlannedOrder(4, 3, receipt),)


def test_fr11_r5_safety_stock() -> None:
    result = run_mrp(_single(_item(safety_stock=2), mps=((2, 3),), weeks=4)).items[0]
    assert result.net_requirements == (2, 3, 0, 0)
    assert result.planned_order_receipts == (2, 3, 0, 0)
    assert result.projected_on_hand == (2, 2, 2, 2)
    assert result.planned_orders == (PlannedOrder(1, 0, 2), PlannedOrder(2, 1, 3))
    assert result.planned_order_releases == (3, 0, 0, 0)


def test_fr11_r8_release_is_receipt_minus_lead_time() -> None:
    result = run_mrp(_single(_item(lead_time=3), mps=((5, 4),))).items[0]
    assert result.planned_orders == (PlannedOrder(5, 2, 4),)
    assert result.planned_order_releases == (0, 4, 0, 0, 0, 0)


@pytest.mark.parametrize(
    "item",
    [
        _item("FOQ-NONE", lot_sizing=LotSizing(rule="FOQ")),
        _item("FOQ-ZERO", lot_sizing=LotSizing(rule="FOQ", quantity=0)),
        _item("POQ-1", lot_sizing=LotSizing(rule="POQ")),  # type: ignore[arg-type]
        _item("LT-NEG", lead_time=-1),
    ],
    ids=["foq-uten-kvantum", "foq-0", "poq", "ledetid-negativ"],
)
def test_fr8_invalid_item_is_rejected(item: Item) -> None:
    with pytest.raises(MrpInputError, match=item.id):
        run_mrp(_single(item, mps=()))


def test_fr8_first_week_other_than_1_is_rejected(scenario_a: MrpInput) -> None:
    with pytest.raises(MrpInputError):
        run_mrp(replace(scenario_a, horizon=Horizon(2, 16)))


@pytest.mark.parametrize(
    ("change", "item", "week"),
    [
        (lambda d: replace(d, mps=(*d.mps, MpsLine("RBE-000", 0, 1, 3))), "RBE-000", 0),
        (lambda d: replace(d, mps=(*d.mps, MpsLine("RBE-000", 17, 1, 3))), "RBE-000", 17),
        (
            lambda d: replace(
                d, scheduled_receipts=(*d.scheduled_receipts, ScheduledReceipt("PRF-910", 0, 1))
            ),
            "PRF-910",
            0,
        ),
        (
            lambda d: replace(
                d, scheduled_receipts=(*d.scheduled_receipts, ScheduledReceipt("PRF-910", 17, 1))
            ),
            "PRF-910",
            17,
        ),
    ],
    ids=["mps-uke-0", "mps-uke-17", "apen-ordre-uke-0", "apen-ordre-uke-17"],
)
def test_fr8_week_outside_horizon_is_rejected(
    scenario_a: MrpInput, change: Callable[[MrpInput], MrpInput], item: str, week: int
) -> None:
    with pytest.raises(MrpInputError) as info:
        run_mrp(change(scenario_a))
    message = str(info.value)
    assert item in message
    assert f"uke {week}" in message


def _chain(
    items: tuple[Item, ...],
    bom: tuple[BomLine, ...],
    mps: tuple[MpsLine, ...],
    weeks: int = 6,
) -> dict[str, ItemResult]:
    data = MrpInput(horizon=Horizon(1, weeks), items=items, bom=bom, mps=mps, scheduled_receipts=())
    return _by_id(data)


def test_fr12_r11_past_due_in_three_levels() -> None:
    """X → Y → Z, ledetid 2 og mengde per 2: alle frigis i uke −1, og behovet går ned i uke 1."""
    items = tuple(_item(i, lead_time=2, source="make") for i in ("X", "Y", "Z"))
    bom = (BomLine("X", "Y", 2), BomLine("Y", "Z", 2))
    by_id = _chain(items, bom, (MpsLine("X", 1, 1, 1),))
    assert by_id["X"].planned_orders == (PlannedOrder(1, -1, 1),)
    assert by_id["Y"].planned_orders == (PlannedOrder(1, -1, 2),)
    assert by_id["Z"].planned_orders == (PlannedOrder(1, -1, 4),)
    assert by_id["Y"].gross_requirements == (2, 0, 0, 0, 0, 0)
    assert by_id["Z"].gross_requirements == (4, 0, 0, 0, 0, 0)
    for item_id in ("X", "Y", "Z"):
        assert by_id[item_id].planned_order_releases == (0,) * 6, item_id


@pytest.mark.parametrize(
    ("mps_weeks", "releases", "child_gross"),
    [
        ((1, 4), (0, 3), (2, 0, 2, 0, 0, 0)),
        ((1, 2), (0, 1), (4, 0, 0, 0, 0, 0)),
    ],
    ids=["FR-12-forfalt-og-gyldig", "FR-12-forfalt-og-gyldig-samme-uke"],
)
def test_fr12_r11_parent_with_past_due_and_valid_orders(
    mps_weeks: tuple[int, int], releases: tuple[int, int], child_gross: tuple[int, ...]
) -> None:
    """P (ledetid 1) → C (mengde per 2): det forfalte forslaget havner i uke 1 hos C."""
    items = (_item("P", lead_time=1, source="make"), _item("C"))
    mps = tuple(MpsLine("P", week, 1, n) for n, week in enumerate(mps_weeks, 1))
    by_id = _chain(items, (BomLine("P", "C", 2),), mps)
    assert tuple(order.release_week for order in by_id["P"].planned_orders) == releases
    assert by_id["C"].gross_requirements == child_gross
