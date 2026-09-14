# Databricks notebook source
# MAGIC %md
# MAGIC # 03 — AI Search for robotics document chunks
# MAGIC
# MAGIC This notebook continues after `01_parse_robotics_documents` and `02_chunking`.
# MAGIC It prepares a Delta source table, creates an AI Search endpoint and a managed
# MAGIC Delta Sync index, then demonstrates four retrieval modes and reranking.

# COMMAND ----------

# MAGIC %md
# MAGIC ## 0. Install required SDK packages
# MAGIC
# MAGIC Run this cell once. After Python restarts, continue from section 1.

# COMMAND ----------

# MAGIC %pip install --upgrade --force-reinstall databricks-ai-search "databricks-sdk>=0.57.0"

# COMMAND ----------

# Restart Python so the newly installed AI Search SDK is available to later cells.
dbutils.library.restartPython()

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Minimal configuration

# COMMAND ----------

from __future__ import annotations

import json
import time
from typing import Any

from pyspark.sql import functions as F
from pyspark.sql.utils import AnalysisException

# Keep names fixed to match the earlier course notebooks in the workspace catalog.
catalog = "workspace"
schema = "default"
chunked_source_table = f"{catalog}.{schema}.robotics_document_chunks"
docs_table = f"{catalog}.{schema}.docs_chunked"
ai_search_endpoint_name = "robotics_ai_search_endpoint"
ai_search_index_name = f"{catalog}.{schema}.robotics_document_chunks_index"
embedding_model_endpoint = "databricks-gte-large-en"

# Return these source columns in every retrieval example and use path as a filterable field.
search_result_columns = ["chunk_id", "path", "chunk_position", "chunk_text"]
required_chunk_columns = set(search_result_columns)

print(f"Chunk source table: {chunked_source_table}")
print(f"AI Search source table: {docs_table}")
print(f"AI Search endpoint: {ai_search_endpoint_name}")
print(f"AI Search index: {ai_search_index_name}")
print(f"Embedding endpoint: {embedding_model_endpoint}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Prepare `docs_chunked`, enable Change Data Feed, and preview data

# COMMAND ----------

def raise_source_table_error(error: Exception) -> None:
    """Raise an actionable error when notebook 02 has not produced its Delta output."""
    raise RuntimeError(
        f"Cannot read {chunked_source_table}. Run notebook 02_chunking through section 5 first, "
        "then rerun this notebook from section 2."
    ) from error


try:
    source_chunk_df = spark.table(chunked_source_table)
    source_chunk_count = source_chunk_df.limit(1).count()
except AnalysisException as source_error:
    raise_source_table_error(source_error)

if source_chunk_count == 0:
    raise ValueError(f"{chunked_source_table} is empty. Run notebook 02_chunking again before creating the index.")

# Create the course-named Delta table once, leaving the output of notebook 02 unchanged.
if not spark.catalog.tableExists(docs_table):
    spark.sql(
        f"""
        CREATE TABLE {docs_table}
        TBLPROPERTIES (delta.enableChangeDataFeed = true)
        AS SELECT * FROM {chunked_source_table}
        """
    )
    print(f"Created {docs_table} from {chunked_source_table}.")
else:
    print(f"Using existing table: {docs_table}")

# CDF is mandatory for a Delta Sync index on a Standard AI Search endpoint.
spark.sql(f"ALTER TABLE {docs_table} SET TBLPROPERTIES (delta.enableChangeDataFeed = true)")
docs_columns = set(spark.table(docs_table).columns)
missing_columns = required_chunk_columns - docs_columns
if missing_columns:
    raise ValueError(
        f"{docs_table} is missing required columns: {sorted(missing_columns)}. "
        "Drop and recreate this course table after running notebook 02_chunking with the expected schema."
    )

cdf_row = spark.sql(f"SHOW TBLPROPERTIES {docs_table} ('delta.enableChangeDataFeed')").first()
if cdf_row is None or str(cdf_row[1]).lower() != "true":
    raise RuntimeError(
        f"Change Data Feed is not enabled for {docs_table}. Verify ALTER TABLE privileges and run this cell again."
    )

display(spark.table(docs_table).orderBy("path", "chunk_position").limit(5))

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Compute one embedding with Model Serving

# COMMAND ----------

import mlflow.deployments


def response_value(payload: Any, field_name: str) -> Any:
    """Read a field from either a dictionary response or an SDK response object."""
    if isinstance(payload, dict):
        return payload.get(field_name)
    return getattr(payload, field_name, None)


def embedding_setup_error(error: Exception) -> None:
    """Explain the Model Serving prerequisites when the embedding request fails."""
    raise RuntimeError(
        f"Could not call the embedding endpoint '{embedding_model_endpoint}'. Confirm that the endpoint exists, "
        "is ready, and that you have Can Query permission."
    ) from error


# Use the Databricks deployment client requested by the course workflow.
deploy_client = mlflow.deployments.get_deploy_client("databricks")
embedding_question = "How generative AI impacts humans?"

try:
    embedding_response = deploy_client.predict(
        endpoint=embedding_model_endpoint,
        inputs={"input": [embedding_question]},
    )
except Exception as embedding_error:
    embedding_setup_error(embedding_error)

embedding_rows = response_value(embedding_response, "data")
if not embedding_rows:
    raise RuntimeError(f"The endpoint '{embedding_model_endpoint}' returned no embedding data: {embedding_response}")

question_embedding = response_value(embedding_rows[0], "embedding")
if not question_embedding:
    raise RuntimeError(f"The endpoint '{embedding_model_endpoint}' response has no embedding vector: {embedding_response}")

embedding_shape = (len(question_embedding),)
embedding_info = {
    "endpoint": embedding_model_endpoint,
    "question": embedding_question,
    "response_type": type(embedding_response).__name__,
    "embedding_shape": embedding_shape,
}
print(json.dumps(embedding_info, indent=2))
print(f"Embedding shape: {embedding_shape}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Create the AI Search endpoint and managed Delta Sync index

# COMMAND ----------

from databricks.ai_search.client import AISearchClient
from databricks.sdk import WorkspaceClient


def is_not_found_error(error: Exception) -> bool:
    """Identify SDK not-found responses without treating permission failures as missing resources."""
    error_text = str(error).upper()
    not_found_markers = (
        "NOT_FOUND",
        "RESOURCE_DOES_NOT_EXIST",
        "STATUS_CODE: 404",
        "HTTP 404",
        "STATUS 404",
        "DOES NOT EXIST",
    )
    return any(marker in error_text for marker in not_found_markers)


def ai_search_setup_error(action: str, error: Exception) -> None:
    """Raise a concise diagnostic for AI Search availability, privilege, and service errors."""
    raise RuntimeError(
        f"AI Search could not {action}. Check that Unity Catalog and serverless are enabled, AI Search is "
        "available in this workspace, and that you have endpoint ACL plus CREATE TABLE and table access privileges. "
        "In the current UI, open Compute > AI Search to inspect endpoint availability. "
        f"Original API error: {type(error).__name__}: {error}"
    ) from error


def wait_for_endpoint_online(client: AISearchClient, endpoint_name: str, timeout_seconds: int = 900) -> dict[str, Any]:
    """Poll an AI Search endpoint until it is online or reports a terminal failure."""
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        endpoint = client.get_endpoint(name=endpoint_name)
        endpoint_json = json.dumps(endpoint, default=str).upper()
        if "ONLINE" in endpoint_json:
            return endpoint
        if "FAILED" in endpoint_json or "ERROR" in endpoint_json:
            raise RuntimeError(f"AI Search endpoint reported a failure: {endpoint}")
        print(f"Waiting for AI Search endpoint '{endpoint_name}' to become ONLINE...")
        time.sleep(10)
    raise TimeoutError(f"AI Search endpoint '{endpoint_name}' did not become ONLINE within {timeout_seconds} seconds.")


def wait_for_index_online(index: Any, timeout_seconds: int = 1800) -> dict[str, Any]:
    """Poll a Delta Sync index until its initial ingestion reaches an online state."""
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        index_description = index.describe()
        detailed_state = str(index_description.get("status", {}).get("detailed_state", ""))
        state_upper = detailed_state.upper()
        if state_upper.startswith("ONLINE"):
            return index_description
        if "FAILED" in state_upper or "ERROR" in state_upper:
            raise RuntimeError(f"AI Search index reported a failure: {index_description}")
        print(f"Waiting for index '{ai_search_index_name}' to become ONLINE (state: {detailed_state or 'unknown'})...")
        time.sleep(10)
    raise TimeoutError(f"AI Search index '{ai_search_index_name}' did not become ONLINE within {timeout_seconds} seconds.")


# WorkspaceClient uses the notebook identity and makes the Databricks SDK connection explicit.
workspace_client = WorkspaceClient()
print(f"Connected workspace host: {workspace_client.config.host}")

# AISearchClient is the current Databricks AI Search Python SDK client.
ai_search_client = AISearchClient()

try:
    endpoint_details = ai_search_client.get_endpoint(name=ai_search_endpoint_name)
    print(f"Using existing AI Search endpoint: {ai_search_endpoint_name}")
except Exception as endpoint_lookup_error:
    if not is_not_found_error(endpoint_lookup_error):
        ai_search_setup_error(f"read endpoint '{ai_search_endpoint_name}'", endpoint_lookup_error)
    try:
        ai_search_client.create_endpoint(name=ai_search_endpoint_name, endpoint_type="STANDARD")
        print(f"Created AI Search endpoint: {ai_search_endpoint_name}")
    except Exception as endpoint_create_error:
        ai_search_setup_error(f"create endpoint '{ai_search_endpoint_name}'", endpoint_create_error)

try:
    endpoint_details = wait_for_endpoint_online(ai_search_client, ai_search_endpoint_name)
    print(json.dumps(endpoint_details, indent=2, default=str))
except Exception as endpoint_wait_error:
    ai_search_setup_error(f"wait for endpoint '{ai_search_endpoint_name}'", endpoint_wait_error)

try:
    index = ai_search_client.get_index(
        endpoint_name=ai_search_endpoint_name,
        index_name=ai_search_index_name,
    )
    index_was_created = False
    print(f"Using existing AI Search index: {ai_search_index_name}")
except Exception as index_lookup_error:
    if not is_not_found_error(index_lookup_error):
        ai_search_setup_error(f"read index '{ai_search_index_name}'", index_lookup_error)
    try:
        index = ai_search_client.create_delta_sync_index(
            endpoint_name=ai_search_endpoint_name,
            source_table_name=docs_table,
            index_name=ai_search_index_name,
            pipeline_type="TRIGGERED",
            primary_key="chunk_id",
            embedding_source_column="chunk_text",
            embedding_model_endpoint_name=embedding_model_endpoint,
            columns_to_sync=["path", "chunk_position"],
        )
        index_was_created = True
        print(f"Created managed Delta Sync index: {ai_search_index_name}")
    except Exception as index_create_error:
        ai_search_setup_error(f"create index '{ai_search_index_name}'", index_create_error)

# A newly created index starts its first ingestion automatically and cannot accept sync requests yet.
try:
    if index_was_created:
        print("Waiting for the initial Delta Sync index ingestion to finish.")
        index_description = wait_for_index_online(index)
    else:
        # Wait for a previously created index before requesting an incremental triggered refresh.
        wait_for_index_online(index)
        index.sync()
        print("Started a Delta Sync index refresh.")
        index_description = wait_for_index_online(index)
    print(json.dumps(index_description, indent=2, default=str))
except Exception as index_wait_error:
    ai_search_setup_error(f"initialize or sync index '{ai_search_index_name}'", index_wait_error)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 5. Shared helpers for displaying retrieval output

# COMMAND ----------

def display_search_output(search_name: str, prompt: str, result: Any) -> None:
    """Display the prompt and JSON response from one AI Search query in a small table."""
    result_json = json.dumps(result, indent=2, default=str)
    print(f"{search_name} prompt: {prompt}")
    display(
        spark.createDataFrame(
            [(search_name, prompt, result_json)],
            ["search_type", "prompt", "result_json"],
        )
    )


def run_search(search_name: str, prompt: str, **search_arguments: Any) -> Any:
    """Run one AI Search request and attach a readable error if the index cannot be queried."""
    try:
        result = index.similarity_search(
            query_text=prompt,
            columns=search_result_columns,
            num_results=3,
            **search_arguments,
        )
    except Exception as search_error:
        raise RuntimeError(
            f"{search_name} failed. Confirm that index '{ai_search_index_name}' is ONLINE and that you have SELECT permission on it."
        ) from search_error
    display_search_output(search_name, prompt, result)
    return result

# COMMAND ----------

# MAGIC %md
# MAGIC ## 6. Query search (ANN)

# COMMAND ----------

# ANN is the default semantic vector search mode for a managed-embedding Delta Sync index.
ann_prompt = "How do mobile robots avoid obstacles while moving?"
ann_results = run_search("ANN query search", ann_prompt, query_type="ann")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 7. Hybrid search

# COMMAND ----------

# Hybrid search combines semantic similarity with keyword matching.
hybrid_prompt = "How do collaborative robots work safely with people?"
hybrid_results = run_search("Hybrid search", hybrid_prompt, query_type="hybrid")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 8. Full-text search

# COMMAND ----------

# Full-text search retrieves chunks using keyword matching on the managed Delta Sync index.
full_text_prompt = "sensors and actuators"
full_text_results = run_search("Full-text search", full_text_prompt, query_type="FULL_TEXT")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 9. Query search filtered by document path

# COMMAND ----------

# Prefer a robot-arm document when it is present, otherwise use the first available source path.
path_source_df = spark.table(docs_table)
path_row = (
    path_source_df.where(F.lower(F.col("path")).contains("arm"))
    .select("path")
    .orderBy("path")
    .first()
)
if path_row is None:
    path_row = path_source_df.select("path").orderBy("path").first()
if path_row is None:
    raise RuntimeError(f"No document paths are available in {docs_table}.")

selected_path = path_row["path"]
path_filter_prompt = "How do robot arms achieve precise motion?"
path_filtered_results = run_search(
    "Path-filtered query search",
    path_filter_prompt,
    query_type="ann",
    filters={"path": selected_path},
)
print(f"Applied path filter: {selected_path}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 10. Hybrid search with Databricks reranking

# COMMAND ----------

from databricks.ai_search.reranker import DatabricksReranker

# Reuse the hybrid question and compare its original ranking with a second-pass reranked result.
display_search_output("Hybrid search before reranking", hybrid_prompt, hybrid_results)

try:
    reranked_results = index.similarity_search(
        query_text=hybrid_prompt,
        columns=search_result_columns,
        num_results=3,
        query_type="hybrid",
        reranker=DatabricksReranker(columns_to_rerank=["chunk_text"]),
        debug_level=1,
    )
except Exception as reranking_error:
    raise RuntimeError(
        "Reranking failed. Confirm that the current AI Search SDK is installed and that reranking is available "
        f"for this workspace and region. Original API error: {type(reranking_error).__name__}: {reranking_error}"
    ) from reranking_error

display_search_output("Hybrid search after Databricks reranking", hybrid_prompt, reranked_results)
