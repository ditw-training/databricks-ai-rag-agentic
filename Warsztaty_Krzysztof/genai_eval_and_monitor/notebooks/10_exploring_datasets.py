# Databricks notebook source
# MAGIC %md
# MAGIC # 10 — Exploring Marketplace datasets
# MAGIC
# MAGIC This notebook starts the `genai_eval_and_monitor` module, inspired by the course
# MAGIC **Generative AI Application Evaluation and Governance**.
# MAGIC
# MAGIC Its purpose is to discover, review, and import two Databricks Marketplace datasets:
# MAGIC
# MAGIC 1. **Amazon Products** from **Bright Data**.
# MAGIC 2. **Personal Income** from **Rearc**.
# MAGIC
# MAGIC Marketplace imports are completed in the Databricks UI because the consumer must review
# MAGIC the listing and explicitly accept the provider's current terms. This notebook then verifies
# MAGIC that each read-only shared catalog is available and displays its schemas and tables.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Before you begin
# MAGIC
# MAGIC Use a Unity Catalog-enabled workspace. To request a Marketplace data product, you need the
# MAGIC `USE MARKETPLACE ASSETS` privilege. Depending on the Marketplace configuration, installing
# MAGIC and managing a shared catalog can also require `CREATE CATALOG`, `USE PROVIDER`, or a
# MAGIC Marketplace/metastore administrator to complete the request.
# MAGIC
# MAGIC Do not replace the Marketplace workflow with a locally downloaded copy of either dataset:
# MAGIC this exercise is specifically about discovering governed data products and their licenses.

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Find, review, and import Amazon Products from Bright Data
# MAGIC
# MAGIC Follow these UI steps:
# MAGIC
# MAGIC 1. In the left navigation, click **Marketplace**.
# MAGIC 2. In the search box, enter **Amazon Products**.
# MAGIC 3. Use the provider filter or inspect the listing and select the dataset published by
# MAGIC    **Bright Data**. Do not select a similarly named product from a different provider.
# MAGIC 4. Open the listing details. Review the dataset description, sample/schema, refresh
# MAGIC    information, provider identity, and the complete **Terms**, **License**, or
# MAGIC    **Terms and conditions** section.
# MAGIC 5. Before requesting access, record the following from the live listing:
# MAGIC    - the exact listing title and provider name;
# MAGIC    - the license or terms URL/name and the date reviewed;
# MAGIC    - permitted use, commercial-use restrictions, redistribution restrictions, retention
# MAGIC      requirements, and any personal-data or compliance obligations;
# MAGIC    - whether the product is free, instantly available, approval-based, or paid.
# MAGIC 6. If the terms are acceptable, click **Get data** or **Get instant access**. Read the
# MAGIC    confirmation dialog, accept the current provider terms, and continue.
# MAGIC 7. Keep the Marketplace default catalog name. In this workspace, the installed shared
# MAGIC    catalog is **`bright_data_amazon_dataset`**. Marketplace creates it as a read-only
# MAGIC    shared catalog; do not try to create or overwrite it manually.
# MAGIC 8. Wait for the request to complete. If provider approval is required, monitor it in
# MAGIC    **Marketplace → My requests**. When the product is installed, use **View data** to
# MAGIC    confirm the catalog name and available tables.
# MAGIC
# MAGIC The exact license is controlled by the live provider listing and can change. This notebook
# MAGIC intentionally does not claim a license type or usage right that has not been reviewed in
# MAGIC your workspace.

# COMMAND ----------

# MAGIC %md
# MAGIC ### License review record — Bright Data
# MAGIC
# MAGIC Fill this record in a Markdown cell, a course note, or your project documentation before
# MAGIC using the data in an evaluation workflow:
# MAGIC
# MAGIC | Field | Record from the Marketplace listing |
# MAGIC | --- | --- |
# MAGIC | Exact product title | |
# MAGIC | Provider | Bright Data |
# MAGIC | Listing URL or identifier | |
# MAGIC | License / terms name or URL | |
# MAGIC | Review date | |
# MAGIC | Allowed purpose | |
# MAGIC | Commercial-use condition | |
# MAGIC | Redistribution / sharing condition | |
# MAGIC | Retention, deletion, or refresh condition | |
# MAGIC | Personal-data / compliance notes | |

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Find, review, and import Personal Income from Rearc
# MAGIC
# MAGIC Follow these UI steps:
# MAGIC
# MAGIC 1. Return to **Marketplace** in the left navigation.
# MAGIC 2. Search for **Personal Income**.
# MAGIC 3. Use the provider filter or inspect the listing and select the dataset published by
# MAGIC    **Rearc**. Confirm both the product title and provider before continuing.
# MAGIC 4. Open the listing details. Review the dataset description, available tables/schema,
# MAGIC    refresh information, provider identity, and the complete **Terms**, **License**, or
# MAGIC    **Terms and conditions** section.
# MAGIC 5. Before requesting access, record the current license and the same practical conditions
# MAGIC    listed in the Bright Data review record below. Do not infer that the Rearc terms match
# MAGIC    the Bright Data terms.
# MAGIC 6. If the terms are acceptable, click **Get data** or **Get instant access**, review the
# MAGIC    confirmation dialog, accept the provider terms, and continue.
# MAGIC 7. Keep the Marketplace default catalog name. In this workspace, the installed shared
# MAGIC    catalog is **`rearc_personal_income_fred`**. It is a read-only shared catalog.
# MAGIC 8. If the request is not immediately fulfilled, open **Marketplace → My requests** and
# MAGIC    wait for the provider status to become installed. Use **View data** to verify the catalog
# MAGIC    and its tables.

# COMMAND ----------

# MAGIC %md
# MAGIC ### License review record — Rearc
# MAGIC
# MAGIC Fill this record before using the dataset in prompts, evaluation sets, dashboards, or model
# MAGIC monitoring experiments:
# MAGIC
# MAGIC | Field | Record from the Marketplace listing |
# MAGIC | --- | --- |
# MAGIC | Exact product title | |
# MAGIC | Provider | Rearc |
# MAGIC | Listing URL or identifier | |
# MAGIC | License / terms name or URL | |
# MAGIC | Review date | |
# MAGIC | Allowed purpose | |
# MAGIC | Commercial-use condition | |
# MAGIC | Redistribution / sharing condition | |
# MAGIC | Retention, deletion, or refresh condition | |
# MAGIC | Personal-data / compliance notes | |

# COMMAND ----------

# MAGIC %md
# MAGIC ## Next step
# MAGIC
# MAGIC After both imports succeed, use the displayed schema and table names in later notebooks.
# MAGIC Do not copy Marketplace data into a managed table unless the reviewed provider terms allow
# MAGIC that use. Keep the Marketplace catalog read-only and document the reviewed terms alongside
# MAGIC any derived evaluation dataset.
