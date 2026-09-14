# Databricks notebook source
# MAGIC %md
# MAGIC # 14 — LLM as a judge: professionalism evaluation
# MAGIC
# MAGIC This notebook evaluates the style of a chatbot response with a custom MLflow
# MAGIC LLM-as-a-judge metric. It uses the same Foundation Model API endpoint used in the
# MAGIC previous notebooks: `databricks-meta-llama-3-3-70b-instruct`.
# MAGIC
# MAGIC **Compatibility note:** `mlflow.metrics.genai.make_genai_metric` is the classic MLflow
# MAGIC evaluation API used by the source course. Current MLflow marks this API as legacy, but it
# MAGIC remains appropriate here because this exercise specifically demonstrates custom
# MAGIC `EvaluationExample`-based metrics.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Runtime dependencies
# MAGIC
# MAGIC Run this cell first. Python restarts before any imports, clients, metrics, or functions are
# MAGIC defined. Then run the remaining cells from top to bottom.

# COMMAND ----------

# MAGIC %pip install --upgrade --quiet "mlflow[databricks]>=3.14.0" pandas

# COMMAND ----------

# MAGIC dbutils.library.restartPython()

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Define `query_chatbot_system`
# MAGIC
# MAGIC The function follows the serving pattern from notebook 13: it sends a system message and a
# MAGIC user message to the Llama Instruct endpoint, then returns only the assistant text.

# COMMAND ----------

from databricks.sdk import WorkspaceClient
from databricks.sdk.service.serving import ChatMessage, ChatMessageRole

llama_endpoint = "databricks-meta-llama-3-3-70b-instruct"

chatbot_system_prompt = """
You are a helpful customer-support chatbot for a grocery retailer. Give a concise, accurate answer.
Follow a requested writing style when it is safe and relevant. Do not invent policies, prices, or
facts that were not supplied by the user.
""".strip()

workspace_client = WorkspaceClient()


def query_chatbot_system(input_text: str) -> str:
    """Send one user message to the Llama endpoint and return the assistant response text."""
    messages = [
        ChatMessage(role=ChatMessageRole.SYSTEM, content=chatbot_system_prompt),
        ChatMessage(role=ChatMessageRole.USER, content=input_text),
    ]
    response = workspace_client.serving_endpoints.query(
        name=llama_endpoint,
        messages=messages,
        temperature=0.1,
        max_tokens=180,
    )
    return response.choices[0].message.content.strip()


print(f"Chatbot endpoint: {llama_endpoint}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Create the custom `professionalism` metric
# MAGIC
# MAGIC `EvaluationExample` objects provide few-shot examples to the judge. The score is an integer
# MAGIC from 1 to 5: **1** is very casual, slang-heavy, and unsuitable for professional use; **5** is
# MAGIC polished, respectful, business-like, and appropriate for an academic setting. The metric logs
# MAGIC both the mean and variance of row-level scores.

# COMMAND ----------

import mlflow
from mlflow.deployments import set_deployments_target
from mlflow.metrics.genai import EvaluationExample, make_genai_metric

set_deployments_target("databricks")

professionalism_examples = [
    EvaluationExample(
        input="How can I request a refund?",
        output="Yo, just hit up support and tell them the order was messed up — they will sort it out.",
        score=1,
        justification=(
            "The response uses slang and an overly casual phrase, so it is not suitable for a "
            "professional customer-support interaction."
        ),
    ),
    EvaluationExample(
        input="How can I request a refund?",
        output=(
            "Please contact customer support with your order details and briefly explain the issue. "
            "The team can then review the available refund options."
        ),
        score=3,
        justification=(
            "The response is clear and respectful, but it is neutral rather than distinctly formal "
            "or business-like."
        ),
    ),
    EvaluationExample(
        input="How can I request a refund?",
        output=(
            "Please contact Customer Support and provide the relevant order information together "
            "with a concise description of the issue. Our team will review your request and advise "
            "you of the applicable next steps."
        ),
        score=5,
        justification=(
            "The response is polished, formal, respectful, and appropriate for a business or "
            "academic communication context."
        ),
    ),
]

professionalism = make_genai_metric(
    name="professionalism",
    definition=(
        "Professionalism measures whether an assistant response uses a formal, respectful, clear, "
        "and context-appropriate style. It penalizes slang, excessive informality, and casual wording."
    ),
    grading_prompt=(
        "Score the assistant output for professionalism using exactly one integer from 1 to 5. "
        "Use these criteria: \n"
        "- Score 1: Very casual, slang-heavy, informal, or unsuitable for professional communication.\n"
        "- Score 2: Informal and conversational, with some casual phrasing, but not offensive.\n"
        "- Score 3: Clear and respectful neutral language; acceptable in ordinary communication.\n"
        "- Score 4: Formal, respectful, and professional; suitable for business communication.\n"
        "- Score 5: Highly polished, formal, respectful, business-like, and suitable for academic or "
        "senior-stakeholder communication."
    ),
    examples=professionalism_examples,
    version="v1",
    model=f"endpoints:/{llama_endpoint}",
    include_input=True,
    parameters={"temperature": 0.0, "max_tokens": 200},
    aggregations=["mean", "variance"],
    greater_is_better=True,
)

print(professionalism.metric_details)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Run test prompts and inspect the MLflow experiment
# MAGIC
# MAGIC The three prompts deliberately request casual, neutral, and formal writing styles. After the
# MAGIC cell completes, open **Experiments** in the left navigation, then open
# MAGIC `genai_eval_and_monitor_llm_as_judge` and its latest run. In **Overview → Metrics**, read
# MAGIC `professionalism/mean` for average style and `professionalism/variance` for variation between
# MAGIC responses. In **Artifacts**, open the evaluation-results table (its name includes
# MAGIC `eval_results_table`) to inspect each row's score and judge justification.

# COMMAND ----------

import pandas as pd
from mlflow import evaluate as mlflow_evaluate

experiment_path = "/Shared/genai_eval_and_monitor_llm_as_judge"
mlflow.set_experiment(experiment_path)

test_prompts = [
    "Explain how I can request a refund. Use a casual, slang-heavy tone.",
    "Explain how I can request a refund using a neutral and clear tone.",
    "Explain how I can request a refund in a formal, respectful business style.",
]
test_data = pd.DataFrame({"input": test_prompts})


def predict_chatbot(input_data: pd.DataFrame) -> list[str]:
    """Generate one chatbot response for every input row in the supplied DataFrame."""
    return [query_chatbot_system(input_text) for input_text in input_data["input"]]


with mlflow.start_run(run_name="professionalism_llm_judge_test") as active_run:
    evaluation_result = mlflow_evaluate(
        model=predict_chatbot,
        data=test_data,
        model_type="text",
        evaluators=["default"],
        evaluator_config={"default": {"col_mapping": {"inputs": "input"}}},
        extra_metrics=[professionalism],
    )

print(f"Experiment path: {experiment_path}")
print(f"Run ID: {active_run.info.run_id}")
print("Aggregated metrics:")
print(evaluation_result.metrics)

evaluation_table = evaluation_result.tables.get("eval_results_table")
if evaluation_table is not None:
    display(evaluation_table)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Best practices for LLM-as-a-judge evaluation
# MAGIC
# MAGIC - Define a narrow, observable rubric. A judge can score tone reliably only when the score
# MAGIC   levels are distinct and concrete.
# MAGIC - Include representative `EvaluationExample` objects, especially boundary cases between two
# MAGIC   neighbouring scores.
# MAGIC - Keep judge temperature at `0.0` and retain the prompt, examples, model endpoint, and metric
# MAGIC   version with every evaluation run.
# MAGIC - Review row-level scores and justifications, not only the mean. A good average can hide a
# MAGIC   small number of unsuitable responses.
# MAGIC - Treat judge scores as an evaluation signal, then calibrate the rubric against human review
# MAGIC   before using it as a release gate.
# MAGIC - Evaluate the same fixed dataset when comparing model or prompt changes, and record any
# MAGIC   changes to the dataset separately.
