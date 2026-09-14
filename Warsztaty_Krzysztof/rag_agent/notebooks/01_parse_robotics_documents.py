# Databricks notebook source
# MAGIC %md
# MAGIC # Parse the robotics PDF course samples
# MAGIC
# MAGIC Run the cells from top to bottom. This notebook parses the same PDF corpus once
# MAGIC through the Python API and once through SQL, then displays metadata and an
# MAGIC interactive visual inspection of one parsed result.

# COMMAND ----------

# MAGIC %md
# MAGIC ## 0. Configuration

# COMMAND ----------

import json

# Keep all course paths fixed so learners can run the notebook without widget setup.
source_documents_path = "/Volumes/workspace/default/robotics_files"
python_rendered_pages_path = "/Volumes/workspace/default/robotics_files/parsed_pages/python"
sql_rendered_pages_path = "/Volumes/workspace/default/robotics_files/parsed_pages/sql"
parsed_delta_table = "workspace.default.robotics_parsed_documents"

print(f"Source PDFs: {source_documents_path}")
print(f"Python page renders: {python_rendered_pages_path}")
print(f"SQL page renders: {sql_rendered_pages_path}")
print(f"Delta table: {parsed_delta_table}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Renderer helper

# COMMAND ----------

# MAGIC %run ./includes/document_renderer

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Parse documents with Python

# COMMAND ----------

from pyspark.sql import functions as F

# Read the PDFs as binary rows because ai_parse_document expects a binary content column.
source_pdf_df = (
    spark.read.format("binaryFile")
    .load(source_documents_path)
    .filter(F.lower(F.col("path")).endswith(".pdf"))
)

if source_pdf_df.limit(1).count() == 0:
    raise FileNotFoundError("No PDF files were found. Upload the generated documents and verify source_documents_path.")

# Parse every binary PDF through the PySpark ai_parse_document API and retain a reusable temp view.
parsed_python_df = (
    source_pdf_df
    .withColumn(
        "parsed",
        F.ai_parse_document(
            col=F.col("content"),
            options={
                "version": "2.0",
                "imageOutputPath": python_rendered_pages_path,
                "descriptionElementTypes": "*",
            },
        ),
    )
    .drop("content")
)
parsed_python_df.createOrReplaceTempView("parsed_python_docs")
display(parsed_python_df.select("path", "length", "parsed"))

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Parse documents with SQL

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Parse the same source files with the SQL AI function and retain a separate temp view.
# MAGIC CREATE OR REPLACE TEMP VIEW parsed_sql_docs AS
# MAGIC SELECT
# MAGIC   path,
# MAGIC   length,
# MAGIC   ai_parse_document(
# MAGIC     content,
# MAGIC     map(
# MAGIC       'version', '2.0',
# MAGIC       'imageOutputPath', '/Volumes/workspace/default/robotics_files/parsed_pages/sql',
# MAGIC       'descriptionElementTypes', '*'
# MAGIC     )
# MAGIC   ) AS parsed
# MAGIC FROM read_files(
# MAGIC   '/Volumes/workspace/default/robotics_files',
# MAGIC   format => 'binaryFile',
# MAGIC   fileNamePattern => '*.pdf'
# MAGIC );
# MAGIC
# MAGIC SELECT path, length, parsed FROM parsed_sql_docs;

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Save parsed output to a Delta table

# COMMAND ----------

# Select only the Python parsing result for persistence in the Delta table.
parsed_delta_df = parsed_python_df.select("path", "length", "parsed")

# Overwrite the course-sample table so rerunning the notebook creates a fresh, reproducible Delta result.
parsed_delta_df.write.format("delta").mode("overwrite").option("overwriteSchema", "true").saveAsTable(parsed_delta_table)
display(spark.table(parsed_delta_table).select("path", "length", "parsed"))

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Display parsed-document metadata

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Count page and element arrays independently so the two counts cannot multiply each other.
# MAGIC WITH parsed_documents AS (
# MAGIC   SELECT 'Python' AS parser, path, parsed FROM parsed_python_docs
# MAGIC   UNION ALL
# MAGIC   SELECT 'SQL' AS parser, path, parsed FROM parsed_sql_docs
# MAGIC ),
# MAGIC page_counts AS (
# MAGIC   SELECT parser, path, COUNT(*) AS page_count
# MAGIC   FROM parsed_documents, LATERAL variant_explode(parsed:document:pages)
# MAGIC   GROUP BY parser, path
# MAGIC ),
# MAGIC element_counts AS (
# MAGIC   SELECT parser, path, COUNT(*) AS element_count
# MAGIC   FROM parsed_documents, LATERAL variant_explode(parsed:document:elements)
# MAGIC   GROUP BY parser, path
# MAGIC )
# MAGIC SELECT
# MAGIC   parsed_documents.parser,
# MAGIC   parsed_documents.path,
# MAGIC   COALESCE(page_counts.page_count, 0) AS page_count,
# MAGIC   COALESCE(element_counts.element_count, 0) AS element_count,
# MAGIC   parsed_documents.parsed:metadata AS metadata,
# MAGIC   parsed_documents.parsed:error_status AS error_status
# MAGIC FROM parsed_documents
# MAGIC LEFT JOIN page_counts USING (parser, path)
# MAGIC LEFT JOIN element_counts USING (parser, path)
# MAGIC ORDER BY parser, path;

# COMMAND ----------

# MAGIC %md
# MAGIC ## 5. Visualize one Python-parsed document

# COMMAND ----------

# Select one VARIANT result as JSON because VARIANT values cannot be collected directly into Python objects.
sample_row = spark.sql("""
    SELECT path, to_json(parsed) AS parsed_json
    FROM parsed_python_docs
    ORDER BY path
    LIMIT 1
""").first()

if sample_row is None:
    raise RuntimeError("No Python parsing result is available. Run the Python parsing cell first.")

# Convert the JSON string to a Python dictionary and render every saved source page with bbox overlays.
sample_document = json.loads(sample_row["parsed_json"])
print(f"Rendering: {sample_row['path']}")
render_ai_parse_output(sample_document, page_selection="all")
