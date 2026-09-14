# Databricks notebook source
# MAGIC %md
# MAGIC # 16 — Deploying and monitoring a robotics RAG chain
# MAGIC
# MAGIC This notebook packages a small LangChain RAG application, registers it in Unity Catalog,
# MAGIC deploys it as a custom Model Serving endpoint, sends test inference requests, and explains
# MAGIC where to inspect the endpoint inference table. It reuses the robotics AI Search index built in
# MAGIC the `rag_agent` module.
# MAGIC
# MAGIC Run the cells from top to bottom. The endpoint deployment in section 3 can take around
# MAGIC **10 minutes** (and sometimes longer when serverless capacity is limited).

# COMMAND ----------

# MAGIC %md
# MAGIC ## Runtime dependencies
# MAGIC
# MAGIC This notebook deliberately uses a simple LCEL chain rather than `AgentExecutor`, avoiding
# MAGIC the LangChain and LangGraph import incompatibilities encountered in earlier exercises. The
# MAGIC Databricks Runtime already provides MLflow and the Databricks SDK. Installing only the
# MAGIC Databricks LangChain integration avoids pip attempting a large, conflicting upgrade of the
# MAGIC entire runtime dependency graph.

# COMMAND ----------

# MAGIC %pip install --quiet "databricks-langchain==0.20.0"

# COMMAND ----------

# MAGIC dbutils.library.restartPython()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Minimal configuration
# MAGIC
# MAGIC The AI Search index must already be `ONLINE`. The secret scope is created in section 2 before
# MAGIC deployment; its values are referenced by Model Serving and are never printed by this notebook.

# COMMAND ----------

catalog = "workspace"
schema = "default"

vector_search_endpoint = "robotics_ai_search_endpoint"
vector_search_index = f"{catalog}.{schema}.robotics_document_chunks_index"
llm_endpoint = "databricks-meta-llama-3-3-70b-instruct"

rag_model_name = f"{catalog}.{schema}.robotics_rag_deployment_chain"
rag_serving_endpoint = "robotics-rag-deployment-endpoint"
mlflow_experiment_path = "/Shared/genai_deploy_and_monitor_rag_deployment"

secret_scope = "rag_deployment_secrets"
host_secret_key = "databricks_host"
token_secret_key = "databricks_token"

inference_table_prefix = "robotics_rag_inference"

rag_input_example = {
    "messages": [
        {"role": "user", "content": "How do collaborative robots work safely near people?"}
    ]
}

print(f"RAG model: {rag_model_name}")
print(f"Serving endpoint: {rag_serving_endpoint}")
print(f"AI Search index: {vector_search_index}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Prepare the RAG client, register it in Unity Catalog, and run a sanity check
# MAGIC
# MAGIC The chain retrieves chunks from the existing robotics AI Search index and then asks the LLM to
# MAGIC answer strictly from that retrieved context. It is logged with explicit Databricks resources so
# MAGIC Unity Catalog can record its dependencies.

# COMMAND ----------

import mlflow
from pathlib import Path
from operator import itemgetter

from databricks_langchain import ChatDatabricks
from databricks_langchain.vectorstores import DatabricksVectorSearch
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableLambda
from mlflow.models.resources import DatabricksServingEndpoint, DatabricksVectorSearchIndex


def extract_latest_question(messages):
    """Return the text of the most recent user message in a chat payload."""
    return messages[-1]["content"]


def format_chat_history(messages):
    """Convert prior chat messages into a compact string for the RAG prompt."""
    return "\n".join(
        f"{message['role']}: {message['content']}" for message in messages[:-1]
    )


def combine_messages_for_retrieval(messages):
    """Combine prior context and the latest question before vector retrieval."""
    history = format_chat_history(messages)
    question = extract_latest_question(messages)
    return f"{history}\nuser: {question}".strip()


def format_retrieved_documents(documents):
    """Format retrieved AI Search documents as context for the language model."""
    if not documents:
        return "No relevant course material was retrieved."
    return "\n\n".join(f"Passage: {document.page_content}" for document in documents)


retriever = DatabricksVectorSearch(
    endpoint=vector_search_endpoint,
    index_name=vector_search_index,
    columns=["chunk_id", "path", "chunk_text"],
).as_retriever(search_kwargs={"k": 3})

rag_prompt = PromptTemplate(
    template=(
        "You are a helpful and professional robotics specialist. Answer only from the retrieved "
        "course material. If the material does not contain the answer, say exactly: 'I do not know "
        "based on the available materials.' Do not invent facts.\n\n"
        "Conversation history:\n{chat_history}\n\n"
        "Retrieved course material:\n{context}\n\n"
        "Question: {question}\nAnswer:"
    ),
    input_variables=["question", "context", "chat_history"],
)

chat_model = ChatDatabricks(
    endpoint=llm_endpoint,
    temperature=0.0,
    max_tokens=500,
)

rag_chain = (
    {
        "question": itemgetter("messages") | RunnableLambda(extract_latest_question),
        "context": (
            itemgetter("messages")
            | RunnableLambda(combine_messages_for_retrieval)
            | retriever
            | RunnableLambda(format_retrieved_documents)
        ),
        "chat_history": itemgetter("messages") | RunnableLambda(format_chat_history),
    }
    | rag_prompt
    | chat_model
    | StrOutputParser()
)

sanity_answer = rag_chain.invoke(rag_input_example)
print("Sanity-check prompt:")
print(rag_input_example)
print("\nSanity-check answer:")
print(sanity_answer)

mlflow.set_registry_uri("databricks-uc")
mlflow.set_experiment(mlflow_experiment_path)

# MLflow 3 logs LangChain applications as models-from-code. The source file repeats the
# deployment-safe chain definition and reads Databricks credentials from endpoint environment variables.
rag_chain_source_path = Path("/tmp/robotics_rag_chain_model.py")
rag_chain_source = '''
import mlflow
from operator import itemgetter

from databricks_langchain import ChatDatabricks
from databricks_langchain.vectorstores import DatabricksVectorSearch
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableLambda

VECTOR_SEARCH_ENDPOINT = __VECTOR_SEARCH_ENDPOINT__
VECTOR_SEARCH_INDEX = __VECTOR_SEARCH_INDEX__
LLM_ENDPOINT = __LLM_ENDPOINT__
SYSTEM_PROMPT = __SYSTEM_PROMPT__


def extract_latest_question(messages):
    """Return the text of the most recent user message in a chat payload."""
    return messages[-1]["content"]


def format_chat_history(messages):
    """Convert prior chat messages into a compact string for the RAG prompt."""
    return "\\n".join(
        f"{message['role']}: {message['content']}" for message in messages[:-1]
    )


def combine_messages_for_retrieval(messages):
    """Combine prior context and the latest question before vector retrieval."""
    history = format_chat_history(messages)
    question = extract_latest_question(messages)
    return f"{history}\\nuser: {question}".strip()


def format_retrieved_documents(documents):
    """Format retrieved AI Search documents as context for the language model."""
    if not documents:
        return "No relevant course material was retrieved."
    return "\\n\\n".join(f"Passage: {document.page_content}" for document in documents)


retriever = DatabricksVectorSearch(
    endpoint=VECTOR_SEARCH_ENDPOINT,
    index_name=VECTOR_SEARCH_INDEX,
    columns=["chunk_id", "path", "chunk_text"],
).as_retriever(search_kwargs={"k": 3})

prompt = PromptTemplate(
    template=SYSTEM_PROMPT,
    input_variables=["question", "context", "chat_history"],
)
model = ChatDatabricks(
    endpoint=LLM_ENDPOINT,
    temperature=0.0,
    max_tokens=500,
)

rag_chain = (
    {
        "question": itemgetter("messages") | RunnableLambda(extract_latest_question),
        "context": (
            itemgetter("messages")
            | RunnableLambda(combine_messages_for_retrieval)
            | retriever
            | RunnableLambda(format_retrieved_documents)
        ),
        "chat_history": itemgetter("messages") | RunnableLambda(format_chat_history),
    }
    | prompt
    | model
    | StrOutputParser()
)

mlflow.models.set_model(model=rag_chain)
'''

for placeholder, value in {
    "__VECTOR_SEARCH_ENDPOINT__": vector_search_endpoint,
    "__VECTOR_SEARCH_INDEX__": vector_search_index,
    "__LLM_ENDPOINT__": llm_endpoint,
    "__SYSTEM_PROMPT__": rag_prompt.template,
}.items():
    rag_chain_source = rag_chain_source.replace(placeholder, repr(value))

rag_chain_source_path.write_text(rag_chain_source, encoding="utf-8")
print(f"Created models-from-code source file: {rag_chain_source_path}")

with mlflow.start_run(run_name="robotics_rag_chain_deployment"):
    logged_rag_model = mlflow.langchain.log_model(
        lc_model=str(rag_chain_source_path),
        name="robotics_rag_chain",
        input_example=rag_input_example,
        resources=[
            DatabricksVectorSearchIndex(index_name=vector_search_index),
            DatabricksServingEndpoint(endpoint_name=llm_endpoint),
        ],
        pip_requirements=[
            "mlflow[databricks]>=3.14.0",
            "databricks-sdk>=0.102.0",
            "databricks-langchain",
            "databricks-ai-search",
            "langchain",
        ],
    )

registered_rag_version = mlflow.register_model(
    model_uri=logged_rag_model.model_uri,
    name=rag_model_name,
)

print(f"Logged model URI: {logged_rag_model.model_uri}")
print(f"Unity Catalog model: {rag_model_name}")
print(f"Registered version: {registered_rag_version.version}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Set up secrets for the deployed RAG chain
# MAGIC
# MAGIC The served chain needs a Databricks host and a token at runtime to call AI Search and the LLM.
# MAGIC Do not paste either value into this notebook.
# MAGIC
# MAGIC ### 2a. Create the personal access token in the workspace UI
# MAGIC
# MAGIC 1. Click your user name in the top-right corner, then select **Settings** â†’ **Developer** â†’
# MAGIC    **Access tokens** â†’ **Manage** â†’ **Generate new token**.
# MAGIC 2. Use the name **`rag-deployment-model-serving`**. It makes this course token identifiable and
# MAGIC    distinct from any general-purpose token.
# MAGIC 3. Set a course-appropriate lifetime, for example **30 days**. Create a replacement token if
# MAGIC    you continue after it expires; never extend a token indefinitely just for convenience.
# MAGIC 4. For **API scope**, select **Other APIs** and then **All APIs**. Do not select **BI Tools**.
# MAGIC    Some Free Edition workspaces do not show the **Auto-scope tokens** switch. In that UI, an
# MAGIC    all-APIs workspace token is the reliable course option: this notebook needs Serving, AI
# MAGIC    Search, and Secrets operations, so a guessed manual scope list can stop deployment later.
# MAGIC    Keep the short lifetime and revoke the token after completing the exercise.
# MAGIC 5. Click **Generate**, copy the token once, and keep it in a temporary secure location. The UI
# MAGIC    will not reveal the token value again. Never put it in a notebook, Git repository, chat, or
# MAGIC    screenshot.
# MAGIC
# MAGIC ### 2b. Create the secret scope in the Databricks UI
# MAGIC
# MAGIC 1. In the browser address bar, open this page in the **same workspace**:
# MAGIC    `https://dbc-0d60e5af-7e80.cloud.databricks.com#secrets/createScope`
# MAGIC 2. In **Scope Name**, enter exactly: `rag_deployment_secrets`.
# MAGIC 3. For **Manage Principal**, choose **Creator**. This keeps scope administration restricted to
# MAGIC    you. Choose **All workspace users** only when you intentionally want other workspace users
# MAGIC    to administer the scope.
# MAGIC 4. Click **Create**. Do not create the scope again from the CLI.
# MAGIC
# MAGIC ### 2c. Store the values from this notebook â€” no local CLI required
# MAGIC
# MAGIC Run the next cell in Databricks after completing sections 2a and 2b. It uses the notebook's
# MAGIC existing workspace authentication to write the two values to the scope. You paste the PAT into
# MAGIC a hidden runtime input only; it is not added to the notebook source, command output, Git, or a
# MAGIC local computer. The host is already defined in the cell. This is the only setup needed outside
# MAGIC the normal endpoint deployment steps.
# MAGIC
# MAGIC The deployed endpoint needs these secrets because it runs separately from your interactive
# MAGIC notebook session and must authenticate when it calls AI Search and the foundation-model
# MAGIC endpoint at inference time.

# COMMAND ----------

from getpass import getpass

from databricks.sdk import WorkspaceClient


def save_deployment_secrets_from_notebook():
    """Store the host and hidden personal access token in the existing Databricks secret scope."""
    personal_access_token = getpass("Paste the personal access token here (input remains hidden): ").strip()
    if not personal_access_token:
        raise ValueError("A personal access token is required.")

    secrets_client = WorkspaceClient()
    try:
        secrets_client.secrets.put_secret(
            scope=secret_scope,
            key=host_secret_key,
            string_value="https://dbc-0d60e5af-7e80.cloud.databricks.com",
        )
        secrets_client.secrets.put_secret(
            scope=secret_scope,
            key=token_secret_key,
            string_value=personal_access_token,
        )
    except Exception as secret_error:
        raise RuntimeError(
            f"Could not write to secret scope '{secret_scope}'. Create it first in section 2b and "
            "confirm that you are its Creator/manager."
        ) from secret_error

    print("Stored databricks_host and databricks_token in the secret scope. Values were not displayed.")


save_deployment_secrets_from_notebook()

try:
    dbutils.secrets.get(scope=secret_scope, key=host_secret_key)
    dbutils.secrets.get(scope=secret_scope, key=token_secret_key)
except Exception as secret_error:
    raise RuntimeError(
        "The secret scope exists, but this notebook cannot read both required keys. "
        f"Expected scope '{secret_scope}' with keys '{host_secret_key}' and '{token_secret_key}'."
    ) from secret_error

print(f"Secret scope '{secret_scope}' is available and both required keys can be read.")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Deploy or update the endpoint with the Databricks SDK
# MAGIC
# MAGIC **Warning:** this cell waits for a custom Model Serving endpoint update and can run for around
# MAGIC **10 minutes**. It creates the endpoint when absent; otherwise it updates the endpoint to the
# MAGIC newest registered RAG model version. The endpoint configuration enables scale-to-zero, maps
# MAGIC the two secret references to environment variables. The SDK submits this long-running operation
# MAGIC without waiting, which avoids the five-minute retry timeout of some Free Edition runtimes. Once
# MAGIC the endpoint status is **Ready**, enable the current **AI Gateway** inference table in the UI
# MAGIC using the exact values printed by the cell. It does not use the removed legacy
# MAGIC `auto_capture_config` API.

# COMMAND ----------

from databricks.sdk import WorkspaceClient
from databricks.sdk.errors import NotFound
from databricks.sdk.service.serving import (
    EndpointCoreConfigInput,
    ServedEntityInput,
)

endpoint_config_dict = {
    "name": rag_serving_endpoint,
    "config": {
        "served_entities": [
            {
                "name": "robotics-rag-chain",
                "entity_name": rag_model_name,
                "entity_version": str(registered_rag_version.version),
                "workload_size": "Small",
                "scale_to_zero_enabled": True,
                "environment_vars": {
                    "DATABRICKS_HOST": f"{{{{secrets/{secret_scope}/{host_secret_key}}}}}",
                    "DATABRICKS_TOKEN": f"{{{{secrets/{secret_scope}/{token_secret_key}}}}}",
                },
            }
        ],
    },
}

# Use notebook-native authentication. Some Free Edition runtimes bundle an SDK version that does not
# accept per-client timeout arguments, so endpoint readiness is handled explicitly below instead.
workspace_client = WorkspaceClient()
served_entities = [
    ServedEntityInput(**entity)
    for entity in endpoint_config_dict["config"]["served_entities"]
]

try:
    existing_endpoint = workspace_client.serving_endpoints.get(rag_serving_endpoint)
except NotFound:
    workspace_client.serving_endpoints.create(
        name=rag_serving_endpoint,
        config=EndpointCoreConfigInput(
            name=rag_serving_endpoint,
            served_entities=served_entities,
        ),
    )
    print(f"Submitted creation of serving endpoint: {rag_serving_endpoint}")
    print("Open Serving and wait for the endpoint status to become READY before continuing.")
else:
    pending_config = getattr(existing_endpoint, "pending_config", None)
    if pending_config is not None:
        print(
            f"Serving endpoint '{rag_serving_endpoint}' is already provisioning or updating. "
            "Open Serving, wait for status READY, and do not submit another update."
        )
    else:
        current_entities = getattr(getattr(existing_endpoint, "config", None), "served_entities", None) or []
        current_version_is_deployed = any(
            entity.entity_name == rag_model_name
            and str(entity.entity_version) == str(registered_rag_version.version)
            for entity in current_entities
        )
        if current_version_is_deployed:
            print(f"Endpoint already serves model version {registered_rag_version.version}; no update was submitted.")
        else:
            workspace_client.serving_endpoints.update_config(
                name=rag_serving_endpoint,
                served_entities=served_entities,
            )
            print(f"Submitted endpoint update to model version {registered_rag_version.version}: {rag_serving_endpoint}")
            print("Open Serving and wait for the endpoint status to become READY before continuing.")

print(
    "\nWhen the endpoint is READY, continue to section 5. In this Free Edition workspace, do not enable "
    "AI Gateway inference tables or telemetry for workspace.default: default storage is unsupported "
    "for the required OpenTelemetry tables."
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Alternative endpoint creation through the Databricks UI
# MAGIC
# MAGIC Use this method when the SDK request in section 3 times out or when you prefer to create the
# MAGIC endpoint visually. The endpoint name must remain exactly the same because sections 5 and 6 and
# MAGIC notebook 17 use it.
# MAGIC
# MAGIC **Important for this Free Edition workspace:** leave **Enable inference tables and telemetry**
# MAGIC disabled for catalog `workspace` and schema `default`. Their default storage cannot host the
# MAGIC OpenTelemetry or AI Gateway tables. The error mentioning `*_otel_spans` and "Tables created in
# MAGIC default storage are not supported" is the expected platform limitation, not an invalid model.
# MAGIC The RAG endpoint can run without telemetry; notebook 17 cannot use live endpoint payloads in
# MAGIC this workspace without an external-storage catalog.
# MAGIC
# MAGIC 1. Before creating the endpoint, open **Catalog**, then `workspace`, `default`, and **Models**.
# MAGIC    Confirm that `robotics_rag_deployment_chain` exists. If it is absent, run section 1 first.
# MAGIC 2. In the left sidebar, click **Serving**, then **Create serving endpoint**.
# MAGIC 3. Enter exactly `robotics-rag-deployment-endpoint` as the endpoint name.
# MAGIC 3. Under **Served entities**, choose **My models – Unity Catalog**, then select
# MAGIC    `workspace.default.robotics_rag_deployment_chain` and the version printed in section 1.
# MAGIC 4. Select **Small** CPU compute and enable **Scale to zero**.
# MAGIC 5. In **Environment variables**, add `DATABRICKS_HOST` with value
# MAGIC    `{{secrets/rag_deployment_secrets/databricks_host}}`, and `DATABRICKS_TOKEN` with value
# MAGIC    `{{secrets/rag_deployment_secrets/databricks_token}}`.
# MAGIC 6. In **AI Gateway** → **Inference tables**, enable logging and select catalog `workspace`,
# MAGIC    schema `default`, and prefix `robotics_rag_inference`.
# MAGIC 7. Click **Create** and wait for status **Ready**. If you need a newer model version later,
# MAGIC    open this endpoint, click **Edit endpoint**, select the new version, and save the update.
# MAGIC    If the create form does not show **AI Gateway** or **Inference tables**, create the endpoint
# MAGIC    without that setting. After it is Ready, open the endpoint and look for **Edit AI Gateway**.
# MAGIC    Configure catalog `workspace`, schema `default`, and prefix `robotics_rag_inference` there.
# MAGIC    If the option is still absent, this workspace does not currently expose AI Gateway inference
# MAGIC    tables for the endpoint; sections 1â€“6 can still work, but notebook 17 cannot receive payloads.
# MAGIC
# MAGIC ### Exact values for this course
# MAGIC
# MAGIC - **Endpoint name:** `robotics-rag-deployment-endpoint`
# MAGIC - **Unity Catalog model:** `workspace.default.robotics_rag_deployment_chain`
# MAGIC - **Model version:** the newest version visible after running section 1
# MAGIC - **Compute:** Small CPU; **Scale to zero:** enabled
# MAGIC - **Environment variable 1:** `DATABRICKS_HOST` =
# MAGIC   `{{secrets/rag_deployment_secrets/databricks_host}}`
# MAGIC - **Environment variable 2:** `DATABRICKS_TOKEN` =
# MAGIC   `{{secrets/rag_deployment_secrets/databricks_token}}`
# MAGIC - **AI Gateway inference table:** enabled; catalog `workspace`; schema `default`; table prefix
# MAGIC   `robotics_rag_inference`
# MAGIC
# MAGIC Wait until the endpoint is **Ready** before section 5. Section 5 creates its own workspace
# MAGIC client, so it also works when you skip the SDK deployment in section 3.

# COMMAND ----------

# MAGIC %md
# MAGIC ## 5. Run inference through the SDK and MLflow Deployments
# MAGIC
# MAGIC Both calls use the same `dataframe_records` request shape produced by the model input example.
# MAGIC The endpoint must be **Ready** before running this cell.

# COMMAND ----------

import mlflow.deployments
from databricks.sdk import WorkspaceClient

# Create the client here as well, so UI-created endpoints do not depend on section 3 having run.
workspace_client = WorkspaceClient()

inference_payload = {"dataframe_records": [rag_input_example]}

sdk_response = workspace_client.serving_endpoints.query(
    name=rag_serving_endpoint,
    dataframe_records=[rag_input_example],
)
print("Databricks SDK response:")
print(sdk_response)

deploy_client = mlflow.deployments.get_deploy_client("databricks")
deployments_response = deploy_client.predict(
    endpoint=rag_serving_endpoint,
    inputs=inference_payload,
)
print("\nMLflow Deployments response:")
print(deployments_response)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 6. View the inference table in the Databricks UI
# MAGIC
# MAGIC After section 5, wait one or two minutes for capture records to arrive.
# MAGIC
# MAGIC 1. Click **Serving** in the left sidebar and open `robotics-rag-deployment-endpoint`.
# MAGIC 2. Open the endpoint's **Monitoring** or **AI Gateway** area and select the linked inference
# MAGIC    table, if the UI shows a link.
# MAGIC 3. Alternatively, open **Catalog** → `workspace` → `default` → **Tables** and search for
# MAGIC    names beginning with `robotics_rag_inference`.
# MAGIC 4. Open the payload table to inspect request and response data, timestamps, endpoint metadata,
# MAGIC    and error fields. Do not expose raw prompts or responses outside the authorized workspace.
# MAGIC
# MAGIC The endpoint uses current AI Gateway inference tables. The table normally appears as
# MAGIC `workspace.default.robotics_rag_inference_payload`; wait briefly after the first request for
# MAGIC the service to deliver the logged payload.
