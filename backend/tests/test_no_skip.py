"""Krokene i ``tests/conftest.py`` gjør alle skip og xfail til feil (SM-1).

Testene kjører pytest inni pytest med ``pytester``. Den indre kjøringen laster ikke
``tests/conftest.py``, så den kopieres inn med ``makeconftest``.
"""

from pathlib import Path

import pytest

CONFTEST = Path(__file__).with_name("conftest.py")

CASES = {
    "skip": """
        import pytest

        def test_it():
            pytest.skip("ikke ferdig")
    """,
    "skipif": """
        import pytest

        @pytest.mark.skipif(True, reason="ikke ferdig")
        def test_it():
            pass
    """,
    "xfail": """
        import pytest

        @pytest.mark.xfail(reason="ikke ferdig")
        def test_it():
            assert False
    """,
    "modulniva": """
        import pytest

        pytest.skip("ikke ferdig", allow_module_level=True)

        def test_it():
            pass
    """,
}


@pytest.mark.parametrize("source", CASES.values(), ids=[f"SM-1-{k}" for k in CASES])
def test_sm1_skip_becomes_failure(pytester: pytest.Pytester, source: str) -> None:
    pytester.makeconftest(CONFTEST.read_text(encoding="utf-8"))
    pytester.makepyfile(test_inner=source)
    result = pytester.runpytest()
    outcomes = result.parseoutcomes()
    assert outcomes.get("skipped", 0) == 0, outcomes
    assert outcomes.get("xfailed", 0) == 0, outcomes
    assert outcomes.get("failed", 0) + outcomes.get("errors", 0) >= 1, outcomes
    result.stdout.fnmatch_lines(["*skip og xfail er ikke lov (SM-1)*ikke ferdig*"])
