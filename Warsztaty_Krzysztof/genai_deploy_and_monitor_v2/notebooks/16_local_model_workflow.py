# Databricks notebook source
# MAGIC %md
# MAGIC # 16 — Local model workflow and offline inference log
# MAGIC
# MAGIC This notebook replaces a serving deployment with a local notebook invocation of the `@champion`
# MAGIC Unity Catalog model. It creates an inference-log Delta table with a stable request identifier.
# MAGIC There is no Model Serving endpoint, secret, AI Gateway, SDK serving call, or network traffic split.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Runtime dependencies

# COMMAND ----------

# MAGIC %pip install --quiet --upgrade "torch>=2.6.0" --index-url https://download.pytorch.org/whl/cpu

# COMMAND ----------

# MAGIC %pip install --quiet "transformers==4.57.1" "sentencepiece>=0.2.0" "safetensors>=0.4.5" "pandas>=2.2"

# COMMAND ----------

dbutils.library.restartPython()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Minimal configuration and prerequisite checks

# COMMAND ----------

catalog = "workspace"
schema = "default"
xsum_table = f"{catalog}.{schema}.xsum_summaries_v2"
registered_model_name = f"{catalog}.{schema}.xsum_t5_small_summarizer_v2"
offline_payload_table = f"{catalog}.{schema}.offline_inference_payload_v2"
model_uri = f"models:/{registered_model_name}@champion"
request_batch_size = 12

if not spark.catalog.tableExists(xsum_table) or spark.table(xsum_table).limit(1).count() == 0:
    raise RuntimeError(
        f"Run 15_offline_batch_inference first. The required source table is missing or empty: {xsum_table}"
    )

print(f"Input table: {xsum_table}")
print(f"Local model URI: {model_uri}")
print(f"Offline inference log: {offline_payload_table}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Prepare deterministic offline inference requests
# MAGIC
# MAGIC These records deliberately resemble a small captured inference workload, but they are created inside
# MAGIC Delta rather than automatically captured from an endpoint. Stable request IDs make reruns idempotent.

# COMMAND ----------

import hashlib
from pyspark.sql import functions as F


def stable_request_id(source_id: str, model_reference: str) -> str:
    """Create a repeatable request identifier for one source record and model version."""
    return hashlib.sha256(f"{source_id}|{model_reference}".encode("utf-8")).hexdigest()


request_rows = spark.table(xsum_table).orderBy("source_id").limit(request_batch_size).collect()
request_records = [
    {
        "request_id": stable_request_id(row.source_id, model_uri),
        "source_id": row.source_id,
        "input_text": row.document,
        "model_uri": model_uri,
    }
    for row in request_rows
]

requests_df = spark.createDataFrame(request_records)
display(requests_df.select("request_id", "source_id", "model_uri").limit(5))

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Load the champion model locally and generate responses
# MAGIC
# MAGIC This is the offline equivalent of an inference request: the model is loaded with MLflow PyFunc in the
# MAGIC notebook process, then called for a small batch. It is not deployed to or called through an endpoint.

# COMMAND ----------

import time
import pandas as pd
import mlflow


def run_local_inference(model_reference: str, input_texts: list[str]) -> tuple[list[str], float]:
    """Load the self-contained Unity Catalog PyFunc model and return its string summaries."""
    local_model = mlflow.pyfunc.load_model(model_reference)
    started_at = time.perf_counter()
    raw_predictions = local_model.predict(input_texts)
    elapsed_ms = round((time.perf_counter() - started_at) * 1000, 2)
    if not isinstance(raw_predictions, list) or not all(isinstance(item, str) for item in raw_predictions):
        raise TypeError("The registered PyFunc model must return a list of summary strings.")
    return raw_predictions, elapsed_ms


requests_pdf = requests_df.toPandas()
generated_summaries, total_elapsed_ms = run_local_inference(model_uri, requests_pdf["input_text"].tolist())

if len(generated_summaries) != len(requests_pdf):
    raise RuntimeError("The local model did not return exactly one output per offline request.")

requests_pdf["output_text"] = generated_summaries
requests_pdf["timestamp"] = pd.Timestamp.now(tz="UTC")
requests_pdf["latency_ms"] = round(total_elapsed_ms / len(requests_pdf), 2)
requests_pdf["status"] = "OK"
requests_pdf["execution_mode"] = "local_mlflow_pyfunc"

offline_payload_df = spark.createDataFrame(requests_pdf)
display(offline_payload_df.select("request_id", "input_text", "output_text", "latency_ms", "status").limit(5))

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Write an idempotent Delta inference log
# MAGIC
# MAGIC Existing request IDs are retained. Re-running this notebook with the same champion model therefore
# MAGIC does not duplicate already logged inference records.

# COMMAND ----------

if not spark.catalog.tableExists(offline_payload_table):
    offline_payload_df.write.format("delta").mode("overwrite").saveAsTable(offline_payload_table)
    print(f"Created {offline_payload_table}.")
else:
    offline_payload_df.createOrReplaceTempView("offline_payload_upserts_v2")
    spark.sql(
        f"""
        MERGE INTO {offline_payload_table} AS target
        USING offline_payload_upserts_v2 AS source
        ON target.request_id = source.request_id
        WHEN NOT MATCHED THEN INSERT *
        """
    )
    print(f"Merged new offline requests into {offline_payload_table}.")

display(spark.table(offline_payload_table).orderBy(F.desc("timestamp")).limit(10))

# COMMAND ----------

# MAGIC %md
# MAGIC ## Validation

# COMMAND ----------

assert spark.table(offline_payload_table).limit(1).count() == 1, "The offline payload table is empty."
duplicate_count = (
    spark.table(offline_payload_table)
    .groupBy("request_id")
    .count()
    .filter("count > 1")
    .count()
)
assert duplicate_count == 0, "Offline inference logging created duplicate request IDs."
print("Local model workflow validation completed successfully.")
