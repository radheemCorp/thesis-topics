"""Versioned scenario metadata for the Wadud baseline comparison.

The paper's eight-ICP surfaces are not all represented by the repository's
two-feature loader. S1-S5 therefore retain their provenance and fixed ICP
metadata here; S6-S7 are directly runnable with the committed synthetic
two-feature datasets.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ScenarioSpec:
    scenario_id: str
    name: str
    datasets: tuple[str, ...]
    xapps: tuple[str, ...]
    shared_icp: str
    weights: tuple[float, ...]
    published: tuple[float, ...] | None = None
    fixed_icps: tuple[tuple[str, float], ...] = (
        ("p2", 20.0), ("p3", 60.0), ("p5", 60.0), ("p7", 60.0)
    )


_PAPER = "data/QACM/"
SCENARIOS = {
    "S1": ScenarioSpec("S1", "Direct, non-priority", (_PAPER + "data1.csv", _PAPER + "data3.csv"), ("xApp1", "xApp2"), "p1", (0.5, 0.5), (0.0, -18.0)),
    "S2": ScenarioSpec("S2", "Direct, priority", (_PAPER + "data1.csv", _PAPER + "data3.csv"), ("xApp1", "xApp2"), "p1", (0.4, 0.6), (22.0,)),
    "S3": ScenarioSpec("S3", "Indirect", (_PAPER + "data3.csv", _PAPER + "data5.csv"), ("xApp2", "xApp4"), "p1", (0.1, 0.9), (12.0, 66.0, 110.0)),
    "S4": ScenarioSpec("S4", "Implicit", (_PAPER + "data1.csv", _PAPER + "data3.csv"), ("xApp1", "xApp3"), "p1", (0.9, 0.1), (-84.0, -62.0, -75.0)),
    "S5": ScenarioSpec("S5", "Four-way scaling", tuple(_PAPER + f"data{i}.csv" for i in range(1, 5)), ("xApp1", "xApp2", "xApp3", "xApp4"), "p1", (0.1, 0.2, 0.3, 0.4)),
    "S6": ScenarioSpec("S6", "Synthetic direct pair", ("data/synthetic/xapp1_direct.csv", "data/synthetic/xapp2_direct.csv"), ("xApp1", "xApp2"), "p1", (0.5, 0.5)),
    "S7": ScenarioSpec("S7", "Synthetic indirect trio", tuple(f"data/synthetic/xapp{i}_{'direct' if i < 3 else 'indirect'}.csv" for i in range(1, 4)), ("xApp1", "xApp2", "xApp3"), "p1", (0.4, 0.4, 0.2)),
    "S8": ScenarioSpec("S8", "Weight sweep", (_PAPER + "data1.csv", _PAPER + "data3.csv"), ("xApp1", "xApp2"), "p1", (0.5, 0.5)),
    "S9": ScenarioSpec("S9", "Edge cases", (), (), "p1", ()),
}


def get_scenario(scenario_id: str) -> ScenarioSpec:
    """Return a registered scenario or raise an actionable error."""
    try:
        return SCENARIOS[scenario_id.upper()]
    except KeyError as exc:
        available = ", ".join(sorted(SCENARIOS))
        raise ValueError(f"unknown scenario {scenario_id!r}; choose one of {available}") from exc


def resolve_datasets(scenario: ScenarioSpec, root: str | Path = ".") -> tuple[Path, ...]:
    """Resolve scenario dataset paths relative to a repository root."""
    root = Path(root)
    return tuple(root / path for path in scenario.datasets)


__all__ = ["ScenarioSpec", "SCENARIOS", "get_scenario", "resolve_datasets"]
