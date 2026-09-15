"""Generate ``workshop/docs/cell_mapping.md`` from the ``source:`` markers in canonical notebooks.

The deck (``Docs/Od pytania do agenta - SQLDay Lite.pptx``) references Mariusz cells by number;
this table maps every demo cell back to its origin (0-based .ipynb index; the deck counts from 1).
"""
from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEMO = ROOT / "workshop" / "demo"
SETUP = ROOT / "workshop" / "00_setup"
PATTERN = ROOT / "workshop" / "pattern"
OUT = ROOT / "workshop" / "docs" / "cell_mapping.md"

sys.path.insert(0, str(ROOT / "workshop" / "scripts"))
from check_notebooks import marker_of, _text  # noqa: E402


def heading_of(cell: dict) -> str:
    for line in _text(cell["source"]).splitlines():
        line = line.strip()
        if line.startswith("#") and not line.startswith("<!--") and cell["cell_type"] == "markdown":
            return line.lstrip("# ").strip()[:70]
        if cell["cell_type"] == "code" and line and not line.startswith(("#", "--", "%")):
            return line[:70]
    return ""


def status_of(cell: dict, source: str) -> str:
    tags = cell.get("metadata", {}).get("tags", [])
    parts = []
    if source == "new":
        parts.append("new")
    else:
        parts.append("adapted")
    if "solution" in tags:
        parts.append("lab")
    if "trainer_only" in tags:
        parts.append("trainer_only")
    if "optional" in tags:
        parts.append("optional")
    if "bonus" in tags:
        parts.append("poziom 2")
    return " / ".join(parts)


def main() -> int:
    lines = [
        "# Mapowanie komórek: notebooki warsztatu → materiał źródłowy",
        "",
        f"Wygenerowano automatycznie ({date.today().isoformat()}) przez `workshop/scripts/build_cell_mapping.py` z markerów `source:`.",
        "Indeksy `WSx[i]` są 0-based (jak w pliku .ipynb); prezentacja i Przewodnik Mariusza liczą komórki od 1 (dodaj 1).",
        "",
    ]
    total = 0
    for path in sorted(list(SETUP.glob("*.ipynb")) + list(DEMO.glob("*.ipynb")) + list(PATTERN.glob("*.ipynb"))):
        nb = json.loads(path.read_text(encoding="utf-8"))
        meta = nb["metadata"].get("workshop", {})
        lines += [f"## `{path.relative_to(ROOT)}` — {meta.get('title', '')}", "",
                  "| # | cell id | typ | nagłówek / pierwsza linia | źródło | status |", "|---|---|---|---|---|---|"]
        for index, cell in enumerate(nb["cells"], 1):
            source = marker_of(cell) or "?"
            heading = heading_of(cell).replace("|", "\\|")
            lines.append(f"| {index} | `{cell.get('id')}` | {cell['cell_type']} | {heading} | `{source}` | {status_of(cell, source)} |")
            total += 1
        lines.append("")
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"{OUT.relative_to(ROOT)}: {total} cells")
    return 0


if __name__ == "__main__":
    sys.exit(main())
