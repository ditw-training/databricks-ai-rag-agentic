# Databricks notebook source
# MAGIC %md
# MAGIC # 06 — Building Unity Catalog functions for a single-agent app
# MAGIC
# MAGIC This notebook prepares a San Francisco Airbnb Delta table and creates Unity Catalog
# MAGIC functions that an AI agent can use as tools. Run the cells from top to bottom.

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Install Unity Catalog AI dependencies
# MAGIC
# MAGIC Run this cell once, then restart Python in the next cell. After the restart, continue
# MAGIC from section 2.

# COMMAND ----------

# MAGIC %pip install --upgrade "unitycatalog-ai[databricks]"

# COMMAND ----------

# Restart Python so the Unity Catalog AI package is available to the notebook.
dbutils.library.restartPython()

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Minimal configuration

# COMMAND ----------

# Define all Python objects after the restart because restartPython clears the interpreter state.
catalog = "workspace"
schema = "default"
airbnb_volume_path = "/Volumes/workspace/default/sf_airbnb_data"
airbnb_csv_path = f"{airbnb_volume_path}/sf_airbnb_listings.csv"
airbnb_table = f"{catalog}.{schema}.sf_airbnb_listings"
average_price_function = f"{catalog}.{schema}.get_average_listing_price"
listing_details_function = f"{catalog}.{schema}.get_listing_details"
python_formatting_function = f"{catalog}.{schema}.format_listing_for_agent"

print(f"Source CSV: {airbnb_csv_path}")
print(f"Delta table: {airbnb_table}")
print(f"Functions schema: {catalog}.{schema}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Load `sf_airbnb_listings` and create a Delta table
# MAGIC
# MAGIC ### Download and upload tutorial
# MAGIC
# MAGIC 1. A ready-to-upload CSV is included locally in `single_agent_app/data/sf_airbnb_listings.csv`.
# MAGIC 2. To download a newer source, open **https://insideairbnb.com/get-the-data/**, find **San Francisco**, and download **Detailed Listings data** (`listings.csv.gz`). The site updates files periodically, so the date can differ from this course sample.
# MAGIC 3. In Databricks, open **Catalog** > `workspace` > `default` > **Create** > **Volume**. Create a managed Volume named `sf_airbnb_data`.
# MAGIC 4. Open the Volume, choose **Upload to this volume**, and upload the provided `sf_airbnb_listings.csv`. Keep the exact file name.
# MAGIC 5. The next cell reads `/Volumes/workspace/default/sf_airbnb_data/sf_airbnb_listings.csv`, converts the `price` column to a numeric value, and creates the managed Delta table `workspace.default.sf_airbnb_listings`.
# MAGIC
# MAGIC The included CSV is a historical educational snapshot. It must not be interpreted as current availability or pricing information.

# COMMAND ----------

from pyspark.sql import functions as F

# Read the uploaded CSV with all fields initially treated as strings for controlled casting.
try:
    raw_listings_df = (
        spark.read.option("header", True)
        .option("multiLine", True)
        .option("quote", '"')
        .option("escape", '"')
        .option("mode", "PERMISSIVE")
        .csv(airbnb_csv_path)
    )
except Exception as csv_error:
    raise FileNotFoundError(
        f"Could not read '{airbnb_csv_path}'. Upload sf_airbnb_listings.csv to the sf_airbnb_data Volume first. "
        f"Original error: {type(csv_error).__name__}: {csv_error}"
    ) from csv_error

required_columns = {
    "id",
    "name",
    "host_name",
    "neighbourhood",
    "room_type",
    "price",
    "minimum_nights",
    "number_of_reviews",
    "availability_365",
}
missing_columns = sorted(required_columns.difference(raw_listings_df.columns))
if missing_columns:
    raise ValueError(
        "The uploaded CSV does not have the expected San Francisco Airbnb columns: "
        + ", ".join(missing_columns)
    )

# Parse numeric values with try_cast so that one malformed CSV record cannot stop table creation.
parsed_listings_df = raw_listings_df.select(
    F.expr("try_cast(id AS BIGINT)").alias("parsed_id"),
    F.expr("try_cast(regexp_replace(trim(price), '[$,]', '') AS DECIMAL(10,2))").alias("parsed_price"),
    F.expr("try_cast(minimum_nights AS INT)").alias("parsed_minimum_nights"),
    F.expr("try_cast(number_of_reviews AS INT)").alias("parsed_number_of_reviews"),
    F.expr("try_cast(availability_365 AS INT)").alias("parsed_availability_365"),
    F.expr("try_cast(latitude AS DOUBLE)").alias("parsed_latitude"),
    F.expr("try_cast(longitude AS DOUBLE)").alias("parsed_longitude"),
    "id",
    "name",
    "host_name",
    "neighbourhood",
    "room_type",
    "price",
)

# Inspect records that cannot be converted to a numeric price.
invalid_price_rows = parsed_listings_df.filter(
    F.col("price").isNotNull() & F.col("parsed_price").isNull()
).select("id", "name", "room_type", "price")
invalid_price_count = invalid_price_rows.count()

if invalid_price_count:
    print(f"[WARNING] Skipping {invalid_price_count} record(s) with an invalid price.")
    display(invalid_price_rows.limit(20))

# Keep a compact agent-friendly schema and exclude records without a usable listing ID or price.
listings_df = parsed_listings_df.select(
    F.col("parsed_id").alias("id"),
    F.trim(F.col("name")).alias("name"),
    F.trim(F.col("host_name")).alias("host_name"),
    F.trim(F.col("neighbourhood")).alias("neighbourhood"),
    F.trim(F.col("room_type")).alias("room_type"),
    F.col("parsed_price").alias("price"),
    F.col("parsed_minimum_nights").alias("minimum_nights"),
    F.col("parsed_number_of_reviews").alias("number_of_reviews"),
    F.col("parsed_availability_365").alias("availability_365"),
    F.col("parsed_latitude").alias("latitude"),
    F.col("parsed_longitude").alias("longitude"),
).filter(F.col("parsed_id").isNotNull() & F.col("parsed_price").isNotNull())

if listings_df.limit(1).count() == 0:
    raise ValueError("No valid listings were found after parsing the CSV.")

(
    listings_df.write.format("delta")
    .mode("overwrite")
    .option("overwriteSchema", "true")
    .saveAsTable(airbnb_table)
)

print(f"Created Delta table: {airbnb_table}")
display(spark.table(airbnb_table).orderBy("id").limit(10))

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Create the Databricks Function Client

# COMMAND ----------

from unitycatalog.ai.core.databricks import DatabricksFunctionClient

# Use serverless execution because AI tools execute UC functions through serverless generic compute.
client = DatabricksFunctionClient(execution_mode="serverless")
print("Databricks Function Client initialized for serverless execution.")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 5. Create SQL functions for Airbnb data
# MAGIC
# MAGIC The function and parameter comments are intentionally detailed. AI agents use these
# MAGIC comments to decide when to call a tool and which values to pass.

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE OR REPLACE FUNCTION workspace.default.get_average_listing_price()
# MAGIC RETURNS DOUBLE
# MAGIC COMMENT 'Returns the average nightly price in USD across all valid rows in the San Francisco Airbnb listings dataset. Use this function for questions about the overall average price, not for an individual listing.'
# MAGIC RETURN SELECT AVG(CAST(price AS DOUBLE))
# MAGIC FROM workspace.default.sf_airbnb_listings
# MAGIC WHERE price IS NOT NULL;

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE OR REPLACE FUNCTION workspace.default.get_listing_details(
# MAGIC   requested_listing_id BIGINT COMMENT 'The numeric Airbnb listing ID to retrieve. Use a listing ID supplied by the user or visible in the dataset.'
# MAGIC )
# MAGIC RETURNS STRING
# MAGIC COMMENT 'Returns an agent-readable profile for one San Francisco Airbnb listing, including name, host, neighbourhood, room type, nightly price, minimum nights, review count, and annual availability. Use this function when a user asks for details of a specific listing ID.'
# MAGIC RETURN SELECT CONCAT_WS(
# MAGIC   '\n',
# MAGIC   CONCAT('Listing ID: ', CAST(id AS STRING)),
# MAGIC   CONCAT('Name: ', COALESCE(name, 'Not provided')),
# MAGIC   CONCAT('Host: ', COALESCE(host_name, 'Not provided')),
# MAGIC   CONCAT('Neighbourhood: ', COALESCE(neighbourhood, 'Not provided')),
# MAGIC   CONCAT('Room type: ', COALESCE(room_type, 'Not provided')),
# MAGIC   CONCAT('Nightly price (USD): ', COALESCE(CAST(price AS STRING), 'Not provided')),
# MAGIC   CONCAT('Minimum nights: ', COALESCE(CAST(minimum_nights AS STRING), 'Not provided')),
# MAGIC   CONCAT('Number of reviews: ', COALESCE(CAST(number_of_reviews AS STRING), 'Not provided')),
# MAGIC   CONCAT('Availability in the next 365 days: ', COALESCE(CAST(availability_365 AS STRING), 'Not provided'))
# MAGIC )
# MAGIC FROM workspace.default.sf_airbnb_listings
# MAGIC WHERE id = requested_listing_id
# MAGIC LIMIT 1;

# COMMAND ----------

# MAGIC %md
# MAGIC ## 6. Call the average-price SQL function

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT workspace.default.get_average_listing_price() AS average_nightly_price_usd;

# COMMAND ----------

# MAGIC %md
# MAGIC ## 7. Create Python functions for listing retrieval and agent-ready formatting
# MAGIC
# MAGIC `get_listing_details_from_table` is a notebook helper that reads the Delta table by
# MAGIC listing ID. `format_listing_for_agent` is pure Python and can therefore be safely
# MAGIC registered as a Unity Catalog Python function in section 8. Registered Python UC
# MAGIC functions cannot use `spark.sql` or read Delta tables directly; the SQL function
# MAGIC `get_listing_details` is the registered lookup tool for agents.

# COMMAND ----------

def format_listing_for_agent(
    listing_id: int,
    name: str,
    host_name: str,
    neighbourhood: str,
    room_type: str,
    nightly_price_usd: float,
    minimum_nights: int,
    number_of_reviews: int,
    availability_365: int,
) -> str:
    """Format one Airbnb listing into concise, factual text for an AI agent.

    Args:
        listing_id: Numeric identifier of the Airbnb listing.
        name: Public listing name.
        host_name: Public host display name.
        neighbourhood: San Francisco neighbourhood of the listing.
        room_type: Accommodation category such as Entire home/apt or Private room.
        nightly_price_usd: Nightly price in US dollars.
        minimum_nights: Minimum number of nights allowed for a booking.
        number_of_reviews: Historical number of reviews for the listing.
        availability_365: Number of available days in the next 365 days in this dataset snapshot.

    Returns:
        A newline-separated listing summary suitable for use as AI-agent context.
    """
    return "\n".join(
        [
            f"Listing ID: {listing_id}",
            f"Name: {name}",
            f"Host: {host_name}",
            f"Neighbourhood: {neighbourhood}",
            f"Room type: {room_type}",
            f"Nightly price (USD): {nightly_price_usd:.2f}",
            f"Minimum nights: {minimum_nights}",
            f"Number of reviews: {number_of_reviews}",
            f"Availability in the next 365 days: {availability_365}",
        ]
    )


def get_listing_details_from_table(listing_id: int) -> str:
    """Fetch one listing by ID from the Delta table and return agent-ready formatted text."""
    rows = (
        spark.table(airbnb_table)
        .filter(F.col("id") == listing_id)
        .limit(1)
        .collect()
    )
    if not rows:
        return f"No listing was found for listing_id={listing_id}."

    listing = rows[0].asDict()
    return format_listing_for_agent(
        listing_id=int(listing["id"]),
        name=listing.get("name") or "Not provided",
        host_name=listing.get("host_name") or "Not provided",
        neighbourhood=listing.get("neighbourhood") or "Not provided",
        room_type=listing.get("room_type") or "Not provided",
        nightly_price_usd=float(listing.get("price") or 0.0),
        minimum_nights=int(listing.get("minimum_nights") or 0),
        number_of_reviews=int(listing.get("number_of_reviews") or 0),
        availability_365=int(listing.get("availability_365") or 0),
    )

# COMMAND ----------

# MAGIC %md
# MAGIC ## 8. Test the Python listing helper

# COMMAND ----------

sample_listing_id = spark.table(airbnb_table).select("id").orderBy("id").first()["id"]
print(f"Testing the listing helper with ID: {sample_listing_id}")
print(get_listing_details_from_table(int(sample_listing_id)))

# COMMAND ----------

# MAGIC %md
# MAGIC ## 9. Register and test the Python formatting function in Unity Catalog
# MAGIC
# MAGIC The registered function is deliberately self-contained: it receives listing fields and
# MAGIC formats them. The SQL function from section 4 remains the correct registered tool for
# MAGIC fetching a row from the Delta table by ID.

# COMMAND ----------

try:
    python_function_info = client.create_python_function(
        func=format_listing_for_agent,
        catalog=catalog,
        schema=schema,
        replace=True,
    )
    print(f"Registered Python UC function: {python_formatting_function}")
    print(python_function_info)
except Exception as registration_error:
    raise RuntimeError(
        "Could not register the Python Unity Catalog function. Confirm USE CATALOG, USE SCHEMA, "
        "CREATE FUNCTION, and compatible serverless Python UDF support. "
        f"Original error: {type(registration_error).__name__}: {registration_error}"
    ) from registration_error

# COMMAND ----------

sample_listing = spark.table(airbnb_table).orderBy("id").first().asDict()
try:
    formatting_result = client.execute_function(
        function_name=python_formatting_function,
        parameters={
            "listing_id": int(sample_listing["id"]),
            "name": sample_listing.get("name") or "Not provided",
            "host_name": sample_listing.get("host_name") or "Not provided",
            "neighbourhood": sample_listing.get("neighbourhood") or "Not provided",
            "room_type": sample_listing.get("room_type") or "Not provided",
            "nightly_price_usd": float(sample_listing.get("price") or 0.0),
            "minimum_nights": int(sample_listing.get("minimum_nights") or 0),
            "number_of_reviews": int(sample_listing.get("number_of_reviews") or 0),
            "availability_365": int(sample_listing.get("availability_365") or 0),
        },
    )
    print(formatting_result.value)
except Exception as execution_error:
    raise RuntimeError(
        "Could not execute the registered Python UC function. Confirm that serverless generic compute is enabled "
        "and that you have EXECUTE on the function. In Free Edition, 'Cannot access Spark Connect' indicates "
        "that this serverless capability is unavailable in the workspace. "
        f"Original error: {type(execution_error).__name__}: {execution_error}"
    ) from execution_error

# COMMAND ----------

# MAGIC %md
# MAGIC ## 10. Add the SQL functions to AI Playground as tools
# MAGIC
# MAGIC 1. In the left navigation, open **Playground**.
# MAGIC 2. Select a tools-capable model. In the current Free Edition course workspace, use **Inkling** if it is the available working model.
# MAGIC 3. Click **Tools** > **Add tool** > **Unity Catalog function**. If the UI calls this item **Function**, select that equivalent option.
# MAGIC 4. Add these two functions from catalog `workspace`, schema `default`:
# MAGIC    - `get_average_listing_price`
# MAGIC    - `get_listing_details`
# MAGIC 5. Submit this test prompt:
# MAGIC
# MAGIC    ```text
# MAGIC    Use the available functions to tell me the average nightly price in the San Francisco Airbnb dataset. Then retrieve and summarize listing ID 958. State only what the functions return.
# MAGIC    ```
# MAGIC
# MAGIC 6. Inspect the tool calls and verify that the model invoked both SQL functions. `get_listing_details` is the lookup tool because it can query the Delta table by ID. `format_listing_for_agent` is available in Catalog Explorer as a separately registered Python formatting tool.
