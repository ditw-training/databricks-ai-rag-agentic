"""Static checks for workshop notebooks: structure, lint, labs parity, schedule, naming."""
import json
import re
import sys
from pathlib import Path

import nbformat
import pytest

ROOT = Path(__file__).resolve().parents[2]
WORKSHOP = ROOT / "workshop"
DEMO, LABS, SETUP, SCRIPTS = WORKSHOP / "demo", WORKSHOP / "labs", WORKSHOP / "00_setup", WORKSHOP / "scripts"
sys.path.insert(0, str(SCRIPTS))
from check_notebooks import check_notebook, check_parity, marker_of  # noqa: E402
from generate_labs import derive_lab  # noqa: E402

MODULES = {
    "m1_agentic_ai_playground.ipynb": 60,
    "m2_tool_calling.ipynb": 75,
    "m3_rag_ai_search.ipynb": 90,
    "m4_sql_genie_governance.ipynb": 55,
    "m5_end_to_end_agent.ipynb": 70,
    "m6_mcp_security_next_steps.ipynb": 35,
}
SETUP_NOTEBOOKS = ["00_setup.ipynb", "01_trainer_prepare_premium.ipynb", "02_trainer_teardown.ipynb"]
TEACHING_MINUTES = 430  # 45 (M0) + 60 + 75 + 90 + 55 + 70 + 35


def load(path: Path):
    notebook = nbformat.read(path, as_version=4)
    nbformat.validate(notebook)
    return notebook


def text_of(path: Path) -> str:
    return "\n".join(cell.source for cell in load(path).cells)


def test_expected_notebook_sets():
    assert sorted(p.name for p in DEMO.glob("*.ipynb")) == sorted(MODULES)
    assert sorted(p.name for p in LABS.glob("*.ipynb")) == sorted(MODULES)
    assert sorted(p.name for p in SETUP.glob("*.ipynb")) == sorted(SETUP_NOTEBOOKS)
    assert (SCRIPTS / "prepare_data_premium.ipynb").exists()


@pytest.mark.parametrize("path", sorted(list(DEMO.glob("*.ipynb")) + list(SETUP.glob("*.ipynb")) + list(SCRIPTS.glob("*.ipynb")) + list(LABS.glob("*.ipynb"))), ids=lambda p: p.name)
def test_notebook_is_valid_and_lint_clean(path):
    load(path)
    assert check_notebook(path, require_markers=True) == []


@pytest.mark.parametrize("name", sorted(MODULES), ids=lambda n: n)
def test_labs_are_generated_from_demo(name):
    demo, lab = DEMO / name, LABS / name
    assert check_parity(demo, lab) == []
    regenerated = derive_lab(json.loads(demo.read_text(encoding="utf-8")))
    assert regenerated == json.loads(lab.read_text(encoding="utf-8")), "labs/ is stale — run generate_labs.py"


@pytest.mark.parametrize("name, minutes", sorted(MODULES.items()), ids=lambda v: str(v))
def test_module_declares_schedule_minutes(name, minutes):
    intro = load(DEMO / name).cells[0].source
    assert f"**Czas:** {minutes} min" in intro


def test_schedule_document_sums_to_teaching_minutes():
    schedule = (WORKSHOP / "docs" / "schedule.md").read_text(encoding="utf-8")
    assert str(TEACHING_MINUTES) in schedule
    assert sum(MODULES.values()) + 45 == TEACHING_MINUTES


def test_every_module_has_labs_and_config_and_summary():
    for name in MODULES:
        nb = load(DEMO / name)
        tags = [t for cell in nb.cells for t in cell.metadata.get("tags", [])]
        assert "solution" in tags, f"{name}: no lab cells"
        code = [cell.source for cell in nb.cells if cell.cell_type == "code"]
        assert any("SYSTEM_PROMPT = (" in src and "GOLD_TABLE = " in src for src in code), f"{name}: shared config cell missing"
        headings = "\n".join(cell.source for cell in nb.cells if cell.cell_type == "markdown")
        assert "## Podsumowanie" in headings, f"{name}: no summary"


def test_current_product_names_and_agenda_evidence():
    demo_text = "\n".join(text_of(DEMO / name) for name in MODULES)
    for needle in ("AI Search", "Genie Agent", "Unity Gateway", "ResponsesAgent", "MCP", "Databricks Apps", "Free Edition"):
        assert needle in demo_text, needle
    assert "Vector Search" in demo_text  # explained as the former name
    m5 = text_of(DEMO / "m5_end_to_end_agent.ipynb")
    assert "search_retail_reports" in m5 and "intermediate_steps" in m5 and "expected_route" in m5
    assert m5.index("mlflow.langchain.autolog()") < m5.index("create_tool_calling_agent(")
    m6 = text_of(DEMO / "m6_mcp_security_next_steps.ipynb")
    assert "/api/2.0/mcp/functions/" in m6 and "prompt=SYSTEM_PROMPT" in m6
    m4 = text_of(DEMO / "m4_sql_genie_governance.ipynb")
    assert "DROP ROW FILTER" in m4 and "DROP MASK" in m4


def test_source_markers_point_to_known_material():
    pattern = re.compile(r"^(new|WS[1-4]\[\d+(?:[–-]\d+)?\]|PRZ\[\d+\]|slide \d+(?:[–-]\d+)?|K:[\w/.\-]+)$")
    for path in list(DEMO.glob("*.ipynb")) + list(SETUP.glob("*.ipynb")) + list(SCRIPTS.glob("*.ipynb")):
        for cell in load(path).cells:
            marker = marker_of(cell)
            if cell.cell_type == "code" and cell.source.lstrip().startswith("%pip"):
                continue
            assert marker, (path.name, cell.id)
            for part in re.split(r"\s*\+\s*", marker):
                assert pattern.match(part), (path.name, cell.id, marker)


def test_no_new_pdf_or_presentation_outside_data_documents():
    for suffix in ("*.pdf", "*.pptx"):
        for path in WORKSHOP.rglob(suffix):
            assert path.parent == WORKSHOP / "data" / "documents", path
