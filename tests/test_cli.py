"""End-to-end integration tests for the scenario CLI (``cli/cli.py``).

Each case invokes ``cli.main`` with real synthetic datasets and a reduced grid
so the suite stays fast, then checks the user-facing report.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
CLI_PATH = REPO_ROOT / "cli" / "cli.py"
SYNTHETIC = REPO_ROOT / "data" / "synthetic"

DATASETS = {
    "app1": SYNTHETIC / "xapp1_direct.csv",
    "app2": SYNTHETIC / "xapp2_direct.csv",
    "app3": SYNTHETIC / "xapp3_indirect.csv",
    "app4": SYNTHETIC / "xapp4_extra.csv",
}

REPORT_IDS = {
    "app1": "xApp1",
    "app2": "xApp2",
    "app3": "xApp3",
    "app4": "xApp4",
}


def _load_cli():
    spec = importlib.util.spec_from_file_location("scenario_cli", CLI_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


cli = _load_cli()


def _argv(apps: list[str]) -> list[str]:
    return [
        "--datasets",
        *[str(DATASETS[app]) for app in apps],
        "--xapps",
        ",".join(apps),
        "--qos",
        *(["0.35"] * len(apps)),
        "--weights",
        *(["1.0"] * len(apps)),
        "--model",
        "ann",
        "--resolution",
        "12",
        "--cmc-resolution",
        "12",
    ]


@pytest.mark.parametrize(
    "apps",
    [
        ["app1", "app2"],
        ["app1", "app2", "app3"],
        ["app1", "app2", "app3", "app4"],
    ],
    ids=["two-app", "three-app", "four-app"],
)
def test_cli_joint_run_reports_clean_two_axis_optimum(apps, capsys):
    exit_code = cli.main(_argv(apps))
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "nan" not in output.lower()
    assert "p* =" in output
    assert "p1=" in output
    assert "p2=" in output

    for app in apps:
        assert REPORT_IDS[app] in output
