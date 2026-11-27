"""Egenskapstester for kjernen (FR-9, FR-11, FR-12, FR-14, SM-C2): massebalanse, ingen tapte
behov, feltene i forfalte meldinger, determinisme og horisont.

Massebalansen går nesten opp per definisjon når BL regnes med R7, men den fanger tapte eller
doble mengder mellom arrayene. «Ingen behov går tapt» (FR-12) fanger behov som forsvinner mellom
forelder og barn, f.eks. fra forfalte forslag uten R11. SM-C2 bæres ellers av enhetstestene i
``test_plan.py``.
"""

from collections.abc import Callable
from dataclasses import replace
from pathlib import Path
from typing import Any

import pytest

from rbe.fixture import load_input
from rbe.mrp import Horizon, MrpInput, result_to_dict, run_mrp
from rbe.mrp.run import WEEK_FIELDS

ResultFor = Callable[[str], dict[str, Any]]

SCENARIOS = ("A", "B", "C", "D", "E")


@pytest.mark.parametrize("scenario", SCENARIOS, ids=[f"{s}-FR-11-massebalanse" for s in SCENARIOS])
def test_fr11_mass_balance_per_item(scenario: str, result_for: ResultFor) -> None:
    """Gjelder hver vare for seg og er uavhengig av R11.

    Tapte behov mellom forelder og barn fanges ikke her, men av
    ``test_fr12_no_requirements_are_lost`` (FR-12).
    """
    for item_id, values in result_for(scenario)["items"].items():
        balance = (
            values["on_hand"]
            + sum(values["scheduled_receipts"])
            + sum(values["planned_order_receipts"])
            - sum(values["gross_requirements"])
        )
        assert balance == values["projected_on_hand"][-1], item_id


@pytest.mark.parametrize(
    "scenario", SCENARIOS, ids=[f"{s}-FR-12-ingen-tapte-behov" for s in SCENARIOS]
)
def test_fr12_no_requirements_are_lost(
    scenario: str, input_path: Path, result_for: ResultFor
) -> None:
    """For hver vare: sum BB = sum MPS + Σ forelderens forslag × mengde per (R3, R11).

    Sjekkes per vare, ikke per BOM-linje, fordi en vare med flere foreldre har ett samlet
    bruttobehov. MPS og BOM leses fra inndataene, forslagene fra resultatet, så testen er
    uavhengig av ``planned_order_releases`` (R9).
    """
    data = load_input(input_path, scenario)
    items = result_for(scenario)["items"]
    expected_gross = {item_id: 0 for item_id in items}
    for mps in data.mps:
        expected_gross[mps.item] += mps.quantity
    for line in data.bom:
        ordered = sum(order["quantity"] for order in items[line.parent]["planned_orders"])
        expected_gross[line.child] += ordered * line.qty_per
    avvik = {
        item_id: (sum(values["gross_requirements"]), expected_gross[item_id])
        for item_id, values in items.items()
        if sum(values["gross_requirements"]) != expected_gross[item_id]
    }
    assert avvik == {}, "vare: (faktisk, forventet)"


@pytest.mark.parametrize(
    "scenario", SCENARIOS, ids=[f"{s}-FR-14-forfalt-forsinkelse" for s in SCENARIOS]
)
def test_fr14_past_due_fields_agree(scenario: str, result_for: ResultFor) -> None:
    """For hver E2: tidligste mottak − mottaksuke = uker forfalt, og frigivelse = 1 − uker
    forfalt."""
    for e in result_for(scenario)["exceptions"]:
        if e["type"] != "PAST_DUE_RELEASE":
            continue
        assert e["earliest_receipt_week"] - e["receipt_week"] == e["weeks_past_due"], e
        assert e["release_week"] == 1 - e["weeks_past_due"], e


def _reversed(data: MrpInput) -> MrpInput:
    return replace(
        data,
        items=data.items[::-1],
        bom=data.bom[::-1],
        mps=data.mps[::-1],
        scheduled_receipts=data.scheduled_receipts[::-1],
    )


@pytest.mark.parametrize("scenario", SCENARIOS, ids=[f"{s}-FR-9-determinisme" for s in SCENARIOS])
def test_ad3_deterministic_and_independent_of_input_order(scenario: str, input_path: Path) -> None:
    data = load_input(input_path, scenario)
    first = run_mrp(data)
    assert run_mrp(data) == first
    assert run_mrp(_reversed(data)) == first
    assert result_to_dict(run_mrp(_reversed(data))) == result_to_dict(first)


def test_fr9_horizon_comes_from_input(input_path: Path, expected: dict[str, Any]) -> None:
    """A med 20 uker: uke 1–16 som fasiten, uke 17–20 er 0, og BL holder siste verdi."""
    data = load_input(input_path, "A")
    result = result_to_dict(run_mrp(replace(data, horizon=Horizon(1, 20))))
    for item_id, fasit in expected["A"]["items"].items():
        values = result["items"][item_id]
        for name in WEEK_FIELDS:
            assert len(values[name]) == 20, (item_id, name)
            assert values[name][:16] == fasit[name], (item_id, name)
            tail = [fasit[name][-1]] * 4 if name == "projected_on_hand" else [0] * 4
            assert values[name][16:] == tail, (item_id, name)
        assert values["planned_orders"] == fasit["planned_orders"], item_id
