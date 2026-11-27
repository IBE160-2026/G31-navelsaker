"""Fasittestene (NFR-3, SM-1): kjernen mot ``testdata/testfartoy-v1/expected.json``.

``conftest.py`` lager ett tilfelle per scenario (A–E) × vare × felt i ``FIELD_FR``, med id-er
som ``A-FR-10-PLT-900-low_level_code``. Story 2.2–2.4 utvider tabellen med feltene sine.
"""

from collections.abc import Callable
from functools import cache
from pathlib import Path
from typing import Any

import pytest

from rbe.fixture import load_input
from rbe.mrp import result_to_dict, run_mrp

FIELD_FR = {"low_level_code": "FR-10"}
SCENARIOS = ("A", "B", "C", "D", "E")

ResultFor = Callable[[str], dict[str, Any]]


@pytest.fixture(scope="session")
def result_for(input_path: Path) -> ResultFor:
    """Kjernens resultat som dict per scenario, beregnet én gang per scenario."""

    @cache
    def compute(scenario: str) -> dict[str, Any]:
        return result_to_dict(run_mrp(load_input(input_path, scenario)))

    return compute


def test_fasit_field(fasit_case: Any, result_for: ResultFor) -> None:
    result = result_for(fasit_case.scenario)
    assert fasit_case.item in result["items"], f"varen {fasit_case.item} mangler i resultatet"
    assert result["items"][fasit_case.item][fasit_case.field] == fasit_case.expected


@pytest.mark.parametrize("scenario", SCENARIOS, ids=[f"{s}-FR-10-varesett" for s in SCENARIOS])
def test_fr10_item_set_matches_fasit(
    scenario: str, result_for: ResultFor, expected: dict[str, Any]
) -> None:
    assert set(result_for(scenario)["items"]) == set(expected[scenario]["items"])


def test_fasit_covers_all_scenarios(expected: dict[str, Any]) -> None:
    assert tuple(sorted(expected)) == SCENARIOS
