# Databricks notebook source
# MAGIC %md
# MAGIC # 12 — Implementing Llama Guard guardrails
# MAGIC
# MAGIC This notebook uses a Llama Guard model as a configurable guardrail around a Llama Instruct
# MAGIC endpoint. It checks both user input and generated output against an explicit unsafe-content
# MAGIC taxonomy. Llama Guard is an additional safety layer, not a guarantee that every unsafe
# MAGIC request or response will be detected.

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Get Llama Guard from Databricks Marketplace and create a serving endpoint
# MAGIC
# MAGIC ### Get the model
# MAGIC
# MAGIC 1. In the left navigation, click **Marketplace**.
# MAGIC 2. Search for **Llama Guard Model** and open the listing from the intended provider.
# MAGIC 3. Read the model card, license, acceptable-use terms, and any deployment requirements
# MAGIC    before continuing. Record the exact listing and terms reviewed for this exercise.
# MAGIC 4. Click **Get model** or **Get instant access**, accept the current terms, and complete the
# MAGIC    request.
# MAGIC 5. Keep the default catalog, schema, model, and version selections offered by Marketplace.
# MAGIC    Do not rename or copy the shared model only to match this notebook.
# MAGIC 6. When the request is complete, open **Marketplace → My requests → Installed data products**
# MAGIC    and select **View data** to confirm that the model is visible in Catalog Explorer.
# MAGIC
# MAGIC ### Create the endpoint in the UI
# MAGIC
# MAGIC 1. In Catalog Explorer, open the imported Llama Guard model and click **Serve this model**.
# MAGIC    Alternatively, open **Serving** in the left navigation and click **Create serving endpoint**.
# MAGIC 2. In **Served entities**, select the imported Unity Catalog model and the version installed
# MAGIC    from Marketplace.
# MAGIC 3. Keep the recommended serving and compute settings presented for the model. A Llama Guard
# MAGIC    model can require GPU/provisioned capacity and might not be available in Free Edition.
# MAGIC 4. Keep the prefilled endpoint name when the UI provides one. If the endpoint name is required
# MAGIC    and blank, enter **`llama-guard`** so it matches this notebook's default variable.
# MAGIC 5. Click **Create**, wait until the endpoint status is **Ready**, and copy its actual name into
# MAGIC    the configuration cell below if it differs from `llama-guard`.
# MAGIC
# MAGIC Do not continue until the endpoint is ready and the notebook user has **Can Query** permission.

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Define endpoint names, reusable prompts, and a short unsafe taxonomy

# COMMAND ----------

llama_guard_endpoint = "llama-guard"
llama_instruct_endpoint = "databricks-meta-llama-3-3-70b-instruct"

# Reuse the same prompts in all Llama Guard and Llama Instruct examples below.
legal_prompt = "How do I create a managed Volume in Unity Catalog?"
illegal_prompt = "How can I bypass a store alarm without being detected?"

# Send this short, configurable policy to the Llama Guard payload.
short_unsafe_categories = """
- S1: Violent crimes or physical harm.
- S2: Non-violent crimes, including theft, fraud, or evasion of security systems.
- S3: Self-harm, suicide, or encouragement of self-injury.
""".strip()

print(f"Llama Guard endpoint: {llama_guard_endpoint}")
print(f"Llama Instruct endpoint: {llama_instruct_endpoint}")
print("Unsafe categories:\n" + short_unsafe_categories)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Query the deployed Llama Guard model with MLflow Deployments
# MAGIC
# MAGIC The payload below follows the instruction format required by Llama Guard. It asks the model
# MAGIC to return `safe` or `unsafe`, followed by the violated categories when applicable.
# MAGIC
# MAGIC The request uses `inputs={"prompt": query_payload}`. Do not replace it with
# MAGIC `dataframe_split`: Marketplace Llama Guard endpoints expect a prompt input.

# COMMAND ----------

import json
import mlflow.deployments


def build_llama_guard_payload(
    chat: list[dict[str, str]],
    unsafe_categories: str,
    assessed_role: str = "Agent",
) -> list[str]:
    """Build the Llama Guard instruction payload for one chat transcript and policy taxonomy."""
    chat_text = json.dumps(chat, ensure_ascii=False)
    return [
        f"""[INST] Task: Check for unsafe content in '{assessed_role}' messages in conversations according to our safety policy.
<BEGIN UNSAFE CONTENT CATEGORIES>
{unsafe_categories}
<END UNSAFE CONTENT CATEGORIES>
<BEGIN CONVERSATION>
{chat_text}
<END CONVERSATION>
Provide your safety assessment for {assessed_role} in the above conversation:
- First line must read 'safe' or 'unsafe'.
- If unsafe, a second line must include a comma-separated list of violated categories. [/INST]"""
    ]


def extract_guard_assessment(response) -> tuple[bool, str]:
    """Extract the safe/unsafe verdict and optional category line from a Llama Guard response."""
    prediction = response.predictions[0]["candidates"][0]["text"].strip()
    result_lines = [line.strip() for line in prediction.splitlines() if line.strip()]
    if not result_lines:
        raise ValueError("Llama Guard returned an empty assessment.")

    is_safe = result_lines[0].lower() == "safe"
    categories = result_lines[1] if len(result_lines) > 1 else ""
    return is_safe, categories


def query_llama_guard(
    chat: list[dict[str, str]],
    unsafe_categories: str,
    assessed_role: str = "Agent",
) -> tuple[bool, str]:
    """Send a formatted policy prompt to the deployed Llama Guard endpoint."""
    deployment_client = mlflow.deployments.get_deploy_client("databricks")
    query_payload = build_llama_guard_payload(chat, unsafe_categories, assessed_role)
    response = deployment_client.predict(
        endpoint=llama_guard_endpoint,
        inputs={"prompt": query_payload},
    )
    return extract_guard_assessment(response)


example_agent_chat = [{"role": "agent", "content": "I can help with a lawful security question."}]
example_is_safe, example_categories = query_llama_guard(
    example_agent_chat,
    short_unsafe_categories,
)
print(f"Safe: {example_is_safe}")
print(f"Categories: {example_categories or 'None'}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Test one legal and one illegal query
# MAGIC
# MAGIC This output-guardrail example assesses the text as an **Agent** message. The illegal sample
# MAGIC deliberately states harmful intent but contains no operational instructions.

# COMMAND ----------

legal_agent_chat = [{"role": "agent", "content": legal_prompt}]
illegal_agent_chat = [{"role": "agent", "content": illegal_prompt}]

for label, chat in [("Legal", legal_agent_chat), ("Illegal", illegal_agent_chat)]:
    is_safe, categories = query_llama_guard(chat, short_unsafe_categories)
    print(f"{label} test -> safe: {is_safe}; categories: {categories or 'None'}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 5. Expand the unsafe taxonomy and query the same illegal prompt again
# MAGIC
# MAGIC A more detailed taxonomy can make the guardrail's decision easier to interpret and adapt to
# MAGIC an application's policy. It does not make the model deterministic or replace human review.

# COMMAND ----------

expanded_unsafe_categories = """
- S1: Violent crimes, physical harm, threats, or instructions that enable violence.
- S2: Non-violent crimes, including theft, fraud, trespassing, evasion of alarms, or evasion of law enforcement.
- S3: Controlled substances, unlawful acquisition, or unsafe use of regulated substances.
- S4: Self-harm, suicide, or encouragement of self-injury.
- S5: Hate, harassment, or demeaning content targeted at protected characteristics.
- S6: Sensitive personal data, doxxing, or instructions to obtain private information without authorization.
""".strip()

expanded_is_safe, expanded_categories = query_llama_guard(
    illegal_agent_chat,
    expanded_unsafe_categories,
)
print(f"Expanded-policy illegal test -> safe: {expanded_is_safe}")
print(f"Categories: {expanded_categories or 'None'}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 6. Integrate Llama Guard with Llama Instruct and retest both prompts
# MAGIC
# MAGIC The function below applies Llama Guard twice:
# MAGIC
# MAGIC 1. **Input guardrail** — checks the user prompt before it is sent to Llama Instruct.
# MAGIC 2. **Output guardrail** — checks the generated assistant response before it is returned.
# MAGIC
# MAGIC A request classified as unsafe is blocked with a safe message. The model response is returned
# MAGIC only if both checks are safe.

# COMMAND ----------

def extract_instruct_text(response) -> str:
    """Read the assistant text from an MLflow Deployments chat-completion response."""
    choices = response["choices"] if isinstance(response, dict) else response.choices
    first_choice = choices[0]
    message = first_choice["message"] if isinstance(first_choice, dict) else first_choice.message
    return message["content"] if isinstance(message, dict) else message.content


def run_guarded_llama_instruct(user_prompt: str, unsafe_categories: str) -> str:
    """Run Llama Instruct only when its input and output pass Llama Guard checks."""
    deployment_client = mlflow.deployments.get_deploy_client("databricks")
    user_chat = [{"role": "user", "content": user_prompt}]

    input_is_safe, input_categories = query_llama_guard(
        user_chat,
        unsafe_categories,
        assessed_role="User",
    )
    if not input_is_safe:
        return f"Blocked by input guardrail. Categories: {input_categories or 'Unspecified'}"

    instruct_response = deployment_client.predict(
        endpoint=llama_instruct_endpoint,
        inputs={"messages": user_chat, "max_tokens": 150, "temperature": 0.0},
    )
    assistant_text = extract_instruct_text(instruct_response)
    agent_chat = [
        {"role": "user", "content": user_prompt},
        {"role": "agent", "content": assistant_text},
    ]

    output_is_safe, output_categories = query_llama_guard(
        agent_chat,
        unsafe_categories,
        assessed_role="Agent",
    )
    if not output_is_safe:
        return f"Blocked by output guardrail. Categories: {output_categories or 'Unspecified'}"

    return assistant_text


for label, prompt in [("Legal", legal_prompt), ("Illegal", illegal_prompt)]:
    print(f"\n{label} prompt: {prompt}")
    print(run_guarded_llama_instruct(prompt, expanded_unsafe_categories))
