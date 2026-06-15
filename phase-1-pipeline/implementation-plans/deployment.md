# Facility Validation Pipeline - Deployment Guide

## Overview

**Pipeline Name:** `facility_validation_framework`

**Pipeline ID:** `27fea50d-7b95-4540-b673-a0c8c92fe08d`

**Notebook Path:** `/Workspace/Users/richthai92@gmail.com/DAIS-2026-AI-for-Good/facility_validation_framework`

**Compute:** Serverless SQL (Photon-enabled)

**Refresh Strategy:** TRIGGER ON UPDATE (cascading from raw → bronze → silver → gold)

---

## Pre-Deployment Checklist

### Source Data Validation

- [ ] Verify raw tables exist and are accessible:
  - `dais2026.raw.facilities`
  - `dais2026.raw.india_post_pincode_directory`
  - `dais2026.raw.nfhs_5_district_health_indicators`

- [ ] Check raw table row counts:
```sql
SELECT 'facilities' as table_name, COUNT(*) as row_count FROM dais2026.raw.facilities
UNION ALL
SELECT 'pincode_directory', COUNT(*) FROM dais2026.raw.india_post_pincode_directory
UNION ALL
SELECT 'nfhs_5', COUNT(*) FROM dais2026.raw.nfhs_5_district_health_indicators;
```

Expected: ~10K facilities, ~165K pincodes, ~750 districts

### Schema Permissions

- [ ] Verify catalog/schema permissions:
```sql
-- Check Bronze schema exists or create
CREATE SCHEMA IF NOT EXISTS bronze COMMENT 'Bronze layer: validated raw data copies';

-- Check Silver schema exists or create  
CREATE SCHEMA IF NOT EXISTS silver COMMENT 'Silver layer: transformed and enriched data';

-- Check Validation schema exists or create
CREATE SCHEMA IF NOT EXISTS validation COMMENT 'Gold layer: validation scoring tables';
```

- [ ] Test write permissions:
```sql
-- Test write access to each schema
CREATE OR REPLACE TABLE bronze.deployment_test (id INT) AS SELECT 1;
CREATE OR REPLACE TABLE silver.deployment_test (id INT) AS SELECT 1;
CREATE OR REPLACE TABLE validation.deployment_test (id INT) AS SELECT 1;

-- Cleanup
DROP TABLE bronze.deployment_test;
DROP TABLE silver.deployment_test;
DROP TABLE validation.deployment_test;
```

### Pipeline Configuration

- [ ] Navigate to pipeline editor: `/editor/pipelines/27fea50d-7b95-4540-b673-a0c8c92fe08d`

- [ ] Verify pipeline settings:
  - **Compute:** Serverless
  - **Channel:** Current (not Preview)
  - **Development mode:** Enabled (for initial run)

---

## Deployment Steps

### Step 1: Initial Validation Run

- [ ] Start pipeline in **Development mode**

Expected duration: 5-10 minutes for full refresh

- [ ] Monitor for errors in Event Log

Watch for:
- Syntax errors (should be 0 if validation passed)
- Constraint violations (track DROP ROW counts)
- FAIL UPDATE violations (should be 0)

### Step 2: Verify Bronze Layer

- [ ] Check Bronze table creation:
```sql
SHOW TABLES IN bronze LIKE 'facilities*';
SHOW TABLES IN bronze LIKE 'pincode*';
SHOW TABLES IN bronze LIKE 'district*';
```

Expected: 3 tables (facilities_clean, pincode_directory_clean, district_health_indicators_clean)

- [ ] Validate Bronze row counts:
```sql
SELECT 'facilities_clean' as table_name, COUNT(*) as row_count FROM bronze.facilities_clean
UNION ALL
SELECT 'pincode_directory_clean', COUNT(*) FROM bronze.pincode_directory_clean
UNION ALL
SELECT 'district_health_indicators_clean', COUNT(*) FROM bronze.district_health_indicators_clean;
```

Expected: ~99% pass-through for facilities, ~100% for others

- [ ] Check constraint violation metrics in pipeline UI

Expected violations:
- `valid_latitude DROP ROW`: ~50 rows (0.5%)
- `valid_longitude DROP ROW`: ~50 rows (0.5%)
- `state_not_null DROP ROW`: ~20 rows (0.2%)
- `unique_id_not_null FAIL UPDATE`: 0 rows

### Step 3: Verify Silver Layer

- [ ] Check Silver table creation:
```sql
SHOW TABLES IN silver;
```

Expected: 4 tables (facilities_capabilities_parsed, facilities_capabilities_exploded, facilities_specialties_index, district_outcome_baselines)

- [ ] Validate Silver row counts:
```sql
SELECT 'facilities_capabilities_parsed' as table_name, COUNT(*) as row_count FROM silver.facilities_capabilities_parsed
UNION ALL
SELECT 'facilities_capabilities_exploded', COUNT(*) FROM silver.facilities_capabilities_exploded
UNION ALL
SELECT 'facilities_specialties_index', COUNT(*) FROM silver.facilities_specialties_index
UNION ALL
SELECT 'district_outcome_baselines', COUNT(*) FROM silver.district_outcome_baselines;
```

Expected:
- parsed: ~10K rows (1:1 with Bronze)
- exploded: ~460K rows (46:1 explosion ratio)
- specialties_index: ~50K rows (5 per facility avg)
- district_baselines: ~750 rows (1 per district)

- [ ] Check explosion ratio:
```sql
SELECT 
  (SELECT COUNT(*) FROM silver.facilities_capabilities_exploded) as exploded_rows,
  (SELECT COUNT(*) FROM silver.facilities_capabilities_parsed) as parsed_rows,
  ROUND((SELECT COUNT(*) FROM silver.facilities_capabilities_exploded) * 1.0 / 
        (SELECT COUNT(*) FROM silver.facilities_capabilities_parsed), 1) as explosion_ratio;
```

Expected: explosion_ratio between 40-50

### Step 4: Verify Gold Layer

- [ ] Check Gold/Validation table creation:
```sql
SHOW TABLES IN validation;
```

Expected: 6 tables (claim_freshness_scores, name_claim_alignment_scores, claim_plausibility_scores, data_quality_signals, facility_confidence_scores, integrated_facility_assessment)

- [ ] Validate Gold row counts:
```sql
SELECT 'claim_freshness_scores' as table_name, COUNT(*) as row_count FROM validation.claim_freshness_scores
UNION ALL
SELECT 'name_claim_alignment_scores', COUNT(*) FROM validation.name_claim_alignment_scores
UNION ALL
SELECT 'claim_plausibility_scores', COUNT(*) FROM validation.claim_plausibility_scores
UNION ALL
SELECT 'data_quality_signals', COUNT(*) FROM validation.data_quality_signals
UNION ALL
SELECT 'facility_confidence_scores', COUNT(*) FROM validation.facility_confidence_scores
UNION ALL
SELECT 'integrated_facility_assessment', COUNT(*) FROM validation.integrated_facility_assessment;
```

Expected: All tables ~10K rows (1:1 with facilities)

- [ ] Check confidence tier distribution:
```sql
SELECT 
  confidence_tier,
  COUNT(*) as facility_count,
  ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 1) as percentage
FROM validation.facility_confidence_scores
GROUP BY confidence_tier;
```

Expected: HIGH 30-40%, MEDIUM 40-50%, LOW 10-20%

### Step 5: Production Readiness Checks

- [ ] Test production filtering query:
```sql
SELECT 
  facility_name,
  state,
  city,
  combined_quality_confidence_score,
  overall_reliability,
  delivery_likelihood
FROM validation.integrated_facility_assessment
WHERE overall_reliability IN ('HIGH_RELIABILITY', 'MODERATE_RELIABILITY')
  AND combined_quality_confidence_score >= 0.60
ORDER BY combined_quality_confidence_score DESC
LIMIT 100;
```

Expected: List of validated facilities with scores

- [ ] Analyze red flag distribution:
```sql
SELECT 
  red_flag,
  COUNT(*) as facility_count,
  ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM validation.integrated_facility_assessment), 1) as percentage
FROM validation.integrated_facility_assessment
LATERAL VIEW EXPLODE(combined_red_flags) AS red_flag
GROUP BY red_flag
ORDER BY facility_count DESC;
```

Expected red flag percentages:
- FUTURE_DATE: <1%
- OVERCLAIMING: 5-10%
- NAME_CLAIM_MISMATCH: 2-5%
- LIKELY_CLIPPED_DATA: 3-7%
- TEMPLATE_CONTENT: 10-15%

### Step 6: Enable Production Mode

- [ ] Stop development mode pipeline

- [ ] Switch to **Production mode**:
  - Uncheck "Development mode" in pipeline settings
  - Save pipeline configuration

- [ ] Start production pipeline

- [ ] Verify continuous refresh:
  - Pipeline shows "Running" status
  - Tables refresh automatically when raw data updates

---

## Post-Deployment Monitoring

### Daily Health Checks

```sql
-- Pipeline health dashboard
SELECT 
  'Total Facilities' as metric,
  COUNT(*) as value
FROM bronze.facilities_clean
UNION ALL
SELECT 
  'High Confidence',
  COUNT(*)
FROM validation.facility_confidence_scores
WHERE confidence_tier = 'HIGH_CONFIDENCE'
UNION ALL
SELECT 
  'Production Ready',
  COUNT(*)
FROM validation.integrated_facility_assessment
WHERE overall_reliability IN ('HIGH_RELIABILITY', 'MODERATE_RELIABILITY')
  AND combined_quality_confidence_score >= 0.60;
```

### Weekly Quality Reports

```sql
-- Weekly data quality trends
SELECT 
  DATE_TRUNC('week', validation_scored_at) as week,
  overall_data_quality_status,
  COUNT(*) as facility_count
FROM validation.data_quality_signals
GROUP BY 1, 2
ORDER BY 1 DESC, 2;
```

### Alert Thresholds

Set up alerts for:

- **High constraint violations** (>5% in Bronze layer)
```sql
SELECT COUNT(*) as violation_count
FROM bronze.facilities_clean
WHERE latitude NOT BETWEEN -90 AND 90 
   OR longitude NOT BETWEEN -180 AND 180;
```

- **Explosion ratio anomaly** (outside 40-50 range)
```sql
SELECT 
  ROUND((SELECT COUNT(*) FROM silver.facilities_capabilities_exploded) * 1.0 / 
        (SELECT COUNT(*) FROM silver.facilities_capabilities_parsed), 1) as explosion_ratio
HAVING explosion_ratio < 40 OR explosion_ratio > 50;
```

- **Confidence drop** (<30% in HIGH tier)
```sql
SELECT 
  ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM validation.facility_confidence_scores), 1) as high_confidence_pct
FROM validation.facility_confidence_scores
WHERE confidence_tier = 'HIGH_CONFIDENCE'
HAVING high_confidence_pct < 30;
```

---

## Rollback Procedure

If deployment fails or produces unexpected results:

### Quick Rollback

- [ ] Stop pipeline

- [ ] Drop Gold tables:
```sql
DROP TABLE IF EXISTS validation.claim_freshness_scores;
DROP TABLE IF EXISTS validation.name_claim_alignment_scores;
DROP TABLE IF EXISTS validation.claim_plausibility_scores;
DROP TABLE IF EXISTS validation.data_quality_signals;
DROP TABLE IF EXISTS validation.facility_confidence_scores;
DROP TABLE IF EXISTS validation.integrated_facility_assessment;
```

- [ ] Drop Silver tables:
```sql
DROP TABLE IF EXISTS silver.facilities_capabilities_parsed;
DROP TABLE IF EXISTS silver.facilities_capabilities_exploded;
DROP TABLE IF EXISTS silver.facilities_specialties_index;
DROP TABLE IF EXISTS silver.district_outcome_baselines;
```

- [ ] Drop Bronze tables:
```sql
DROP TABLE IF EXISTS bronze.facilities_clean;
DROP TABLE IF EXISTS bronze.pincode_directory_clean;
DROP TABLE IF EXISTS bronze.district_health_indicators_clean;
```

- [ ] Fix pipeline code issues

- [ ] Re-run deployment from Step 1

---

## Optimization & Tuning

### Performance Tuning

- [ ] Enable row tracking on raw tables for incremental refresh:
```sql
ALTER TABLE dais2026.raw.facilities 
SET TBLPROPERTIES ('delta.enableRowTracking' = 'true');

ALTER TABLE dais2026.raw.india_post_pincode_directory
SET TBLPROPERTIES ('delta.enableRowTracking' = 'true');

ALTER TABLE dais2026.raw.nfhs_5_district_health_indicators
SET TBLPROPERTIES ('delta.enableRowTracking' = 'true');
```

- [ ] Monitor table sizes:
```sql
DESCRIBE DETAIL silver.facilities_capabilities_exploded;
```

- [ ] If exploded table grows too large, consider partitioning:
```sql
-- Add partitioning to exploded table (requires recreation)
ALTER TABLE silver.facilities_capabilities_exploded
CLUSTER BY (claim_type, state);
```

### Scoring Weight Adjustments

If production feedback suggests adjustments:

- [ ] Update plausibility weights in `claim_plausibility_scores`
- [ ] Update confidence weights in `facility_confidence_scores`
- [ ] Update combined assessment weights in `integrated_facility_assessment`
- [ ] Refresh Gold tables to recompute scores

---

## Success Metrics

### Deployment Success

✅ All 13 tables (3 Bronze + 4 Silver + 6 Gold) created
✅ Row counts match expectations
✅ Constraint violations <5%
✅ Pipeline running in production mode

### Data Quality Success

✅ Bronze pass-through ≥99%
✅ Silver explosion ratio 40-50:1
✅ <5% facilities with LIKELY_CLIPPED_DATA
✅ <2% facilities with FUTURE_DATE

### Production Readiness

✅ ≥30% facilities in HIGH_CONFIDENCE tier
✅ ≥70% facilities in HIGH/MEDIUM tiers
✅ Production filtering query returns validated facilities
✅ Red flag distribution matches expectations

---

## Troubleshooting

### Pipeline Fails on Initial Run

**Check Event Log** for specific errors:

- **Syntax error**: Fix SQL in pipeline notebook, re-run validation
- **Permission error**: Grant write access to schemas
- **Missing table**: Verify raw tables exist and are accessible
- **Constraint FAIL UPDATE**: Check for null unique_ids in raw data

### Unexpected Row Counts

**Too few rows in Bronze**:
- Check constraint violation rates
- May need to relax geographic constraints

**Explosion ratio too low**:
- Investigate array parsing logic
- Check for NULL arrays in Silver parsed table

**Missing Gold rows**:
- Check for failed joins in confidence scoring
- Verify all component tables have matching unique_ids

### Scoring Distribution Anomalies

**Too many LOW_CONFIDENCE facilities**:
- Review scoring weights
- Check if district_outcome_baselines joined properly
- Analyze component score distributions

**Too many UNRELIABLE_DATA facilities**:
- Check data_quality_signals for clipping prevalence
- May indicate systemic issues in raw data

---

## Next Steps After Deployment

1. **Schedule regular audits** - Weekly review of scoring distributions
2. **Set up dashboards** - Visualize confidence tiers over time
3. **Document edge cases** - Track unusual scoring patterns
4. **Iterate on weights** - Adjust based on production feedback
5. **Expand validation signals** - Add new quality checks as needed

---

## Contact & Support

**Pipeline Owner:** [Your Name]

**Documentation:** `/Workspace/Users/richthai92@gmail.com/docs/superpowers/plans/`

**Related Plans:**
- Architecture: `2025-01-15-facility-validation-pipeline-architecture.md`
- Bronze Layer: `2025-01-15-facility-validation-bronze-layer.md`
- Silver Layer: `2025-01-15-facility-validation-silver-layer.md`
- Gold Layer: `2025-01-15-facility-validation-gold-layer.md`
