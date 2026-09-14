# Databricks notebook source
# MAGIC %md
# MAGIC # 07 - Building an Airbnb Unity Catalog function agent
# MAGIC
# MAGIC This notebook continues from `06_building_uc_functions.py`. It uses the Airbnb Delta
# MAGIC table and the Unity Catalog functions created there to build and test a LangChain agent.
# MAGIC Run the cells from top to bottom.

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Install and import dependencies
# MAGIC
# MAGIC Run the installation cell once. The next cell restarts Python; then continue from the
# MAGIC import cell in this section. LangChain Classic preserves the requested `AgentExecutor`
# MAGIC API, while the LangChain and LangGraph versions are pinned together to prevent
# MAGIC incompatible `langgraph-prebuilt` imports.

# COMMAND ----------

# MAGIC %pip install --upgrade --force-reinstall --no-cache-dir "databricks-langchain==0.18.0" "langchain==1.3.14" "langchain-classic>=1.0.1" "langgraph==1.2.9" "langgraph-prebuilt>=1.1.0,<1.2.0" mlflow "unitycatalog-ai[databricks]"

# COMMAND ----------

# Restart Python so the installed packages are available in subsequent cells.
dbutils.library.restartPython()

# COMMAND ----------

from databricks_langchain import UCFunctionToolkit
from unitycatalog.ai.core.databricks import DatabricksFunctionClient
from importlib.metadata import version

# Define notebook objects after restartPython because it clears the Python interpreter state.
catalog = "workspace"
schema = "default"
airbnb_table = f"{catalog}.{schema}.sf_airbnb_listings"
average_price_function = f"{catalog}.{schema}.get_average_listing_price"
listing_details_function = f"{catalog}.{schema}.get_listing_details"
python_formatting_function = f"{catalog}.{schema}.format_listing_for_agent"
agent_config_path = "/Volumes/workspace/default/sf_airbnb_data/airbnb_agent_config.json"

print("Databricks LangChain and Unity Catalog AI dependencies are available.")
print(f"databricks-langchain: {version('databricks-langchain')}")
print(f"langchain: {version('langchain')}")
print(f"langchain-classic: {version('langchain-classic')}")
print(f"langgraph: {version('langgraph')}")
print(f"langgraph-prebuilt: {version('langgraph-prebuilt')}")
print(f"Airbnb Delta table: {airbnb_table}")
print(f"Agent configuration file: {agent_config_path}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Display five Airbnb Delta table records

# COMMAND ----------

try:
    airbnb_df = spark.table(airbnb_table)
except Exception as table_error:
    raise RuntimeError(
        f"Could not read {airbnb_table}. Run notebook 06 successfully before running this notebook. "
        f"Original error: {type(table_error).__name__}: {table_error}"
    ) from table_error

if airbnb_df.limit(1).count() == 0:
    raise ValueError(f"The Delta table {airbnb_table} is empty.")

display(airbnb_df.orderBy("id").limit(5))

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Create a Databricks Function Client

# COMMAND ----------

# Use serverless execution because Unity Catalog function tools execute on serverless generic compute.
client = DatabricksFunctionClient(execution_mode="serverless")
print("Databricks Function Client initialized for serverless execution.")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Load the Unity Catalog tools

# COMMAND ----------

# Keep the complete names so the agent invokes the governed functions created in notebook 06.
function_names = [
    average_price_function,
    listing_details_function,
    python_formatting_function,
]

print("Unity Catalog functions available to the agent:")
for function_name in function_names:
    print(f"- {function_name}")

# Wrap the Unity Catalog functions as LangChain tools and preserve their UC comments as tool descriptions.
toolkit = UCFunctionToolkit(function_names=function_names)
tools = toolkit.tools

print("\nLangChain tool definitions:")
for tool in tools:
    print(f"- {tool.name}: {tool.description}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 5. Test the Unity Catalog functions with client payloads

# COMMAND ----------

# Build valid payloads from a real table row so all registered functions can be tested directly.
sample_listing = airbnb_df.orderBy("id").first().asDict()
sample_listing_id = int(sample_listing["id"])

function_test_payloads = [
    {
        "label": "Average nightly price",
        "function_name": average_price_function,
        "parameters": {},
    },
    {
        "label": "Listing details",
        "function_name": listing_details_function,
        "parameters": {"requested_listing_id": sample_listing_id},
    },
    {
        "label": "Formatted listing",
        "function_name": python_formatting_function,
        "parameters": {
            "listing_id": sample_listing_id,
            "name": sample_listing.get("name") or "Not provided",
            "host_name": sample_listing.get("host_name") or "Not provided",
            "neighbourhood": sample_listing.get("neighbourhood") or "Not provided",
            "room_type": sample_listing.get("room_type") or "Not provided",
            "nightly_price_usd": float(sample_listing.get("price") or 0.0),
            "minimum_nights": int(sample_listing.get("minimum_nights") or 0),
            "number_of_reviews": int(sample_listing.get("number_of_reviews") or 0),
            "availability_365": int(sample_listing.get("availability_365") or 0),
        },
    },
]

for payload in function_test_payloads:
    try:
        result = client.execute_function(
            function_name=payload["function_name"],
            parameters=payload["parameters"],
        )
        print(f"\n{payload['label']}:")
        print(result.value)
    except Exception as function_error:
        raise RuntimeError(
            f"Function test failed for {payload['function_name']}. Confirm USE CATALOG, USE SCHEMA, "
            f"and EXECUTE privileges. Original error: {type(function_error).__name__}: {function_error}"
        ) from function_error

# COMMAND ----------

# MAGIC %md
# MAGIC ## 6. Create and load the JSON agent configuration

# COMMAND ----------

import json

# Store only stable agent settings in JSON so the model and instructions can be changed without editing agent code.
agent_config = {
    "llm_endpoint": "databricks-meta-llama-3-3-70b-instruct",
    "llm_temperature": 0.1,
    "system_prompt": (
        "You are a helpful and professional assistant for the San Francisco Airbnb course dataset. "
        "Use Unity Catalog tools whenever the question asks for facts, prices, averages, or listing details. "
        "Treat tool results as the only source of truth for dataset facts. Do not invent listing values. "
        "If the available tools cannot answer a question, say that you do not know based on the available data."
    ),
}

dbutils.fs.put(agent_config_path, json.dumps(agent_config, indent=2), overwrite=True)
print(f"Created JSON configuration: {agent_config_path}")
print(dbutils.fs.head(agent_config_path))

# Load the same JSON file that will provide runtime settings for the agent.
loaded_agent_config = json.loads(dbutils.fs.head(agent_config_path))

# COMMAND ----------

# MAGIC %md
# MAGIC ## 7. Import the agent and tracing libraries

# COMMAND ----------

import mlflow
from databricks_langchain import ChatDatabricks
from langchain_classic.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate

# COMMAND ----------

# MAGIC %md
# MAGIC ## 8. Initialize the LLM and define the prompt payload

# COMMAND ----------

# Initialize the model selected in the JSON configuration.
llm = ChatDatabricks(
    endpoint=loaded_agent_config["llm_endpoint"],
    temperature=loaded_agent_config["llm_temperature"],
)

# Preserve the standard tool-calling message structure required by create_tool_calling_agent.
prompt_payload = [
    ("system", loaded_agent_config["system_prompt"]),
    ("placeholder", "{chat_history}"),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}"),
]
prompt = ChatPromptTemplate.from_messages(prompt_payload)

print(f"LLM endpoint: {loaded_agent_config['llm_endpoint']}")
print(f"LLM temperature: {loaded_agent_config['llm_temperature']}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 9. Enable MLflow tracing and create the agent configuration

# COMMAND ----------

# Enable automatic LangChain traces before the agent executes its first request.
mlflow.langchain.autolog()
mlflow.set_experiment("/Shared/single_agent_app_airbnb_function_agent")

# Keep a readable runtime summary that combines the model, tools, and prompt structure.
agent_runtime_configuration = {
    "llm": {
        "endpoint": loaded_agent_config["llm_endpoint"],
        "temperature": loaded_agent_config["llm_temperature"],
    },
    "tools": [tool.name for tool in tools],
    "prompt_payload": prompt_payload,
}
print(json.dumps(agent_runtime_configuration, indent=2))

# Build an agent that can decide when to call the Unity Catalog function tools.
agent = create_tool_calling_agent(llm=llm, tools=tools, prompt=prompt)
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    return_intermediate_steps=True,
    handle_parsing_errors=True,
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 10. Run a sample agent prompt

# COMMAND ----------

sample_prompt = (
    f"What is the average nightly price in the dataset? Then summarize listing ID {sample_listing_id}. "
    "Use the available tools and state only what they return."
)

print("Agent prompt:")
print(sample_prompt)

try:
    agent_result = agent_executor.invoke({"input": sample_prompt, "chat_history": []})
except Exception as agent_error:
    raise RuntimeError(
        "The Airbnb function agent could not run. Confirm that the Meta Llama 3.3 70B Instruct endpoint is available and that you "
        "have EXECUTE privileges on the Unity Catalog functions. "
        f"Original error: {type(agent_error).__name__}: {agent_error}"
    ) from agent_error

# COMMAND ----------

# MAGIC %md
# MAGIC ## 11. Parse and display the agent response

# COMMAND ----------

def parse_agent_response(result: dict) -> dict:
    """Extract the final text and a compact record of tool calls from an AgentExecutor result."""
    parsed_tool_calls = []
    for action, observation in result.get("intermediate_steps", []):
        parsed_tool_calls.append(
            {
                "tool": action.tool,
                "tool_input": action.tool_input,
                "observation": str(observation),
            }
        )
    return {
        "prompt": result.get("input", ""),
        "answer": result.get("output", ""),
        "tool_calls": parsed_tool_calls,
    }


parsed_agent_response = parse_agent_response(agent_result)
print("Final agent answer:")
print(parsed_agent_response["answer"])

print("\nParsed response:")
print(json.dumps(parsed_agent_response, indent=2, default=str))
