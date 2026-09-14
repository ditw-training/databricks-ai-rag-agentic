# Databricks notebook source
# MAGIC %md
# MAGIC # 08 - MLflow tracing for an Airbnb function agent
# MAGIC
# MAGIC This notebook continues from notebooks 06 and 07. It reads the persisted Airbnb Delta
# MAGIC table and Unity Catalog functions, then demonstrates MLflow experiments, artifacts, and traces.
# MAGIC Run the cells from top to bottom.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Setup - Install compatible dependencies
# MAGIC
# MAGIC Run this installation cell once. The following cell restarts Python. All configuration
# MAGIC objects are defined after that restart so this notebook does not rely on in-memory state
# MAGIC from an earlier notebook.

# COMMAND ----------

# MAGIC %pip install --upgrade --force-reinstall --no-cache-dir "mlflow[databricks]>=3.14.0" "openai>=1.0.0" "databricks-langchain==0.18.0" "langchain==1.3.14" "langchain-classic>=1.0.1" "langgraph==1.2.9" "langgraph-prebuilt>=1.1.0,<1.2.0" "unitycatalog-ai[databricks]"

# COMMAND ----------

# Restart Python so all installed packages and their compatible dependencies are available.
dbutils.library.restartPython()

# COMMAND ----------

import json
import os
from importlib.metadata import version

import mlflow
from databricks.sdk import WorkspaceClient
from databricks_langchain import ChatDatabricks, UCFunctionToolkit
from langchain_classic.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from mlflow.entities import SpanType
from unitycatalog.ai.core.databricks import DatabricksFunctionClient


def get_workspace_username() -> str:
    """Return the current Databricks username for a valid Workspace experiment path."""
    try:
        return dbutils.notebook.entry_point.getDbutils().notebook().getContext().userName().get()
    except Exception:
        return spark.sql("SELECT current_user() AS username").first()["username"]


catalog = "workspace"
schema = "default"
airbnb_table = f"{catalog}.{schema}.sf_airbnb_listings"
average_price_function = f"{catalog}.{schema}.get_average_listing_price"
listing_details_function = f"{catalog}.{schema}.get_listing_details"
python_formatting_function = f"{catalog}.{schema}.format_listing_for_agent"
agent_volume_name = "agent_vol"
agent_volume_fqn = f"{catalog}.{schema}.{agent_volume_name}"
agent_volume_path = f"/Volumes/{catalog}/{schema}/{agent_volume_name}"
agent_config_path = f"{agent_volume_path}/mlflow_tracing_agent_config.json"
username = get_workspace_username()

print(f"mlflow: {version('mlflow')}")
print(f"databricks-langchain: {version('databricks-langchain')}")
print(f"Current workspace user: {username}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Load five Airbnb Delta table records

# COMMAND ----------

try:
    airbnb_df = spark.table(airbnb_table)
except Exception as table_error:
    raise RuntimeError(
        f"Could not read {airbnb_table}. Run notebook 06 successfully before this notebook. "
        f"Original error: {type(table_error).__name__}: {table_error}"
    ) from table_error

if airbnb_df.limit(1).count() == 0:
    raise ValueError(f"The Delta table {airbnb_table} is empty.")

display(airbnb_df.orderBy("id").limit(5))
sample_listing = airbnb_df.orderBy("id").first().asDict()
sample_listing_id = int(sample_listing["id"])

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Create a JSON configuration file and tool list

# COMMAND ----------

# Create the Volume only when it is missing because it stores MLflow artifacts and this notebook's JSON file.
spark.sql(f"CREATE VOLUME IF NOT EXISTS {agent_volume_fqn}")

function_names = [
    average_price_function,
    listing_details_function,
    python_formatting_function,
]
agent_config = {
    "llm_endpoint": "databricks-meta-llama-3-3-70b-instruct",
    "llm_temperature": 0.1,
    "system_prompt": (
        "You are a helpful and professional assistant for the San Francisco Airbnb course dataset. "
        "Use Unity Catalog tools whenever a question asks for dataset facts, prices, averages, or listing details. "
        "Treat tool results as the only source of truth and do not invent listing values. "
        "If the tools cannot answer a question, say that you do not know based on the available data."
    ),
    "tool_functions": function_names,
}

dbutils.fs.put(agent_config_path, json.dumps(agent_config, indent=2), overwrite=True)
print(f"Created agent configuration: {agent_config_path}")
print(dbutils.fs.head(agent_config_path))

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Enable MLflow autologging

# COMMAND ----------

# Enable automatic tracing for the LangChain agent and for OpenAI-compatible Databricks Foundation Model calls.
mlflow.set_tracking_uri("databricks")
mlflow.langchain.autolog()
mlflow.openai.autolog()
print("MLflow LangChain and OpenAI-compatible autologging are enabled.")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Define and display MLflow experiment locations
# MAGIC
# MAGIC A Workspace experiment path starts with `/Users/`; it does not include the UI label
# MAGIC `Workspace`. A Unity Catalog Volume artifact location must use `dbfs:/Volumes/`.

# COMMAND ----------

workspace_experiment_demo1 = f"/Users/{username}/single_agents_demo1"
workspace_experiment_demo2 = f"/Users/{username}/single_agents_demo2"
artifact_location = f"dbfs:/Volumes/{catalog}/{schema}/{agent_volume_name}/mlflow_artifacts"

experiment_locations = {
    "Workspace experiment 1": workspace_experiment_demo1,
    "Workspace experiment 2": workspace_experiment_demo2,
    "Unity Catalog Volume artifact location": artifact_location,
}

for label, location in experiment_locations.items():
    print(f"{label}: {location}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 5. Create an MLflow experiment and log an artifact

# COMMAND ----------

# Create the Workspace experiment only once, with artifacts stored in the Unity Catalog Volume.
existing_experiment = mlflow.get_experiment_by_name(workspace_experiment_demo2)
if existing_experiment is None:
    mlflow.create_experiment(
        name=workspace_experiment_demo2,
        artifact_location=artifact_location,
    )

artifact_experiment = mlflow.set_experiment(workspace_experiment_demo2)
with mlflow.start_run(run_name="airbnb-tracing-configuration") as artifact_run:
    mlflow.log_dict(agent_config, "agent_config.json")
    mlflow.log_text(
        "This run stores the configuration for the Airbnb MLflow tracing demonstration.",
        "artifact_readme.txt",
    )
    artifact_run_id = artifact_run.info.run_id
    artifact_uri = mlflow.get_artifact_uri()

print(f"Active experiment ID: {artifact_experiment.experiment_id}")
print(f"Created run with artifacts: {artifact_run_id}")
print(f"Artifact URI: {artifact_uri}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 6. Load and test the demo agent, then inspect its trace in the UI
# MAGIC
# MAGIC After running the next cell:
# MAGIC
# MAGIC 1. In the left navigation, open **Experiments**.
# MAGIC 2. Open `single_agents_demo2` under your user folder.
# MAGIC 3. Open the **Traces** tab and select the newest trace.
# MAGIC 4. Inspect the model call, Unity Catalog function calls, tool inputs, tool outputs, and final answer.

# COMMAND ----------

# Load the JSON file so the demo agent is configured from a persisted artifact rather than notebook constants.
loaded_agent_config = json.loads(dbutils.fs.head(agent_config_path))
toolkit = UCFunctionToolkit(function_names=loaded_agent_config["tool_functions"])
tools = toolkit.tools
function_client = DatabricksFunctionClient(execution_mode="serverless")

llm = ChatDatabricks(
    endpoint=loaded_agent_config["llm_endpoint"],
    temperature=loaded_agent_config["llm_temperature"],
)
prompt_payload = [
    ("system", loaded_agent_config["system_prompt"]),
    ("placeholder", "{chat_history}"),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}"),
]
prompt = ChatPromptTemplate.from_messages(prompt_payload)
agent = create_tool_calling_agent(llm=llm, tools=tools, prompt=prompt)
demo_agent = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    return_intermediate_steps=True,
    handle_parsing_errors=True,
)

demo_prompt = (
    f"What is the average nightly price in the dataset? Then summarize listing ID {sample_listing_id}. "
    "Use the Unity Catalog tools and state only what they return."
)
print("Demo agent prompt:")
print(demo_prompt)

try:
    demo_agent_result = demo_agent.invoke({"input": demo_prompt, "chat_history": []})
    print("\nDemo agent answer:")
    print(demo_agent_result["output"])
except Exception as agent_error:
    raise RuntimeError(
        "The demo agent could not run. Confirm that Meta Llama 3.3 70B Instruct is available and that you have "
        "EXECUTE privileges on the Unity Catalog functions. "
        f"Original error: {type(agent_error).__name__}: {agent_error}"
    ) from agent_error

# COMMAND ----------

# MAGIC %md
# MAGIC ## 7. Create a custom Unity Catalog trace location
# MAGIC
# MAGIC This optional production-style configuration stores traces in four governed OpenTelemetry
# MAGIC Delta tables in `workspace.default`. It requires an accessible SQL Warehouse, MLflow 3.14+,
# MAGIC the Unity Catalog tracing preview, and `USE CATALOG`, `USE SCHEMA`, `MODIFY`, and `SELECT`
# MAGIC privileges. The code detects the available SQL Warehouse. If the workspace does not support
# MAGIC this preview, it prints a diagnostic and leaves the Workspace experiment from section 5 usable.

# COMMAND ----------

from mlflow.entities.trace_location import UnityCatalog


def get_accessible_sql_warehouse_id() -> str:
    """Return the first SQL Warehouse visible to the current user for Unity Catalog trace queries."""
    warehouses = list(WorkspaceClient().warehouses.list())
    if not warehouses:
        raise RuntimeError(
            "No SQL Warehouse is available. Create or start a SQL Warehouse, then run this section again."
        )
    return warehouses[0].id


uc_trace_experiment_path = f"/Users/{username}/single_agents_demo1_uc_traces"
uc_trace_table_prefix = "single_agents_demo1"

try:
    sql_warehouse_id = get_accessible_sql_warehouse_id()
    os.environ["MLFLOW_TRACING_SQL_WAREHOUSE_ID"] = sql_warehouse_id
    uc_trace_experiment = mlflow.set_experiment(
        experiment_name=uc_trace_experiment_path,
        trace_location=UnityCatalog(
            catalog_name=catalog,
            schema_name=schema,
            table_prefix=uc_trace_table_prefix,
        ),
    )
    print(f"Unity Catalog trace experiment ID: {uc_trace_experiment.experiment_id}")
    print(f"SQL Warehouse ID: {sql_warehouse_id}")
    print(f"OTel spans table: {uc_trace_experiment.trace_location.full_otel_spans_table_name}")
except Exception as uc_trace_error:
    print(
        "[NOTICE] Unity Catalog trace storage was not configured. The Workspace experiment remains available. "
        "Confirm the Unity Catalog tracing preview, an accessible SQL Warehouse, MLflow 3.14+, and UC privileges. "
        f"Original error: {type(uc_trace_error).__name__}: {uc_trace_error}"
    )

# COMMAND ----------

# MAGIC %md
# MAGIC ## 8. Use the MLflow trace decorator with an intentional invalid prompt
# MAGIC
# MAGIC The `CallLLM` function deliberately treats `Hej` as an invalid test prompt. The resulting
# MAGIC exception is recorded in an MLflow trace and can be inspected in the **Traces** tab.

# COMMAND ----------

@mlflow.trace(
    name="CallLLM",
    span_type=SpanType.LLM,
    attributes={"model": loaded_agent_config["llm_endpoint"], "demo": "intentional-invalid-prompt"},
)
def CallLLM(user_prompt: str) -> str:
    """Validate a course prompt and invoke the configured Databricks Foundation Model."""
    if user_prompt.strip() == "Hej":
        raise ValueError("Intentional tracing demonstration: 'Hej' is not a valid Airbnb agent prompt.")
    response = llm.invoke(user_prompt)
    return response.content


invalid_prompt = "Hej"
try:
    CallLLM(invalid_prompt)
except ValueError as intentional_error:
    print(f"Captured intentional prompt error: {intentional_error}")

print(f"Most recent MLflow trace ID: {mlflow.get_last_active_trace_id()}")
