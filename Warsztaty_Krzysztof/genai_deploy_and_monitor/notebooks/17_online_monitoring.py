# Databricks notebook source
# MAGIC %md
# MAGIC # 17 — Online monitoring for the deployed robotics RAG chain
# MAGIC
# MAGIC This notebook reads the real inference payload table for the RAG endpoint created in notebook
# MAGIC 16, unpacks request and response JSON, computes text-quality metrics incrementally, and creates
# MAGIC a five-minute Time Series monitor over the processed Delta table.
# MAGIC
# MAGIC Run the notebook in order. The first metric calculation downloads public Hugging Face models,
# MAGIC and Data Quality refreshes run asynchronously on serverless compute.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Runtime dependencies
# MAGIC
# MAGIC `evaluate` supplies the course-faithful toxicity and perplexity metrics. `textstat` supplies
# MAGIC Flesch Reading Ease as the readability score. The pinned Transformers release keeps the model
# MAGIC runtime compatible with the earlier course notebooks.

# COMMAND ----------

# MAGIC %pip install --upgrade --quiet "databricks-sdk>=0.102.0" "transformers==4.57.1" "evaluate==0.4.3" "textstat>=0.7.5" "torch>=2.3"

# COMMAND ----------

# MAGIC dbutils.library.restartPython()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Minimal configuration

# COMMAND ----------

catalog = "workspace"
schema = "default"

rag_serving_endpoint = "robotics-rag-deployment-endpoint"
payload_table = f"{catalog}.{schema}.robotics_rag_inference_payload"
processed_table = f"{catalog}.{schema}.robotics_rag_processed_inference"
checkpoint_volume = f"{catalog}.{schema}.genai_deploy_monitoring"
checkpoint_path = f"/Volumes/{catalog}/{schema}/genai_deploy_monitoring/checkpoints/online_monitoring"
monitor_assets_root = "genai_deploy_and_monitor/online_monitoring"

print(f"Serving endpoint: {rag_serving_endpoint}")
print(f"Inference payload table: {payload_table}")
print(f"Processed monitoring table: {processed_table}")
print(f"Streaming checkpoint: {checkpoint_path}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Load the real pre-populated inference table
# MAGIC
# MAGIC Notebook 16 must have an AI Gateway inference table enabled for
# MAGIC `robotics-rag-deployment-endpoint`. Send a few requests to the endpoint first. If the table is
# MAGIC absent or still empty, enable **Serving → robotics-rag-deployment-endpoint → Edit AI Gateway →
# MAGIC Enable inference tables**, use the prefix `robotics_rag_inference`, invoke the endpoint, and
# MAGIC wait for the platform to deliver payload logs.

# COMMAND ----------

required_payload_columns = {
    "databricks_request_id",
    "timestamp_ms",
    "request",
    "response",
    "request_metadata",
}

if not spark.catalog.tableExists(payload_table):
    raise RuntimeError(
        f"Inference table '{payload_table}' does not exist. Enable AI Gateway inference tables for "
        f"'{rag_serving_endpoint}', invoke the endpoint, and retry this cell."
    )

payload_df = spark.table(payload_table)
missing_payload_columns = required_payload_columns.difference(payload_df.columns)
if missing_payload_columns:
    raise RuntimeError(
        "The inference table schema does not match the expected request/response payload format. "
        f"Missing columns: {sorted(missing_payload_columns)}"
    )

if payload_df.limit(1).count() == 0:
    raise RuntimeError(
        f"Inference table '{payload_table}' exists but contains no payload rows yet. "
        "Invoke the endpoint with several requests and retry after log delivery."
    )

display(payload_df.orderBy("timestamp_ms", ascending=False).limit(10))

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Define and display the JSON unpacking configuration
# MAGIC
# MAGIC The deployed chain receives `dataframe_records` with a `messages` array and returns the text in
# MAGIC the first item of `predictions`. `KEEP_LAST_QUESTION_ONLY = False` preserves all conversation
# MAGIC messages in the processed input text.

# COMMAND ----------

INPUT_REQUEST_JSON_PATH = "$.dataframe_records[0].messages"
INPUT_JSON_PATH_TYPE = "array<struct<role:string,content:string>>"
KEEP_LAST_QUESTION_ONLY = False
OUTPUT_REQUEST_JSON_PATH = "$.predictions[0]"
OUTPUT_JSON_PATH_TYPE = "string"

unpacking_configuration = {
    "INPUT_REQUEST_JSON_PATH": INPUT_REQUEST_JSON_PATH,
    "INPUT_JSON_PATH_TYPE": INPUT_JSON_PATH_TYPE,
    "KEEP_LAST_QUESTION_ONLY": KEEP_LAST_QUESTION_ONLY,
    "OUTPUT_REQUEST_JSON_PATH": OUTPUT_REQUEST_JSON_PATH,
    "OUTPUT_JSON_PATH_TYPE": OUTPUT_JSON_PATH_TYPE,
}

display(spark.createDataFrame([unpacking_configuration]))

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Unpack inference requests with a reusable helper

# COMMAND ----------

from pyspark.sql import functions as F
from pyspark.sql import types as T

messages_schema = T.ArrayType(
    T.StructType(
        [
            T.StructField("role", T.StringType(), True),
            T.StructField("content", T.StringType(), True),
        ]
    )
)


def unpack_requests(inference_dataframe):
    """Extract timestamp, conversation input, output text, and endpoint metadata from payload JSON."""
    parsed_messages = F.from_json(
        F.get_json_object(F.col("request"), INPUT_REQUEST_JSON_PATH),
        messages_schema,
    )
    parsed_output = F.get_json_object(F.col("response"), OUTPUT_REQUEST_JSON_PATH).cast(
        OUTPUT_JSON_PATH_TYPE
    )

    if KEEP_LAST_QUESTION_ONLY:
        user_messages = F.filter(parsed_messages, lambda message: message["role"] == F.lit("user"))
        input_text = F.element_at(user_messages, -1)["content"]
    else:
        input_text = F.concat_ws(
            "\n",
            F.transform(
                parsed_messages,
                lambda message: F.concat(
                    message["role"],
                    F.lit(": "),
                    message["content"],
                ),
            ),
        )

    return (
        inference_dataframe
        .withColumn("timestamp", F.expr("timestamp_millis(timestamp_ms)"))
        .withColumn("parsed_messages", parsed_messages)
        .withColumn("input_text", input_text)
        .withColumn("output_text", parsed_output)
        .select(
            "databricks_request_id",
            "client_request_id",
            "timestamp",
            "timestamp_ms",
            "status_code",
            "execution_time_ms",
            F.element_at(F.col("request_metadata"), "endpoint_name").alias("endpoint_name"),
            F.element_at(F.col("request_metadata"), "model_name").alias("model_name"),
            F.element_at(F.col("request_metadata"), "model_version").alias("model_version"),
            "input_text",
            "output_text",
        )
        .filter(F.col("output_text").isNotNull() & (F.length(F.trim("output_text")) > 0))
    )


unpacked_preview = unpack_requests(payload_df)
display(unpacked_preview.orderBy("timestamp", ascending=False).limit(10))

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Compute toxicity, perplexity, and readability metrics
# MAGIC
# MAGIC Each metric is computed on the generated output. Toxicity and perplexity use the public Hugging
# MAGIC Face Evaluate implementations. Readability is Flesch Reading Ease, where larger values are
# MAGIC generally easier to read. The helper below displays the final metric columns as a DataFrame.

# COMMAND ----------

import pandas as pd
from pyspark.sql.functions import pandas_udf


@pandas_udf("double")
def compute_toxicity(texts: pd.Series) -> pd.Series:
    """Compute one Hugging Face toxicity score for each non-empty generated text."""
    import evaluate

    cleaned_texts = texts.fillna("").astype(str).tolist()
    metric = evaluate.load("toxicity", module_type="measurement")
    scores = metric.compute(predictions=cleaned_texts)["toxicity"]
    return pd.Series(scores, index=texts.index, dtype="float64")


@pandas_udf("double")
def compute_perplexity(texts: pd.Series) -> pd.Series:
    """Compute GPT-2 perplexity for each non-empty generated text."""
    import evaluate

    cleaned_texts = texts.fillna("").astype(str).tolist()
    metric = evaluate.load("perplexity", module_type="metric")
    scores = metric.compute(
        predictions=cleaned_texts,
        model_id="gpt2",
        add_start_token=True,
    )["perplexities"]
    return pd.Series(scores, index=texts.index, dtype="float64")


@pandas_udf("double")
def compute_readability(texts: pd.Series) -> pd.Series:
    """Compute Flesch Reading Ease for each generated text."""
    import textstat

    return texts.fillna("").astype(str).map(textstat.flesch_reading_ease).astype("float64")


def compute_text_metrics(unpacked_dataframe):
    """Add the three text-quality metric columns to an unpacked inference DataFrame."""
    return (
        unpacked_dataframe
        .withColumn("toxicity", compute_toxicity(F.col("output_text")))
        .withColumn("perplexity", compute_perplexity(F.col("output_text")))
        .withColumn("readability", compute_readability(F.col("output_text")))
    )


def display_metrics_dataframe(metrics_dataframe, limit=20):
    """Display key input, output, and metric columns for monitoring validation."""
    display(
        metrics_dataframe.select(
            "databricks_request_id",
            "timestamp",
            "input_text",
            "output_text",
            "toxicity",
            "perplexity",
            "readability",
        ).orderBy("timestamp", ascending=False).limit(limit)
    )


metrics_preview = compute_text_metrics(unpacked_preview.limit(5))
display_metrics_dataframe(metrics_preview, limit=5)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 5. Incrementally unpack payloads, compute metrics, and save the processed Delta table
# MAGIC
# MAGIC Structured Streaming tracks consumed source offsets in a durable Volume checkpoint. The
# MAGIC `availableNow` trigger processes all currently available payloads and stops; later runs process
# MAGIC only rows that arrived after the previous checkpoint. The final table is configured with Change
# MAGIC Data Feed for downstream monitoring and analysis.

# COMMAND ----------

spark.sql(f"CREATE VOLUME IF NOT EXISTS {checkpoint_volume}")

incremental_payload_stream = spark.readStream.table(payload_table)
incremental_metrics_stream = compute_text_metrics(unpack_requests(incremental_payload_stream))

streaming_query = (
    incremental_metrics_stream.writeStream
    .format("delta")
    .outputMode("append")
    .option("checkpointLocation", checkpoint_path)
    .trigger(availableNow=True)
    .toTable(processed_table)
)
streaming_query.awaitTermination()

spark.sql(
    f"ALTER TABLE {processed_table} SET TBLPROPERTIES (delta.enableChangeDataFeed = true)"
)

processed_df = spark.table(processed_table)
if processed_df.limit(1).count() == 0:
    raise RuntimeError(
        "The incremental stream completed but no usable output records were written. "
        "Check the payload JSON paths and the endpoint response format."
    )

display_metrics_dataframe(processed_df, limit=20)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 6. Create a five-minute Time Series monitor through the UI
# MAGIC
# MAGIC Use this UI path as an alternative to the SDK cell below. If you create the monitor here,
# MAGIC section 7 detects and reuses it instead of creating a duplicate.
# MAGIC
# MAGIC 1. Open **Catalog** in the left sidebar.
# MAGIC 2. Navigate to **workspace** → **default** → `robotics_rag_processed_inference`.
# MAGIC 3. Open the **Quality** tab and click **Get started**.
# MAGIC 4. Select **Time series profile**.
# MAGIC 5. Set the timestamp column to `timestamp`.
# MAGIC 6. Select **5 minutes** as the granularity, then create the monitor.
# MAGIC 7. Wait for the first refresh to complete before opening the generated metrics tables or dashboard.

# COMMAND ----------

# MAGIC %md
# MAGIC ## 7. Create or validate the same monitor through the Databricks SDK
# MAGIC
# MAGIC This cell uses the current `data_quality` API, not the deprecated `quality_monitors` API. Only
# MAGIC one monitor can exist for a Unity Catalog table, so an existing monitor created through the UI is
# MAGIC displayed and reused.

# COMMAND ----------

from databricks.sdk import WorkspaceClient
from databricks.sdk.errors import NotFound
from databricks.sdk.service.dataquality import (
    AggregationGranularity,
    DataProfilingConfig,
    Monitor,
    TimeSeriesConfig,
)

workspace_client = WorkspaceClient()
processed_table_info = workspace_client.tables.get(full_name=processed_table)
schema_info = workspace_client.schemas.get(full_name=f"{catalog}.{schema}")
current_user = workspace_client.current_user.me()
assets_dir = f"/Workspace/Users/{current_user.user_name}/{monitor_assets_root}"

monitor_config = DataProfilingConfig(
    output_schema_id=schema_info.schema_id,
    assets_dir=assets_dir,
    time_series=TimeSeriesConfig(
        timestamp_column="timestamp",
        granularities=[AggregationGranularity.AGGREGATION_GRANULARITY_5_MINUTES],
    ),
)

try:
    monitor_info = workspace_client.data_quality.get_monitor(
        object_type="table",
        object_id=processed_table_info.table_id,
    )
    print("Using the existing Time Series monitor created earlier.")
except NotFound:
    monitor_info = workspace_client.data_quality.create_monitor(
        monitor=Monitor(
            object_type="table",
            object_id=processed_table_info.table_id,
            data_profiling_config=monitor_config,
        )
    )
    print("Created a Time Series monitor through the Databricks SDK.")

print(monitor_info)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 8. Refresh the monitor and verify profile and drift metric tables
# MAGIC
# MAGIC This cell waits until the serverless refresh reaches a terminal state. On success it discovers
# MAGIC the profile and drift metric table names from monitor metadata, verifies both tables exist, and
# MAGIC displays their latest rows.

# COMMAND ----------

import time

from databricks.sdk.service.dataquality import Refresh, RefreshState


def find_monitor_value(value, target_key):
    """Recursively find a named value in a monitor response serialized as Python objects."""
    if isinstance(value, dict):
        if value.get(target_key):
            return value[target_key]
        for nested_value in value.values():
            found_value = find_monitor_value(nested_value, target_key)
            if found_value:
                return found_value
    elif isinstance(value, list):
        for nested_value in value:
            found_value = find_monitor_value(nested_value, target_key)
            if found_value:
                return found_value
    return None


refresh_info = workspace_client.data_quality.create_refresh(
    object_type="table",
    object_id=processed_table_info.table_id,
    refresh=Refresh(
        object_type="table",
        object_id=processed_table_info.table_id,
    ),
)

pending_refresh_states = {
    RefreshState.MONITOR_REFRESH_STATE_PENDING,
    RefreshState.MONITOR_REFRESH_STATE_RUNNING,
}

while refresh_info.state in pending_refresh_states:
    print(f"Waiting for monitor refresh {refresh_info.refresh_id}: {refresh_info.state}")
    time.sleep(30)
    refresh_info = workspace_client.data_quality.get_refresh(
        object_type="table",
        object_id=processed_table_info.table_id,
        refresh_id=refresh_info.refresh_id,
    )

if refresh_info.state != RefreshState.MONITOR_REFRESH_STATE_SUCCESS:
    raise RuntimeError(
        f"Monitor refresh ended with state {refresh_info.state}. "
        f"Service message: {refresh_info.message}"
    )

print(f"Monitor refresh completed successfully: {refresh_info.refresh_id}")

monitor_info = workspace_client.data_quality.get_monitor(
    object_type="table",
    object_id=processed_table_info.table_id,
)
monitor_metadata = monitor_info.as_dict()
profile_metrics_table = find_monitor_value(monitor_metadata, "profile_metrics_table_name")
drift_metrics_table = find_monitor_value(monitor_metadata, "drift_metrics_table_name")

if not profile_metrics_table or not drift_metrics_table:
    raise RuntimeError(
        "The monitor refresh succeeded but metric table names were not present in the monitor metadata. "
        "Open the Quality tab in Catalog to inspect the monitor output."
    )

for metric_table_name, metric_table_label in [
    (profile_metrics_table, "Profile metrics"),
    (drift_metrics_table, "Drift metrics"),
]:
    if not spark.catalog.tableExists(metric_table_name):
        raise RuntimeError(f"{metric_table_label} table is not ready: {metric_table_name}")
    print(f"{metric_table_label} table is ready: {metric_table_name}")
    display(spark.table(metric_table_name).limit(20))

# COMMAND ----------

# MAGIC %md
# MAGIC ## 9. Explore online monitoring in the Databricks dashboard UI
# MAGIC
# MAGIC 1. Open **Catalog** → **workspace** → **default** → `robotics_rag_processed_inference`.
# MAGIC 2. Select the **Quality** tab and open the monitor dashboard created for the table.
# MAGIC 3. Review five-minute trends for `toxicity`, `perplexity`, and `readability` in the profile
# MAGIC    metrics. Compare time windows to identify unusual changes in output quality.
# MAGIC 4. Open the drift metrics view to compare the current window with prior data. Investigate a
# MAGIC    drift spike together with the affected request IDs in the processed table.
# MAGIC 5. Use the dashboard share controls only with authorized workspace users, because prompt and
# MAGIC    response-derived metrics can reveal production usage patterns.
