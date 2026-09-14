# Databricks notebook source
# MAGIC %md
# MAGIC # 17 — Offline inference monitoring
# MAGIC
# MAGIC This notebook monitors the Delta inference log produced by notebook 16. It computes text metrics,
# MAGIC writes processed records, and creates five-minute profile and drift tables. It intentionally replaces
# MAGIC AI Gateway capture, streaming, and the managed Data Quality monitor with repeatable offline batches.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Runtime dependencies
# MAGIC
# MAGIC Metric models are downloaded from Hugging Face on first use into the local Serverless disk. Each metric
# MAGIC has independent error handling, so a temporary model-download failure is recorded instead of preventing
# MAGIC readability or other available metrics from being written.

# COMMAND ----------

# MAGIC %pip install --quiet --upgrade "torch>=2.6.0" --index-url https://download.pytorch.org/whl/cpu

# COMMAND ----------

# MAGIC %pip install --quiet --upgrade "evaluate==0.4.3" "textstat>=0.7.4" "transformers==4.57.1" "huggingface_hub>=0.34.0" "safetensors>=0.4.5" "sentencepiece>=0.2.0" "pandas>=2.2"

# COMMAND ----------

dbutils.library.restartPython()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Hugging Face environment configuration
# MAGIC
# MAGIC The Xet/CAS transfer path is disabled before importing `evaluate`, `transformers`, or
# MAGIC `huggingface_hub`. Metric artifacts use the local Serverless disk rather than a mounted Volume.

# COMMAND ----------

import os
from pathlib import Path

local_hf_root = "/local_disk0/genai_deploy_and_monitor_v2_hf"
os.environ.update(
    {
        "HF_HOME": local_hf_root,
        "HF_HUB_CACHE": f"{local_hf_root}/hub",
        "HF_XET_CACHE": f"{local_hf_root}/xet",
        "HF_HUB_DISABLE_XET": "1",
        "HF_HUB_DOWNLOAD_TIMEOUT": "120",
        "HF_HUB_DISABLE_TELEMETRY": "1",
    }
)
Path(local_hf_root).mkdir(parents=True, exist_ok=True)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Minimal configuration

# COMMAND ----------

catalog = "workspace"
schema = "default"
offline_payload_table = f"{catalog}.{schema}.offline_inference_payload_v2"
processed_table = f"{catalog}.{schema}.offline_processed_inference_v2"
profile_table = f"{catalog}.{schema}.offline_inference_profile_5m_v2"
drift_table = f"{catalog}.{schema}.offline_inference_drift_5m_v2"
hf_cache_dir = os.environ["HF_HUB_CACHE"]

if not spark.catalog.tableExists(offline_payload_table):
    raise RuntimeError(
        f"Run 16_local_model_workflow first. The required offline log table does not exist: {offline_payload_table}"
    )
if spark.table(offline_payload_table).limit(1).count() == 0:
    raise RuntimeError(f"The offline log table is empty: {offline_payload_table}")

print(f"Payload table: {offline_payload_table}")
print(f"Processed table: {processed_table}")
print(f"Temporary metric cache: {hf_cache_dir}")
display(spark.table(offline_payload_table).orderBy("timestamp").limit(5))

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Metric helpers
# MAGIC
# MAGIC `toxicity` and `perplexity` use Hugging Face Evaluate locally; `readability` uses `textstat`.
# MAGIC A metric returns its own status and error message so that the monitoring pipeline remains usable when
# MAGIC one optional public model is temporarily unavailable.

# COMMAND ----------

import torch
import transformers
import huggingface_hub
import pandas as pd
import evaluate
import textstat

print(
    {
        "torch": torch.__version__,
        "transformers": transformers.__version__,
        "huggingface_hub": huggingface_hub.__version__,
        "HF_HUB_DISABLE_XET": os.environ.get("HF_HUB_DISABLE_XET"),
    }
)


def load_metric_safely(metric_name: str):
    """Load a Hugging Face Evaluate metric and return an error instead of raising on download failure."""
    try:
        return evaluate.load(metric_name, cache_dir=hf_cache_dir), None
    except Exception as error:
        return None, f"{type(error).__name__}: {error}"


toxicity_metric, toxicity_load_error = load_metric_safely("toxicity")
perplexity_metric, perplexity_load_error = load_metric_safely("perplexity")


def metric_value_or_error(metric_name: str, text: str) -> tuple[float | None, str, str | None]:
    """Compute one text metric and preserve a per-metric error without failing the full batch."""
    try:
        if metric_name == "readability":
            return float(textstat.flesch_reading_ease(text)), "OK", None
        if metric_name == "toxicity":
            if toxicity_metric is None:
                raise RuntimeError(toxicity_load_error)
            value = toxicity_metric.compute(predictions=[text]).get("toxicity")
            return float(value[0] if isinstance(value, list) else value), "OK", None
        if metric_name == "perplexity":
            if perplexity_metric is None:
                raise RuntimeError(perplexity_load_error)
            value = perplexity_metric.compute(predictions=[text], model_id="gpt2", add_start_token=True)
            scores = value.get("perplexities", [])
            return float(scores[0]), "OK", None
        raise ValueError(f"Unsupported metric: {metric_name}")
    except Exception as error:
        return None, "ERROR", f"{type(error).__name__}: {error}"


def display_metrics_dataframe(metrics_df):
    """Display monitoring metrics in a concise, analysis-friendly DataFrame."""
    display(metrics_df)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Incrementally process new offline inference records
# MAGIC
# MAGIC The anti-join on `request_id` is the offline replacement for a streaming checkpoint. It means that
# MAGIC later runs process only unseen log records, while all rows remain available in the source log table.

# COMMAND ----------

from pyspark.sql import functions as F
from pyspark.sql.types import DoubleType, StringType, StructField, StructType, TimestampType

payload_df = spark.table(offline_payload_table)
if spark.catalog.tableExists(processed_table):
    existing_ids = spark.table(processed_table).select("request_id").distinct()
    pending_df = payload_df.join(existing_ids, on="request_id", how="left_anti")
else:
    pending_df = payload_df

pending_pdf = pending_df.orderBy("timestamp").toPandas()
print(f"New offline records to process: {len(pending_pdf)}")

if not pending_pdf.empty:
    metric_rows = []
    for _, row in pending_pdf.iterrows():
        output_text = str(row["output_text"])
        toxicity, toxicity_status, toxicity_error = metric_value_or_error("toxicity", output_text)
        perplexity, perplexity_status, perplexity_error = metric_value_or_error("perplexity", output_text)
        readability, readability_status, readability_error = metric_value_or_error("readability", output_text)
        metric_rows.append(
            {
                **row.to_dict(),
                "toxicity": toxicity,
                "toxicity_status": toxicity_status,
                "toxicity_error": toxicity_error,
                "perplexity": perplexity,
                "perplexity_status": perplexity_status,
                "perplexity_error": perplexity_error,
                "readability": readability,
                "readability_status": readability_status,
                "readability_error": readability_error,
                "processed_timestamp": pd.Timestamp.now(tz="UTC"),
            }
        )

    processed_pdf = pd.DataFrame(metric_rows)
    # An explicit schema keeps the batch writable even when an unavailable metric produces only NULL values.
    processed_schema = StructType(
        [
            StructField("request_id", StringType(), False),
            StructField("source_id", StringType(), False),
            StructField("input_text", StringType(), False),
            StructField("model_uri", StringType(), False),
            StructField("output_text", StringType(), False),
            StructField("timestamp", TimestampType(), False),
            StructField("latency_ms", DoubleType(), True),
            StructField("status", StringType(), True),
            StructField("execution_mode", StringType(), True),
            StructField("toxicity", DoubleType(), True),
            StructField("toxicity_status", StringType(), False),
            StructField("toxicity_error", StringType(), True),
            StructField("perplexity", DoubleType(), True),
            StructField("perplexity_status", StringType(), False),
            StructField("perplexity_error", StringType(), True),
            StructField("readability", DoubleType(), True),
            StructField("readability_status", StringType(), False),
            StructField("readability_error", StringType(), True),
            StructField("processed_timestamp", TimestampType(), False),
        ]
    )
    processed_batch_df = spark.createDataFrame(processed_pdf, schema=processed_schema)
    processed_batch_df.write.format("delta").mode("append").saveAsTable(processed_table)
    print(f"Appended {len(metric_rows)} processed records to {processed_table}.")
else:
    print("No new offline records were found; the processed table is already up to date.")

display_metrics_dataframe(
    spark.table(processed_table)
    .select(
        "request_id", "timestamp", "toxicity", "toxicity_status", "perplexity", "perplexity_status",
        "readability", "readability_status",
    )
    .orderBy(F.desc("timestamp"))
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Create five-minute profile and drift tables
# MAGIC
# MAGIC These Delta tables are the portable offline substitute for a managed Time Series monitor. Profile
# MAGIC values describe each five-minute window; drift values compare every window with the first window.

# COMMAND ----------

processed_df = spark.table(processed_table).withColumn(
    "window_start", F.date_trunc("minute", F.col("timestamp"))
).withColumn(
    "window_start",
    F.expr("timestamp_seconds(floor(unix_timestamp(window_start) / 300) * 300)"),
)

profile_df = (
    processed_df.groupBy("window_start")
    .agg(
        F.count("*").alias("request_count"),
        F.avg("toxicity").alias("avg_toxicity"),
        F.avg("perplexity").alias("avg_perplexity"),
        F.avg("readability").alias("avg_readability"),
        F.avg("latency_ms").alias("avg_latency_ms"),
        F.sum(F.when(F.col("toxicity_status") == "ERROR", 1).otherwise(0)).alias("toxicity_error_count"),
        F.sum(F.when(F.col("perplexity_status") == "ERROR", 1).otherwise(0)).alias("perplexity_error_count"),
    )
    .orderBy("window_start")
)
profile_df.write.format("delta").mode("overwrite").option("overwriteSchema", "true").saveAsTable(profile_table)

baseline = profile_df.orderBy("window_start").limit(1).select(
    F.col("window_start").alias("baseline_window_start"),
    F.col("avg_toxicity").alias("baseline_avg_toxicity"),
    F.col("avg_perplexity").alias("baseline_avg_perplexity"),
    F.col("avg_readability").alias("baseline_avg_readability"),
).collect()

if baseline:
    baseline_row = baseline[0]
    drift_df = (
        profile_df
        .withColumn("baseline_window_start", F.lit(baseline_row["baseline_window_start"]))
        .withColumn("toxicity_drift", F.col("avg_toxicity") - F.lit(baseline_row["baseline_avg_toxicity"]))
        .withColumn("perplexity_drift", F.col("avg_perplexity") - F.lit(baseline_row["baseline_avg_perplexity"]))
        .withColumn("readability_drift", F.col("avg_readability") - F.lit(baseline_row["baseline_avg_readability"]))
    )
    drift_df.write.format("delta").mode("overwrite").option("overwriteSchema", "true").saveAsTable(drift_table)

display(spark.table(profile_table).orderBy("window_start"))
display(spark.table(drift_table).orderBy("window_start"))

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Inspect the offline monitoring trend
# MAGIC
# MAGIC Use the table visualization controls in this output: select a line chart, use `window_start` as the
# MAGIC X axis, and add `avg_toxicity`, `avg_perplexity`, or `avg_readability` as values. This provides a
# MAGIC lightweight dashboard without a managed endpoint or Data Quality monitor.

# COMMAND ----------

trend_df = spark.table(profile_table).select(
    "window_start", "request_count", "avg_toxicity", "avg_perplexity", "avg_readability", "avg_latency_ms"
).orderBy("window_start")
display(trend_df)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Validation

# COMMAND ----------

assert spark.catalog.tableExists(processed_table), "The processed inference table was not created."
assert spark.catalog.tableExists(profile_table), "The profile table was not created."
assert spark.catalog.tableExists(drift_table), "The drift table was not created."
assert spark.table(processed_table).limit(1).count() == 1, "The processed inference table is empty."
print("Offline monitoring validation completed successfully.")
