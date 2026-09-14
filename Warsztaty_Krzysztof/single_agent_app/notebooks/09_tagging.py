# Databricks notebook source
# MAGIC %md
# MAGIC # 09 - Tagging, logging, and registering an Airbnb function agent
# MAGIC
# MAGIC This notebook continues from notebooks 06 to 08. It uses persisted Unity Catalog assets,
# MAGIC creates tagged MLflow traces, packages the agent as a Python function model, and registers it
# MAGIC in Unity Catalog. Run the cells from top to bottom.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Setup - Install compatible dependencies
# MAGIC
# MAGIC Run this cell once. The next cell restarts Python. All notebook variables are recreated
# MAGIC after the restart, so this notebook does not rely on Python objects from earlier notebooks.

# COMMAND ----------

# MAGIC %pip install --upgrade --force-reinstall --no-cache-dir "mlflow[databricks]>=3.14.0" "openai>=1.0.0" "databricks-langchain==0.18.0" "langchain==1.3.14" "langchain-classic>=1.0.1" "langgraph==1.2.9" "langgraph-prebuilt>=1.1.0,<1.2.0" "unitycatalog-ai[databricks]" pandas

# COMMAND ----------

# Restart Python so the pinned dependency set is available to the notebook.
dbutils.library.restartPython()

# COMMAND ----------

import json
from importlib.metadata import version

import mlflow
import pandas as pd
from databricks_langchain import ChatDatabricks, UCFunctionToolkit
from langchain_classic.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from mlflow.entities import SpanType
from mlflow.models import infer_signature
from mlflow.models.resources import DatabricksFunction, DatabricksServingEndpoint, DatabricksTable


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
tracing_agent_config_path = f"{agent_volume_path}/mlflow_tracing_agent_config.json"
pyfunc_agent_config_path = f"{agent_volume_path}/demo_agent2_config.json"
agent_python_path = f"{agent_volume_path}/demo_agent2.py"
username = get_workspace_username()
workspace_experiment_path = f"/Users/{username}/single_agents_demo2"
uc_model_name = f"{catalog}.{schema}.airbnb_demo_agent"

print(f"mlflow: {version('mlflow')}")
print(f"databricks-langchain: {version('databricks-langchain')}")
print(f"Workspace experiment: {workspace_experiment_path}")
print(f"Unity Catalog model name: {uc_model_name}")

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
sample_listing_id = int(airbnb_df.orderBy("id").first()["id"])

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Enable MLflow autologging and set the experiment location

# COMMAND ----------

mlflow.set_tracking_uri("databricks")
mlflow.set_registry_uri("databricks-uc")
active_experiment = mlflow.set_experiment(workspace_experiment_path)
mlflow.langchain.autolog()
mlflow.openai.autolog()

print(f"Active MLflow experiment: {workspace_experiment_path}")
print(f"Experiment ID: {active_experiment.experiment_id}")
print("MLflow LangChain and OpenAI-compatible autologging are enabled.")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Load the demo agent
# MAGIC
# MAGIC Notebook 08 created `mlflow_tracing_agent_config.json`. The earlier notebooks did not need a
# MAGIC standalone Python agent file because they ran the agent directly in a notebook. This notebook
# MAGIC creates `demo_agent2.py` in section 6, immediately before packaging it as an MLflow pyfunc model.

# COMMAND ----------

try:
    loaded_agent_config = json.loads(dbutils.fs.head(tracing_agent_config_path))
except Exception as config_error:
    raise RuntimeError(
        f"Could not load {tracing_agent_config_path}. Run notebook 08 successfully before this notebook. "
        f"Original error: {type(config_error).__name__}: {config_error}"
    ) from config_error

toolkit = UCFunctionToolkit(function_names=loaded_agent_config["tool_functions"])
tools = toolkit.tools
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

print(f"Loaded agent endpoint: {loaded_agent_config['llm_endpoint']}")
print("Loaded tools:")
for tool in tools:
    print(f"- {tool.name}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Create tags for the trace decorator

# COMMAND ----------

# Keep tag values short and stable so traces can be filtered and grouped in the MLflow UI.
trace_tags = {
    "course_module": "single_agent_app",
    "agent_name": "airbnb_function_agent",
    "validation_policy": "prompt_length_20_to_500",
    "environment": "development",
}
print(json.dumps(trace_tags, indent=2))

# COMMAND ----------

# MAGIC %md
# MAGIC ## 5. Validate prompt length and attach trace tags

# COMMAND ----------

@mlflow.trace(name="ValidatePrompt", span_type=SpanType.CHAIN)
def validate_prompt(user_prompt: str) -> str:
    """Validate the prompt length and add the current course tags to its active MLflow trace."""
    mlflow.update_current_trace(tags=trace_tags)
    normalized_prompt = user_prompt.strip()
    if not 20 <= len(normalized_prompt) <= 500:
        raise ValueError("Prompt length must be between 20 and 500 characters.")
    return normalized_prompt


valid_prompt = validate_prompt(
    f"What is the average nightly price and what are the details for listing ID {sample_listing_id}?"
)
print(f"Validated prompt: {valid_prompt}")

try:
    validate_prompt("Too short")
except ValueError as validation_error:
    print(f"Captured intentional validation error: {validation_error}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 6. Export, log, and save the agent as an MLflow pyfunc model

# COMMAND ----------

# Create the managed Volume only if it does not exist. It stores the agent code and configuration.
spark.sql(f"CREATE VOLUME IF NOT EXISTS {agent_volume_fqn}")
dbutils.fs.put(pyfunc_agent_config_path, json.dumps(loaded_agent_config, indent=2), overwrite=True)

# The exported file is a Models from Code pyfunc implementation, not a notebook-only copy.
agent_python_source = '''import json
import pandas as pd
import mlflow
from databricks_langchain import ChatDatabricks, UCFunctionToolkit
from langchain_classic.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate


class AirbnbFunctionAgentModel(mlflow.pyfunc.PythonModel):
    """Serve the Airbnb Unity Catalog function agent through the MLflow pyfunc interface."""

    def load_context(self, context):
        with open(context.artifacts["agent_config"], "r", encoding="utf-8") as config_file:
            config = json.load(config_file)
        toolkit = UCFunctionToolkit(function_names=config["tool_functions"])
        tools = toolkit.tools
        llm = ChatDatabricks(
            endpoint=config["llm_endpoint"],
            temperature=config["llm_temperature"],
        )
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", config["system_prompt"]),
                ("placeholder", "{chat_history}"),
                ("human", "{input}"),
                ("placeholder", "{agent_scratchpad}"),
            ]
        )
        agent = create_tool_calling_agent(llm=llm, tools=tools, prompt=prompt)
        self.agent_executor = AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=False,
            handle_parsing_errors=True,
        )

    def predict(self, context, model_input, params=None):
        if not isinstance(model_input, pd.DataFrame):
            model_input = pd.DataFrame(model_input)
        if "prompt" not in model_input.columns:
            raise ValueError("Model input must contain a 'prompt' column.")
        answers = []
        for user_prompt in model_input["prompt"].astype(str).tolist():
            result = self.agent_executor.invoke({"input": user_prompt, "chat_history": []})
            answers.append(result["output"])
        return pd.DataFrame({"answer": answers})


mlflow.models.set_model(AirbnbFunctionAgentModel())
'''
dbutils.fs.put(agent_python_path, agent_python_source, overwrite=True)

input_example = pd.DataFrame(
    {
        "prompt": [
            f"What is the average nightly price in the dataset and what are the details for listing ID {sample_listing_id}?"
        ]
    }
)
output_example = pd.DataFrame({"answer": ["The agent returns a tool-grounded Airbnb dataset answer."]})
model_signature = infer_signature(input_example, output_example)
model_tags = {
    "course_module": "single_agent_app",
    "agent_type": "unity_catalog_function_agent",
    "validation_policy": trace_tags["validation_policy"],
    "source_table": airbnb_table,
}
model_resources = [
    DatabricksServingEndpoint(endpoint_name=loaded_agent_config["llm_endpoint"]),
    DatabricksFunction(function_name=average_price_function),
    DatabricksFunction(function_name=listing_details_function),
    DatabricksFunction(function_name=python_formatting_function),
    DatabricksTable(table_name=airbnb_table),
]

with mlflow.start_run(run_name="log-airbnb-demo-agent"):
    mlflow.set_tags(model_tags)
    logged_model_info = mlflow.pyfunc.log_model(
        name="airbnb_function_agent",
        python_model=agent_python_path,
        artifacts={"agent_config": pyfunc_agent_config_path},
        input_example=input_example,
        signature=model_signature,
        pip_requirements=[
            f"mlflow=={version('mlflow')}",
            "pandas",
            "databricks-langchain==0.18.0",
            "langchain==1.3.14",
            "langchain-classic>=1.0.1",
            "langgraph==1.2.9",
            "langgraph-prebuilt>=1.1.0,<1.2.0",
            "unitycatalog-ai[databricks]",
        ],
        resources=model_resources,
        tags=model_tags,
        model_type="databricks-agent",
    )
    model_uri = logged_model_info.model_uri

print(f"Created agent source file: {agent_python_path}")
print(f"Created agent configuration file: {pyfunc_agent_config_path}")
print(f"Saved model URI: {model_uri}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 7. Load the logged model with `mlflow.pyfunc.load_model`

# COMMAND ----------

loaded_pyfunc_model = mlflow.pyfunc.load_model(model_uri)
pyfunc_prediction = loaded_pyfunc_model.predict(input_example)
display(pyfunc_prediction)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 8. Register the agent in Unity Catalog

# COMMAND ----------

try:
    registered_model_version = mlflow.register_model(model_uri, uc_model_name)
    mlflow_client = mlflow.tracking.MlflowClient()
    for tag_key, tag_value in model_tags.items():
        mlflow_client.set_registered_model_tag(uc_model_name, tag_key, tag_value)
        mlflow_client.set_model_version_tag(
            uc_model_name,
            registered_model_version.version,
            tag_key,
            tag_value,
        )
except Exception as registration_error:
    raise RuntimeError(
        "Could not register the agent in Unity Catalog. Confirm USE CATALOG, USE SCHEMA, and CREATE MODEL "
        f"privileges on {catalog}.{schema}. Original error: {type(registration_error).__name__}: {registration_error}"
    ) from registration_error

registered_model_uri = f"models:/{uc_model_name}/{registered_model_version.version}"
print(f"Registered Unity Catalog model version: {registered_model_uri}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 9. Explore traces, the model, and lineage in the Databricks UI
# MAGIC
# MAGIC 1. Open **Experiments** in the left navigation, then open `single_agents_demo2` in your user folder.
# MAGIC 2. Open the **Traces** tab. Filter traces with `tags.agent_name = 'airbnb_function_agent'` or open a trace to inspect its tags, validation span, model call, and Unity Catalog function calls.
# MAGIC 3. Open **Catalog** > `workspace` > `default` > **Models** > `airbnb_demo_agent` and select the version created in section 8.
# MAGIC 4. On the model-version page, open **Lineage** to inspect the declared LLM endpoint, Unity Catalog functions, and Airbnb Delta table dependencies.

# COMMAND ----------

# MAGIC %md
# MAGIC ## 10. Load the model from Unity Catalog

# COMMAND ----------

uc_loaded_model = mlflow.pyfunc.load_model(registered_model_uri)
uc_prediction = uc_loaded_model.predict(input_example)
display(uc_prediction)
