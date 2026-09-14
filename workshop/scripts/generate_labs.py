"""Derive participant lab notebooks (``workshop/labs``) from canonical demo notebooks (``workshop/demo``).

Rules:
- ``demo/`` is canonical; never edit ``labs/`` by hand.
- a code cell tagged ``solution`` is replaced by its ``metadata.exercise_source`` (tag becomes ``exercise``);
- a cell tagged ``trainer_only`` is replaced by a markdown note built from ``metadata.trainer_note``;
- outputs and execution counts are always cleared.

Run: ``python workshop/scripts/generate_labs.py``
"""
from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEMO_DIR = ROOT / "workshop" / "demo"
LABS_DIR = ROOT / "workshop" / "labs"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_notebooks import marker_of  # noqa: E402

TRAINER_PREFIX = "> **Demo prowadzącego (Premium).** "


def _validate(notebook: dict, path: Path) -> None:
    """Reject ambiguous sources before overwriting generated notebooks."""
    workshop = notebook.get("metadata", {}).get("workshop", {})
    if workshop.get("variant") != "solution":
        raise ValueError(f"Not a canonical solution notebook: {path.name}")
    ids = [cell.get("id") for cell in notebook.get("cells", [])]
    if not ids or any(not cell_id for cell_id in ids):
        raise ValueError(f"Missing cell id: {path.name}")
    if len(ids) != len(set(ids)):
        raise ValueError(f"Duplicate cell id: {path.name}")
    for cell in notebook["cells"]:
        tags = cell.get("metadata", {}).get("tags", [])
        if "solution" in tags:
            if cell["cell_type"] != "code":
                raise ValueError(f"Only code cells may be solutions: {path.name}/{cell['id']}")
            source = cell["metadata"].get("exercise_source")
            if not isinstance(source, (str, list)) or not source:
                raise ValueError(f"Missing exercise_source: {path.name}/{cell['id']}")
        if "trainer_only" in tags and not cell.get("metadata", {}).get("trainer_note"):
            raise ValueError(f"Missing trainer_note: {path.name}/{cell['id']}")


def _as_text(source) -> str:
    return "".join(source) if isinstance(source, list) else source


def derive_lab(notebook: dict) -> dict:
    lab = copy.deepcopy(notebook)
    for cell in lab["cells"]:
        metadata = cell.setdefault("metadata", {})
        tags = list(metadata.get("tags", []))
        if "trainer_only" in tags:
            note = _as_text(metadata.pop("trainer_note")).strip()
            origin = marker_of(cell)
            marker = f"<!-- source: {origin} -->\n" if origin else ""
            cell["cell_type"] = "markdown"
            cell["source"] = f"{marker}{TRAINER_PREFIX}{note}\n"
            cell.pop("outputs", None)
            cell.pop("execution_count", None)
            metadata.pop("exercise_source", None)
            tags = [t for t in tags if t not in ("trainer_only", "solution")]
            metadata["tags"] = tags + ["trainer_demo"]
        elif "solution" in tags:
            cell["source"] = metadata.pop("exercise_source")
            metadata["tags"] = ["exercise" if t == "solution" else t for t in tags]
        if cell["cell_type"] == "code":
            cell["execution_count"] = None
            cell["outputs"] = []
    lab["metadata"]["workshop"]["variant"] = "lab"
    return lab


def generate(demo_dir: Path = DEMO_DIR, labs_dir: Path = LABS_DIR) -> list[Path]:
    labs_dir.mkdir(parents=True, exist_ok=True)
    generated: list[Path] = []
    for source_path in sorted(demo_dir.glob("*.ipynb")):
        notebook = json.loads(source_path.read_text(encoding="utf-8"))
        _validate(notebook, source_path)
        target = labs_dir / source_path.name
        target.write_text(json.dumps(derive_lab(notebook), ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        generated.append(target)
    expected = {path.name for path in generated}
    for stale in labs_dir.glob("*.ipynb"):
        if stale.name not in expected:
            stale.unlink()
    return generated


if __name__ == "__main__":
    for path in generate():
        print(path.relative_to(ROOT))
    sys.exit(0)
