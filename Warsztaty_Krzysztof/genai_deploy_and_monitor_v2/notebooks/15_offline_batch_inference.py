# Databricks notebook source
# MAGIC %md
# MAGIC # 15 — Offline batch inference with a self-contained T5 model
# MAGIC
# MAGIC This notebook creates a small XSum Delta table, builds a local `google-t5/t5-small` summarizer,
# MAGIC logs it as a self-contained MLflow PyFunc model, registers it in Unity Catalog, and runs a small
# MAGIC offline batch. It does not create or call a Model Serving endpoint, AI Gateway, or `ai_query`.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Runtime dependencies
# MAGIC
# MAGIC Serverless environments can omit a deep-learning backend, so PyTorch is installed explicitly. The
# MAGIC second command updates only the libraries used for local Hugging Face downloads and inference.

# COMMAND ----------

# MAGIC %pip install --quiet --upgrade "torch>=2.6.0" --index-url https://download.pytorch.org/whl/cpu

# COMMAND ----------

# MAGIC %pip install --quiet --upgrade "transformers==4.57.1" "huggingface_hub>=0.34.0" "safetensors>=0.4.5" "sentencepiece>=0.2.0" "requests>=2.31" "pandas>=2.2"

# COMMAND ----------

dbutils.library.restartPython()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Hugging Face environment configuration
# MAGIC
# MAGIC These variables are defined before importing `huggingface_hub` or `transformers`. The cache uses the
# MAGIC local Serverless disk because the Hugging Face Xet/CAS downloader can fail on a mounted UC Volume.
# MAGIC The final, reusable model is persisted in MLflow and Unity Catalog instead of this temporary cache.

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
xsum_table = f"{catalog}.{schema}.xsum_summaries_v2"
batch_predictions_table = f"{catalog}.{schema}.xsum_t5_batch_predictions_v2"
registered_model_name = f"{catalog}.{schema}.xsum_t5_small_summarizer_v2"
mlflow_experiment_path = "/Shared/genai_deploy_and_monitor_v2_offline_batch"
xsum_dataset_name = "EdinburghNLP/xsum"
xsum_sample_size = 24
batch_size = 12
hf_dataset_rows_url = "https://datasets-server.huggingface.co/rows"
t5_model_id = "google-t5/t5-small"
local_model_dir = f"{local_hf_root}/models/google-t5--t5-small"
inference_config = {
    "min_length": 20,
    "max_length": 40,
    "truncation": True,
    "do_sample": True,
}

print(f"Source table: {xsum_table}")
print(f"Registered model: {registered_model_name}")
print(f"Temporary Hugging Face cache: {local_hf_root}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Create or reuse the XSum Delta table
# MAGIC
# MAGIC The public Dataset Viewer API is used instead of the `datasets` package. The table is reused when it
# MAGIC already has rows, so repeated notebook runs do not download the sample again.

# COMMAND ----------

import requests

table_exists = spark.catalog.tableExists(xsum_table)
has_existing_rows = table_exists and spark.table(xsum_table).limit(1).count() > 0

if has_existing_rows:
    print(f"Reusing existing XSum table: {xsum_table}")
else:
    response = requests.get(
        hf_dataset_rows_url,
        params={
            "dataset": xsum_dataset_name,
            "config": "default",
            "split": "train",
            "offset": 0,
            "length": xsum_sample_size,
        },
        timeout=90,
    )
    response.raise_for_status()
    api_rows = response.json().get("rows", [])
    if not api_rows:
        raise RuntimeError("The public XSum API returned no rows. Retry later if Hugging Face is rate-limited.")

    xsum_records = [
        {
            "source_id": str(item["row"]["id"]),
            "document": str(item["row"]["document"]),
            "reference_summary": str(item["row"]["summary"]),
        }
        for item in api_rows
    ]
    spark.createDataFrame(xsum_records).write.format("delta").mode("overwrite").saveAsTable(xsum_table)
    print(f"Created {xsum_table} with {len(xsum_records)} rows.")

display(spark.table(xsum_table).select("source_id", "document", "reference_summary").limit(5))

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Build and test the local T5 summarizer
# MAGIC
# MAGIC The diagnostic output confirms that Xet was disabled before Hub imports. On the first run the full model
# MAGIC snapshot is downloaded serially to `/local_disk0`. Later runs reuse the `@champion` model artifact from
# MAGIC Unity Catalog and therefore skip the Hugging Face download.

# COMMAND ----------

import shutil
import torch
import transformers
import huggingface_hub
import mlflow
from huggingface_hub import snapshot_download
from mlflow import MlflowClient
from mlflow.exceptions import MlflowException
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

required_model_files = ("config.json", "spiece.model")


def champion_model_uri_or_none(model_name: str) -> str | None:
    """Return the Unity Catalog champion URI when it exists, otherwise return None."""
    try:
        MlflowClient().get_model_version_by_alias(model_name, "champion")
        return f"models:/{model_name}@champion"
    except MlflowException:
        return None


def has_complete_t5_snapshot(model_directory: str) -> bool:
    """Check that a local T5 directory contains config, tokenizer, and one supported weight file."""
    directory = Path(model_directory)
    weights_exist = (directory / "model.safetensors").is_file() or (directory / "pytorch_model.bin").is_file()
    return directory.is_dir() and weights_exist and all((directory / name).is_file() for name in required_model_files)


def download_t5_snapshot(model_id: str, model_directory: str) -> str:
    """Download a serial, direct-HTTP T5 snapshot to the local Serverless disk."""
    target = Path(model_directory)
    if has_complete_t5_snapshot(model_directory):
        return str(target)

    if target.exists():
        shutil.rmtree(target)
    try:
        downloaded_path = snapshot_download(
            repo_id=model_id,
            local_dir=str(target),
            cache_dir=os.environ["HF_HUB_CACHE"],
            allow_patterns=["config.json", "generation_config.json", "model.safetensors", "pytorch_model.bin", "spiece.model", "tokenizer.json", "tokenizer_config.json", "special_tokens_map.json"],
            max_workers=1,
        )
    except Exception as error:
        raise RuntimeError(
            f"Could not download '{model_id}' through direct Hugging Face HTTP. "
            "The notebook has disabled Xet before importing the Hub library. If this fails again, "
            "the current Serverless session cannot reach the public Hugging Face artifact service. "
            f"Original error: {type(error).__name__}: {error}"
        ) from error

    if not has_complete_t5_snapshot(downloaded_path):
        raise RuntimeError(f"The downloaded T5 snapshot is incomplete: {downloaded_path}")
    return downloaded_path


def generate_t5_summaries(model, tokenizer, texts: list[str], config: dict) -> list[str]:
    """Generate one T5 summary per text without using the patched Transformers pipeline registry."""
    prompts = [f"summarize: {str(text).strip()}" for text in texts]
    encoded = tokenizer(prompts, return_tensors="pt", padding=True, truncation=config["truncation"], max_length=512)
    with torch.inference_mode():
        generated_tokens = model.generate(
            **encoded,
            min_length=config["min_length"],
            max_length=config["max_length"],
            do_sample=config["do_sample"],
        )
    return [tokenizer.decode(tokens, skip_special_tokens=True) for tokens in generated_tokens]


print(
    {
        "torch": torch.__version__,
        "transformers": transformers.__version__,
        "huggingface_hub": huggingface_hub.__version__,
        "HF_HUB_DISABLE_XET": os.environ.get("HF_HUB_DISABLE_XET"),
        "local_snapshot_complete": has_complete_t5_snapshot(local_model_dir),
    }
)

sample_text = (
    "A community garden added rainwater collection, composting workshops, and evening classes. "
    "Residents reported that the shared space made it easier to meet neighbours and grow herbs."
)
champion_model_uri = champion_model_uri_or_none(registered_model_name)

if champion_model_uri:
    pyfunc_model = mlflow.pyfunc.load_model(champion_model_uri)
    sample_output = pyfunc_model.predict([sample_text])[0]
    print("Reused the registered champion model.\nSample summary:\n" + sample_output)
    local_snapshot_path = None
else:
    local_snapshot_path = download_t5_snapshot(t5_model_id, local_model_dir)
    tokenizer = AutoTokenizer.from_pretrained(local_snapshot_path, local_files_only=True)
    t5_model = AutoModelForSeq2SeqLM.from_pretrained(local_snapshot_path, local_files_only=True)
    t5_model.eval()
    sample_output = generate_t5_summaries(t5_model, tokenizer, [sample_text], inference_config)[0]
    print("Downloaded and tested the local T5 model.\nSample summary:\n" + sample_output)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Log a self-contained PyFunc model and register it in Unity Catalog
# MAGIC
# MAGIC The model stores the complete local T5 snapshot as an MLflow artifact. Future `@champion` loads use
# MAGIC Unity Catalog rather than contacting Hugging Face again.

# COMMAND ----------

class LocalT5Summarizer(mlflow.pyfunc.PythonModel):
    """A portable MLflow PyFunc wrapper around a local T5 summarization snapshot."""

    def __init__(self, generation_config: dict):
        self.generation_config = generation_config

    def load_context(self, context):
        """Load the packaged tokenizer and model from the MLflow artifact directory."""
        from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

        model_directory = context.artifacts["t5_snapshot"]
        self.tokenizer = AutoTokenizer.from_pretrained(model_directory, local_files_only=True)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(model_directory, local_files_only=True)
        self.model.eval()

    def predict(self, context, model_input: list[str], params=None) -> list[str]:
        """Summarize a list of source texts with the packaged T5 model."""
        import torch

        configuration = self.generation_config.copy()
        if params:
            configuration.update({key: value for key, value in params.items() if key in configuration})
        prompts = [f"summarize: {str(text).strip()}" for text in model_input]
        encoded = self.tokenizer(
            prompts,
            return_tensors="pt",
            padding=True,
            truncation=configuration["truncation"],
            max_length=512,
        )
        with torch.inference_mode():
            generated_tokens = self.model.generate(
                **encoded,
                min_length=configuration["min_length"],
                max_length=configuration["max_length"],
                do_sample=configuration["do_sample"],
            )
        return [self.tokenizer.decode(tokens, skip_special_tokens=True) for tokens in generated_tokens]


mlflow.set_experiment(mlflow_experiment_path)

if champion_model_uri:
    print(f"A champion model already exists, so no new model version was registered: {champion_model_uri}")
else:
    with mlflow.start_run(run_name="t5_small_offline_pyfunc") as run:
        mlflow.log_params(inference_config)
        model_info = mlflow.pyfunc.log_model(
            name="t5_summarizer",
            python_model=LocalT5Summarizer(inference_config),
            artifacts={"t5_snapshot": local_snapshot_path},
            input_example=[sample_text],
            pip_requirements=[
                "mlflow>=3.0.0",
                "torch>=2.6.0",
                "transformers==4.57.1",
                "sentencepiece>=0.2.0",
                "safetensors>=0.4.5",
            ],
        )
        run_id = run.info.run_id

    registered_version = mlflow.register_model(
        model_uri=model_info.model_uri,
        name=registered_model_name,
        await_registration_for=600,
    )
    MlflowClient().set_registered_model_alias(
        name=registered_model_name,
        alias="champion",
        version=registered_version.version,
    )
    champion_model_uri = f"models:/{registered_model_name}@champion"
    print(f"Run ID: {run_id}")
    print(f"Registered version: {registered_version.version}")

print(f"Champion model URI: {champion_model_uri}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Run local batch inference through MLflow PyFunc
# MAGIC
# MAGIC The registry model accepts a list of strings and returns a list of strings. No Transformers pipeline,
# MAGIC serving endpoint, or output-shape conversion is required.

# COMMAND ----------

import pandas as pd

pyfunc_model = mlflow.pyfunc.load_model(champion_model_uri)
batch_pdf = spark.table(xsum_table).orderBy("source_id").limit(batch_size).toPandas()
batch_summaries = pyfunc_model.predict(batch_pdf["document"].tolist())

if len(batch_summaries) != len(batch_pdf):
    raise RuntimeError("The local PyFunc model returned a different number of summaries than input documents.")

batch_pdf["generated_summary"] = batch_summaries
batch_pdf["model_uri"] = champion_model_uri
batch_pdf["prediction_timestamp"] = pd.Timestamp.now(tz="UTC")
spark.createDataFrame(batch_pdf).write.format("delta").mode("overwrite").saveAsTable(batch_predictions_table)
display(spark.table(batch_predictions_table).select("source_id", "generated_summary", "reference_summary").limit(5))

# COMMAND ----------

# MAGIC %md
# MAGIC ## Validation

# COMMAND ----------

assert spark.table(xsum_table).limit(1).count() == 1, "The XSum source table is empty."
assert spark.table(batch_predictions_table).limit(1).count() == 1, "The offline batch table is empty."
assert champion_model_uri.endswith("@champion"), "The Unity Catalog champion model alias is missing."
print("Offline batch inference validation completed successfully.")
