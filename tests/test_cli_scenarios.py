"""Tests for the synthetic scenario CLI (cli/cli.py)."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
CLI_PATH = REPO_ROOT / "cli" / "cli.py"
SYNTHETIC = REPO_ROOT / "data" / "synthetic"


def _load_cli():
    spec = importlib.util.spec_from_file_location("scenario_cli", CLI_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


cli = _load_cli()


def _base_args(tmp_path: Path, apps: list[str], optimize_over: str,
               cmc_resolution: list[str]) -> list[str]:
    files = {
        "app1": "xapp1_direct.csv",
        "app2": "xapp2_direct.csv",
        "app3": "xapp3_indirect.csv",
        "app4": "xapp4_extra.csv",
    }
    args = ["--datasets", *[str(SYNTHETIC / files[app]) for app in apps]]
    args += ["--xapps", ",".join(apps)]
    args += ["--qos", *(["0.35"] * len(apps))]
    args += ["--weights", *(["1.0"] * len(apps))]
    args += ["--model", "ann", "--resolution", "24"]
    args += ["--cmc-resolution", *cmc_resolution]
    args += ["--optimize-over", optimize_over]
    return args


def test_cli_parser_defaults():
    args = cli.build_parser().parse_args(
        ["--datasets", "a.csv", "--xapps", "app1"]
    )
    assert args.optimize_over == "joint"
    assert args.cmc_resolution == [300]


def test_cli_parser_accepts_per_axis_resolution():
    args = cli.build_parser().parse_args(
        ["--datasets", "a.csv", "--xapps", "app1",
         "--cmc-resolution", "16", "24"]
    )
    assert args.cmc_resolution == [16, 24]


def test_cli_parser_rejects_unknown_axis_mode():
    with pytest.raises(SystemExit):
        cli.build_parser().parse_args(
            ["--datasets", "a.csv", "--xapps", "app1",
             "--optimize-over", "p3"]
        )


def test_cli_joint_prints_two_coordinates(tmp_path, capsys):
    rc = cli.main(_base_args(tmp_path, ["app1", "app2"], "joint", ["24"]))
    out = capsys.readouterr().out
    assert rc == 0
    assert "p1=" in out and "p2=" in out


def test_cli_p1_mode_prints_one_coordinate(tmp_path, capsys):
    rc = cli.main(_base_args(tmp_path, ["app1", "app2"], "p1", ["24"]))
    out = capsys.readouterr().out
    assert rc == 0
    assert "p1=" in out
    assert "p2=" not in out


def test_cli_p2_mode_prints_one_coordinate(tmp_path, capsys):
    rc = cli.main(_base_args(tmp_path, ["app1", "app2"], "p2", ["24", "16"]))
    out = capsys.readouterr().out
    assert rc == 0
    assert "p2=" in out
    assert "p1=" not in out


def test_cli_three_apps_have_no_nan(tmp_path, capsys):
    rc = cli.main(_base_args(tmp_path, ["app1", "app2", "app3"], "joint", ["16"]))
    out = capsys.readouterr().out
    assert rc == 0
    assert "nan" not in out.lower()
    for name in ("xApp1", "xApp2", "xApp3"):
        assert name in out
