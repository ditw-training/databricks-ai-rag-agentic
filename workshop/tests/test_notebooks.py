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
PATTERN = WORKSHOP / "pattern"
sys.path.insert(0, str(SCRIPTS))
from check_notebooks import check_notebook, check_parity, marker_of  # noqa: E402
from generate_labs import derive_lab  # noqa: E402

MODULES = [
    "m1_agentic_ai_playground.ipynb",
    "m2_tool_calling.ipynb",
    "m3_rag_ai_search.ipynb",
    "m4_sql_genie_governance.ipynb",
    "m5_end_to_end_agent.ipynb",
    "m5b_transfer_capstone.ipynb",
    "m6_mcp_security_next_steps.ipynb",
]
PATTERN_NOTEBOOKS = ["p2_uc_functions_bakehouse.ipynb", "p3_rag_robotics.ipynb"]
SETUP_NOTEBOOKS = ["00_setup.ipynb", "01_trainer_prepare_premium.ipynb", "02_trainer_teardown.ipynb"]
# Timing lives only in docs/schedule.md; notebooks stay free of minutes so trainers can pace the day.
SCHEDULE_MINUTES = [45, 55, 70, 80, 50, 60, 40, 30]  # M0, M1-M5, capstone, M6


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
    assert sorted(p.name for p in PATTERN.glob("*.ipynb")) == sorted(PATTERN_NOTEBOOKS)


@pytest.mark.parametrize("path", sorted(list(DEMO.glob("*.ipynb")) + list(SETUP.glob("*.ipynb")) + list(SCRIPTS.glob("*.ipynb")) + list(LABS.glob("*.ipynb")) + list(PATTERN.glob("*.ipynb"))), ids=lambda p: p.name)
def test_notebook_is_valid_and_lint_clean(path):
    load(path)
    assert check_notebook(path, require_markers=True) == []


@pytest.mark.parametrize("name", sorted(MODULES), ids=lambda n: n)
def test_labs_are_generated_from_demo(name):
    demo, lab = DEMO / name, LABS / name
    assert check_parity(demo, lab) == []
    regenerated = derive_lab(json.loads(demo.read_text(encoding="utf-8")))
    assert regenerated == json.loads(lab.read_text(encoding="utf-8")), "labs/ is stale — run generate_labs.py"


@pytest.mark.parametrize("path", sorted(list(DEMO.glob("*.ipynb")) + list(SETUP.glob("*.ipynb")) + list(SCRIPTS.glob("*.ipynb")) + list(PATTERN.glob("*.ipynb"))), ids=lambda p: p.name)
def test_notebooks_have_no_timeboxes(path):
    nb = json.loads(path.read_text(encoding="utf-8"))
    assert "minutes" not in nb["metadata"].get("workshop", {})
    for cell in nb["cells"]:
        texts = ["".join(cell["source"]), "".join(cell.get("metadata", {}).get("exercise_source") or [])]
        for text in texts:
            assert not re.search(r"\d+\s?(min\b|minut)|\*\*Czas:\*\*", text), f"{path.name}/{cell.get('id')}: minutes in notebook"


SERVERLESS_ENVIRONMENT_VERSION = "5"  # Python 3.12; an imported notebook without it falls back to version 1 (Python 3.10)


@pytest.mark.parametrize("path", sorted(list(DEMO.glob("*.ipynb")) + list(LABS.glob("*.ipynb")) + list(SETUP.glob("*.ipynb")) + list(SCRIPTS.glob("*.ipynb")) + list(PATTERN.glob("*.ipynb"))), ids=lambda p: p.name)
def test_notebooks_pin_serverless_environment(path):
    meta = json.loads(path.read_text(encoding="utf-8"))["metadata"].get("application/vnd.databricks.v1+notebook", {})
    assert meta.get("environmentMetadata", {}).get("environment_version") == SERVERLESS_ENVIRONMENT_VERSION


def test_pandas_exports_clear_spark_connect_attrs():
    # Spark Connect puts PlanMetrics into DataFrame.attrs; to_parquet then fails with
    # "Object of type PlanMetrics is not JSON serializable" (trial dry-run 2026-09-15).
    for path in sorted(list(DEMO.glob("*.ipynb")) + list(SETUP.glob("*.ipynb")) + list(SCRIPTS.glob("*.ipynb")) + list(PATTERN.glob("*.ipynb"))):
        for cell in json.loads(path.read_text(encoding="utf-8"))["cells"]:
            text = "".join(cell["source"])
            if "to_parquet(" in text and "toPandas()" in text:
                assert text.count(".attrs.clear()") >= text.count("toPandas()"), f"{path.name}/{cell.get('id')}"


def test_schedule_document_sums_to_teaching_minutes():
    schedule = (WORKSHOP / "docs" / "schedule.md").read_text(encoding="utf-8")
    assert str(sum(SCHEDULE_MINUTES)) in schedule


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
    assert "/api/2.0/mcp/functions/" in m6 and "system_prompt=SYSTEM_PROMPT" in m6
    m4 = text_of(DEMO / "m4_sql_genie_governance.ipynb")
    assert "DROP ROW FILTER" in m4 and "DROP MASK" in m4


def test_source_markers_point_to_known_material():
    pattern = re.compile(r"^(new|WS[1-4]\[\d+(?:[–-]\d+)?\]|PRZ\[\d+\]|slide \d+(?:[–-]\d+)?|K:[\w/.\-]+)$")
    for path in list(DEMO.glob("*.ipynb")) + list(SETUP.glob("*.ipynb")) + list(SCRIPTS.glob("*.ipynb")) + list(PATTERN.glob("*.ipynb")):
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


def _config_source(path: Path) -> str:
    cells = [cell.source for cell in load(path).cells
             if cell.cell_type == "code" and re.search(r"^SYSTEM_PROMPT = \(", cell.source, flags=re.MULTILINE) and "GOLD_TABLE = " in cell.source]
    assert len(cells) == 1, f"{path.name}: expected exactly one shared config cell"
    return cells[0]


def test_shared_config_cell_is_identical_everywhere():
    reference = _config_source(SETUP / "00_setup.ipynb")
    for path in [DEMO / name for name in MODULES] + [SETUP / name for name in SETUP_NOTEBOOKS] + [PATTERN / name for name in PATTERN_NOTEBOOKS]:
        assert _config_source(path) == reference, f"{path.name}: config differs from 00_setup (copy the cell 1:1)"


def test_requirements_pin_mcp_below_2():
    requirements = (WORKSHOP / "requirements.txt").read_text(encoding="utf-8")
    assert re.search(r"^mcp>=[\d.]+,<2", requirements, flags=re.MULTILINE), "mcp 2.x breaks `import databricks_langchain`"


def test_labs_keep_exercises_runnable_as_python():
    for name in MODULES:
        for cell in load(LABS / name).cells:
            if "exercise" in cell.metadata.get("tags", []):
                assert "TODO" in cell.source, f"{name}:{cell.id}: exercise without TODO"


def test_day_concept_levels_cards_and_capstone():
    for name in [n for n in MODULES if n != "m5b_transfer_capstone.ipynb"]:
        headings = "\n".join(cell.source for cell in load(DEMO / name).cells if cell.cell_type == "markdown")
        assert "## Karta wzorca:" in headings, f"{name}: no pattern card"
    for name in ("m1_agentic_ai_playground.ipynb", "m2_tool_calling.ipynb", "m3_rag_ai_search.ipynb",
                 "m4_sql_genie_governance.ipynb", "m5_end_to_end_agent.ipynb"):
        headings = "\n".join(cell.source for cell in load(DEMO / name).cells if cell.cell_type == "markdown")
        assert "## Poziomy 2 i 3" in headings, f"{name}: no level 2/3 tasks"
    capstone = text_of(DEMO / "m5b_transfer_capstone.ipynb")
    for needle in ("samples.bakehouse", "sf_airbnb_listings.csv", "MY_ROUTE_CASES", "route_case", "Bezpieczeństwo danych"):
        assert needle in capstone, needle
    assert (WORKSHOP / "transfer" / "canvas_agenta.md").exists()
    assert (WORKSHOP / "data" / "practice" / "sf_airbnb_listings.csv").exists()
