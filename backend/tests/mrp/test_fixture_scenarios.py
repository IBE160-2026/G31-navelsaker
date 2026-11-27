"""Fasittestene (NFR-3, SM-1): kjernen mot ``testdata/testfartoy-v1/expected.json``.

``conftest.py`` lager ett tilfelle per scenario (A–E) × vare × felt i ``FIELD_FR``, med id-er
som ``A-FR-10-PLT-900-low_level_code``. I scenario D får feltene fra 2.2 FR-12 (R11) i stedet,
se ``fasit_fr``. Meldingene (E1 og E2, FR-13 og FR-14) sammenlignes for seg per scenario og
type som usortert multimengde, se ``test_fasit_exceptions``.
Fixturen ``result_for`` ligger i ``tests/mrp/conftest.py``.
"""

from collections import Counter
from collections.abc import Callable
from typing import Any

import pytest

FIELD_FR = {
    "low_level_code": "FR-10",
    "gross_requirements": "FR-10",
    "scheduled_receipts": "FR-11",
    "projected_on_hand": "FR-11",
    "net_requirements": "FR-11",
    "planned_order_receipts": "FR-11",
    "planned_order_releases": "FR-11",
    "planned_orders": "FR-11",
}
SCENARIOS = ("A", "B", "C", "D", "E")
EXCEPTION_FR = {"LEAD_TIME_EXCEEDS_HORIZON": "FR-13", "PAST_DUE_RELEASE": "FR-14"}

ResultFor = Callable[[str], dict[str, Any]]


def fasit_fr(scenario: str, field: str, fr: str) -> str:
    """FR-nummeret i id-en: i D viser feltene fra 2.2 R11 (FR-12). LLC beholder FR-10."""
    if scenario == "D" and field != "low_level_code":
        return "FR-12"
    return fr


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


def _exception_counter(exceptions: list[dict[str, Any]], kind: str) -> Counter[tuple[Any, ...]]:
    """Meldingene av typen ``kind`` som multimengde av sorterte nøkkel/verdi-par."""
    return Counter(tuple(sorted(e.items())) for e in exceptions if e["type"] == kind)


@pytest.mark.parametrize(
    ("scenario", "kind"),
    [(s, kind) for s in SCENARIOS for kind in EXCEPTION_FR],
    ids=[f"{s}-{fr}-meldinger" for s in SCENARIOS for fr in EXCEPTION_FR.values()],
)
def test_fasit_exceptions(
    scenario: str, kind: str, result_for: ResultFor, expected: dict[str, Any]
) -> None:
    """E1 (FR-13) og E2 (FR-14) som usortert multimengde, så rekkefølgen ikke teller."""
    result = result_for(scenario)["exceptions"]
    known = set(EXCEPTION_FR)
    assert {e["type"] for e in result} <= known, "ukjent meldingstype i resultatet"
    assert {e["type"] for e in expected[scenario]["exceptions"]} <= known, "ukjent type i fasiten"
    actual = _exception_counter(result, kind)
    fasit = _exception_counter(expected[scenario]["exceptions"], kind)
    missing = fasit - actual
    extra = actual - fasit
    assert not missing and not extra, f"mangler: {dict(missing)}, for mye: {dict(extra)}"
