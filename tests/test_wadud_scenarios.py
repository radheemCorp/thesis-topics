from __future__ import annotations

import pytest

from surrogate_xapps.scenarios import SCENARIOS, get_scenario


def test_all_registered_scenarios_have_stable_metadata() -> None:
    assert set(SCENARIOS) == {f"S{i}" for i in range(1, 10)}
    assert all(spec.shared_icp == "p1" for spec in SCENARIOS.values())


def test_unknown_scenario_error_lists_choices() -> None:
    with pytest.raises(ValueError, match="S1"):
        get_scenario("unknown")
