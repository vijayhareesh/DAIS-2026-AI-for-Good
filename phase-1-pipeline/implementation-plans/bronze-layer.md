# Bronze Layer Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create type-validated Bronze tables with geographic constraints and parsed numeric fields

**Architecture:** Three materialized views cleaning raw data with quality constraints

**Tech Stack:** Lakeflow Spark Declarative Pipelines (SQL), Serverless compute

---

## File Structure

**Pipeline Notebook:**
- Modify: `/Workspace/Users/richthai92@gmail.com/DAIS-2026-AI-for-Good/facility_validation_framework` (pipeline notebook)

**Tables Created:**
1. `bronze.facilities_clean`
2. `bronze.pincode_directory_clean`
3. `bronze.district_health_indicators_clean`

---

## Task 1: Create Bronze Facilities Table

**Files:**
- Modify: `/Workspace/Users/richthai92@gmail.com/DAIS-2026-AI-for-Good/facility_validation_framework`

- [ ] **Step 1: Add facilities_clean table definition**

```sql
-- ============================================================================
-- BRONZE LAYER: Clean validated copies with basic quality checks
-- ============================================================================

-- -----------------------------------------------------------------------------
-- 1. facilities_clean
-- Validated facilities with type casting and geographic constraints
-- -----------------------------------------------------------------------------
CREATE OR REFRESH MATERIALIZED VIEW bronze.facilities_clean (
  CONSTRAINT valid_latitude EXPECT (latitude IS NULL OR (latitude BETWEEN -90 AND 90)) ON VIOLATION DROP ROW,
  CONSTRAINT valid_longitude EXPECT (longitude IS NULL OR (longitude BETWEEN -180 AND 180)) ON VIOLATION DROP ROW,
  CONSTRAINT state_not_null EXPECT (address_stateOrRegion IS NOT NULL) ON VIOLATION DROP ROW,
  CONSTRAINT unique_id_not_null EXPECT (unique_id IS NOT NULL) ON VIOLATION FAIL UPDATE
)
COMMENT "Bronze: Validated facilities with parsed numeric fields and geographic constraints"
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
  
  -- Parse numeric fields with TRY_CAST (nulls on failure)
  TRY_CAST(yearEstablished AS INT) as yearEstablished,
  acceptsVolunteers,
  facebookLink,
  
  -- Address fields
  address_line1,
  address_line2,
  address_line3,
  address_city,
  address_stateOrRegion,
  address_zipOrPostcode,
  address_country,
  address_countryCode,
  countries,
  
  -- Type identifiers
  facilityTypeId,
  operatorTypeId,
  affiliationTypeIds,
  
  -- Descriptive fields
  description,
  area,
  
  -- Capacity metrics (parsed to INT)
  TRY_CAST(numberDoctors AS INT) as numberDoctors,
  TRY_CAST(capacity AS INT) as capacity,
  
  -- Capability arrays (kept as JSON strings, will parse in Silver)
  specialties,
  procedure,
  equipment,
  capability,
  
  -- Temporal field
  recency_of_page_update,
  
  -- Social media metrics (parsed to INT)
  TRY_CAST(distinct_social_media_presence_count AS INT) as distinct_social_media_presence_count,
  affiliated_staff_presence,
  custom_logo_presence,
  TRY_CAST(number_of_facts_about_the_organization AS INT) as number_of_facts_about_the_organization,
  
  -- Post metrics
  post_metrics_most_recent_social_media_post_date,
  TRY_CAST(post_metrics_post_count AS INT) as post_metrics_post_count,
  
  -- Engagement metrics (parsed to INT)
  TRY_CAST(engagement_metrics_n_followers AS INT) as engagement_metrics_n_followers,
  TRY_CAST(engagement_metrics_n_likes AS INT) as engagement_metrics_n_likes,
  TRY_CAST(engagement_metrics_n_engagements AS INT) as engagement_metrics_n_engagements,
  
  source,
  coordinates,
  latitude,
  longitude,
  cluster_id,
  source_urls,
  
  -- Metadata
  CURRENT_TIMESTAMP() as bronze_processed_at
FROM dais2026.raw.facilities;
```

- [ ] **Step 2: Validate table syntax**

Navigate to pipeline editor and verify:
- Syntax highlighting shows no errors
- All column names match raw.facilities schema
- Constraints are properly formatted

Expected: No syntax errors

- [ ] **Step 3: Document expected constraints**

Add comment block above table:

```sql
-- Expected constraint violations per 10K facilities:
-- - valid_latitude DROP ROW: ~50 rows (0.5%) - invalid coordinates
-- - valid_longitude DROP ROW: ~50 rows (0.5%) - invalid coordinates  
-- - state_not_null DROP ROW: ~20 rows (0.2%) - missing state
-- - unique_id_not_null FAIL UPDATE: 0 rows (critical integrity check)
```

- [ ] **Step 4: Commit Bronze facilities table**

```bash
cd /Workspace/Users/richthai92@gmail.com/DAIS-2026-AI-for-Good
git add facility_validation_framework
git commit -m "feat(bronze): add facilities_clean table with geographic constraints"
```

---

## Task 2: Create Bronze Pincode Directory Table

**Files:**
- Modify: `/Workspace/Users/richthai92@gmail.com/DAIS-2026-AI-for-Good/facility_validation_framework`

- [ ] **Step 1: Add pincode_directory_clean table definition**

```sql
-- -----------------------------------------------------------------------------
-- 2. pincode_directory_clean
-- India Post pincode data with state name normalization
-- -----------------------------------------------------------------------------
CREATE OR REFRESH MATERIALIZED VIEW bronze.pincode_directory_clean (
  CONSTRAINT pincode_not_null EXPECT (pincode IS NOT NULL) ON VIOLATION DROP ROW,
  CONSTRAINT state_not_null EXPECT (statename IS NOT NULL) ON VIOLATION DROP ROW
)
COMMENT "Bronze: India Post Pincode Directory with normalized state/district names"
CLUSTER BY (statename, district)
AS
SELECT 
  circlename,
  regionname,
  divisionname,
  officename,
  pincode,
  officetype,
  delivery,
  
  -- Normalize state and district names for joining
  TRIM(UPPER(statename)) as statename,
  TRIM(UPPER(district)) as district,
  
  -- Metadata
  CURRENT_TIMESTAMP() as bronze_processed_at
FROM dais2026.raw.india_post_pincode_directory;
```

- [ ] **Step 2: Validate normalization logic**

Add comment explaining normalization:

```sql
-- Geographic normalization strategy:
-- - TRIM: Remove leading/trailing whitespace
-- - UPPER: Standardize case for case-insensitive joins
-- Purpose: Enable reliable joins between facilities (mixed case) and pincode directory
```

Expected: Comment added successfully

- [ ] **Step 3: Document expected pass-through**

Add comment:

```sql
-- Expected pass-through rate: >99.9%
-- Violations: ~10 rows with null pincode/state (data quality issues)
```

- [ ] **Step 4: Commit pincode directory table**

```bash
cd /Workspace/Users/richthai92@gmail.com/DAIS-2026-AI-for-Good
git add facility_validation_framework
git commit -m "feat(bronze): add pincode_directory_clean with normalized geographies"
```

---

## Task 3: Create Bronze District Health Indicators Table

**Files:**
- Modify: `/Workspace/Users/richthai92@gmail.com/DAIS-2026-AI-for-Good/facility_validation_framework`

- [ ] **Step 1: Add district_health_indicators_clean table definition**

```sql
-- -----------------------------------------------------------------------------
-- 3. district_health_indicators_clean
-- NFHS-5 district health data with normalized location names
-- -----------------------------------------------------------------------------
CREATE OR REFRESH MATERIALIZED VIEW bronze.district_health_indicators_clean (
  CONSTRAINT state_not_null EXPECT (State IS NOT NULL) ON VIOLATION DROP ROW,
  CONSTRAINT district_not_null EXPECT (District IS NOT NULL) ON VIOLATION DROP ROW
)
COMMENT "Bronze: NFHS-5 district health indicators with normalized state/district names"
CLUSTER BY (state_normalized, district_normalized)
AS
SELECT 
  -- Normalize state and district for joining
  TRIM(UPPER(State)) as state_normalized,
  TRIM(UPPER(District)) as district_normalized,
  
  -- Original values for reference
  State as state_original,
  District as district_original,
  
  -- Health indicators (all columns from raw table)
  *,
  
  -- Metadata
  CURRENT_TIMESTAMP() as bronze_processed_at
FROM dais2026.raw.nfhs_5_district_health_indicators;
```

- [ ] **Step 2: Add NFHS column discovery note**

Add comment:

```sql
-- NOTE: This table uses SELECT * to preserve all NFHS-5 indicator columns
-- Column names will need verification against actual schema during Silver layer development
-- Common indicators: maternal health (%), immunization (%), nutrition (%)
-- Action required: Update Silver layer to reference actual column names
```

Expected: Note added for downstream tasks

- [ ] **Step 3: Validate dual geography approach**

Add comment explaining why we keep both normalized and original:

```sql
-- Geographic handling:
-- - state_normalized/district_normalized: For joins (UPPER + TRIM)
-- - state_original/district_original: For human-readable output
-- This allows reliable joins while preserving original formatting for reports
```

- [ ] **Step 4: Commit district health indicators table**

```bash
cd /Workspace/Users/richthai92@gmail.com/DAIS-2026-AI-for-Good
git add facility_validation_framework
git commit -m "feat(bronze): add district_health_indicators_clean with dual geographies"
```

---

## Task 4: Add Bronze Layer Documentation Header

**Files:**
- Modify: `/Workspace/Users/richthai92@gmail.com/DAIS-2026-AI-for-Good/facility_validation_framework`

- [ ] **Step 1: Add Bronze layer header at top of file**

```sql
-- ============================================================================
-- FACILITY VALIDATION FRAMEWORK
-- Lakeflow Spark Declarative Pipeline (SQL, Serverless)
-- ============================================================================
--
-- Architecture: Medallion (Bronze → Silver → Gold)
-- 
-- Bronze Layer: Type-validated copies with geographic constraints
-- Silver Layer: Parse arrays, explode claims, aggregate outcomes
-- Gold Layer: Multi-dimensional validation scoring
--
-- Source Data:
--   - dais2026.raw.facilities (~10K facilities)
--   - dais2026.raw.india_post_pincode_directory (~165K pincodes)
--   - dais2026.raw.nfhs_5_district_health_indicators (~750 districts)
--
-- Target Schemas:
--   - bronze.* (validated copies)
--   - silver.* (transformed data)
--   - validation.* (scored outputs)
-- ============================================================================
```

- [ ] **Step 2: Verify header placement**

Expected: Header appears at the very top of the notebook, before any CREATE statements

- [ ] **Step 3: Commit documentation header**

```bash
cd /Workspace/Users/richthai92@gmail.com/DAIS-2026-AI-for-Good
git add facility_validation_framework
git commit -m "docs(bronze): add pipeline documentation header"
```

---

## Task 5: Validate Bronze Layer Schema References

**Files:**
- Read: `dais2026.raw.facilities` (via Data Explorer or query)
- Read: `dais2026.raw.india_post_pincode_directory`
- Read: `dais2026.raw.nfhs_5_district_health_indicators`

- [ ] **Step 1: Query facilities table schema**

```sql
DESCRIBE TABLE dais2026.raw.facilities;
```

Expected: Column list matching Bronze SELECT statement

- [ ] **Step 2: Verify critical columns exist**

Check that these columns are present:
- `unique_id`
- `address_stateOrRegion`
- `latitude`, `longitude`
- `specialties`, `procedure`, `equipment`, `capability`
- `engagement_metrics_n_followers`
- `recency_of_page_update`

Expected: All critical columns exist

- [ ] **Step 3: Query pincode directory schema**

```sql
DESCRIBE TABLE dais2026.raw.india_post_pincode_directory;
```

Expected: Columns include `pincode`, `statename`, `district`

- [ ] **Step 4: Query NFHS table schema**

```sql
DESCRIBE TABLE dais2026.raw.nfhs_5_district_health_indicators;
```

Expected: Columns include `State`, `District`, plus numeric health indicators

- [ ] **Step 5: Document schema validation results**

Create note in pipeline:

```sql
-- Schema Validation Results (completed YYYY-MM-DD):
-- ✅ facilities: All 50+ columns verified
-- ✅ pincode_directory: Geographic columns present
-- ✅ nfhs_5: Health indicator columns identified (see Silver layer plan for exact names)
```

- [ ] **Step 6: Commit schema validation notes**

```bash
cd /Workspace/Users/richthai92@gmail.com/DAIS-2026-AI-for-Good
git add facility_validation_framework
git commit -m "docs(bronze): add schema validation notes"
```

---

## Task 6: Test Bronze Layer with Pipeline Validation

**Files:**
- Pipeline: `facility_validation_framework`

- [ ] **Step 1: Navigate to pipeline editor**

URL: `/editor/pipelines/27fea50d-7b95-4540-b673-a0c8c92fe08d`

Expected: Pipeline editor loads with Bronze layer code visible

- [ ] **Step 2: Run pipeline validation (syntax check)**

Click "Validate" button in pipeline editor

Expected: 
- No syntax errors
- All table dependencies resolved
- Constraints properly formatted

- [ ] **Step 3: Review validation results**

Check for:
- ✅ All CREATE statements valid
- ✅ No missing column references
- ✅ Constraint syntax correct
- ✅ CLUSTER BY columns exist

Expected: All checks pass

- [ ] **Step 4: Document validation status**

If validation passes, add to commit message:
```bash
git commit -m "test(bronze): pipeline validation passed - all tables valid"
```

If validation fails, document errors and fix before proceeding to Silver layer

---

## Task 7: Initial Bronze Layer Run (Dry Run)

**Files:**
- Pipeline: `facility_validation_framework`

- [ ] **Step 1: Start pipeline in development mode**

Click "Start" in pipeline editor with development mode enabled

Expected: Pipeline begins refresh of Bronze tables

- [ ] **Step 2: Monitor constraint violations**

Watch for constraint violation metrics:
- `valid_latitude DROP ROW`
- `valid_longitude DROP ROW`
- `state_not_null DROP ROW`
- `unique_id_not_null FAIL UPDATE` (should be zero)

Expected: Violations match predicted rates (<1%)

- [ ] **Step 3: Verify row counts**

```sql
-- Check Bronze table counts
SELECT 'facilities_clean' as table_name, COUNT(*) as row_count FROM bronze.facilities_clean
UNION ALL
SELECT 'pincode_directory_clean', COUNT(*) FROM bronze.pincode_directory_clean
UNION ALL
SELECT 'district_health_indicators_clean', COUNT(*) FROM bronze.district_health_indicators_clean;
```

Expected:
- facilities_clean: ~9,900-9,980 rows (after constraint drops)
- pincode_directory_clean: ~165,000 rows
- district_health_indicators_clean: ~750 rows

- [ ] **Step 4: Sample Bronze data quality**

```sql
-- Sample facilities_clean for data quality checks
SELECT 
  unique_id,
  name,
  address_stateOrRegion as state,
  address_city as city,
  latitude,
  longitude,
  numberDoctors,
  capacity,
  yearEstablished,
  engagement_metrics_n_followers,
  recency_of_page_update
FROM bronze.facilities_clean
LIMIT 100;
```

Expected: 
- All coordinates within valid ranges
- Numeric fields properly cast (or NULL)
- No null unique_ids or states

- [ ] **Step 5: Document initial run results**

Create validation report:

```markdown
## Bronze Layer Initial Run Results

**Date:** YYYY-MM-DD
**Duration:** ~X minutes

**Row Counts:**
- facilities_clean: X rows (Y% pass-through)
- pincode_directory_clean: X rows
- district_health_indicators_clean: X rows

**Constraint Violations:**
- valid_latitude: X rows dropped
- valid_longitude: X rows dropped
- state_not_null: X rows dropped
- unique_id_not_null: 0 violations (PASS)

**Data Quality Spot Checks:**
- ✅ Geographic coordinates valid
- ✅ Numeric fields properly cast
- ✅ State normalization working
- ✅ No critical integrity failures

**Status:** READY FOR SILVER LAYER
```

- [ ] **Step 6: Commit validation report**

Save report to:
`/Workspace/Users/richthai92@gmail.com/DAIS-2026-AI-for-Good/docs/bronze-layer-validation-results.md`

```bash
cd /Workspace/Users/richthai92@gmail.com/DAIS-2026-AI-for-Good
git add docs/bronze-layer-validation-results.md
git commit -m "test(bronze): add initial run validation results"
```

---

## Success Criteria

✅ **Schema Validation:**
- All raw table columns verified
- No missing column references
- Constraint syntax valid

✅ **Pipeline Validation:**
- Syntax check passes
- All dependencies resolved
- No validation errors

✅ **Initial Run:**
- All Bronze tables created
- Constraint violations <1%
- Row counts match expectations
- No FAIL UPDATE violations

✅ **Data Quality:**
- Geographic coordinates valid
- Numeric fields properly cast
- State normalization working
- No null critical fields

---

## Next Steps

After completing Bronze layer:
1. **Proceed to Silver Layer** - See `2025-01-15-facility-validation-silver-layer.md`
2. **Monitor Bronze refresh** - Set up alerts for constraint violations
3. **Document anomalies** - Track any unexpected data patterns

---

## Troubleshooting

### High Constraint Violation Rates

**Symptom:** >5% rows dropped by constraints

**Root Cause:** Upstream data quality issues

**Fix:**
```sql
-- Query violation patterns
SELECT 
  CASE 
    WHEN latitude NOT BETWEEN -90 AND 90 THEN 'invalid_latitude'
    WHEN longitude NOT BETWEEN -180 AND 180 THEN 'invalid_longitude'
    WHEN address_stateOrRegion IS NULL THEN 'missing_state'
    ELSE 'valid'
  END as violation_type,
  COUNT(*) as count
FROM dais2026.raw.facilities
GROUP BY 1;
```

**Action:** Review raw data quality, consider relaxing constraints if legitimate data

### FAIL UPDATE Triggered

**Symptom:** Pipeline fails with unique_id_not_null violation

**Root Cause:** Raw facilities table has rows with null unique_id

**Fix:**
```sql
-- Identify null unique_ids
SELECT * 
FROM dais2026.raw.facilities 
WHERE unique_id IS NULL;
```

**Action:** Fix upstream data or change constraint to DROP ROW

### Missing Columns

**Symptom:** Column not found error during validation

**Root Cause:** Schema mismatch with raw table

**Fix:**
- Query raw table schema: `DESCRIBE TABLE dais2026.raw.facilities`
- Update Bronze SELECT to match actual columns
- Remove or rename mismatched columns

---

## Execution Handoff

**Bronze Layer Plan Complete!**

**Two execution options:**

**1. Subagent-Driven (recommended)** - Fresh subagent per task, review between tasks, fast iteration

**2. Inline Execution** - Execute tasks in this session with checkpoints

**Which approach?**
