# Facility Validation Pipeline - Architecture & Specification

## Overview

**Purpose:** Production data pipeline to validate healthcare facility capability claims using multi-dimensional scoring and external reference data (geographic, health outcomes).

**Architecture:** Medallion (Bronze → Silver → Gold) using Lakeflow Spark Declarative Pipelines (SQL, Serverless)

**Source Data:**
- `dais2026.raw.facilities` (~10K facilities with capability claims)
- `dais2026.raw.india_post_pincode_directory` (~165K pincodes for geographic validation)
- `dais2026.raw.nfhs_5_district_health_indicators` (~750 districts for outcome correlation)

**Target Schema:** `validation.*` (final Gold tables for production consumption)

---

## Layer Architecture

### Bronze Layer (Clean & Validate)

**Purpose:** Type-validated copies with geographic constraints and parsed numeric fields

**Tables:**
1. `bronze.facilities_clean` - Validated facilities with lat/lon bounds, parsed engagement metrics
2. `bronze.pincode_directory_clean` - Normalized state/district names for geographic joins
3. `bronze.district_health_indicators_clean` - NFHS-5 with normalized geographies

**Quality Gates:**
- Geographic constraints (lat: -90 to 90, lon: -180 to 180)
- Required fields (unique_id, state, pincode)
- Type casting with `TRY_CAST` (nulls on parse failures)
- `ON VIOLATION DROP ROW` for constraint violations

### Silver Layer (Transform & Enrich)

**Purpose:** Parse structured arrays, explode claims, aggregate district outcomes

**Tables:**
1. `silver.facilities_capabilities_parsed` - Count claims per type, preserve arrays
2. `silver.facilities_capabilities_exploded` - One row per claim (4 claim types × facilities)
3. `silver.facilities_specialties_index` - Facility-specialty mapping with position ranking
4. `silver.district_outcome_baselines` - NFHS-5 aggregated with percentile rankings

**Transformations:**
- JSON array parsing: `REGEXP_REPLACE` → `SPLIT` → `FILTER` → `SIZE`
- Array explosions: `LATERAL VIEW EXPLODE` and `POSEXPLODE`
- Percentile rankings: `PERCENT_RANK() OVER (ORDER BY ...)`
- Window functions for position tracking

### Gold Layer (Validate & Score)

**Purpose:** Multi-dimensional validation scoring for production filtering

**Tables:**
1. `validation.claim_freshness_scores` - Temporal validation (freshness_score, FUTURE_DATE detection)
2. `validation.name_claim_alignment_scores` - Semantic validation (specialty-name alignment)
3. `validation.claim_plausibility_scores` - 6-component plausibility (volume, balance, social, location, contact, name-claim)
4. `validation.data_quality_signals` - Clipping detection (200/150/50 ceilings), template reuse, duplication
5. `validation.facility_confidence_scores` - Final confidence (4-component weighted: plausibility 45%, district 30%, freshness 15%, match 10%)
6. `validation.integrated_facility_assessment` - Combined quality + confidence for production filtering

**Scoring Weights:**

**Plausibility Components (overall_plausibility_score):**
- Name-claim alignment: 20%
- Volume plausibility: 25%
- Claim balance: 15%
- Social signals: 15%
- Location quality: 15%
- Contact quality: 10%

**Final Confidence (final_confidence_score):**
- Overall plausibility: 45%
- District outcomes: 30%
- Freshness: 15%
- District match: 10%

**Combined Assessment (combined_quality_confidence_score):**
- Confidence: 60%
- Data quality: 40%

---

## Validation Signals Catalogue

### Signal Set 1: Temporal Validation
- **FUTURE_DATE**: Update date > current date
- **STALE**: Update date > 365 days old
- **NO_DATE**: Missing recency_of_page_update

### Signal Set 2: Semantic Validation
- **HIGH_MISMATCH**: Specialty-named facility claiming 15+ off-specialty services
- **MODERATE_MISMATCH**: 5-15 off-specialty claims
- **LOW_MISMATCH**: 1-5 off-specialty claims

### Signal Set 3: Data Quality
- **AT_CLAIM_CEILING_200**: Exactly 200 total claims
- **AT_EXPLODED_CEILING_150**: Exactly 150 exploded rows
- **AT_SPECIALTY_CEILING_50**: Exactly 50 specialties
- **HIGH_DUPLICATION**: >50% within-facility duplicate claims
- **HIGH_TEMPLATE_USAGE**: 20+ shared claims across 5+ facilities

### Signal Set 4: Plausibility
- **OVERCLAIMING**: 150+ total claims
- **UNRELIABLE_DATE**: Future date or missing
- **NAME_CLAIM_MISMATCH**: Alignment score < 0.4

### Signal Set 5: Geographic Validation
- Pincode-state mismatch
- District match quality (0.0 = mismatch, 1.0 = match, NULL = no pincode data)

### Signal Set 6: External Outcomes
- District capacity score (0-1, from NFHS-5 percentile aggregation)
- Maternal health percentile
- Immunization percentile
- Nutrition percentile (inverted - lower is better)

---

## Key Design Decisions

### 1. Array Parsing Strategy
**Challenge:** Raw arrays stored as JSON strings: `["specialty1", "specialty2"]`

**Solution:**
```sql
-- Clean brackets/quotes → split → filter empties → count
COALESCE(SIZE(
  FILTER(
    SPLIT(REGEXP_REPLACE(REGEXP_REPLACE(specialties, '[\\[\\]"]', ''), ',\\s*', '|'), '\\|'),
    x -> LENGTH(TRIM(x)) > 0
  )
), 0) as specialty_count
```

### 2. Specialty Detection
**Challenge:** Identify specialty-focused facilities for semantic validation

**Solution:** Pattern matching on facility name
```sql
CASE 
  WHEN LOWER(name) LIKE '%eye%' OR LOWER(name) LIKE '%ophthal%' THEN 'EYE_SPECIALTY'
  WHEN LOWER(name) LIKE '%dental%' OR LOWER(name) LIKE '%dent %' THEN 'DENTAL_SPECIALTY'
  WHEN LOWER(name) LIKE '%cardiac%' OR LOWER(name) LIKE '%heart%' THEN 'CARDIAC_SPECIALTY'
  -- ... more patterns
  ELSE 'GENERAL_OR_MULTI'
END as name_implied_specialty
```

### 3. Clipping Detection
**Challenge:** Detect systematic data ceilings

**Solution:** Exact equality checks + near-ceiling thresholds
- `total_capability_claims = 200` → AT_CLAIM_CEILING_200
- `actual_exploded_rows = 150` → AT_EXPLODED_CEILING_150
- `specialty_count = 50` → AT_SPECIALTY_CEILING_50

### 4. Template Reuse Detection
**Challenge:** Identify copy-pasted capability lists

**Solution:** Count claims appearing in 5+ facilities
```sql
SELECT DISTINCT claim_text
FROM silver.facilities_capabilities_exploded
WHERE LENGTH(claim_text) > 20  -- Exclude generic short claims
GROUP BY claim_text
HAVING COUNT(DISTINCT unique_id) >= 5
```

### 5. Incremental Refresh
**Optimization:** Serverless pipelines with row tracking enabled support incremental materialized view refresh

**Requirements:**
- Delta sources with row tracking enabled
- Deterministic functions only (except `CURRENT_DATE()` in WHERE clauses)
- Window functions must specify `PARTITION BY`

---

## Performance Optimizations

### Liquid Clustering
**All tables use `CLUSTER BY` on query access patterns:**

| Table | Cluster Keys | Reason |
|-------|-------------|---------|
| Bronze facilities | (state, city) | Geographic filtering |
| Silver exploded | (claim_type, state) | Type-based analysis |
| Gold validation | (status_field, state) | Status filtering + geography |

### Constraint Strategy
**DROP ROW vs FAIL UPDATE:**
- `DROP ROW`: Data quality issues (invalid lat/lon, empty claims)
- `FAIL UPDATE`: Critical integrity (unique_id not null)

### Array Processing
**Minimize repeated parsing:**
- Parse arrays once in Silver (facilities_capabilities_parsed)
- Reuse parsed arrays for explosions and aggregations
- Store both counts and raw arrays for downstream flexibility

---

## Data Quality Expectations

### Bronze Layer Pass-Through Rates
**Expected violations per 10K facilities:**
- Invalid lat/lon: ~50 rows (0.5%)
- Missing state: ~20 rows (0.2%)
- Missing unique_id: 0 rows (FAIL UPDATE if occurs)

### Silver Layer Transformation Rates
**Expected output volumes:**
- `facilities_capabilities_parsed`: ~10K rows (1:1 with input)
- `facilities_capabilities_exploded`: ~460K rows (avg 46 claims/facility)
- `facilities_specialties_index`: ~50K rows (avg 5 specialties/facility)
- `district_outcome_baselines`: ~750 rows (1 per district)

### Gold Layer Scoring Distribution (Expected)
**Confidence tiers:**
- HIGH_CONFIDENCE (≥0.70): 30-40%
- MEDIUM_CONFIDENCE (0.50-0.69): 40-50%
- LOW_CONFIDENCE (<0.50): 10-20%

**Red flag prevalence:**
- FUTURE_DATE: <1%
- OVERCLAIMING: 5-10%
- NAME_CLAIM_MISMATCH: 2-5%
- LIKELY_CLIPPED_DATA: 3-7%
- TEMPLATE_CONTENT: 10-15%

---

## Production Usage

### Primary Filtering Query
```sql
SELECT 
  facility_name,
  state,
  city,
  total_capability_claims,
  final_confidence_score,
  data_quality_score,
  combined_quality_confidence_score,
  overall_reliability,
  delivery_likelihood
FROM validation.integrated_facility_assessment
WHERE overall_reliability IN ('HIGH_RELIABILITY', 'MODERATE_RELIABILITY')
  AND combined_quality_confidence_score >= 0.60
  AND delivery_likelihood IN ('HIGHLY_LIKELY', 'LIKELY')
ORDER BY combined_quality_confidence_score DESC;
```

### Red Flag Analysis
```sql
SELECT 
  red_flag,
  COUNT(*) as facility_count,
  ROUND(AVG(combined_quality_confidence_score), 3) as avg_confidence
FROM validation.integrated_facility_assessment
LATERAL VIEW EXPLODE(combined_red_flags) AS red_flag
GROUP BY red_flag
ORDER BY facility_count DESC;
```

### Specialty Validation Deep-Dive
```sql
SELECT 
  name_implied_specialty,
  alignment_status,
  COUNT(*) as facility_count,
  ROUND(AVG(off_specialty_claims), 1) as avg_off_specialty_claims,
  ROUND(AVG(name_claim_alignment_score), 3) as avg_alignment_score
FROM validation.name_claim_alignment_scores
WHERE name_implied_specialty != 'GENERAL_OR_MULTI'
GROUP BY name_implied_specialty, alignment_status
ORDER BY name_implied_specialty, alignment_status;
```

---

## Pipeline Configuration

**Compute:** Serverless (SQL-optimized, Photon enabled)

**Refresh Strategy:**
- Bronze: TRIGGER ON UPDATE (auto-refresh when raw tables update)
- Silver: TRIGGER ON UPDATE (cascade from Bronze)
- Gold: TRIGGER ON UPDATE (cascade from Silver)

**Notebook Path:** `/Workspace/Users/richthai92@gmail.com/DAIS-2026-AI-for-Good/facility_validation_framework`

**Target Catalog/Schema:**
- Bronze: `bronze.*`
- Silver: `silver.*`
- Gold: `validation.*`

**Pipeline Name:** `facility_validation_framework`

---

## Success Criteria

### Pipeline Health
✅ All tables refresh successfully without FAIL UPDATE violations
✅ Bronze pass-through rate ≥99%
✅ Silver explosion ratio 40-50:1 (expected ~46:1)
✅ Gold scoring coverage 100% (no null confidence scores)

### Data Quality
✅ <5% facilities with LIKELY_CLIPPED_DATA status
✅ <2% facilities with FUTURE_DATE
✅ Geographic match rate ≥85% (pincode validation)

### Production Readiness
✅ ≥30% facilities in HIGH_CONFIDENCE tier
✅ ≥70% facilities in HIGH or MEDIUM tiers combined
✅ Red flag documentation complete with mitigation strategies

---

## Next Steps

1. **Implement Bronze Layer** - Validate data quality constraints
2. **Implement Silver Layer** - Verify array parsing and explosion logic
3. **Implement Gold Layer** - Validate scoring formulas and weights
4. **Run Initial Validation** - Check constraint violation rates
5. **Tune NFHS Column Names** - Adjust to actual schema
6. **Deploy to Production** - Enable continuous refresh
7. **Monitor & Iterate** - Track scoring distributions and adjust weights

---

## Related Documentation

- Bronze Layer Implementation Plan: `2025-01-15-facility-validation-bronze-layer.md`
- Silver Layer Implementation Plan: `2025-01-15-facility-validation-silver-layer.md`
- Gold Layer Implementation Plan: `2025-01-15-facility-validation-gold-layer.md`
- Deployment Guide: `2025-01-15-facility-validation-deployment.md`
