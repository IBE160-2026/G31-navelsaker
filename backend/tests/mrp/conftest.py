"""Felles fixturer for kjernetestene: ``result_for`` gir kjernens resultat per scenario.

Fixturen ligger her og ikke i en testmodul, fordi ``--import-mode=importlib`` gjør import
mellom testmoduler skjør.
"""

from collections.abc import Callable
from functools import cache
from pathlib import Path
from typing import Any

import pytest

from rbe.fixture import load_input
from rbe.mrp import result_to_dict, run_mrp


@pytest.fixture(scope="session")
def result_for(input_path: Path) -> Callable[[str], dict[str, Any]]:
    """Kjernens resultat som dict per scenario, beregnet én gang per scenario."""

    @cache
    def compute(scenario: str) -> dict[str, Any]:
        return result_to_dict(run_mrp(load_input(input_path, scenario)))

    return compute
