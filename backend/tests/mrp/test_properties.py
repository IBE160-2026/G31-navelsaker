"""Egenskapstester for kjernen (FR-9, FR-11, SM-C2): massebalanse, determinisme og horisont.

Massebalansen går nesten opp per definisjon når BL regnes med R7, men den fanger tapte eller
doble mengder mellom arrayene. SM-C2 bæres ellers av enhetstestene i ``test_plan.py``.
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

BALANCE_SCENARIOS = ("A", "B", "C", "E")
"""D venter på R11 (story 2.3): uten den går barnas behov fra forfalte frigivelser tapt."""
SCENARIOS = ("A", "B", "C", "D", "E")


@pytest.mark.parametrize(
    "scenario", BALANCE_SCENARIOS, ids=[f"{s}-FR-11-massebalanse" for s in BALANCE_SCENARIOS]
)
def test_fr11_mass_balance_per_item(scenario: str, result_for: ResultFor) -> None:
    for item_id, values in result_for(scenario)["items"].items():
        balance = (
            values["on_hand"]
            + sum(values["scheduled_receipts"])
            + sum(values["planned_order_receipts"])
            - sum(values["gross_requirements"])
        )
        assert balance == values["projected_on_hand"][-1], item_id


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
