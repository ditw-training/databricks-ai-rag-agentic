"""Static lint for workshop notebooks: forbidden patterns, source markers, parity, structure.

Run: ``python workshop/scripts/check_notebooks.py`` (exit code 1 on findings).
Used by ``workshop/tests/test_notebooks.py`` as well.
"""
from __future__ import annotations

import ast
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WORKSHOP = ROOT / "workshop"
NOTEBOOK_DIRS = [WORKSHOP / "demo", WORKSHOP / "labs", WORKSHOP / "00_setup", WORKSHOP / "scripts", WORKSHOP / "pattern"]

FORBIDDEN = [
    (r"^# MAGIC", "Databricks .py source-format prefix inside an .ipynb"),
    (r"^%%sql", "Jupyter cell magic; Databricks uses %sql"),
    (r"adb-\d+\.\d+\.azuredatabricks\.net", "foreign workspace URL"),
    (r"dbc-[0-9a-f]+-[0-9a-f]+\.cloud\.databricks\.com", "foreign workspace URL"),
    (r"#notebook-\d{6,}", "workspace-specific notebook link"),
    (r"databricks\.vector_search|VectorSearchClient|databricks-vectorsearch", "Vector Search SDK renamed to AI Search"),
    (r"w\.vector_search_(endpoints|indexes)", "legacy Vector Search SDK"),
    (r"state_modifier\s*=", "removed in LangGraph 1.x"),
    (r"create_react_agent\(", "deprecated in LangGraph 1.x; use langchain.agents.create_agent(system_prompt=...)"),
    (r"system\.ai\.google_drive", "MCP demo uses managed UC-function servers"),
    (r"agents\.deploy\(", "Model Serving agent deployment is legacy"),
    (r"<YOUR_CATALOG>|<YOUR_SCHEMA>", "unresolved placeholder"),
    (r"models:/[^\s'\"]+/latest", "UC models have no /latest; use @champion"),
    (r"set_experiment\(\s*['\"]/Shared/", "experiments live under /Users/<user>/"),
    (r"dbutils\.fs\.cp\(\s*['\"]file:", "not supported on Serverless"),
    (r"is_account_group_member\('users'\)", "no-op predicate (see Mariusz commit 659e70e)"),
    (r"\d+\s?(min\b|minut)|\*\*Czas:\*\*", "no minutes in notebooks: timing lives in docs/schedule.md"),
    (r"spark\.sql\(f?[\"']SHOW USER FUNCTIONS IN", "CROSS_CATALOG_SCHEMA_REFERENCE_NOT_SUPPORTED on serverless; query information_schema.routines"),
    (r"mlflow\.deployments", "retries a 429 silently for 10 minutes; use get_open_ai_client().with_options(max_retries=..., timeout=...)"),
]
MARKER_RE = re.compile(r"^(?:#|--|<!--)\s*source:\s*(.+?)\s*(?:-->)?$")


def _text(source) -> str:
    return "".join(source) if isinstance(source, list) else source


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def marker_of(cell: dict) -> str | None:
    lines = _text(cell.get("source", "")).splitlines()
    if not lines:
        return None
    candidates = lines[:2] if lines[0].strip().startswith("%sql") else lines[:1]
    for line in candidates:
        match = MARKER_RE.match(line.strip())
        if match:
            return match.group(1)
    return None


def check_notebook(path: Path, require_markers: bool) -> list[str]:
    findings: list[str] = []
    nb = load(path)
    for index, cell in enumerate(nb.get("cells", []), 1):
        text = _text(cell.get("source", ""))
        where = f"{path.relative_to(ROOT)}:{cell.get('id', index)}"
        for pattern, why in FORBIDDEN:
            if re.search(pattern, text, flags=re.MULTILINE):
                findings.append(f"{where}: forbidden `{pattern}` — {why}")
        if cell["cell_type"] == "code":
            if cell.get("outputs"):
                findings.append(f"{where}: saved outputs")
            if cell.get("execution_count") is not None:
                findings.append(f"{where}: execution_count set")
            stripped = text.lstrip()
            if require_markers and not stripped.startswith("%pip") and marker_of(cell) is None:
                findings.append(f"{where}: missing `# source:` marker")
            if not stripped.startswith("%"):
                try:
                    ast.parse(text, filename=where)
                except SyntaxError as exc:
                    findings.append(f"{where}: python syntax error: {exc}")
        elif require_markers and marker_of(cell) is None:
            findings.append(f"{where}: missing `<!-- source: -->` marker")
    return findings


def check_parity(demo: Path, lab: Path) -> list[str]:
    findings: list[str] = []
    d, l = load(demo), load(lab)
    if len(d["cells"]) != len(l["cells"]):
        return [f"{lab.relative_to(ROOT)}: cell count differs from demo"]
    for solved, task in zip(d["cells"], l["cells"]):
        tags = solved.get("metadata", {}).get("tags", [])
        where = f"{lab.relative_to(ROOT)}:{task.get('id')}"
        if "trainer_only" in tags:
            if task["cell_type"] != "markdown" or "Demo prowadzącego" not in _text(task["source"]):
                findings.append(f"{where}: trainer_only cell not replaced by note")
        elif "solution" in tags:
            if _text(task["source"]) != _text(solved["metadata"]["exercise_source"]):
                findings.append(f"{where}: exercise text differs from exercise_source")
            if "solution" in task.get("metadata", {}).get("tags", []):
                findings.append(f"{where}: solution tag leaked into lab")
        elif _text(task["source"]) != _text(solved["source"]):
            findings.append(f"{where}: non-exercise cell differs from demo (labs are generated — edit demo/)")
    return findings


def main() -> int:
    findings: list[str] = []
    if not any((WORKSHOP / "demo").glob("*.ipynb")):
        findings.append("workshop/demo: no canonical notebooks — nothing to lint")
    for directory in NOTEBOOK_DIRS:
        for path in sorted(directory.glob("*.ipynb")):
            findings += check_notebook(path, require_markers=directory.name in ("demo", "labs", "00_setup", "scripts", "pattern"))
    for demo in sorted((WORKSHOP / "demo").glob("*.ipynb")):
        lab = WORKSHOP / "labs" / demo.name
        if not lab.exists():
            findings.append(f"{lab.relative_to(ROOT)}: missing (run generate_labs.py)")
        else:
            findings += check_parity(demo, lab)
    for line in findings:
        print(line)
    print(f"{len(findings)} finding(s)")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
