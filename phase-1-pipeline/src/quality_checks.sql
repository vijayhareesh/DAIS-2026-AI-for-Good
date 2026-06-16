-- HealthVerify India pipeline verification checks.
-- Run after the Lakeflow pipeline completes.

-- Source data checks.
SELECT 'raw.facilities' AS check_name, COUNT(*) AS row_count
FROM dais2026.raw.facilities;

SELECT 'raw.india_post_pincode_directory' AS check_name, COUNT(*) AS row_count
FROM dais2026.raw.india_post_pincode_directory;

SELECT 'raw.nfhs_5_district_health_indicators' AS check_name, COUNT(*) AS row_count
FROM dais2026.raw.nfhs_5_district_health_indicators;

-- Layer row counts.
SELECT 'bronze.facilities_clean' AS table_name, COUNT(*) AS row_count FROM bronze.facilities_clean
UNION ALL SELECT 'bronze.pincode_directory_clean', COUNT(*) FROM bronze.pincode_directory_clean
UNION ALL SELECT 'bronze.district_health_indicators_clean', COUNT(*) FROM bronze.district_health_indicators_clean
UNION ALL SELECT 'silver.facilities_capabilities_parsed', COUNT(*) FROM silver.facilities_capabilities_parsed
UNION ALL SELECT 'silver.facilities_capabilities_exploded', COUNT(*) FROM silver.facilities_capabilities_exploded
UNION ALL SELECT 'silver.facilities_specialties_index', COUNT(*) FROM silver.facilities_specialties_index
UNION ALL SELECT 'silver.district_outcome_baselines', COUNT(*) FROM silver.district_outcome_baselines
UNION ALL SELECT 'validation.claim_freshness_scores', COUNT(*) FROM validation.claim_freshness_scores
UNION ALL SELECT 'validation.name_claim_alignment_scores', COUNT(*) FROM validation.name_claim_alignment_scores
UNION ALL SELECT 'validation.claim_plausibility_scores', COUNT(*) FROM validation.claim_plausibility_scores
UNION ALL SELECT 'validation.data_quality_signals', COUNT(*) FROM validation.data_quality_signals
UNION ALL SELECT 'validation.facility_confidence_scores', COUNT(*) FROM validation.facility_confidence_scores
UNION ALL SELECT 'validation.integrated_facility_assessment', COUNT(*) FROM validation.integrated_facility_assessment;

-- Final score distribution: target is about 10K facilities with 30-40% high,
-- 40-50% medium, and 10-20% low confidence.
SELECT
  COUNT(*) AS total_facilities,
  AVG(combined_quality_confidence_score) AS avg_combined_score,
  SUM(CASE WHEN final_confidence_score >= 0.70 THEN 1 ELSE 0 END) AS high_confidence_count,
  SUM(CASE WHEN final_confidence_score >= 0.50 AND final_confidence_score < 0.70 THEN 1 ELSE 0 END) AS medium_confidence_count,
  SUM(CASE WHEN final_confidence_score < 0.50 THEN 1 ELSE 0 END) AS low_confidence_count,
  SUM(CASE WHEN final_confidence_score IS NULL OR data_quality_score IS NULL OR combined_quality_confidence_score IS NULL THEN 1 ELSE 0 END) AS null_score_count
FROM validation.integrated_facility_assessment;

-- Demo facility lookup. If absent, seed it into Lakebase with scripts/seed_demo_data.py.
SELECT
  unique_id,
  facility_name,
  city,
  state,
  total_capability_claims,
  final_confidence_score,
  data_quality_score,
  combined_quality_confidence_score,
  red_flags
FROM validation.integrated_facility_assessment
WHERE LOWER(facility_name) LIKE '%heritage%hospital%'
  AND LOWER(city) LIKE '%varanasi%'
ORDER BY combined_quality_confidence_score DESC
LIMIT 10;
