# Databricks notebook source
# MAGIC %md
# MAGIC # 05 — Building a robotics Knowledge Assistant
# MAGIC
# MAGIC This notebook continues after the previous robotics notebooks. It does not create
# MAGIC a Knowledge Assistant through code and does not modify any tables. Instead, it
# MAGIC verifies the source PDFs in the Unity Catalog Volume and provides the current UI
# MAGIC steps for creating and improving a grounded Knowledge Assistant.

# COMMAND ----------

# MAGIC %md
# MAGIC ## 0. Minimal configuration

# COMMAND ----------

from pyspark.sql import DataFrame
from pyspark.sql import functions as F

# Keep the course source path fixed so learners do not need to enter widgets.
source_documents_path = "/Volumes/workspace/default/robotics_files"

print(f"Knowledge Assistant source Volume: {source_documents_path}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Load the robotics source documents

# COMMAND ----------

def load_robotics_pdf_metadata(volume_path: str) -> DataFrame:
    """Load course PDFs as binary files and return only safe file metadata for inspection."""
    pdf_df = (
        spark.read.format("binaryFile")
        .load(volume_path)
        .filter(F.lower(F.col("path")).endswith(".pdf"))
    )

    if pdf_df.limit(1).count() == 0:
        raise FileNotFoundError(
            "No PDF files were found in the configured Volume. "
            "Upload the course PDFs and verify source_documents_path."
        )

    return pdf_df.select(
        "path",
        F.regexp_extract("path", r"([^/]+)$", 1).alias("file_name"),
        F.col("length").alias("file_size_bytes"),
        F.col("modificationTime").alias("modification_time"),
    )


robotics_pdf_metadata_df = load_robotics_pdf_metadata(source_documents_path)
print(f"Found {robotics_pdf_metadata_df.count()} PDF source document(s).")
display(robotics_pdf_metadata_df.orderBy("file_name"))

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Create a Knowledge Assistant in the UI
# MAGIC
# MAGIC 1. In the left navigation, click **Agents**.
# MAGIC 2. Click **Create agent**, then choose **Knowledge Assistant**.
# MAGIC 3. Enter the following agent values:
# MAGIC
# MAGIC    - **Name:** `robotics-course-specialist`
# MAGIC    - **Description:** `A helpful professional specialist that answers questions about the fictional robotics course samples.`
# MAGIC
# MAGIC 4. In the **Knowledge sources** panel, click **Add knowledge source** and select **Files in a Volume**.
# MAGIC 5. In **Source**, select `workspace` > `default` > `robotics_files`. If the UI accepts a path, use `/Volumes/workspace/default/robotics_files`.
# MAGIC 6. Enter these source values:
# MAGIC
# MAGIC    - **Name:** `robotics-course-pdfs`
# MAGIC    - **Content description:** `Ten fictional educational PDF course samples covering everyday robotics, sensing, motion, mobile robots, robot arms, collaborative robots, logistics, AI, safety, ethics, and future robotics. Use this source for questions about the course material.`
# MAGIC
# MAGIC 7. In **Instructions**, paste the following grounding prompt. It is adapted from notebook 04 for a Knowledge Assistant, which manages retrieval internally:
# MAGIC
# MAGIC    ```text
# MAGIC    You are a helpful and professional robotics specialist.
# MAGIC    Answer only with information supported by the available robotics course materials.
# MAGIC    If the materials do not contain the answer, say that you do not know based on the available materials.
# MAGIC    Do not invent facts, make assumptions, or use information outside the available context.
# MAGIC    ```
# MAGIC
# MAGIC 8. Click **Create agent**. Wait until the Volume source finishes synchronizing and the agent is ready. Source ingestion can take some time.
# MAGIC 9. In **Test your agent**, submit this prompt: `How do mobile robots avoid obstacles?`
# MAGIC 10. Open **View sources** in the response and confirm that the answer cites one or more robotics PDF files.
# MAGIC
# MAGIC If you later add or change files in the Volume, open the agent's source configuration and click **Sync** so the Knowledge Assistant ingests the changes.

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Improve the agent with Examples and Guidelines
# MAGIC
# MAGIC Use this section to demonstrate how expert feedback can guide an answer even when a question is outside the course PDFs.
# MAGIC
# MAGIC 1. Open the created Knowledge Assistant and select the **Examples** tab.
# MAGIC 2. Click **+ Add**.
# MAGIC 3. In the add-question dialog, enter: `How do I configure a Kratos robot?`
# MAGIC 4. Click **Add**, then select the newly added question in the Examples list.
# MAGIC 5. In the side panel, add the following items under **Guidelines**:
# MAGIC
# MAGIC    - `For this Kratos robot configuration question, explain that the user should download the Kratos Control mobile app.`
# MAGIC    - `Tell the user to sign in to the app, select Add Robot, and follow the in-app pairing instructions.`
# MAGIC    - `State clearly that this is a demonstration guideline and is not information found in the robotics course PDFs.`
# MAGIC
# MAGIC 6. Save the guidelines. They are applied to the Knowledge Assistant as feedback for this example.
# MAGIC 7. Return to **Test your agent** and submit the Kratos question again. Compare the result with the original grounded behavior and verify that it clearly labels the mobile-app procedure as a demonstration guideline rather than course content.
