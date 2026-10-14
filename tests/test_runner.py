"""Tests for orchestration, conflict detection, and the CLI."""

from __future__ import annotations

from pathlib import Path

from surrogate_xapps.runner import build_parser, detect_conflict, main, run


def test_run_returns_validated_actions(cco_file: Path, es_file: Path):
    action_cco, action_es, cco, es = run(cco_file, es_file, resolution=60)
    assert action_cco["xapp_id"] == "xApp_CCO"
    assert action_es["xapp_id"] == "xApp_ES"
    assert len(action_cco["requested_value"]) == 2
    assert len(action_es["requested_value"]) == 2


def test_detect_conflict_true_for_opposing_requests():
    a = {"target_parameter": ["p1", "p2"], "requested_value": [-51.0, 20.0]}
    b = {"target_parameter": ["p1", "p2"], "requested_value": [49.0, 60.0]}
    assert detect_conflict(a, b) is True


def test_detect_conflict_false_for_identical_requests():
    a = {"target_parameter": ["p1", "p2"], "requested_value": [10.0, 20.0]}
    b = {"target_parameter": ["p1", "p2"], "requested_value": [10.0, 20.0]}
    assert detect_conflict(a, b) is False


def test_cli_parses_defaults():
    args = build_parser().parse_args([])
    assert args.model == "ann"
    assert args.resolution == 200
    assert args.no_plot is False


def test_cli_parses_overrides():
    args = build_parser().parse_args(
        ["--model", "ann", "--resolution", "50", "--no-plot", "--out", "tmp"]
    )
    assert args.model == "ann"
    assert args.resolution == 50
    assert args.no_plot is True
    assert args.out == "tmp"


def test_main_end_to_end(cco_file: Path, es_file: Path, tmp_path: Path, capsys):
    rc = main(
        [
            "--cco-file",
            str(cco_file),
            "--es-file",
            str(es_file),
            "--resolution",
            "60",
            "--out",
            str(tmp_path),
        ]
    )
    assert rc == 0
    out = capsys.readouterr().out
    assert "xApp_CCO" in out
    assert "xApp_ES" in out
    assert "CONFLICT" in out
    assert (tmp_path / "xapp_kpi_comparison.png").exists()
