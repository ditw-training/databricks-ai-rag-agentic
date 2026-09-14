# Databricks notebook source
# MAGIC %md
# MAGIC # 02 — Chunking parsed robotics documents
# MAGIC
# MAGIC This notebook continues after `01_parse_robotics_documents`. It reads the
# MAGIC persisted Python parsing output from Delta, creates two text representations,
# MAGIC chunks the plain-text representation, and writes chunks to Delta.

# COMMAND ----------

# MAGIC %md
# MAGIC ## 0. Minimal configuration

# COMMAND ----------

import html
import json
import re

from pyspark.sql import functions as F
from pyspark.sql.types import ArrayType, StringType

# Keep table names fixed to match the output of notebook 01 in the workspace catalog.
parsed_delta_table = "workspace.default.robotics_parsed_documents"
chunked_delta_table = "workspace.default.robotics_document_chunks"

print(f"Source parsed table: {parsed_delta_table}")
print(f"Output chunked table: {chunked_delta_table}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Load previously parsed data as JSON

# COMMAND ----------

# Convert the persisted VARIANT parsing result to JSON text for downstream Python and LLM processing.
parsed_json_df = (
    spark.table(parsed_delta_table)
    .select("path", "length", F.to_json(F.col("parsed")).alias("parsed_json"))
)

if parsed_json_df.limit(1).count() == 0:
    raise ValueError("The source Delta table is empty. Run notebook 01 and its Delta save cell first.")

display(parsed_json_df)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Clean parsed JSON into readable Markdown with an LLM

# COMMAND ----------

prompt_prefix = """You are a helpful assistant. Given a JSON object representing a parsed document, convert the data into clean, readable Markdown.
Use exactly `== page ==` to separate pages.
Preserve useful headings, tables, captions, and all necessary document structure.
Return only the Markdown content: do not return JSON and do not include code fences.

JSON:
"""

# Escape the fixed prompt once so it can be safely embedded in the ai_query SQL expression.
escaped_prompt_prefix = prompt_prefix.replace("'", "''")

# Send the full parsed JSON to the requested Databricks-hosted model and request plain text output.
markdown_df = parsed_json_df.withColumn(
    "clean_markdown",
    F.expr(
        f"""ai_query(
            'databricks-gpt-oss-20b',
            concat('{escaped_prompt_prefix}', parsed_json),
            responseFormat => '{{"type":"text"}}'
        )"""
    ),
)
display(markdown_df.select("path", "clean_markdown"))

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Convert parsed JSON to one plain-text string

# COMMAND ----------

def html_to_plain_text(value: str) -> str:
    """Remove simple HTML markup from table content while retaining readable spacing."""
    with_line_breaks = re.sub(r"</(p|div|tr|li|h[1-6])>", "\n", value, flags=re.IGNORECASE)
    without_tags = re.sub(r"<[^>]+>", " ", with_line_breaks)
    return re.sub(r"[ \t]+", " ", html.unescape(without_tags)).strip()


def parsed_json_to_plain_text(parsed_json: str) -> str:
    """Flatten parsed elements into page-delimited text without retaining element semantics."""
    parsed_document = json.loads(parsed_json)
    document = parsed_document.get("document") or {}
    pages = document.get("pages") or []
    elements = document.get("elements") or []
    elements_by_page = {int(page.get("id", index)): [] for index, page in enumerate(pages)}

    for element in sorted(elements, key=lambda item: item.get("id", 0)):
        content = element.get("content")
        if not content:
            continue
        clean_content = html_to_plain_text(str(content))
        if not clean_content:
            continue
        bounding_boxes = element.get("bbox") or []
        page_id = int(bounding_boxes[0].get("page_id", 0)) if bounding_boxes else 0
        elements_by_page.setdefault(page_id, []).append(clean_content)

    ordered_page_ids = [int(page.get("id", index)) for index, page in enumerate(pages)] or sorted(elements_by_page)
    page_texts = ["\n".join(elements_by_page.get(page_id, [])) for page_id in ordered_page_ids]
    return "\n== page ==\n".join(page_texts)


# Apply the semantic-free conversion to every JSON row and retain only ordinary text plus page separators.
parsed_json_to_plain_text_udf = F.udf(parsed_json_to_plain_text, StringType())
plain_text_df = parsed_json_df.withColumn("plain_text", parsed_json_to_plain_text_udf(F.col("parsed_json")))
display(plain_text_df.select("path", "plain_text"))

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Chunk plain text with RecursiveCharacterTextSplitter

# COMMAND ----------

try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
except ImportError as import_error:
    raise ImportError(
        "Install the required package in a separate notebook cell with: %pip install langchain-text-splitters; then restart Python and rerun this notebook from section 0."
    ) from import_error

# Keep page separators in the output and use the requested chunk size and overlap.
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=2000,
    chunk_overlap=200,
    separators=["\n== page ==\n", "== page ==", "\n\n", "\n", " ", ""],
    keep_separator=True,
)


def split_plain_text(plain_text: str) -> list[str]:
    """Split one page-delimited text string into ordered overlapping LangChain chunks."""
    return text_splitter.split_text(plain_text or "")


# Use posexplode to preserve a zero-based chunk position for every source document.
split_plain_text_udf = F.udf(split_plain_text, ArrayType(StringType()))
chunked_df = (
    plain_text_df
    .select("path", F.posexplode(split_plain_text_udf(F.col("plain_text"))).alias("chunk_position", "chunk_text"))
    .withColumn("chunk_id", F.sha2(F.concat_ws("||", F.col("path"), F.col("chunk_position"), F.col("chunk_text")), 256))
    .select("chunk_id", "path", "chunk_position", "chunk_text")
)
display(chunked_df.orderBy("path", "chunk_position"))

# COMMAND ----------

# MAGIC %md
# MAGIC ## 5. Save chunks to a Delta table

# COMMAND ----------

# Overwrite only the configured output table so reruns leave the source parsing table unchanged.
chunked_df.write.format("delta").mode("overwrite").option("overwriteSchema", "true").saveAsTable(chunked_delta_table)
display(spark.table(chunked_delta_table).orderBy("path", "chunk_position"))
