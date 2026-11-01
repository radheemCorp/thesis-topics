from __future__ import annotations

import numpy as np
import pytest

from surrogate_xapps.baselines import (
    ArithmeticMeanPolicy,
    EisenbergGalePolicy,
    NSWFPolicy,
)
from surrogate_xapps.utility import normalize_utility


class FakeXApp:
    def __init__(self, xapp_id, preferred, values, weight=1.0):
        self.xapp_id = xapp_id
        self.objective = "max"
        self.qos_threshold = 0.5
        self.priority_weight = weight
        self.preferred_point = preferred
        self.values = values

    def predict_at(self, p1, p2=None):
        return float(self.values[round(p1)])


def test_minmax10_and_min_objective() -> None:
    values, bounds = normalize_utility([1, 3, 5], objective="max")
    assert values.tolist() == pytest.approx([0.0, 5.0, 10.0])
    assert bounds == (1.0, 5.0)
    values, _ = normalize_utility([1, 3, 5], objective="min")
    assert values.tolist() == pytest.approx([10.0, 5.0, 0.0])


def test_constant_utility_warns_and_returns_zero() -> None:
    with pytest.warns(UserWarning, match="constant"):
        values, bounds = normalize_utility([2, 2], objective="max")
    assert np.all(values == 0)
    assert bounds == (2.0, 2.0)


def test_arithmetic_mean_projects_and_does_not_need_predictions() -> None:
    apps = [
        FakeXApp("a", (-10.0,), {-10: 1.0, 0: 0.1, 10: 0.1}),
        FakeXApp("b", (10.0,), {-10: 0.1, 0: 0.1, 10: 1.0}),
    ]
    result = ArithmeticMeanPolicy().mitigate(apps, [(-10, 10)], 3)
    assert result.optimal_point == (0.0,)


def test_nswf_selects_product_optimum() -> None:
    apps = [
        FakeXApp("a", (-10.0,), {-10: 10.0, 0: 8.0, 10: 1.0}),
        FakeXApp("b", (10.0,), {-10: 1.0, 0: 8.0, 10: 10.0}),
    ]
    result = NSWFPolicy().mitigate(apps, [(-10, 10)], 3)
    assert result.optimal_point == (0.0,)


def test_eg_favors_higher_weight() -> None:
    apps = [
        FakeXApp("a", (-10.0,), {-10: 10.0, 0: 8.0, 10: 1.0}, weight=0.9),
        FakeXApp("b", (10.0,), {-10: 1.0, 0: 8.0, 10: 10.0}, weight=0.1),
    ]
    result = EisenbergGalePolicy().mitigate(apps, [(-10, 10)], 3)
    assert result.optimal_point == (-10.0,)


def test_eg_rejects_nonfinite_weights() -> None:
    app = FakeXApp("a", (0.0,), {0: 1.0}, weight=float("nan"))
    with pytest.raises(ValueError, match="finite"):
        EisenbergGalePolicy().mitigate([app], [(0, 0)], 1)
