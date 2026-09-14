"""Integrity checks for prepared participant data (skipped until the trainer exports it)."""
import hashlib
import json
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "workshop" / "data"
MANIFEST = DATA / "manifest.json"

EXPECTED_ROWS = 28_813
EXPECTED_COLUMNS = [
    "customer_id", "customer_name", "tax_id", "state", "city", "loyalty_segment", "units_purchased", "lat", "lon",
    "recency_days", "frequency", "num_orders", "monetary", "avg_item_value", "promo_orders", "first_order_date",
    "last_order_date", "has_orders", "promo_ratio",
]
EXPECTED_SEGMENTS = {0: 11_097, 1: 3_883, 2: 4_292, 3: 9_541}
MAX_TOTAL_BYTES = 20 * 1024 * 1024


def _needs(path: Path):
    if not path.exists():
        pytest.skip(f"{path.relative_to(ROOT)} not prepared yet — run workshop/scripts/prepare_data_premium.ipynb and build_manifest.py")


def test_manifest_matches_files():
    _needs(MANIFEST)
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    total = 0
    for entry in manifest["files"]:
        path = DATA / entry["path"]
        assert path.is_file(), entry["path"]
        data = path.read_bytes()
        total += len(data)
        assert len(data) == entry["bytes"], entry["path"]
        assert hashlib.sha256(data).hexdigest() == entry["sha256"], entry["path"]
    assert total <= MAX_TOTAL_BYTES


def test_gold_table_shape_and_pseudonymisation():
    path = DATA / "tables" / "gold_customer_360.parquet"
    _needs(path)
    pd = pytest.importorskip("pandas")
    frame = pd.read_parquet(path)
    assert len(frame) == EXPECTED_ROWS
    assert list(frame.columns) == EXPECTED_COLUMNS
    assert frame.groupby("loyalty_segment").size().to_dict() == EXPECTED_SEGMENTS
    tax = frame["tax_id"].dropna()
    assert 0.6 < frame["tax_id"].isna().mean() < 0.75
    assert tax.map(lambda v: bool(re.fullmatch(r"\d{2}-\d{7}", str(v)))).all()
    assert frame["customer_name"].str.startswith("Customer ").all()
    assert frame["state"].notna().all()


def test_documents_and_checkpoints():
    docs = DATA / "documents"
    _needs(docs)
    pdfs = sorted(docs.glob("*.pdf"))
    assert len(pdfs) == 10
    assert pdfs[0].name.startswith("01_") and pdfs[-1].name.startswith("10_")
    pd = pytest.importorskip("pandas")
    chunks = pd.read_parquet(DATA / "checkpoints" / "retail_rag_chunks.parquet")
    assert 30 <= len(chunks) <= 120
    assert {"chunk_id", "doc_id", "filename", "chunk_position", "content"} <= set(chunks.columns)
    assert chunks["chunk_id"].is_unique
    embeddings = pd.read_parquet(DATA / "checkpoints" / "retail_rag_chunk_embeddings.parquet")
    assert len(embeddings) == len(chunks)
    assert set(embeddings["chunk_id"]) == set(chunks["chunk_id"])
    assert len(embeddings["embedding"].iloc[0]) == 1024
    docs_table = pd.read_parquet(DATA / "checkpoints" / "retail_rag_docs.parquet")
    assert len(docs_table) == 10 and "parsed_json" not in docs_table.columns


def test_route_test_cases_cover_five_routes():
    path = DATA / "evaluation" / "route_test_cases.json"
    _needs(path)
    cases = json.loads(path.read_text(encoding="utf-8"))
    routes = {case["expected_route"] for case in cases}
    assert {"function", "RAG", "oba", "odmowa", "fallback"} <= routes
    assert all({"id", "question", "expected_route"} <= set(case) for case in cases)


def test_genie_baseline_is_dated():
    path = DATA / "evaluation" / "genie_baseline_scores.json"
    _needs(path)
    baseline = json.loads(path.read_text(encoding="utf-8"))
    assert re.match(r"\d{4}-\d{2}-\d{2}", baseline["evaluated_at"])
    assert {"safety", "correctness", "no_pii_leak", "retail_domain"} <= set(baseline["scores"])
