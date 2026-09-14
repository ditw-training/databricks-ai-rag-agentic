# Databricks notebook source
# MAGIC %md
# MAGIC # 04 — Building and logging a robotics RAG agent
# MAGIC
# MAGIC This notebook continues after notebooks 01–03. It uses the managed Delta Sync
# MAGIC index created in notebook 03. The reranker is intentionally not used because
# MAGIC it is unavailable in the current Free Edition workspace configuration.

# COMMAND ----------

# MAGIC %md
# MAGIC ## 0. Install required packages
# MAGIC
# MAGIC Run this cell once. After Python restarts, continue from section 1.

# COMMAND ----------

# MAGIC %pip install --upgrade --force-reinstall "mlflow[databricks]" databricks-langchain databricks-ai-search databricks-vectorsearch "langchain>=1.2" "langgraph>=1.1" pyyaml

# COMMAND ----------

# Restart Python so the installed LangChain and MLflow integrations are available.
dbutils.library.restartPython()

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Minimal configuration

# COMMAND ----------

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from typing import Any

import mlflow
from pyspark.sql.utils import AnalysisException

# Keep all course resource names fixed to the tables and index created by notebooks 02 and 03.
catalog = "workspace"
schema = "default"
ai_search_index_name = f"{catalog}.{schema}.robotics_document_chunks_index"
llm_endpoint = "databricks-meta-llama-3-3-70b-instruct"
max_tokens = 500
retrieval_result_count = 4
registered_model_name = f"{catalog}.{schema}.robotics_rag_agent"

# Store traces in a personal workspace experiment so each learner can inspect their own run.
current_user = spark.sql("SELECT current_user() AS current_user").first()["current_user"]
mlflow_experiment_name = f"/Users/{current_user}/robotics_agent_traces"

system_prompt = """You are a helpful and professional robotics specialist.
Use the robotics course-material search tool before giving any factual answer.
Answer only with information supported by the retrieved course materials.
If the materials do not contain the answer, say that you do not know based on the available materials.
Do not invent facts, make assumptions, or use information outside the retrieved context.
"""

print(f"AI Search index: {ai_search_index_name}")
print(f"LLM endpoint: {llm_endpoint}")
print(f"MLflow experiment: {mlflow_experiment_name}")
print(f"Unity Catalog model: {registered_model_name}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Test AI Search in AI Playground (UI instructions)
# MAGIC
# MAGIC 1. In the left sidebar, click **Playground** under **AI/ML**.
# MAGIC 2. Select `Inkling` in the model selector. Choose a tools-enabled variant if the UI labels one.
# MAGIC 3. Click **Tools** > **Add tool** > **AI Search**, then select `workspace.default.robotics_document_chunks_index`.
# MAGIC 4. Enter a short question, for example: `How do mobile robots avoid obstacles?`
# MAGIC 5. Send the question and inspect the retrieved document excerpts and citations shown with the answer.
# MAGIC 6. If AI Search is not offered as a tool, verify that the index is `ONLINE` in Catalog Explorer before continuing with the code sections below.

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Enable MLflow tracing

# COMMAND ----------

try:
    mlflow.set_experiment(mlflow_experiment_name)
except Exception as experiment_error:
    raise RuntimeError(
        f"Could not create or select MLflow experiment '{mlflow_experiment_name}'. "
        "Verify that you can create experiments in your Workspace user folder."
    ) from experiment_error

# Enable automatic tracing for LangChain calls, including the model and AI Search tool spans.
mlflow.langchain.autolog()
print(f"MLflow tracing is enabled for experiment: {mlflow_experiment_name}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Build and test the LangChain robotics agent

# COMMAND ----------

from databricks_langchain import ChatDatabricks, VectorSearchRetrieverTool
from langchain.agents import create_agent


def build_robotics_agent() -> Any:
    """Create a grounded LangChain agent with a retriever tool for the robotics index."""
    llm = ChatDatabricks(
        endpoint=llm_endpoint,
        max_tokens=max_tokens,
        temperature=0,
    )
    search_tool = VectorSearchRetrieverTool(
        name="search_robotics_course_materials",
        description=(
            "Search the robotics course materials for evidence before answering. "
            "Use this tool for every factual robotics question."
        ),
        index_name=ai_search_index_name,
        columns=["chunk_id", "path", "chunk_position", "chunk_text"],
        num_results=retrieval_result_count,
        query_type="HYBRID",
    )
    return create_agent(model=llm, tools=[search_tool], system_prompt=system_prompt)


def extract_final_answer(agent_result: dict[str, Any]) -> str:
    """Return the final text message from a LangChain agent invocation result."""
    messages = agent_result.get("messages", [])
    if not messages:
        return str(agent_result)
    final_message = messages[-1]
    return str(getattr(final_message, "content", final_message))


try:
    robotics_agent = build_robotics_agent()
    test_prompt = "How do mobile robots avoid obstacles?"
    test_result = robotics_agent.invoke(
        {"messages": [{"role": "user", "content": test_prompt}]}
    )
    test_answer = extract_final_answer(test_result)
except Exception as agent_error:
    raise RuntimeError(
        "The robotics agent could not run. Confirm that the AI Search index is ONLINE, the LLM endpoint "
        "is available, and that you have permission to query both resources. "
        f"Original error: {type(agent_error).__name__}: {agent_error}"
    ) from agent_error

display(
    spark.createDataFrame(
        [(test_prompt, test_answer)],
        ["prompt", "agent_answer"],
    )
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 5. Inspect the trace of the previous query (UI instructions)
# MAGIC
# MAGIC 1. In the left sidebar, open **Experiments** and select `robotics_agent_traces` in your user folder.
# MAGIC 2. Open the **Traces** tab and select the newest trace created by the test prompt.
# MAGIC 3. Inspect the root agent span, then the child spans for the LLM call and `search_robotics_course_materials`.
# MAGIC 4. Check the LLM prompt, the tool input, the retrieved chunks, latency, and the final answer.
# MAGIC 5. Verify that the answer is supported by the retrieved chunks. If no relevant chunk was found, the agent should state that it does not know.

# COMMAND ----------

# MAGIC %md
# MAGIC ## 6. Create `agent.py` and `agent_config.yaml` beside this notebook

# COMMAND ----------

import yaml


def get_workspace_notebook_directory() -> Path:
    """Resolve the Workspace Files directory that contains the running Databricks notebook."""
    notebook_path = (
        dbutils.notebook.entry_point.getDbutils().notebook().getContext().notebookPath().get()
    )
    return Path("/Workspace" + notebook_path).parent


# Store generated source files next to the imported notebook, not in the local course project.
workspace_notebook_directory = get_workspace_notebook_directory()
agent_file_path = workspace_notebook_directory / "agent.py"
agent_config_path = workspace_notebook_directory / "agent_config.yaml"

agent_config = {
    "llm_endpoint": llm_endpoint,
    "max_tokens": max_tokens,
    "index_name": ai_search_index_name,
    "retrieval_result_count": retrieval_result_count,
    "system_prompt": system_prompt,
}

agent_source = '''"""Robotics RAG agent generated by 04_building_and_logging."""

from pathlib import Path

import mlflow
import yaml
from databricks_langchain import ChatDatabricks, VectorSearchRetrieverTool
from langchain.agents import create_agent


DEFAULT_CONFIG = {
    "llm_endpoint": "databricks-meta-llama-3-3-70b-instruct",
    "max_tokens": 500,
    "index_name": "workspace.default.robotics_document_chunks_index",
    "retrieval_result_count": 4,
    "system_prompt": """You are a helpful and professional robotics specialist.
Use the robotics course-material search tool before giving any factual answer.
Answer only with information supported by the retrieved course materials.
If the materials do not contain the answer, say that you do not know based on the available materials.
Do not invent facts, make assumptions, or use information outside the retrieved context.
""",
}


def load_agent_config() -> dict:
    """Load the adjacent YAML configuration and retain safe defaults for MLflow model loading."""
    config_path = Path(__file__).with_name("agent_config.yaml")
    if not config_path.exists():
        return DEFAULT_CONFIG
    with config_path.open("r", encoding="utf-8") as config_file:
        return {**DEFAULT_CONFIG, **yaml.safe_load(config_file)}


def build_agent(config: dict):
    """Build a grounded LangChain agent that retrieves robotics course material before answering."""
    llm = ChatDatabricks(
        endpoint=config["llm_endpoint"],
        max_tokens=int(config["max_tokens"]),
        temperature=0,
    )
    search_tool = VectorSearchRetrieverTool(
        name="search_robotics_course_materials",
        description=(
            "Search the robotics course materials for evidence before answering. "
            "Use this tool for every factual robotics question."
        ),
        index_name=config["index_name"],
        columns=["chunk_id", "path", "chunk_position", "chunk_text"],
        num_results=int(config["retrieval_result_count"]),
        query_type="HYBRID",
    )
    return create_agent(model=llm, tools=[search_tool], system_prompt=config["system_prompt"])


agent = build_agent(load_agent_config())

# Expose this LangChain agent when MLflow logs this file as a model-from-code artifact.
mlflow.models.set_model(agent)
'''

try:
    agent_file_path.write_text(agent_source, encoding="utf-8")
    agent_config_path.write_text(yaml.safe_dump(agent_config, allow_unicode=True, sort_keys=False), encoding="utf-8")
except OSError as file_error:
    raise RuntimeError(
        "Could not write agent.py and agent_config.yaml beside this notebook. "
        "Confirm that the notebook is stored in a writable Workspace folder."
    ) from file_error

print(f"Created agent source: {agent_file_path}")
print(f"Created agent configuration: {agent_config_path}")
print("\nagent_config.yaml:\n")
print(agent_config_path.read_text(encoding="utf-8"))
print("\nagent.py:\n")
print(agent_file_path.read_text(encoding="utf-8"))

# COMMAND ----------

# MAGIC %md
# MAGIC ## 7. Log the generated agent and register it in Unity Catalog

# COMMAND ----------

from mlflow.models.resources import DatabricksServingEndpoint, DatabricksVectorSearchIndex

# Register the generated model code with its explicit Databricks resource dependencies.
mlflow.set_registry_uri("databricks-uc")
agent_input_example = {
    "messages": [{"role": "user", "content": "How do mobile robots avoid obstacles?"}]
}

try:
    with mlflow.start_run(run_name="log_robotics_rag_agent"):
        logged_model_info = mlflow.langchain.log_model(
            lc_model=str(agent_file_path),
            name="robotics_rag_agent",
            model_type="agent",
            input_example=agent_input_example,
            params={
                "llm_endpoint": llm_endpoint,
                "max_tokens": max_tokens,
                "index_name": ai_search_index_name,
            },
            resources=[
                DatabricksServingEndpoint(endpoint_name=llm_endpoint),
                DatabricksVectorSearchIndex(index_name=ai_search_index_name),
            ],
            code_paths=[str(agent_config_path)],
            pip_requirements=[
                "mlflow[databricks]",
                "databricks-langchain",
                "databricks-ai-search",
                "databricks-vectorsearch",
                "langchain",
                "pyyaml",
            ],
        )
    registered_model_version = mlflow.register_model(
        model_uri=logged_model_info.model_uri,
        name=registered_model_name,
    )
except Exception as registration_error:
    raise RuntimeError(
        f"Could not log and register '{registered_model_name}'. Confirm that you have USE CATALOG, USE SCHEMA, "
        "CREATE MODEL, and permissions for the LLM endpoint and AI Search index."
    ) from registration_error

print(f"Logged model URI: {logged_model_info.model_uri}")
print(f"Logged model ID: {logged_model_info.model_id}")
print(f"Registered model: {registered_model_name}")
print(f"Registered version: {registered_model_version.version}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 8. Find the registered agent in the UI
# MAGIC
# MAGIC 1. In the left sidebar, click **Catalog**.
# MAGIC 2. Open catalog `workspace`, then schema `default`.
# MAGIC 3. Open **Models** and select `robotics_rag_agent`.
# MAGIC 4. Select the newly created version to inspect its MLflow artifacts, dependencies, parameters, and source code.
# MAGIC 5. To inspect the logged model and its traces, open **Experiments** > `robotics_agent_traces`, then use the **Models** and **Traces** tabs.
