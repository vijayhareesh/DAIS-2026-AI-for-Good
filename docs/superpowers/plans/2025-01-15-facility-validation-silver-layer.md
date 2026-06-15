# Silver Layer Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Transform Bronze data with array parsing, explosions, and district outcome aggregations

**Architecture:** Four materialized views with JSON array processing and window functions

**Tech Stack:** Lakeflow Spark Declarative Pipelines (SQL), Serverless compute, LATERAL VIEW EXPLODE

---

## File Structure

**Pipeline Notebook:**
- Modify: `/Workspace/Users/richthai92@gmail.com/DAIS-2026-AI-for-Good/facility_validation_framework`

**Tables Created:**
1. `silver.facilities_capabilities_parsed`
2. `silver.facilities_capabilities_exploded`
3. `silver.facilities_specialties_index`
4. `silver.district_outcome_baselines`

---

## Task 1: Create Facilities Capabilities Parsed Table

**Files:**
- Modify: `/Workspace/Users/richthai92@gmail.com/DAIS-2026-AI-for-Good/facility_validation_framework`

- [ ] **Step 1: Add Silver layer header comment**

```sql
-- ============================================================================
-- SILVER LAYER: Transformed and enriched data
-- ============================================================================
```

- [ ] **Step 2: Add array parsing helper function documentation**

```sql
-- Array Parsing Strategy:
-- Raw format: ["specialty1", "specialty2", "specialty3"]
-- Steps:
--   1. REGEXP_REPLACE('[\\[\\]"]', '') → Remove brackets and quotes
--   2. SPLIT(',\\s*', '|') → Split on commas into array
--   3. FILTER(x -> LENGTH(TRIM(x)) > 0) → Remove empty strings
--   4. SIZE(...) → Count elements
--   5. COALESCE(..., 0) → Default to 0 if null
```

- [ ] **Step 3: Add facilities_capabilities_parsed table definition**

```sql
-- -----------------------------------------------------------------------------
-- 1. facilities_capabilities_parsed
-- Parse structured arrays and calculate total capability claims
-- -----------------------------------------------------------------------------
CREATE OR REFRESH MATERIALIZED VIEW silver.facilities_capabilities_parsed (
  CONSTRAINT unique_id_not_null EXPECT (unique_id IS NOT NULL) ON VIOLATION FAIL UPDATE,
  CONSTRAINT total_claims_non_negative EXPECT (total_capability_claims >= 0)
)
COMMENT "Silver: Parsed capability arrays with claim counts and facility metadata"
CLUSTER BY (state, city)
AS
WITH parsed_capabilities AS (
  SELECT 
    unique_id,
    name as facility_name,
    address_city as city,
    address_stateOrRegion as state,
    address_zipOrPostcode as pincode,
    
    -- Parse JSON arrays - count non-null array elements
    COALESCE(SIZE(
      FILTER(
        SPLIT(REGEXP_REPLACE(REGEXP_REPLACE(specialties, '[\\[\\]"]', ''), ',\\s*', '|'), '\\|'),
        x -> LENGTH(TRIM(x)) > 0
      )
    ), 0) as specialty_count,
    
    COALESCE(SIZE(
      FILTER(
        SPLIT(REGEXP_REPLACE(REGEXP_REPLACE(procedure, '[\\[\\]"]', ''), ',\\s*', '|'), '\\|'),
        x -> LENGTH(TRIM(x)) > 0
      )
    ), 0) as procedure_count,
    
    COALESCE(SIZE(
      FILTER(
        SPLIT(REGEXP_REPLACE(REGEXP_REPLACE(equipment, '[\\[\\]"]', ''), ',\\s*', '|'), '\\|'),
        x -> LENGTH(TRIM(x)) > 0
      )
    ), 0) as equipment_count,
    
    COALESCE(SIZE(
      FILTER(
        SPLIT(REGEXP_REPLACE(REGEXP_REPLACE(capability, '[\\[\\]"]', ''), ',\\s*', '|'), '\\|'),
        x -> LENGTH(TRIM(x)) > 0
      )
    ), 0) as capability_count,
    
    -- Keep raw arrays for downstream explosion
    specialties,
    procedure,
    equipment,
    capability,
    
    -- Facility metadata
    organization_type,
    description,
    numberDoctors,
    capacity,
    yearEstablished,
    
    -- Contact info
    phone_numbers,
    email,
    officialWebsite,
    
    -- Social metrics
    engagement_metrics_n_followers,
    post_metrics_post_count,
    distinct_social_media_presence_count,
    custom_logo_presence,
    affiliated_staff_presence,
    number_of_facts_about_the_organization,
    
    -- Temporal
    recency_of_page_update,
    
    -- Geographic
    latitude,
    longitude,
    
    -- Metadata
    CURRENT_TIMESTAMP() as silver_processed_at
  FROM bronze.facilities_clean
)
SELECT 
  *,
  -- Calculate total capability claims
  (specialty_count + procedure_count + equipment_count + capability_count) as total_capability_claims
FROM parsed_capabilities;
```

- [ ] **Step 4: Verify array parsing logic**

Test with sample data:

```sql
-- Test array parsing on a single facility
SELECT 
  unique_id,
  specialties,
  COALESCE(SIZE(
    FILTER(
      SPLIT(REGEXP_REPLACE(REGEXP_REPLACE(specialties, '[\\[\\]"]', ''), ',\\s*', '|'), '\\|'),
      x -> LENGTH(TRIM(x)) > 0
    )
  ), 0) as specialty_count
FROM bronze.facilities_clean
WHERE specialties IS NOT NULL
LIMIT 5;
```

Expected: Counts match actual number of specialties in raw array

- [ ] **Step 5: Commit parsed capabilities table**

```bash
cd /Workspace/Users/richthai92@gmail.com/DAIS-2026-AI-for-Good
git add facility_validation_framework
git commit -m "feat(silver): add facilities_capabilities_parsed with array parsing"
```

---

## Task 2: Create Facilities Capabilities Exploded Table

**Files:**
- Modify: `/Workspace/Users/richthai92@gmail.com/DAIS-2026-AI-for-Good/facility_validation_framework`

- [ ] **Step 1: Add explosion logic documentation**

```sql
-- Array Explosion Strategy:
-- Goal: Convert one facility row with N claims into N rows (one per claim)
-- Approach: LATERAL VIEW EXPLODE for each claim type, then UNION ALL
-- Output: claim_type (specialty|procedure|equipment|capability) + claim_text
```

- [ ] **Step 2: Add facilities_capabilities_exploded table definition**

```sql
-- -----------------------------------------------------------------------------
-- 2. facilities_capabilities_exploded
-- Explode claims to one row per claim for analysis
-- -----------------------------------------------------------------------------
CREATE OR REFRESH MATERIALIZED VIEW silver.facilities_capabilities_exploded (
  CONSTRAINT unique_id_not_null EXPECT (unique_id IS NOT NULL) ON VIOLATION DROP ROW,
  CONSTRAINT claim_type_valid EXPECT (claim_type IN ('specialty', 'procedure', 'equipment', 'capability')) ON VIOLATION DROP ROW,
  CONSTRAINT claim_text_not_empty EXPECT (claim_text IS NOT NULL AND LENGTH(TRIM(claim_text)) > 0) ON VIOLATION DROP ROW
)
COMMENT "Silver: One row per facility capability claim for detailed analysis"
CLUSTER BY (claim_type, state)
AS
WITH exploded_specialties AS (
  SELECT 
    unique_id,
    facility_name,
    state,
    city,
    'specialty' as claim_type,
    TRIM(specialty_value) as claim_text
  FROM silver.facilities_capabilities_parsed
  LATERAL VIEW EXPLODE(
    FILTER(
      SPLIT(REGEXP_REPLACE(REGEXP_REPLACE(specialties, '[\\[\\]"]', ''), ',\\s*', '|'), '\\|'),
      x -> LENGTH(TRIM(x)) > 0
    )
  ) AS specialty_value
  WHERE specialties IS NOT NULL
),
exploded_procedures AS (
  SELECT 
    unique_id,
    facility_name,
    state,
    city,
    'procedure' as claim_type,
    TRIM(procedure_value) as claim_text
  FROM silver.facilities_capabilities_parsed
  LATERAL VIEW EXPLODE(
    FILTER(
      SPLIT(REGEXP_REPLACE(REGEXP_REPLACE(procedure, '[\\[\\]"]', ''), ',\\s*', '|'), '\\|'),
      x -> LENGTH(TRIM(x)) > 0
    )
  ) AS procedure_value
  WHERE procedure IS NOT NULL
),
exploded_equipment AS (
  SELECT 
    unique_id,
    facility_name,
    state,
    city,
    'equipment' as claim_type,
    TRIM(equipment_value) as claim_text
  FROM silver.facilities_capabilities_parsed
  LATERAL VIEW EXPLODE(
    FILTER(
      SPLIT(REGEXP_REPLACE(REGEXP_REPLACE(equipment, '[\\[\\]"]', ''), ',\\s*', '|'), '\\|'),
      x -> LENGTH(TRIM(x)) > 0
    )
  ) AS equipment_value
  WHERE equipment IS NOT NULL
),
exploded_capabilities AS (
  SELECT 
    unique_id,
    facility_name,
    state,
    city,
    'capability' as claim_type,
    TRIM(capability_value) as claim_text
  FROM silver.facilities_capabilities_parsed
  LATERAL VIEW EXPLODE(
    FILTER(
      SPLIT(REGEXP_REPLACE(REGEXP_REPLACE(capability, '[\\[\\]"]', ''), ',\\s*', '|'), '\\|'),
      x -> LENGTH(TRIM(x)) > 0
    )
  ) AS capability_value
  WHERE capability IS NOT NULL
)
SELECT 
  *,
  CURRENT_TIMESTAMP() as silver_processed_at
FROM exploded_specialties
UNION ALL
SELECT 
  *,
  CURRENT_TIMESTAMP() as silver_processed_at
FROM exploded_procedures
UNION ALL
SELECT 
  *,
  CURRENT_TIMESTAMP() as silver_processed_at
FROM exploded_equipment
UNION ALL
SELECT 
  *,
  CURRENT_TIMESTAMP() as silver_processed_at
FROM exploded_capabilities;
```

- [ ] **Step 3: Validate explosion multiplier**

Test row count ratio:

```sql
-- Check explosion ratio
SELECT 
  (SELECT COUNT(*) FROM silver.facilities_capabilities_exploded) as exploded_rows,
  (SELECT COUNT(*) FROM silver.facilities_capabilities_parsed) as parsed_rows,
  ROUND(
    (SELECT COUNT(*) FROM silver.facilities_capabilities_exploded) * 1.0 / 
    (SELECT COUNT(*) FROM silver.facilities_capabilities_parsed),
    1
  ) as explosion_ratio;
```

Expected: explosion_ratio between 40-50 (avg 46 claims per facility)

- [ ] **Step 4: Verify claim type distribution**

```sql
-- Check claim type distribution
SELECT 
  claim_type,
  COUNT(*) as claim_count,
  COUNT(DISTINCT unique_id) as facility_count,
  ROUND(COUNT(*) * 1.0 / COUNT(DISTINCT unique_id), 1) as avg_claims_per_facility
FROM silver.facilities_capabilities_exploded
GROUP BY claim_type
ORDER BY claim_count DESC;
```

Expected: All 4 claim types present with reasonable distributions

- [ ] **Step 5: Commit exploded capabilities table**

```bash
cd /Workspace/Users/richthai92@gmail.com/DAIS-2026-AI-for-Good
git add facility_validation_framework
git commit -m "feat(silver): add facilities_capabilities_exploded with LATERAL VIEW"
```

---

## Task 3: Create Facilities Specialties Index Table

**Files:**
- Modify: `/Workspace/Users/richthai92@gmail.com/DAIS-2026-AI-for-Good/facility_validation_framework`

- [ ] **Step 1: Add specialties index documentation**

```sql
-- Specialty Index Strategy:
-- Goal: Create facility-specialty mapping with position ranking
-- Use case: Semantic validation (match facility name to specialty claims)
-- Technique: POSEXPLODE to preserve array position
```

- [ ] **Step 2: Add facilities_specialties_index table definition**

```sql
-- -----------------------------------------------------------------------------
-- 3. facilities_specialties_index
-- One row per facility-specialty pair with position ranking
-- -----------------------------------------------------------------------------
CREATE OR REFRESH MATERIALIZED VIEW silver.facilities_specialties_index (
  CONSTRAINT unique_id_not_null EXPECT (unique_id IS NOT NULL) ON VIOLATION DROP ROW,
  CONSTRAINT specialty_not_empty EXPECT (specialty IS NOT NULL AND LENGTH(TRIM(specialty)) > 0) ON VIOLATION DROP ROW,
  CONSTRAINT position_positive EXPECT (specialty_position >= 1)
)
COMMENT "Silver: Facility specialties with ranking position"
CLUSTER BY (state, city)
AS
SELECT 
  fcp.unique_id,
  fcp.facility_name,
  fcp.state,
  fcp.city,
  fcp.pincode,
  TRIM(specialty_value) as specialty,
  
  -- Position in the specialty list (1-indexed from POSEXPLODE)
  (specialty_position + 1) as specialty_position,
  
  -- Contact info
  fcp.phone_numbers as primary_phone,
  fcp.officialWebsite as primary_website,
  
  -- Geographic
  fcp.latitude,
  fcp.longitude,
  
  -- Temporal and engagement
  fcp.recency_of_page_update,
  fcp.engagement_metrics_n_followers,
  
  -- Metadata
  CURRENT_TIMESTAMP() as silver_processed_at
FROM silver.facilities_capabilities_parsed fcp
LATERAL VIEW POSEXPLODE(
  FILTER(
    SPLIT(REGEXP_REPLACE(REGEXP_REPLACE(specialties, '[\\[\\]"]', ''), ',\\s*', '|'), '\\|'),
    x -> LENGTH(TRIM(x)) > 0
  )
) AS specialty_position, specialty_value
WHERE fcp.specialties IS NOT NULL;
```

- [ ] **Step 3: Verify position tracking**

```sql
-- Test position tracking for a single facility
SELECT 
  unique_id,
  facility_name,
  specialty,
  specialty_position
FROM silver.facilities_specialties_index
WHERE unique_id IN (
  SELECT unique_id FROM silver.facilities_capabilities_parsed LIMIT 1
)
ORDER BY specialty_position;
```

Expected: Positions start at 1 and increment sequentially

- [ ] **Step 4: Check specialty distribution**

```sql
-- Check top specialties
SELECT 
  specialty,
  COUNT(DISTINCT unique_id) as facility_count
FROM silver.facilities_specialties_index
GROUP BY specialty
ORDER BY facility_count DESC
LIMIT 20;
```

Expected: Reasonable medical specialty names (Cardiology, Orthopedics, etc.)

- [ ] **Step 5: Commit specialties index table**

```bash
cd /Workspace/Users/richthai92@gmail.com/DAIS-2026-AI-for-Good
git add facility_validation_framework
git commit -m "feat(silver): add facilities_specialties_index with position ranking"
```

---

## Task 4: Create District Outcome Baselines Table

**Files:**
- Modify: `/Workspace/Users/richthai92@gmail.com/DAIS-2026-AI-for-Good/facility_validation_framework`

- [ ] **Step 1: Identify NFHS-5 column names**

```sql
-- Query actual NFHS-5 schema
DESCRIBE TABLE bronze.district_health_indicators_clean;
```

Expected: List of health indicator columns (maternal, immunization, nutrition, etc.)

- [ ] **Step 2: Document NFHS column mapping**

```sql
-- NFHS-5 Column Mapping:
-- Note: Update these column names based on actual schema
-- Expected patterns:
--   - Maternal: "Institutional births (%)", "Mothers who had at least 4 antenatal care visits (%)"
--   - Immunization: "Children age 12-23 months fully immunized (%)"
--   - Nutrition: "Children under 5 years who are stunted (%)", "Children under 5 years who are wasted (%)"
--
-- Action: Replace placeholder column references with actual names from DESCRIBE output
```

- [ ] **Step 3: Add district_outcome_baselines table definition**

```sql
-- -----------------------------------------------------------------------------
-- 4. district_outcome_baselines
-- Aggregate NFHS health indicators by district with percentile rankings
-- -----------------------------------------------------------------------------
CREATE OR REFRESH MATERIALIZED VIEW silver.district_outcome_baselines (
  CONSTRAINT state_not_null EXPECT (state_normalized IS NOT NULL) ON VIOLATION DROP ROW,
  CONSTRAINT district_not_null EXPECT (district_normalized IS NOT NULL) ON VIOLATION DROP ROW
)
COMMENT "Silver: District health indicators with percentile rankings for validation"
CLUSTER BY (state_normalized, district_normalized)
AS
WITH indicator_columns AS (
  SELECT 
    state_normalized,
    district_normalized,
    state_original,
    district_original,
    
    -- NOTE: Update these column references to match actual NFHS-5 schema
    -- Example indicators (adjust based on DESCRIBE TABLE output):
    
    -- Maternal health indicator
    TRY_CAST(
      COALESCE(
        `Institutional births (%)`,
        `Mothers who had at least 4 antenatal care visits (%)`
      ) AS DOUBLE
    ) as maternal_health_score,
    
    -- Child immunization indicator
    TRY_CAST(
      COALESCE(
        `Children age 12-23 months fully immunized (%)`,
        `Children age 12-23 months fully immunized`
      ) AS DOUBLE
    ) as immunization_score,
    
    -- Nutrition indicator (lower is better)
    TRY_CAST(
      COALESCE(
        `Children under 5 years who are stunted (%)`,
        `Children under 5 years who are wasted (%)`
      ) AS DOUBLE
    ) as nutrition_score,
    
    -- Metadata
    bronze_processed_at
  FROM bronze.district_health_indicators_clean
)
SELECT 
  state_normalized,
  district_normalized,
  state_original,
  district_original,
  
  -- Raw indicator values
  maternal_health_score,
  immunization_score,
  nutrition_score,
  
  -- Percentile rankings (0-1 scale)
  PERCENT_RANK() OVER (ORDER BY maternal_health_score) as maternal_percentile,
  PERCENT_RANK() OVER (ORDER BY immunization_score) as immunization_percentile,
  PERCENT_RANK() OVER (ORDER BY nutrition_score DESC) as nutrition_percentile,  -- DESC: lower is better
  
  -- Overall district capacity score (average of percentiles)
  ROUND(
    (
      COALESCE(PERCENT_RANK() OVER (ORDER BY maternal_health_score), 0.5) +
      COALESCE(PERCENT_RANK() OVER (ORDER BY immunization_score), 0.5) +
      COALESCE(PERCENT_RANK() OVER (ORDER BY nutrition_score DESC), 0.5)
    ) / 3.0,
    3
  ) as district_capacity_score,
  
  -- Tier classification
  CASE 
    WHEN ROUND(
      (
        COALESCE(PERCENT_RANK() OVER (ORDER BY maternal_health_score), 0.5) +
        COALESCE(PERCENT_RANK() OVER (ORDER BY immunization_score), 0.5) +
        COALESCE(PERCENT_RANK() OVER (ORDER BY nutrition_score DESC), 0.5)
      ) / 3.0, 3
    ) >= 0.75 THEN 'HIGH_CAPACITY'
    WHEN ROUND(
      (
        COALESCE(PERCENT_RANK() OVER (ORDER BY maternal_health_score), 0.5) +
        COALESCE(PERCENT_RANK() OVER (ORDER BY immunization_score), 0.5) +
        COALESCE(PERCENT_RANK() OVER (ORDER BY nutrition_score DESC), 0.5)
      ) / 3.0, 3
    ) >= 0.50 THEN 'MEDIUM_CAPACITY'
    ELSE 'LOW_CAPACITY'
  END as district_capacity_tier,
  
  -- Metadata
  CURRENT_TIMESTAMP() as silver_processed_at
FROM indicator_columns;
```

- [ ] **Step 4: Verify percentile calculations**

```sql
-- Check percentile distribution
SELECT 
  district_capacity_tier,
  COUNT(*) as district_count,
  ROUND(AVG(district_capacity_score), 3) as avg_capacity_score,
  ROUND(MIN(district_capacity_score), 3) as min_score,
  ROUND(MAX(district_capacity_score), 3) as max_score
FROM silver.district_outcome_baselines
GROUP BY district_capacity_tier
ORDER BY 
  CASE district_capacity_tier
    WHEN 'HIGH_CAPACITY' THEN 1
    WHEN 'MEDIUM_CAPACITY' THEN 2
    WHEN 'LOW_CAPACITY' THEN 3
  END;
```

Expected: Roughly even distribution across tiers (HIGH: 25%, MEDIUM: 50%, LOW: 25%)

- [ ] **Step 5: Sample district baselines**

```sql
-- Sample district outcomes
SELECT 
  state_original,
  district_original,
  maternal_percentile,
  immunization_percentile,
  nutrition_percentile,
  district_capacity_score,
  district_capacity_tier
FROM silver.district_outcome_baselines
ORDER BY district_capacity_score DESC
LIMIT 20;
```

Expected: Top districts have high percentile ranks across all indicators

- [ ] **Step 6: Commit district baselines table**

```bash
cd /Workspace/Users/richthai92@gmail.com/DAIS-2026-AI-for-Good
git add facility_validation_framework
git commit -m "feat(silver): add district_outcome_baselines with percentile rankings"
```

---

## Task 5: Validate Silver Layer Dependencies

**Files:**
- Pipeline: `facility_validation_framework`

- [ ] **Step 1: Check table dependency graph**

Expected dependency order:
1. Bronze tables (no dependencies)
2. `silver.facilities_capabilities_parsed` (depends on bronze.facilities_clean)
3. `silver.facilities_capabilities_exploded` (depends on silver.facilities_capabilities_parsed)
4. `silver.facilities_specialties_index` (depends on silver.facilities_capabilities_parsed)
5. `silver.district_outcome_baselines` (depends on bronze.district_health_indicators_clean)

- [ ] **Step 2: Validate all Silver tables in pipeline**

Click "Validate" in pipeline editor

Expected:
- ✅ All Silver CREATE statements valid
- ✅ Dependencies correctly ordered
- ✅ No circular dependencies
- ✅ All CLUSTER BY columns exist

- [ ] **Step 3: Document Silver layer structure**

```sql
-- Silver Layer Structure:
-- 
-- Parsing Path:
--   bronze.facilities_clean → silver.facilities_capabilities_parsed
--                          ↓
--   silver.facilities_capabilities_exploded (row-per-claim)
--                          ↓
--   silver.facilities_specialties_index (specialty focus)
--
-- Reference Data Path:
--   bronze.district_health_indicators_clean → silver.district_outcome_baselines
--
-- All Silver tables feed into Gold validation layer
```

- [ ] **Step 4: Commit Silver validation notes**

```bash
cd /Workspace/Users/richthai92@gmail.com/DAIS-2026-AI-for-Good
git add facility_validation_framework
git commit -m "docs(silver): add layer structure and dependency notes"
```

---

## Task 6: Test Silver Layer with Sample Data

**Files:**
- Pipeline: `facility_validation_framework`

- [ ] **Step 1: Run pipeline with Silver tables**

Start pipeline in development mode

Expected: All Silver tables refresh successfully

- [ ] **Step 2: Verify Silver row counts**

```sql
-- Silver layer row counts
SELECT 'facilities_capabilities_parsed' as table_name, COUNT(*) as row_count 
FROM silver.facilities_capabilities_parsed
UNION ALL
SELECT 'facilities_capabilities_exploded', COUNT(*) 
FROM silver.facilities_capabilities_exploded
UNION ALL
SELECT 'facilities_specialties_index', COUNT(*) 
FROM silver.facilities_specialties_index
UNION ALL
SELECT 'district_outcome_baselines', COUNT(*) 
FROM silver.district_outcome_baselines;
```

Expected:
- parsed: ~10K rows (1:1 with Bronze)
- exploded: ~460K rows (46:1 explosion ratio)
- specialties_index: ~50K rows (5 specialties per facility avg)
- district_baselines: ~750 rows (1 per district)

- [ ] **Step 3: Validate array parsing accuracy**

```sql
-- Compare parsed counts to raw array lengths
SELECT 
  fcp.unique_id,
  fcp.specialty_count as parsed_specialty_count,
  (SELECT COUNT(*) 
   FROM silver.facilities_specialties_index fsi 
   WHERE fsi.unique_id = fcp.unique_id) as index_specialty_count
FROM silver.facilities_capabilities_parsed fcp
WHERE fcp.specialty_count > 0
LIMIT 100;
```

Expected: parsed_specialty_count = index_specialty_count for all rows

- [ ] **Step 4: Check for NULL claim_text violations**

```sql
-- Verify no empty claims slipped through
SELECT 
  claim_type,
  COUNT(*) as empty_claim_count
FROM silver.facilities_capabilities_exploded
WHERE claim_text IS NULL OR LENGTH(TRIM(claim_text)) = 0
GROUP BY claim_type;
```

Expected: 0 rows (all should be filtered by constraint)

- [ ] **Step 5: Sample cross-facility template detection**

```sql
-- Find claims shared across multiple facilities
SELECT 
  claim_text,
  COUNT(DISTINCT unique_id) as facility_count
FROM silver.facilities_capabilities_exploded
WHERE LENGTH(claim_text) > 20
GROUP BY claim_text
HAVING COUNT(DISTINCT unique_id) >= 5
ORDER BY facility_count DESC
LIMIT 20;
```

Expected: Some generic claims (e.g., "Emergency Services", "Outpatient Care") appear in many facilities

- [ ] **Step 6: Document Silver layer test results**

Create test report:

```markdown
## Silver Layer Test Results

**Date:** YYYY-MM-DD
**Duration:** ~X minutes

**Row Counts:**
- facilities_capabilities_parsed: X rows
- facilities_capabilities_exploded: X rows (Y:1 explosion ratio)
- facilities_specialties_index: X rows
- district_outcome_baselines: X rows

**Data Quality Checks:**
- ✅ Array parsing accuracy: parsed_count matches index_count
- ✅ No NULL or empty claim_text
- ✅ Explosion ratio within expected range (40-50:1)
- ✅ Percentile rankings properly distributed

**Template Detection:**
- X claims shared across 5+ facilities
- Top shared claims: [list top 5]

**Status:** READY FOR GOLD LAYER
```

- [ ] **Step 7: Commit Silver test results**

```bash
cd /Workspace/Users/richthai92@gmail.com/DAIS-2026-AI-for-Good
git add docs/silver-layer-test-results.md
git commit -m "test(silver): add array parsing and explosion validation results"
```

---

## Success Criteria

✅ **Array Parsing:**
- Counts match actual array lengths
- No empty strings in parsed results
- All 4 array types processed correctly

✅ **Explosions:**
- Explosion ratio 40-50:1 (expected ~46:1)
- All claim types present
- No NULL claim_text values

✅ **Position Tracking:**
- Specialty positions start at 1
- Positions increment sequentially
- POSEXPLODE working correctly

✅ **District Aggregations:**
- Percentile rankings distributed across 0-1
- District capacity tiers balanced
- Window functions computing correctly

---

## Next Steps

After completing Silver layer:
1. **Proceed to Gold Layer** - See `2025-01-15-facility-validation-gold-layer.md`
2. **Update NFHS column references** - Adjust to actual schema
3. **Monitor explosion ratios** - Track for data drift

---

## Troubleshooting

### Low Explosion Ratio

**Symptom:** Explosion ratio <30:1

**Root Cause:** Facilities have fewer claims than expected

**Investigation:**
```sql
-- Check claim distribution
SELECT 
  total_capability_claims,
  COUNT(*) as facility_count
FROM silver.facilities_capabilities_parsed
GROUP BY total_capability_claims
ORDER BY total_capability_claims DESC;
```

**Action:** Review if raw data quality has changed

### High NULL Claim Counts

**Symptom:** Many NULL values in exploded table

**Root Cause:** Array parsing failing silently

**Investigation:**
```sql
-- Test array parsing on raw data
SELECT 
  specialties,
  REGEXP_REPLACE(REGEXP_REPLACE(specialties, '[\\[\\]"]', ''), ',\\s*', '|') as cleaned,
  SPLIT(REGEXP_REPLACE(REGEXP_REPLACE(specialties, '[\\[\\]"]', ''), ',\\s*', '|'), '\\|') as split_result
FROM bronze.facilities_clean
WHERE specialties IS NOT NULL
LIMIT 10;
```

**Action:** Adjust REGEXP patterns based on actual array format

### NFHS Column Not Found

**Symptom:** Column not found error in district_outcome_baselines

**Root Cause:** NFHS column names don't match placeholders

**Fix:**
1. Run: `DESCRIBE TABLE bronze.district_health_indicators_clean`
2. Identify actual column names for maternal/immunization/nutrition indicators
3. Update TRY_CAST references in district_outcome_baselines
4. Re-run pipeline validation

---

## Execution Handoff

**Silver Layer Plan Complete!**

**Two execution options:**

**1. Subagent-Driven (recommended)** - Fresh subagent per task, review between tasks, fast iteration

**2. Inline Execution** - Execute tasks in this session with checkpoints

**Which approach?**
