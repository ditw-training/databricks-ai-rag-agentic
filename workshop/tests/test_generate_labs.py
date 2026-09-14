"""Unit checks for the lab generator on synthetic notebooks (no workshop content needed)."""
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
from check_notebooks import marker_of  # noqa: E402
from generate_labs import TRAINER_PREFIX, derive_lab  # noqa: E402


def _cell(cell_id, cell_type, source, tags, **meta):
    cell = {"id": cell_id, "cell_type": cell_type, "metadata": {"tags": tags, **meta}, "source": source}
    if cell_type == "code":
        cell.update(outputs=[{"output_type": "stream", "name": "stdout", "text": "x"}], execution_count=3)
    return cell


def _lab(*cells):
    return derive_lab({"metadata": {"workshop": {"variant": "solution"}}, "cells": list(cells)})["cells"]


@pytest.mark.parametrize(
    "cell_type, source",
    [
        ("code", "# source: WS4[22]\nprint(1)"),
        ("code", "%sql\n-- source: WS2[20]\nSELECT 1"),
        ("markdown", "<!-- source: WS3[29] -->\n## Knowledge Assistant"),
    ],
    ids=["python", "sql", "markdown"],
)
def test_trainer_only_keeps_source_marker(cell_type, source):
    original = _cell("t", cell_type, source, ["trainer_only"], trainer_note="Pokazuje prowadzący.")
    expected = marker_of(original)
    (lab,) = _lab(original)
    assert lab["cell_type"] == "markdown"
    assert marker_of(lab) == expected
    assert TRAINER_PREFIX in lab["source"] and "trainer_demo" in lab["metadata"]["tags"]
    assert "outputs" not in lab and "trainer_note" not in lab["metadata"]


def test_solution_becomes_exercise_and_outputs_are_cleared():
    solved = _cell("s", "code", "# source: new\nx = 42", ["solution"], exercise_source="# source: new\nx = ...  # TODO")
    plain = _cell("p", "code", "# source: new\nprint(x)", [])
    exercise, untouched = _lab(solved, plain)
    assert exercise["source"] == "# source: new\nx = ...  # TODO"
    assert exercise["metadata"]["tags"] == ["exercise"] and "exercise_source" not in exercise["metadata"]
    assert exercise["outputs"] == [] and exercise["execution_count"] is None
    assert untouched["source"] == plain["source"] and untouched["outputs"] == []
