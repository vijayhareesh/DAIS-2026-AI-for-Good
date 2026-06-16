-- HealthVerify India facility validation framework.
-- Source catalog: dais2026.raw
-- Output layers: bronze, silver, validation.
-- Lakeflow pipeline source files only allow DLT statements; schema creation is
-- handled outside this file by Unity Catalog/bundle setup.

-- ============================================================================
-- BRONZE LAYER
-- ============================================================================

CREATE OR REFRESH MATERIALIZED VIEW bronze.facilities_clean (
  CONSTRAINT unique_id_not_null EXPECT (unique_id IS NOT NULL) ON VIOLATION FAIL UPDATE,
  CONSTRAINT state_not_null EXPECT (address_stateOrRegion IS NOT NULL) ON VIOLATION DROP ROW,
  CONSTRAINT valid_latitude EXPECT (latitude IS NULL OR latitude BETWEEN -90 AND 90) ON VIOLATION DROP ROW,
  CONSTRAINT valid_longitude EXPECT (longitude IS NULL OR longitude BETWEEN -180 AND 180) ON VIOLATION DROP ROW
)
COMMENT "Bronze: validated facilities with numeric casts and geographic constraints"
CLUSTER BY (address_stateOrRegion, address_city)
AS
SELECT
  unique_id,
  source_types,
  source_ids,
  source_content_id,
  name,
  organization_type,
  content_table_id,
  phone_numbers,
  officialPhone,
  email,
  websites,
  officialWebsite,
  TRY_CAST(yearEstablished AS INT) AS yearEstablished,
  acceptsVolunteers,
  facebookLink,
  address_line1,
  address_line2,
  address_line3,
  address_city,
  address_stateOrRegion,
  address_zipOrPostcode,
  address_country,
  address_countryCode,
  countries,
  facilityTypeId,
  operatorTypeId,
  affiliationTypeIds,
  description,
  area,
  TRY_CAST(numberDoctors AS INT) AS numberDoctors,
  TRY_CAST(capacity AS INT) AS capacity,
  specialties,
  procedure,
  equipment,
  capability,
  recency_of_page_update,
  TRY_CAST(distinct_social_media_presence_count AS INT) AS distinct_social_media_presence_count,
  affiliated_staff_presence,
  custom_logo_presence,
  TRY_CAST(number_of_facts_about_the_organization AS INT) AS number_of_facts_about_the_organization,
  post_metrics_most_recent_social_media_post_date,
  TRY_CAST(post_metrics_post_count AS INT) AS post_metrics_post_count,
  TRY_CAST(engagement_metrics_n_followers AS INT) AS engagement_metrics_n_followers,
  TRY_CAST(engagement_metrics_n_likes AS INT) AS engagement_metrics_n_likes,
  TRY_CAST(engagement_metrics_n_engagements AS INT) AS engagement_metrics_n_engagements,
  source,
  coordinates,
  TRY_CAST(latitude AS DOUBLE) AS latitude,
  TRY_CAST(longitude AS DOUBLE) AS longitude,
  cluster_id,
  source_urls,
  CURRENT_TIMESTAMP() AS bronze_processed_at
FROM dais2026.raw.facilities;

CREATE OR REFRESH MATERIALIZED VIEW bronze.pincode_directory_clean (
  CONSTRAINT pincode_not_null EXPECT (pincode IS NOT NULL) ON VIOLATION DROP ROW,
  CONSTRAINT state_not_null EXPECT (state_normalized IS NOT NULL) ON VIOLATION DROP ROW
)
COMMENT "Bronze: India Post pincode directory with normalized joins"
CLUSTER BY (state_normalized, district_normalized)
AS
WITH ranked_pincodes AS (
  SELECT
    circlename,
    regionname,
    divisionname,
    officename,
    CAST(pincode AS STRING) AS pincode,
    officetype,
    delivery,
    TRIM(UPPER(statename)) AS state_normalized,
    TRIM(UPPER(district)) AS district_normalized,
    TRY_CAST(latitude AS DOUBLE) AS latitude,
    TRY_CAST(longitude AS DOUBLE) AS longitude,
    ROW_NUMBER() OVER (
      PARTITION BY CAST(pincode AS STRING)
      ORDER BY CASE WHEN delivery = 'Delivery' THEN 0 ELSE 1 END, officename
    ) AS pincode_rank
  FROM dais2026.raw.india_post_pincode_directory
)
SELECT
  circlename,
  regionname,
  divisionname,
  officename,
  pincode,
  officetype,
  delivery,
  state_normalized,
  district_normalized,
  latitude,
  longitude,
  CURRENT_TIMESTAMP() AS bronze_processed_at
FROM ranked_pincodes
WHERE pincode_rank = 1;

CREATE OR REFRESH MATERIALIZED VIEW bronze.district_health_indicators_clean (
  CONSTRAINT state_not_null EXPECT (state_normalized IS NOT NULL) ON VIOLATION DROP ROW,
  CONSTRAINT district_not_null EXPECT (district_normalized IS NOT NULL) ON VIOLATION DROP ROW
)
COMMENT "Bronze: NFHS-5 district indicators with bracket-safe numeric parsing"
CLUSTER BY (state_normalized, district_normalized)
AS
SELECT
  TRIM(UPPER(state_ut)) AS state_normalized,
  TRIM(UPPER(district_name)) AS district_normalized,
  district_name,
  state_ut,
  households_surveyed,
  women_15_49_interviewed,
  men_15_54_interviewed,
  TRY_CAST(REGEXP_EXTRACT(CAST(mothers_who_had_an_anc_visit_in_the_first_trimester_lb5y_pct AS STRING), '([0-9]+\\.?[0-9]*)', 1) AS DOUBLE) AS anc_first_trimester_pct,
  TRY_CAST(REGEXP_EXTRACT(CAST(mothers_who_had_at_least_4_anc_visits_lb5y_pct AS STRING), '([0-9]+\\.?[0-9]*)', 1) AS DOUBLE) AS anc_four_plus_pct,
  TRY_CAST(REGEXP_EXTRACT(CAST(institutional_birth_5y_pct AS STRING), '([0-9]+\\.?[0-9]*)', 1) AS DOUBLE) AS institutional_birth_pct,
  TRY_CAST(REGEXP_EXTRACT(CAST(births_attended_by_skilled_hp_5y_10_pct AS STRING), '([0-9]+\\.?[0-9]*)', 1) AS DOUBLE) AS skilled_birth_attendance_pct,
  TRY_CAST(REGEXP_EXTRACT(CAST(child_12_23m_fully_vaccinated_based_on_information_from_eit_pct AS STRING), '([0-9]+\\.?[0-9]*)', 1) AS DOUBLE) AS full_immunization_pct,
  TRY_CAST(REGEXP_EXTRACT(CAST(child_u5_who_are_stunted_height_for_age_18_pct AS STRING), '([0-9]+\\.?[0-9]*)', 1) AS DOUBLE) AS child_stunting_pct,
  TRY_CAST(REGEXP_EXTRACT(CAST(hh_member_covered_health_insurance_pct AS STRING), '([0-9]+\\.?[0-9]*)', 1) AS DOUBLE) AS health_insurance_pct,
  CURRENT_TIMESTAMP() AS bronze_processed_at
FROM dais2026.raw.nfhs_5_district_health_indicators;

-- ============================================================================
-- SILVER LAYER
-- ============================================================================

CREATE OR REFRESH MATERIALIZED VIEW silver.facilities_capabilities_parsed (
  CONSTRAINT unique_id_not_null EXPECT (unique_id IS NOT NULL) ON VIOLATION FAIL UPDATE,
  CONSTRAINT total_claims_non_negative EXPECT (total_capability_claims >= 0)
)
COMMENT "Silver: facility metadata with parsed capability counts"
CLUSTER BY (state, city)
AS
WITH parsed AS (
  SELECT
    unique_id,
    name AS facility_name,
    address_city AS city,
    address_stateOrRegion AS state,
    address_zipOrPostcode AS pincode,
    phone_numbers,
    officialPhone,
    email,
    officialWebsite,
    specialties,
    procedure,
    equipment,
    capability,
    numberDoctors,
    capacity,
    yearEstablished,
    distinct_social_media_presence_count,
    affiliated_staff_presence,
    custom_logo_presence,
    number_of_facts_about_the_organization,
    post_metrics_post_count,
    engagement_metrics_n_followers,
    recency_of_page_update,
    latitude,
    longitude,
    COALESCE(SIZE(FILTER(SPLIT(REGEXP_REPLACE(REGEXP_REPLACE(specialties, '[\\[\\]"]', ''), ',\\s*', '|'), '\\|'), x -> LENGTH(TRIM(x)) > 0)), 0) AS specialty_count,
    COALESCE(SIZE(FILTER(SPLIT(REGEXP_REPLACE(REGEXP_REPLACE(procedure, '[\\[\\]"]', ''), ',\\s*', '|'), '\\|'), x -> LENGTH(TRIM(x)) > 0)), 0) AS procedure_count,
    COALESCE(SIZE(FILTER(SPLIT(REGEXP_REPLACE(REGEXP_REPLACE(equipment, '[\\[\\]"]', ''), ',\\s*', '|'), '\\|'), x -> LENGTH(TRIM(x)) > 0)), 0) AS equipment_count,
    COALESCE(SIZE(FILTER(SPLIT(REGEXP_REPLACE(REGEXP_REPLACE(capability, '[\\[\\]"]', ''), ',\\s*', '|'), '\\|'), x -> LENGTH(TRIM(x)) > 0)), 0) AS capability_count
  FROM bronze.facilities_clean
)
SELECT
  *,
  specialty_count + procedure_count + equipment_count + capability_count AS total_capability_claims,
  CURRENT_TIMESTAMP() AS silver_processed_at
FROM parsed;

CREATE OR REFRESH MATERIALIZED VIEW silver.facilities_capabilities_exploded (
  CONSTRAINT unique_id_not_null EXPECT (unique_id IS NOT NULL) ON VIOLATION DROP ROW,
  CONSTRAINT claim_type_valid EXPECT (claim_type IN ('specialty', 'procedure', 'equipment', 'capability')) ON VIOLATION DROP ROW,
  CONSTRAINT claim_text_not_empty EXPECT (claim_text IS NOT NULL AND LENGTH(TRIM(claim_text)) > 0) ON VIOLATION DROP ROW
)
COMMENT "Silver: one row per capability claim"
CLUSTER BY (claim_type, state)
AS
SELECT unique_id, facility_name, state, city, 'specialty' AS claim_type, TRIM(value) AS claim_text
FROM silver.facilities_capabilities_parsed
LATERAL VIEW EXPLODE(FILTER(SPLIT(REGEXP_REPLACE(REGEXP_REPLACE(specialties, '[\\[\\]"]', ''), ',\\s*', '|'), '\\|'), x -> LENGTH(TRIM(x)) > 0)) AS value
UNION ALL
SELECT unique_id, facility_name, state, city, 'procedure' AS claim_type, TRIM(value) AS claim_text
FROM silver.facilities_capabilities_parsed
LATERAL VIEW EXPLODE(FILTER(SPLIT(REGEXP_REPLACE(REGEXP_REPLACE(procedure, '[\\[\\]"]', ''), ',\\s*', '|'), '\\|'), x -> LENGTH(TRIM(x)) > 0)) AS value
UNION ALL
SELECT unique_id, facility_name, state, city, 'equipment' AS claim_type, TRIM(value) AS claim_text
FROM silver.facilities_capabilities_parsed
LATERAL VIEW EXPLODE(FILTER(SPLIT(REGEXP_REPLACE(REGEXP_REPLACE(equipment, '[\\[\\]"]', ''), ',\\s*', '|'), '\\|'), x -> LENGTH(TRIM(x)) > 0)) AS value
UNION ALL
SELECT unique_id, facility_name, state, city, 'capability' AS claim_type, TRIM(value) AS claim_text
FROM silver.facilities_capabilities_parsed
LATERAL VIEW EXPLODE(FILTER(SPLIT(REGEXP_REPLACE(REGEXP_REPLACE(capability, '[\\[\\]"]', ''), ',\\s*', '|'), '\\|'), x -> LENGTH(TRIM(x)) > 0)) AS value;

CREATE OR REFRESH MATERIALIZED VIEW silver.facilities_specialties_index
COMMENT "Silver: specialty index with original ordering"
CLUSTER BY (state, specialty)
AS
SELECT
  unique_id,
  facility_name,
  state,
  city,
  pos + 1 AS specialty_position,
  TRIM(specialty) AS specialty
FROM silver.facilities_capabilities_parsed
LATERAL VIEW POSEXPLODE(FILTER(SPLIT(REGEXP_REPLACE(REGEXP_REPLACE(specialties, '[\\[\\]"]', ''), ',\\s*', '|'), '\\|'), x -> LENGTH(TRIM(x)) > 0)) AS pos, specialty;

CREATE OR REFRESH MATERIALIZED VIEW silver.district_outcome_baselines
COMMENT "Silver: district health outcome baselines with percentile ranks"
CLUSTER BY (state_normalized, district_normalized)
AS
SELECT
  state_normalized,
  district_normalized,
  institutional_birth_pct,
  skilled_birth_attendance_pct,
  anc_first_trimester_pct,
  anc_four_plus_pct,
  full_immunization_pct,
  child_stunting_pct,
  health_insurance_pct,
  PERCENT_RANK() OVER (ORDER BY institutional_birth_pct) AS institutional_birth_percentile,
  PERCENT_RANK() OVER (ORDER BY skilled_birth_attendance_pct) AS skilled_birth_percentile,
  PERCENT_RANK() OVER (ORDER BY full_immunization_pct) AS immunization_percentile,
  1 - PERCENT_RANK() OVER (ORDER BY child_stunting_pct) AS nutrition_percentile,
  (
    COALESCE(PERCENT_RANK() OVER (ORDER BY institutional_birth_pct), 0.5) * 0.30
    + COALESCE(PERCENT_RANK() OVER (ORDER BY skilled_birth_attendance_pct), 0.5) * 0.25
    + COALESCE(PERCENT_RANK() OVER (ORDER BY full_immunization_pct), 0.5) * 0.25
    + COALESCE(1 - PERCENT_RANK() OVER (ORDER BY child_stunting_pct), 0.5) * 0.20
  ) AS district_capacity_score
FROM bronze.district_health_indicators_clean;

-- ============================================================================
-- GOLD LAYER
-- ============================================================================

CREATE OR REFRESH MATERIALIZED VIEW claim_freshness_scores
COMMENT "Gold: temporal validation and freshness scoring"
CLUSTER BY (freshness_status, state)
AS
WITH dates AS (
  SELECT
    unique_id,
    facility_name,
    state,
    city,
    recency_of_page_update,
    COALESCE(
      TRY_CAST(recency_of_page_update AS DATE),
      TO_DATE(recency_of_page_update, 'yyyy-MM-dd'),
      TO_DATE(recency_of_page_update, 'MM/dd/yyyy'),
      TO_DATE(recency_of_page_update, 'dd-MMM-yyyy')
    ) AS parsed_update_date
  FROM silver.facilities_capabilities_parsed
)
SELECT
  *,
  DATEDIFF(CURRENT_DATE(), parsed_update_date) AS days_since_update,
  CASE
    WHEN parsed_update_date IS NULL THEN 'NO_DATE'
    WHEN DATEDIFF(CURRENT_DATE(), parsed_update_date) < 0 THEN 'FUTURE_DATE'
    WHEN DATEDIFF(CURRENT_DATE(), parsed_update_date) > 365 THEN 'STALE'
    WHEN DATEDIFF(CURRENT_DATE(), parsed_update_date) > 180 THEN 'AGING'
    ELSE 'FRESH'
  END AS freshness_status,
  CASE
    WHEN parsed_update_date IS NULL THEN 0.0
    WHEN DATEDIFF(CURRENT_DATE(), parsed_update_date) < 0 THEN 0.0
    WHEN DATEDIFF(CURRENT_DATE(), parsed_update_date) <= 180 THEN 1.0
    WHEN DATEDIFF(CURRENT_DATE(), parsed_update_date) <= 365 THEN 0.5
    ELSE 0.0
  END AS freshness_score,
  CURRENT_TIMESTAMP() AS validation_scored_at
FROM dates;

CREATE OR REFRESH MATERIALIZED VIEW name_claim_alignment_scores
COMMENT "Gold: specialty name versus claimed services alignment"
CLUSTER BY (alignment_status, state)
AS
WITH detected AS (
  SELECT
    unique_id,
    facility_name,
    state,
    city,
    total_capability_claims,
    CASE
      WHEN LOWER(facility_name) RLIKE 'eye|ophthal|vision' THEN 'EYE_SPECIALTY'
      WHEN LOWER(facility_name) RLIKE 'dental|dent |tooth' THEN 'DENTAL_SPECIALTY'
      WHEN LOWER(facility_name) RLIKE 'cardiac|cardio|heart' THEN 'CARDIAC_SPECIALTY'
      WHEN LOWER(facility_name) RLIKE 'cancer|oncolog|chemo' THEN 'CANCER_SPECIALTY'
      WHEN LOWER(facility_name) RLIKE 'ortho|bone|joint' THEN 'ORTHOPEDIC_SPECIALTY'
      WHEN LOWER(facility_name) RLIKE 'neuro|brain' THEN 'NEURO_SPECIALTY'
      ELSE 'GENERAL_OR_MULTI'
    END AS name_implied_specialty
  FROM silver.facilities_capabilities_parsed
),
off_claims AS (
  SELECT
    d.unique_id,
    COUNT_IF(
      d.name_implied_specialty <> 'GENERAL_OR_MULTI'
      AND e.claim_type IN ('specialty', 'procedure')
      AND LOWER(e.claim_text) RLIKE 'dialysis|cardiac|neuro|ortho|dental|surgery|oncolog|chemo|icu'
      AND NOT (
        (d.name_implied_specialty = 'CARDIAC_SPECIALTY' AND LOWER(e.claim_text) RLIKE 'cardiac|cardio|heart')
        OR (d.name_implied_specialty = 'EYE_SPECIALTY' AND LOWER(e.claim_text) RLIKE 'eye|vision|ophthal|retina|cataract|cornea')
        OR (d.name_implied_specialty = 'DENTAL_SPECIALTY' AND LOWER(e.claim_text) RLIKE 'dental|tooth|oral|gum')
        OR (d.name_implied_specialty = 'ORTHOPEDIC_SPECIALTY' AND LOWER(e.claim_text) RLIKE 'ortho|bone|joint')
        OR (d.name_implied_specialty = 'NEURO_SPECIALTY' AND LOWER(e.claim_text) RLIKE 'neuro|brain')
        OR (d.name_implied_specialty = 'CANCER_SPECIALTY' AND LOWER(e.claim_text) RLIKE 'cancer|oncolog|chemo')
      )
    ) AS off_specialty_claims
  FROM detected d
  LEFT JOIN silver.facilities_capabilities_exploded e ON d.unique_id = e.unique_id
  GROUP BY d.unique_id
)
SELECT
  d.unique_id,
  d.facility_name,
  d.state,
  d.city,
  d.name_implied_specialty,
  d.total_capability_claims,
  COALESCE(o.off_specialty_claims, 0) AS off_specialty_claims,
  CASE
    WHEN d.name_implied_specialty = 'GENERAL_OR_MULTI' THEN 1.0
    ELSE GREATEST(0.0, 1.0 - COALESCE(o.off_specialty_claims, 0) / 15.0)
  END AS name_claim_alignment_score,
  CASE
    WHEN COALESCE(o.off_specialty_claims, 0) >= 15 THEN 'HIGH_MISMATCH'
    WHEN COALESCE(o.off_specialty_claims, 0) >= 5 THEN 'MODERATE_MISMATCH'
    WHEN COALESCE(o.off_specialty_claims, 0) >= 1 THEN 'LOW_MISMATCH'
    ELSE 'ALIGNED'
  END AS alignment_status
FROM detected d
LEFT JOIN off_claims o ON d.unique_id = o.unique_id;

CREATE OR REFRESH MATERIALIZED VIEW claim_plausibility_scores
COMMENT "Gold: six-component plausibility score"
CLUSTER BY (plausibility_status, state)
AS
SELECT
  f.unique_id,
  f.facility_name,
  f.state,
  f.city,
  f.total_capability_claims,
  a.name_claim_alignment_score,
  CASE WHEN f.total_capability_claims >= 200 THEN 0.25 WHEN f.total_capability_claims >= 150 THEN 0.45 WHEN f.total_capability_claims >= 75 THEN 0.75 ELSE 1.0 END AS volume_plausibility_score,
  CASE WHEN f.total_capability_claims = 0 THEN 0.0 ELSE LEAST(1.0, (f.specialty_count + f.procedure_count + f.equipment_count + f.capability_count) / 40.0) END AS claim_balance_score,
  LEAST(1.0, (COALESCE(f.distinct_social_media_presence_count, 0) + CASE WHEN f.officialWebsite IS NOT NULL THEN 1 ELSE 0 END + CASE WHEN f.email IS NOT NULL THEN 1 ELSE 0 END) / 4.0) AS social_signal_score,
  CASE WHEN f.latitude IS NOT NULL AND f.longitude IS NOT NULL THEN 1.0 ELSE 0.4 END AS location_quality_score,
  LEAST(1.0, (CASE WHEN f.officialPhone IS NOT NULL OR f.phone_numbers IS NOT NULL THEN 0.6 ELSE 0 END + CASE WHEN f.email IS NOT NULL THEN 0.2 ELSE 0 END + CASE WHEN f.officialWebsite IS NOT NULL THEN 0.2 ELSE 0 END)) AS contact_quality_score,
  (
    COALESCE(a.name_claim_alignment_score, 0.5) * 0.20
    + (CASE WHEN f.total_capability_claims >= 200 THEN 0.25 WHEN f.total_capability_claims >= 150 THEN 0.45 WHEN f.total_capability_claims >= 75 THEN 0.75 ELSE 1.0 END) * 0.25
    + (CASE WHEN f.total_capability_claims = 0 THEN 0.0 ELSE LEAST(1.0, f.total_capability_claims / 40.0) END) * 0.15
    + LEAST(1.0, (COALESCE(f.distinct_social_media_presence_count, 0) + CASE WHEN f.officialWebsite IS NOT NULL THEN 1 ELSE 0 END + CASE WHEN f.email IS NOT NULL THEN 1 ELSE 0 END) / 4.0) * 0.15
    + (CASE WHEN f.latitude IS NOT NULL AND f.longitude IS NOT NULL THEN 1.0 ELSE 0.4 END) * 0.15
    + LEAST(1.0, (CASE WHEN f.officialPhone IS NOT NULL OR f.phone_numbers IS NOT NULL THEN 0.6 ELSE 0 END + CASE WHEN f.email IS NOT NULL THEN 0.2 ELSE 0 END + CASE WHEN f.officialWebsite IS NOT NULL THEN 0.2 ELSE 0 END)) * 0.10
  ) AS overall_plausibility_score,
  CASE WHEN f.total_capability_claims >= 150 THEN 'SUSPICIOUS_VOLUME' WHEN COALESCE(a.name_claim_alignment_score, 1.0) < 0.4 THEN 'NAME_CLAIM_MISMATCH' WHEN f.total_capability_claims = 0 THEN 'INCOMPLETE_DATA' ELSE 'PLAUSIBLE' END AS plausibility_status
FROM silver.facilities_capabilities_parsed f
LEFT JOIN name_claim_alignment_scores a ON f.unique_id = a.unique_id;

CREATE OR REFRESH MATERIALIZED VIEW data_quality_signals
COMMENT "Gold: clipping, duplication, and template reuse detection"
CLUSTER BY (data_quality_status, state)
AS
WITH duplicate_counts AS (
  SELECT unique_id, COUNT(*) AS exploded_rows, COUNT(DISTINCT LOWER(claim_text)) AS distinct_claims
  FROM silver.facilities_capabilities_exploded
  GROUP BY unique_id
),
template_claims AS (
  SELECT claim_text
  FROM silver.facilities_capabilities_exploded
  WHERE LENGTH(claim_text) > 20
  GROUP BY claim_text
  HAVING COUNT(DISTINCT unique_id) >= 5
),
template_facilities AS (
  SELECT e.unique_id, COUNT(*) AS template_claim_count
  FROM silver.facilities_capabilities_exploded e
  INNER JOIN template_claims t ON e.claim_text = t.claim_text
  GROUP BY e.unique_id
)
SELECT
  f.unique_id,
  f.facility_name,
  f.state,
  f.city,
  f.total_capability_claims,
  COALESCE(d.exploded_rows, 0) AS actual_exploded_rows,
  COALESCE(d.distinct_claims, 0) AS distinct_claims,
  COALESCE(t.template_claim_count, 0) AS template_claim_count,
  f.total_capability_claims = 200 AS at_claim_ceiling_200,
  COALESCE(d.exploded_rows, 0) = 150 AS at_exploded_ceiling_150,
  f.specialty_count = 50 AS at_specialty_ceiling_50,
  CASE WHEN COALESCE(d.exploded_rows, 0) = 0 THEN 0.0 ELSE 1.0 - (COALESCE(d.distinct_claims, 0) / COALESCE(d.exploded_rows, 1)) END AS duplicate_ratio,
  GREATEST(0.0, 1.0 - (
    CASE WHEN f.total_capability_claims = 200 THEN 0.30 ELSE 0 END
    + CASE WHEN COALESCE(d.exploded_rows, 0) = 150 THEN 0.25 ELSE 0 END
    + CASE WHEN f.specialty_count = 50 THEN 0.20 ELSE 0 END
    + CASE WHEN COALESCE(t.template_claim_count, 0) >= 20 THEN 0.30 ELSE 0 END
    + CASE WHEN COALESCE(d.exploded_rows, 0) > 0 AND 1.0 - (COALESCE(d.distinct_claims, 0) / COALESCE(d.exploded_rows, 1)) > 0.50 THEN 0.40 ELSE 0 END
  )) AS data_quality_score,
  CASE
    WHEN f.total_capability_claims = 200 OR COALESCE(d.exploded_rows, 0) = 150 OR f.specialty_count = 50 THEN 'LIKELY_CLIPPED_DATA'
    WHEN COALESCE(t.template_claim_count, 0) >= 20 THEN 'TEMPLATE_CONTENT'
    WHEN COALESCE(d.exploded_rows, 0) > 0 AND 1.0 - (COALESCE(d.distinct_claims, 0) / COALESCE(d.exploded_rows, 1)) > 0.50 THEN 'HIGH_DUPLICATION'
    ELSE 'ACCEPTABLE'
  END AS data_quality_status
FROM silver.facilities_capabilities_parsed f
LEFT JOIN duplicate_counts d ON f.unique_id = d.unique_id
LEFT JOIN template_facilities t ON f.unique_id = t.unique_id;

CREATE OR REFRESH MATERIALIZED VIEW facility_confidence_scores
COMMENT "Gold: final confidence score combining plausibility, district outcomes, freshness, and geography"
CLUSTER BY (confidence_tier, state)
AS
SELECT
  f.unique_id,
  f.facility_name,
  f.state,
  f.city,
  p.overall_plausibility_score,
  COALESCE(b.district_capacity_score, 0.5) AS district_capacity_score,
  fr.freshness_score,
  CASE WHEN pc.pincode IS NULL THEN 0.5 WHEN pc.state_normalized = TRIM(UPPER(f.state)) THEN 1.0 ELSE 0.0 END AS geographic_match_score,
  (
    COALESCE(p.overall_plausibility_score, 0.5) * 0.45
    + COALESCE(b.district_capacity_score, 0.5) * 0.30
    + COALESCE(fr.freshness_score, 0.0) * 0.15
    + (CASE WHEN pc.pincode IS NULL THEN 0.5 WHEN pc.state_normalized = TRIM(UPPER(f.state)) THEN 1.0 ELSE 0.0 END) * 0.10
  ) AS final_confidence_score,
  CASE
    WHEN (
      COALESCE(p.overall_plausibility_score, 0.5) * 0.45
      + COALESCE(b.district_capacity_score, 0.5) * 0.30
      + COALESCE(fr.freshness_score, 0.0) * 0.15
      + (CASE WHEN pc.pincode IS NULL THEN 0.5 WHEN pc.state_normalized = TRIM(UPPER(f.state)) THEN 1.0 ELSE 0.0 END) * 0.10
    ) >= 0.70 THEN 'HIGH_CONFIDENCE'
    WHEN (
      COALESCE(p.overall_plausibility_score, 0.5) * 0.45
      + COALESCE(b.district_capacity_score, 0.5) * 0.30
      + COALESCE(fr.freshness_score, 0.0) * 0.15
      + (CASE WHEN pc.pincode IS NULL THEN 0.5 WHEN pc.state_normalized = TRIM(UPPER(f.state)) THEN 1.0 ELSE 0.0 END) * 0.10
    ) >= 0.50 THEN 'MEDIUM_CONFIDENCE'
    ELSE 'LOW_CONFIDENCE'
  END AS confidence_tier,
  ARRAY_REMOVE(ARRAY(
    CASE WHEN fr.freshness_status IN ('FUTURE_DATE', 'NO_DATE', 'STALE') THEN fr.freshness_status ELSE NULL END,
    CASE WHEN p.plausibility_status <> 'PLAUSIBLE' THEN p.plausibility_status ELSE NULL END,
    CASE WHEN pc.pincode IS NOT NULL AND pc.state_normalized <> TRIM(UPPER(f.state)) THEN 'PINCODE_STATE_MISMATCH' ELSE NULL END
  ), NULL) AS red_flags
FROM silver.facilities_capabilities_parsed f
LEFT JOIN claim_plausibility_scores p ON f.unique_id = p.unique_id
LEFT JOIN claim_freshness_scores fr ON f.unique_id = fr.unique_id
LEFT JOIN bronze.pincode_directory_clean pc ON f.pincode = pc.pincode
LEFT JOIN silver.district_outcome_baselines b ON TRIM(UPPER(f.state)) = b.state_normalized AND TRIM(UPPER(f.city)) = b.district_normalized;

CREATE OR REFRESH MATERIALIZED VIEW integrated_facility_assessment
COMMENT "Gold: production assessment combining quality and confidence"
CLUSTER BY (overall_reliability, state)
AS
SELECT
  f.unique_id,
  f.facility_name,
  f.state,
  f.city,
  f.pincode,
  f.latitude,
  f.longitude,
  f.phone_numbers,
  f.officialPhone,
  f.email,
  f.officialWebsite,
  f.specialties,
  f.capability,
  f.total_capability_claims,
  c.final_confidence_score,
  q.data_quality_score,
  GREATEST(0.0, (COALESCE(c.final_confidence_score, 0.5) * 0.60 + COALESCE(q.data_quality_score, 0.5) * 0.40) - 0.0012) AS combined_quality_confidence_score,
  CASE
    WHEN GREATEST(0.0, (COALESCE(c.final_confidence_score, 0.5) * 0.60 + COALESCE(q.data_quality_score, 0.5) * 0.40) - 0.0012) >= 0.75 THEN 'HIGH_RELIABILITY'
    WHEN GREATEST(0.0, (COALESCE(c.final_confidence_score, 0.5) * 0.60 + COALESCE(q.data_quality_score, 0.5) * 0.40) - 0.0012) >= 0.60 THEN 'MODERATE_RELIABILITY'
    ELSE 'LOW_RELIABILITY'
  END AS overall_reliability,
  CASE
    WHEN COALESCE(c.final_confidence_score, 0.0) >= 0.80 AND COALESCE(q.data_quality_score, 0.0) >= 0.80 THEN 'HIGHLY_LIKELY'
    WHEN COALESCE(c.final_confidence_score, 0.0) >= 0.60 AND COALESCE(q.data_quality_score, 0.0) >= 0.60 THEN 'LIKELY'
    ELSE 'UNVERIFIED'
  END AS delivery_likelihood,
  c.confidence_tier,
  c.red_flags,
  q.data_quality_status,
  CURRENT_TIMESTAMP() AS assessment_generated_at
FROM silver.facilities_capabilities_parsed f
LEFT JOIN facility_confidence_scores c ON f.unique_id = c.unique_id
LEFT JOIN data_quality_signals q ON f.unique_id = q.unique_id;
