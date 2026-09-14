# Databricks notebook source
# MAGIC %md
# MAGIC # 13 — Benchmark evaluation for text summarization
# MAGIC
# MAGIC This notebook compares two deployed LLM endpoints on a small summarization evaluation set:
# MAGIC
# MAGIC - **Baseline**: `databricks-meta-llama-3-3-70b-instruct`.
# MAGIC - **Challenger**: `databricks-gpt-oss-20b`.
# MAGIC
# MAGIC The evaluation uses the course-compatible classic MLflow evaluation API and ROUGE-1, which
# MAGIC is the ROUGE-N metric for `n=1`. Modern MLflow recommends `mlflow.genai.evaluate()` for
# MAGIC new GenAI evaluation work; this notebook intentionally keeps `mlflow_evaluate` because it
# MAGIC reproduces the benchmark-comparison workflow used in the source course.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Runtime dependencies
# MAGIC
# MAGIC Run this cell first. The restart happens before any endpoint clients or functions are
# MAGIC defined, so the remaining cells can be run top to bottom after the restart.

# COMMAND ----------

# MAGIC %pip install --upgrade --quiet "mlflow[databricks]>=3.14.0" evaluate rouge-score nltk pandas

# COMMAND ----------

# MAGIC dbutils.library.restartPython()

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Define the baseline and challenger summary systems
# MAGIC
# MAGIC Both systems use the same system prompt and generation parameters. The only intended
# MAGIC difference is the endpoint under evaluation:
# MAGIC
# MAGIC - `query_summary_system` uses the Llama Instruct endpoint from the previous notebooks.
# MAGIC - `challenger_query_summary_system` uses the Databricks GPT-OSS 20B endpoint.

# COMMAND ----------

from databricks.sdk import WorkspaceClient
from databricks.sdk.service.serving import ChatMessage, ChatMessageRole

baseline_model_endpoint = "databricks-meta-llama-3-3-70b-instruct"
challenger_model_endpoint = "databricks-gpt-oss-20b"

summary_system_prompt = """
You are an assistant that summarizes text. Given a text input, you need to provide a one-sentence
summary. You specialize in summarizing reviews of grocery products. Please keep the reviews in
first-person perspective if they are originally written in first person. Do not change the sentiment.
Do not create a run-on sentence — be concise.
""".strip()

workspace_client = WorkspaceClient()


def extract_response_text(content) -> str:
    """Normalize string and GPT-OSS content-part responses to one plain text value."""
    if isinstance(content, str):
        return content.strip()

    if isinstance(content, list):
        text_parts = [extract_response_text(item) for item in content]
        return "".join(part for part in text_parts if part).strip()

    if isinstance(content, dict):
        for key in ("text", "content", "value", "output_text", "parts", "data", "message", "summary"):
            value = content.get(key)
            if value is not None:
                return extract_response_text(value)

    text_value = getattr(content, "text", None)
    if text_value is not None:
        return extract_response_text(text_value)

    as_dict = getattr(content, "as_dict", None)
    if callable(as_dict):
        return extract_response_text(as_dict())

    raise TypeError(
        "The serving endpoint returned an unsupported message-content format: "
        f"{type(content).__name__} with keys {list(content.keys()) if isinstance(content, dict) else 'n/a'}."
    )


def query_summary_system(input_text: str) -> str:
    """Generate one grocery-review summary with the baseline Llama Instruct endpoint."""
    messages = [
        ChatMessage(role=ChatMessageRole.SYSTEM, content=summary_system_prompt),
        ChatMessage(role=ChatMessageRole.USER, content=input_text),
    ]
    chat_response = workspace_client.serving_endpoints.query(
        name=baseline_model_endpoint,
        messages=messages,
        temperature=0.1,
        max_tokens=128,
    )
    return extract_response_text(chat_response.choices[0].message.content)


def challenger_query_summary_system(input_text: str) -> str:
    """Generate the same summary with the challenger GPT-OSS 20B endpoint."""
    messages = [
        ChatMessage(role=ChatMessageRole.SYSTEM, content=summary_system_prompt),
        ChatMessage(role=ChatMessageRole.USER, content=input_text),
    ]
    chat_response = workspace_client.serving_endpoints.query(
        name=challenger_model_endpoint,
        messages=messages,
        temperature=0.1,
        max_tokens=128,
    )
    return extract_response_text(chat_response.choices[0].message.content)


print(f"Baseline endpoint: {baseline_model_endpoint}")
print(f"Challenger endpoint: {challenger_model_endpoint}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Call both systems with the same grocery-review prompt

# COMMAND ----------

sample_review_prompt = (
    "This is the best frozen pizza I've ever had! Sure, it's not the healthiest, but it tasted just "
    "like it was delivered from our favorite pizzeria down the street. The cheese browned nicely and "
    "fresh tomatoes are a nice touch, too! I would buy it again despite its high price. If I could "
    "change one thing, I'd make it a little healthier — could we get a gluten-free crust option? "
    "My son would love that!"
)

print("Baseline summary:\n" + query_summary_system(sample_review_prompt))
print("\nChallenger summary:\n" + challenger_query_summary_system(sample_review_prompt))

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Prepare and load `eval_data`
# MAGIC
# MAGIC The linked paper, [*Benchmarking Large Language Models for News Summarization*](https://arxiv.org/abs/2301.13848),
# MAGIC evaluates models on news summarization and releases evaluation resources. Its paper data and
# MAGIC the grocery-review prompt used in this course example are different task domains.
# MAGIC
# MAGIC For this notebook, prepare a small, licensed CSV evaluation set with exactly these columns:
# MAGIC
# MAGIC | Column | Meaning |
# MAGIC | --- | --- |
# MAGIC | `input` | Review or article text sent to the summarization system. |
# MAGIC | `output` | Human reference summary for the same input. |
# MAGIC
# MAGIC Recommended setup:
# MAGIC
# MAGIC 1. Read the paper and its code/data release at
# MAGIC    [Tiiiger/benchmark_llm_summarization](https://github.com/Tiiiger/benchmark_llm_summarization).
# MAGIC 2. Review the applicable data license and prepare a small evaluation CSV for this exercise.
# MAGIC    Do not claim that an arbitrary grocery-review file is the paper's original dataset.
# MAGIC 3. In **Catalog**, open `workspace` → `default`, click **Create** → **Volume**, and create
# MAGIC    the managed Volume `genai_eval_data` if it does not already exist.
# MAGIC 4. Open the Volume, click **Upload to this volume**, and upload the file as
# MAGIC    `news-summarization.csv`.
# MAGIC 5. The fixed path used below is:
# MAGIC    `/Volumes/workspace/default/genai_eval_data/news-summarization.csv`.

# COMMAND ----------

import os
import pandas as pd

eval_data_path = "/Volumes/workspace/default/genai_eval_data/news-summarization.csv"

if not os.path.exists(eval_data_path):
    raise FileNotFoundError(
        f"Evaluation CSV was not found at {eval_data_path}. Create the managed Volume, upload "
        "news-summarization.csv, and run this cell again."
    )

eval_data = pd.read_csv(eval_data_path)
required_columns = {"input", "output"}
missing_columns = required_columns.difference(eval_data.columns)
if missing_columns:
    raise ValueError(
        "The evaluation CSV must contain exactly the required input and output columns. "
        f"Missing: {sorted(missing_columns)}; found: {list(eval_data.columns)}"
    )

eval_data = eval_data[["input", "output"]].dropna().reset_index(drop=True)
if eval_data.empty:
    raise ValueError("The evaluation dataset has no non-empty input/output rows.")

display(eval_data)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Iterate through `eval_data` and evaluate the baseline with ROUGE-1
# MAGIC
# MAGIC `summarize_with_baseline` is the custom prediction function passed to `mlflow_evaluate`.
# MAGIC It iterates through every input row and calls the baseline endpoint. ROUGE-1 measures unigram
# MAGIC overlap between the generated summary and the human reference summary.

# COMMAND ----------

import mlflow
from mlflow import evaluate as mlflow_evaluate
from mlflow.metrics import rouge1


def summarize_with_baseline(input_data: pd.DataFrame) -> list[str]:
    """Iterate through evaluation rows and return baseline summaries in input order."""
    return [query_summary_system(input_text) for input_text in input_data["input"]]


with mlflow.start_run(run_name="news_summarization_baseline"):
    baseline_evaluation = mlflow_evaluate(
        model=summarize_with_baseline,
        data=eval_data,
        targets="output",
        model_type="text-summarization",
        evaluators=["default"],
        evaluator_config={"default": {"col_mapping": {"inputs": "input"}}},
        extra_metrics=[rouge1()],
    )

print("Baseline evaluation metrics:")
print(baseline_evaluation.metrics)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 5. Evaluate and compare the challenger
# MAGIC
# MAGIC The challenger uses the identical CSV, reference summaries, prompt, temperature, maximum
# MAGIC tokens, and ROUGE-1 metric. Only the model endpoint changes, so the comparison is fair at
# MAGIC the application-configuration level.

# COMMAND ----------

def summarize_with_challenger(input_data: pd.DataFrame) -> list[str]:
    """Iterate through evaluation rows and return GPT-OSS 20B challenger summaries in input order."""
    return [challenger_query_summary_system(input_text) for input_text in input_data["input"]]


with mlflow.start_run(run_name="news_summarization_challenger_gpt_oss_20b"):
    challenger_evaluation = mlflow_evaluate(
        model=summarize_with_challenger,
        data=eval_data,
        targets="output",
        model_type="text-summarization",
        evaluators=["default"],
        evaluator_config={"default": {"col_mapping": {"inputs": "input"}}},
        extra_metrics=[rouge1()],
    )


def summarize_rouge_metrics(metrics: dict) -> dict:
    """Keep only ROUGE metrics so baseline and challenger results are easy to compare."""
    return {name: value for name, value in metrics.items() if "rouge" in name.lower()}


comparison = pd.DataFrame(
    [
        {"system": "baseline_llama", **summarize_rouge_metrics(baseline_evaluation.metrics)},
        {"system": "challenger_gpt_oss_20b", **summarize_rouge_metrics(challenger_evaluation.metrics)},
    ]
)

print("All challenger metrics:")
print(challenger_evaluation.metrics)
display(comparison)
