from __future__ import annotations

import json
import os

from pyspark.sql import functions as F


CATALOG = os.environ.get("HEALTHVERIFY_CATALOG", "dais2026")
SOURCE_TABLE = f"{CATALOG}.validation.integrated_facility_assessment"
LAKEBASE_URL = os.environ["LAKEBASE_JDBC_URL"]
LAKEBASE_USER = os.environ["LAKEBASE_USER"]
LAKEBASE_PASSWORD = os.environ["LAKEBASE_PASSWORD"]


def write_jdbc(df, table_name: str, mode: str = "append") -> None:
    (
        df.write.format("jdbc")
        .option("url", LAKEBASE_URL)
        .option("dbtable", table_name)
        .option("user", LAKEBASE_USER)
        .option("password", LAKEBASE_PASSWORD)
        .option("driver", "org.postgresql.Driver")
        .mode(mode)
        .save()
    )


def risk_category_expr():
    return (
        F.when(F.col("combined_quality_confidence_score") < 0.60, F.lit("HIGH"))
        .when(F.col("combined_quality_confidence_score") < 0.75, F.lit("MEDIUM"))
        .otherwise(F.lit("LOW"))
    )


source = spark.table(SOURCE_TABLE)

facilities = source.select(
    F.col("unique_id"),
    F.col("facility_name"),
    F.col("state"),
    F.col("city"),
    F.lit(None).cast("string").alias("address_line1"),
    F.lit(None).cast("string").alias("address_line2"),
    F.lit(None).cast("string").alias("address_line3"),
    F.col("pincode").alias("zip_code"),
    F.col("latitude"),
    F.col("longitude"),
    F.coalesce(F.col("officialPhone"), F.col("phone_numbers")).alias("phone_number"),
    F.col("email"),
    F.col("officialWebsite").alias("website"),
    F.array().cast("array<string>").alias("social_media_links"),
    F.split(F.regexp_replace(F.regexp_replace(F.col("specialties"), r'[\[\]"]', ""), r",\s*", ","), ",").alias("specialties"),
    F.split(F.regexp_replace(F.regexp_replace(F.col("capability"), r'[\[\]"]', ""), r",\s*", ","), ",").alias("capabilities"),
    F.array().cast("array<string>").alias("equipment"),
    F.array().cast("array<string>").alias("procedures"),
    F.lit(None).cast("int").alias("bed_capacity"),
    F.lit(None).cast("int").alias("icu_capacity"),
    F.lit(None).cast("int").alias("doctor_count"),
    F.round(F.col("combined_quality_confidence_score"), 3).alias("trust_score"),
    F.col("data_quality_status").alias("plausibility_status"),
    F.when(F.array_contains(F.col("red_flags"), "STALE"), F.lit("STALE"))
    .when(F.array_contains(F.col("red_flags"), "NO_DATE"), F.lit("NO_DATE"))
    .otherwise(F.lit("FRESH"))
    .alias("freshness_status"),
    F.lit(None).cast("timestamp").alias("last_verified_date"),
    F.lit(0).alias("verification_count"),
    F.lit(0).alias("total_claims_checked"),
    F.lit(0).alias("total_claims_verified"),
    F.lit("unity_catalog_sync").alias("data_source"),
)

queue = source.where(F.col("combined_quality_confidence_score") < 0.75).select(
    F.concat(F.lit("q_"), F.col("unique_id")).alias("queue_id"),
    F.col("unique_id").alias("facility_id"),
    F.col("facility_name"),
    F.col("city"),
    F.col("state"),
    F.coalesce(F.col("officialPhone"), F.col("phone_numbers")).alias("phone_number"),
    (
        F.when(F.col("combined_quality_confidence_score") < 0.50, F.lit(95))
        .when(F.col("combined_quality_confidence_score") < 0.60, F.lit(85))
        .when(F.col("combined_quality_confidence_score") < 0.75, F.lit(75))
        .otherwise(F.lit(50))
    ).alias("priority_score"),
    risk_category_expr().alias("risk_category"),
    F.col("red_flags").alias("risk_factors"),
    F.to_json(
        F.array(
            F.struct(F.lit("basic").alias("section"), F.lit("Is this facility currently operational?").alias("prompt")),
            F.struct(F.lit("basic").alias("section"), F.lit("Can you confirm this phone number is correct?").alias("prompt")),
            F.struct(F.lit("progressive").alias("section"), F.lit("Can you confirm the top claimed specialties are available?").alias("prompt")),
        )
    ).alias("verification_script"),
    F.lit(1).alias("script_version"),
    F.current_timestamp().alias("script_generated_at"),
    F.lit("PENDING").alias("status"),
)

write_jdbc(facilities, "facilities_verified", mode="overwrite")
write_jdbc(queue, "verification_queue", mode="overwrite")

print(f"Synced {facilities.count()} facilities and {queue.count()} queue entries from {SOURCE_TABLE}.")
