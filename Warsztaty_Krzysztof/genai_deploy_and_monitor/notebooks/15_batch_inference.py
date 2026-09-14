# Databricks notebook source
# MAGIC %md
# MAGIC # 15 — Batch inference with a Hugging Face T5 summarizer
# MAGIC
# MAGIC This notebook creates a small Delta table from the public XSum dataset, logs a `t5-small`
# MAGIC summarization pipeline to MLflow, registers the model in Unity Catalog, assigns the
# MAGIC `@champion` alias, deploys that version to Model Serving, and demonstrates SQL batch
# MAGIC inference with a hosted Databricks foundation-model endpoint.
# MAGIC
# MAGIC The notebook uses fixed course names in `workspace.default`. Run the cells from top to bottom.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Runtime dependencies
# MAGIC
# MAGIC The public XSum rows and `t5-small` model are downloaded from Hugging Face during this
# MAGIC exercise. The XSum sample is retrieved through the public Dataset Viewer API instead of the
# MAGIC `datasets` package, avoiding version conflicts with Databricks runtime patches. The environment
# MAGIC therefore needs outbound access to Hugging Face. Run this cell before defining Spark, MLflow,
# MAGIC or model objects.

# COMMAND ----------

# MAGIC %pip install --upgrade --quiet "mlflow[databricks]>=3.14.0" "transformers==4.57.1" "torch>=2.3" databricks-sdk requests

# COMMAND ----------

# MAGIC dbutils.library.restartPython()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Minimal configuration

# COMMAND ----------

catalog = "workspace"
schema = "default"
xsum_table = f"{catalog}.{schema}.xsum_summaries"
batch_predictions_table = f"{catalog}.{schema}.xsum_t5_batch_predictions"
registered_model_name = f"{catalog}.{schema}.xsum_t5_small_summarizer"
serving_endpoint_name = "xsum-t5-small-summarizer-endpoint"
batch_llm_endpoint = "databricks-meta-llama-3-3-70b-instruct"
mlflow_experiment_path = "/Shared/genai_deploy_and_monitor_batch_inference"
xsum_dataset_name = "EdinburghNLP/xsum"
xsum_sample_size = 100
hf_dataset_rows_url = "https://datasets-server.huggingface.co/rows"

print(f"Source table: {xsum_table}")
print(f"Registered model: {registered_model_name}")
print(f"Serving endpoint: {serving_endpoint_name}")
print(f"Batch LLM endpoint: {batch_llm_endpoint}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Create a Delta table with XSum source texts and reference summaries
# MAGIC
# MAGIC XSum is a public document-summarization dataset. The cell first checks whether the target
# MAGIC Delta table already exists and contains rows. When it does, it reuses the existing data and
# MAGIC skips the Hugging Face download. Otherwise, it retrieves a small training sample through the
# MAGIC Hugging Face Dataset Viewer API. The resulting table contains the source document in
# MAGIC `document` and its human reference in `reference_summary`.

# COMMAND ----------

table_exists = spark.catalog.tableExists(xsum_table)
existing_row_count = spark.table(xsum_table).limit(1).count() if table_exists else 0

if table_exists and existing_row_count > 0:
    print(f"Reusing existing Delta table with data: {xsum_table}")
else:
    import requests

    print(f"Creating {xsum_table} from a {xsum_sample_size}-row XSum sample.")
    response = requests.get(
        hf_dataset_rows_url,
        params={
            "dataset": xsum_dataset_name,
            "config": "default",
            "split": "train",
            "offset": 0,
            "length": xsum_sample_size,
        },
        timeout=60,
    )
    response.raise_for_status()
    rows = response.json().get("rows", [])

    if len(rows) < xsum_sample_size:
        raise RuntimeError(
            f"Hugging Face returned {len(rows)} XSum rows; expected {xsum_sample_size}. "
            "Retry later or configure a Hugging Face token if the public API is rate-limited."
        )

    xsum_records = [
        {
            "id": item["row"]["id"],
            "document": item["row"]["document"],
            "reference_summary": item["row"]["summary"],
        }
        for item in rows
    ]
    xsum_spark = spark.createDataFrame(xsum_records)
    (
        xsum_spark.write.format("delta")
        .mode("overwrite")
        .option("overwriteSchema", "true")
        .saveAsTable(xsum_table)
    )

display(spark.table(xsum_table).select("id", "document", "reference_summary").limit(5))

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Create and test a Hugging Face `t5-small` summarization pipeline
# MAGIC
# MAGIC The pipeline configuration is intentionally fixed for this course exercise: `min_length=20`,
# MAGIC `max_length=40`, `truncation=True`, and `do_sample=True`. This cell requires the pinned
# MAGIC Transformers 4.x release from the runtime dependency cell; the current Transformers 5.x task
# MAGIC registry does not expose the legacy `summarization` pipeline task used in this exercise.

# COMMAND ----------

import transformers
from transformers import pipeline

if not transformers.__version__.startswith("4."):
    raise RuntimeError(
        f"Transformers {transformers.__version__} is installed, but this notebook requires "
        "transformers==4.57.1. Run the runtime dependency cell, restart Python, and retry this cell."
    )

inference_config = {
    "min_length": 20,
    "max_length": 40,
    "truncation": True,
    "do_sample": True,
}

summarizer = pipeline(
    task="summarization",
    model="t5-small",
    **inference_config,
)

sample_text = (
    "Urban parks improve daily life by providing shade, recreation, and places for social contact. "
    "When cities protect trees and maintain safe paths, residents can walk more often and spend time "
    "outdoors. Small parks can also support birds, insects, and local biodiversity."
)
sample_summary = summarizer(sample_text)

print("Input text:\n", sample_text)
print("\nPipeline output:\n", sample_summary)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Prepare the MLflow signature, inference configuration, and model metadata
# MAGIC
# MAGIC `infer_signature` records the input and output contract observed for the pipeline. The same
# MAGIC `inference_config` is passed to MLflow as `model_config`, so pyfunc consumers use the intended
# MAGIC summarization defaults unless they provide compatible signature parameters.

# COMMAND ----------

from mlflow.models import infer_signature

input_example = sample_text
output_example = summarizer(input_example)
signature = infer_signature(input_example, output_example)
model_metadata = {
    "source_model": "t5-small",
    "task": "summarization",
    "dataset": xsum_dataset_name,
    "sample_size": xsum_sample_size,
}

print("Inference configuration:")
print(inference_config)
print("\nInferred signature:")
print(signature)
print("\nModel metadata:")
print(model_metadata)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Log a test experiment and the T5 pipeline to MLflow

# COMMAND ----------

import mlflow

mlflow.set_registry_uri("databricks-uc")
mlflow.set_experiment(mlflow_experiment_path)

with mlflow.start_run(run_name="t5_small_xsum_summarization_test") as active_run:
    mlflow.log_params(inference_config)
    mlflow.log_params(model_metadata)
    mlflow.log_text(sample_text, "examples/sample_input.txt")
    mlflow.log_text(str(sample_summary), "examples/sample_output.txt")

    model_info = mlflow.transformers.log_model(
        transformers_model=summarizer,
        name="t5_small_summarizer",
        task="summarization",
        signature=signature,
        input_example=input_example,
        model_config=inference_config,
        metadata=model_metadata,
        pip_requirements=[
            "mlflow>=3.14.0",
        "transformers==4.57.1",
            "torch>=2.3",
        ],
    )

print(f"Experiment: {mlflow_experiment_path}")
print(f"Run ID: {active_run.info.run_id}")
print(f"Logged model URI: {model_info.model_uri}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 5. Load the logged model as a PyFunc pipeline and call `.predict()`

# COMMAND ----------

import mlflow.pyfunc

pyfunc_summarizer = mlflow.pyfunc.load_model(model_info.model_uri)
pyfunc_prediction = pyfunc_summarizer.predict(sample_text)

print("PyFunc prediction:")
print(pyfunc_prediction)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 6. Register the model in Unity Catalog and assign the latest version to `@champion`
# MAGIC
# MAGIC Unity Catalog model aliases are mutable references. Batch and serving workloads can target
# MAGIC `@champion`, while a later validated version can replace the alias without changing their
# MAGIC model reference.

# COMMAND ----------

from mlflow import MlflowClient

registered_model_version = mlflow.register_model(
    model_uri=model_info.model_uri,
    name=registered_model_name,
)

registry_client = MlflowClient(registry_uri="databricks-uc")
registry_client.set_registered_model_alias(
    name=registered_model_name,
    alias="champion",
    version=registered_model_version.version,
)

champion_model_uri = f"models:/{registered_model_name}@champion"
champion_version = registry_client.get_model_version_by_alias(
    name=registered_model_name,
    alias="champion",
)

print(f"Registered version: {registered_model_version.version}")
print(f"Champion model URI: {champion_model_uri}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 7. Create the production workflow endpoint for batch inference
# MAGIC
# MAGIC `ai_query` targets a Model Serving endpoint, not a Unity Catalog alias directly. This cell
# MAGIC resolves `@champion` to a version and creates a custom CPU endpoint the first time it runs.
# MAGIC If an endpoint with the configured name already exists, the cell leaves it unchanged. After a
# MAGIC new champion is promoted, update the existing endpoint to that resolved version before the next
# MAGIC production batch run.

# COMMAND ----------

from databricks.sdk import WorkspaceClient
from databricks.sdk.errors import NotFound
from databricks.sdk.service.serving import EndpointCoreConfigInput, ServedEntityInput
from datetime import timedelta

serving_client = WorkspaceClient()

try:
    endpoint_details = serving_client.serving_endpoints.get(serving_endpoint_name)
    print(f"Using existing serving endpoint: {serving_endpoint_name}")
except NotFound:
    endpoint_details = serving_client.serving_endpoints.create_and_wait(
        name=serving_endpoint_name,
        config=EndpointCoreConfigInput(
            name=serving_endpoint_name,
            served_entities=[
                ServedEntityInput(
                    name="xsum-t5-small-champion",
                    entity_name=registered_model_name,
                    entity_version=str(champion_version.version),
                    workload_size="Small",
                    scale_to_zero_enabled=True,
                )
            ]
        ),
        timeout=timedelta(minutes=30),
    )
    print(f"Created serving endpoint: {serving_endpoint_name}")

print(endpoint_details)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 8. Run SQL batch inference with `ai_query`
# MAGIC
# MAGIC This section follows the course pattern for SQL batch inference: it sends a plain text prompt
# MAGIC to a hosted Databricks foundation model and stores its direct text response. It is separate
# MAGIC from the T5 custom-model deployment in section 7, whose lifecycle is demonstrated through
# MAGIC MLflow, Unity Catalog, and Model Serving. Limiting the first run to ten documents keeps the
# MAGIC example suitable for a course workspace.
# MAGIC
# MAGIC Requirements: run this cell on serverless compute or a Databricks Runtime 18.2+ environment,
# MAGIC wait for the serving endpoint to become ready, and confirm that the endpoint's **Query endpoint**
# MAGIC page accepts the generated input example.

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE OR REPLACE TABLE workspace.default.xsum_t5_batch_predictions AS
# MAGIC SELECT
# MAGIC   id,
# MAGIC   document,
# MAGIC   reference_summary,
# MAGIC   ai_query(
# MAGIC     endpoint => 'databricks-meta-llama-3-3-70b-instruct',
# MAGIC     request => CONCAT(
# MAGIC       'Summarize the following news article in no more than 60 words. ',
# MAGIC       'Preserve its central facts and do not add information. Document: ',
# MAGIC       document
# MAGIC     )
# MAGIC   ) AS generated_summary
# MAGIC FROM workspace.default.xsum_summaries
# MAGIC LIMIT 10;
# MAGIC
# MAGIC SELECT id, reference_summary, generated_summary
# MAGIC FROM workspace.default.xsum_t5_batch_predictions
# MAGIC LIMIT 5;
