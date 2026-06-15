# Virtue Foundation Dataset - Data Quality Addendum

**Critical Finding**: STRING columns contain brackets representing negative/suppressed values  
**Date**: June 15, 2026  
**Status**: 🚨 REQUIRES IMMEDIATE ATTENTION  
**Impact**: Medium (4% of districts, secondary metrics only)

---

## Executive Summary

A critical data quality issue has been identified in the NFHS-5 district health indicators table: **Several STRING-type columns contain numeric data with parentheses/brackets indicating negative or statistically suppressed values**.

### The Pattern
- `(92.6)` should be interpreted as **-92.6** (or suppressed/unreliable)
- `123.4 ` (with trailing space) should be **123.4**
- `*` indicates missing/suppressed data

### Quick Facts
- **28 districts affected** (4% of 706 total)
- **3 primary columns** with bracket patterns
- **Main dashboard metrics are SAFE** (use DOUBLE-type columns)
- **Risk**: Extended analysis using STRING columns will produce incorrect results

---

## Affected Columns Analysis

### Prevalence by Column

| Column Name | Total Rows | Bracket Count | Asterisk | % Affected |
|-------------|------------|---------------|----------|------------|
| `deaths_in_the_last_3_years_civil_reg_pct` | 706 | 27 | 1 | 3.8% |
| `all_w15_19_who_are_anaemic_pct` | 706 | 3 | 0 | 0.4% |
| `sex_ratio_at_birth_5y_f_per_1000_m` | 706 | 2 | 0 | 0.3% |

### Sample Affected Districts

| District | State | Sex Ratio | Death Reg % | Teen Anemia % |
|----------|-------|-----------|-------------|---------------|
| Bhopal | Madhya Pradesh | **(1261)** | **(88.1)** | **(54.6)** |
| Jabalpur | Madhya Pradesh | **(1111)** | **\*** | **(49.0)** |
| Mumbai Suburban | Maharashtra | 703 | **(92.7)** | **(67.2)** |
| North Andaman | Andaman & Nicobar | 844 | **(92.6)** | 47.8 |
| Kamrup Metropolitan | Assam | 986 | **(77.4)** | 80.6 |

---

## What Brackets Likely Mean

### NFHS Survey Convention

In official NFHS (National Family Health Survey) data, parentheses around numbers typically indicate:

1. **Small Sample Size**: Estimate based on <25 unweighted cases
2. **Statistical Unreliability**: Wide confidence intervals, high standard error
3. **Data Suppression**: Below threshold for reliable reporting
4. **NOT Literal Negatives**: Percentages/ratios cannot actually be negative

### Interpretation Guidance

**For analysts**:
- Treat bracketed values as **"unreliable estimate"** flags
- Consider excluding from aggregations (or flag in visualizations)
- Do NOT interpret as negative numbers in mathematical sense

**For applications**:
- Show warning: "⚠️ Estimate based on small sample (unreliable)"
- Gray out or mark with uncertainty indicator
- Exclude from state/national averages (or footnote)

### Example: Death Registration Rate

`deaths_in_the_last_3_years_civil_reg_pct = "(92.6)"`

**Incorrect interpretation**: -92.6% (nonsensical - can't register negative deaths)  
**Correct interpretation**: 92.6% estimate, but **unreliable due to small sample**

The district likely had very few deaths recorded in the survey period, making the percentage estimate statistically unstable.

---

## Impact on Current Dashboard

### ✅ GOOD NEWS: Main Metrics Are Safe

The **Virtue Foundation Healthcare Analysis** dashboard uses these columns:
- `institutional_birth_5y_pct` (DOUBLE type) ✅
- `all_w15_49_who_are_anaemic_pct` (DOUBLE type) ✅
- `hh_electricity_pct` (DOUBLE type) ✅
- `hh_use_improved_sanitation_pct` (DOUBLE type) ✅
- `households_using_clean_fuel_for_cooking_pct` (DOUBLE type) ✅

**Result**: All current dashboard calculations are correct. The bracket issue affects **STRING-type columns NOT used in the dashboard**.

### ⚠️ RISK: Future Analysis Extensions

**If analysts extend the dashboard** to include:
- Teen anemia rates (ages 15-19): `all_w15_19_who_are_anaemic_pct`
- Death registration rates: `deaths_in_the_last_3_years_civil_reg_pct`
- Sex ratio at birth: `sex_ratio_at_birth_5y_f_per_1000_m`
- Child vaccination rates (many STRING columns)
- Child nutrition indicators (stunting, wasting)

They will encounter **incorrect values** without proper parsing.

---

## Full List of STRING Columns (50+ Potential Issues)

### Columns Requiring Parsing

The NFHS-5 table has **50+ STRING-type columns** that likely follow the bracket convention:

**Child Health** (11 columns):
- `child_5y_who_attended_pre_primary_school_during_the_school_pct`
- `child_u5_who_are_stunted_height_for_age_18_pct`
- `child_u5_who_are_wasted_weight_for_height_18_pct`
- `child_u5_who_are_severe_wasted_weight_for_height_19_pct`
- `child_u5_who_are_underweight_weight_for_age_18_pct`
- `child_u5_who_are_overweight_weight_for_height_20_pct`
- `child_6_59m_who_are_anaemic_lt_11_0_g_dl_22_pct`
- `children_born_at_home_who_were_taken_to_a_health_facility_f_pct`
- And 3 more...

**Maternal Health** (9 columns):
- `mothers_who_had_an_anc_visit_in_the_first_trimester_lb5y_pct`
- `mothers_who_had_at_least_4_anc_visits_lb5y_pct`
- `mothers_whose_last_birth_was_protected_against_neo_tetanus_pct`
- `mothers_who_consumed_ifa_for_100_days_or_more_when_they_wer_pct`
- And 5 more...

**Vaccination** (13 columns):
- `child_12_23m_fully_vaccinated_based_on_information_from_eit_pct`
- `child_12_23m_who_have_received_bcg_pct`
- `child_12_23m_who_have_received_3_doses_of_polio_vaccine_pct`
- And 10 more...

**Nutrition & Feeding** (9 columns):
- `children_under_age_3_years_breastfed_within_one_hour_of_bir_pct`
- `child_u6m_exclusively_breastfed_pct`
- `breastfeeding_child_6_23m_receiving_an_adequate_diet16_17_pct`
- And 6 more...

**Other** (8+ columns):
- `w20_24_married_before_age_18_years_pct`
- `births_in_the_5_years_preceding_the_survey_that_are_birth_3_pct`
- `w15_19_who_were_already_mothers_or_pregnant_at_the_time_of_pct`
- And 5 more...

**Total**: At least **50 STRING columns** across 109 total columns in the table.

---

## SQL Parsing Function

### Handle Brackets, Asterisks, and Trailing Spaces

```sql
-- Universal parsing function for STRING-to-numeric conversion
CASE 
  -- Pattern 1: (123.4) = -123.4 or suppressed
  WHEN TRIM(column_name) RLIKE '^\\([0-9.]+\\)$' THEN 
    -CAST(REGEXP_REPLACE(TRIM(column_name), '[()]', '') AS DOUBLE)
  
  -- Pattern 2: 123.4 (with or without spaces) = 123.4
  WHEN TRIM(column_name) RLIKE '^[0-9.]+$' THEN 
    CAST(TRIM(column_name) AS DOUBLE)
  
  -- Pattern 3: * or other non-numeric = NULL
  ELSE NULL
END AS parsed_column_name
```

### Alternative: Flag Instead of Negate

If brackets indicate "unreliable" rather than "negative":

```sql
-- Parse value and create reliability flag
CASE 
  WHEN TRIM(column_name) RLIKE '^\\([0-9.]+\\)$' THEN 
    CAST(REGEXP_REPLACE(TRIM(column_name), '[()]', '') AS DOUBLE)
  WHEN TRIM(column_name) RLIKE '^[0-9.]+$' THEN 
    CAST(TRIM(column_name) AS DOUBLE)
  ELSE NULL
END AS parsed_value,

CASE 
  WHEN TRIM(column_name) RLIKE '^\\([0-9.]+\\)$' THEN TRUE
  ELSE FALSE
END AS is_unreliable_estimate
```

---

## Cleaned Dataset Creation

### Step 1: Create Cleaned View with All STRING Columns Parsed

```sql
CREATE OR REPLACE VIEW databricks_virtue_foundation_dataset_dais_2026.virtue_foundation_dataset.nfhs_5_district_health_indicators_cleaned AS
SELECT 
  -- Keep original string columns
  district_name,
  state_ut,
  
  -- Keep DOUBLE columns as-is
  households_surveyed,
  women_15_49_interviewed,
  institutional_birth_5y_pct,
  all_w15_49_who_are_anaemic_pct,
  hh_electricity_pct,
  -- ... all other DOUBLE columns ...
  
  -- Parse STRING columns with reliability flags
  CASE 
    WHEN TRIM(sex_ratio_at_birth_5y_f_per_1000_m) RLIKE '^\\([0-9.]+\\)$' THEN 
      CAST(REGEXP_REPLACE(TRIM(sex_ratio_at_birth_5y_f_per_1000_m), '[()]', '') AS DOUBLE)
    WHEN TRIM(sex_ratio_at_birth_5y_f_per_1000_m) RLIKE '^[0-9.]+$' THEN 
      CAST(TRIM(sex_ratio_at_birth_5y_f_per_1000_m) AS DOUBLE)
    ELSE NULL
  END AS sex_ratio_at_birth_5y_f_per_1000_m_cleaned,
  
  CASE 
    WHEN TRIM(sex_ratio_at_birth_5y_f_per_1000_m) RLIKE '^\\([0-9.]+\\)$' THEN TRUE
    ELSE FALSE
  END AS sex_ratio_at_birth_5y_unreliable,
  
  -- Repeat for all 50+ STRING columns...
  
FROM databricks_virtue_foundation_dataset_dais_2026.virtue_foundation_dataset.nfhs_5_district_health_indicators;
```

### Step 2: Create Aggregation-Ready Table (Exclude Unreliable)

```sql
CREATE OR REPLACE TABLE databricks_virtue_foundation_dataset_dais_2026.virtue_foundation_dataset.nfhs_5_aggregation_ready AS
SELECT 
  district_name,
  state_ut,
  
  -- Include value only if reliable
  CASE 
    WHEN sex_ratio_at_birth_5y_unreliable = FALSE THEN sex_ratio_at_birth_5y_f_per_1000_m_cleaned
    ELSE NULL
  END AS sex_ratio_at_birth_5y_f_per_1000_m,
  
  -- Repeat for all parsed columns...
  
FROM databricks_virtue_foundation_dataset_dais_2026.virtue_foundation_dataset.nfhs_5_district_health_indicators_cleaned;
```

---

## Recommendations

### Immediate Actions

1. **✅ No action required for current dashboard** - metrics are safe
2. **Document this issue** in all data dictionaries and handoff materials
3. **Create cleaned view** with parsed columns before extending analysis
4. **Add data quality checks** to ETL pipelines

### For Hackathon Teams

**If building apps using STRING columns**:

1. **Identify affected columns**: Check column type with `DESCRIBE TABLE`
2. **Apply parsing logic**: Use the SQL CASE statement above
3. **Communicate uncertainty**: Show "⚠️ Unreliable estimate" for bracketed values
4. **Exclude from aggregations**: Or weight differently in calculations
5. **Test edge cases**: Handle `*`, `na`, `(value)`, and trailing spaces

### For Data Engineering

**Best practice for production pipelines**:

```python
# PySpark example
from pyspark.sql import functions as F

def parse_nfhs_string_column(col_name):
    """Parse NFHS STRING columns handling brackets and asterisks."""
    return (
        F.when(
            F.trim(F.col(col_name)).rlike(r'^\([0-9.]+\)$'),
            F.regexp_replace(F.trim(F.col(col_name)), r'[()]', '').cast('double')
        )
        .when(
            F.trim(F.col(col_name)).rlike(r'^[0-9.]+$'),
            F.trim(F.col(col_name)).cast('double')
        )
        .otherwise(None)
    )

# Apply to all STRING columns
df_cleaned = (
    df.withColumn('sex_ratio_cleaned', parse_nfhs_string_column('sex_ratio_at_birth_5y_f_per_1000_m'))
      .withColumn('sex_ratio_unreliable', F.trim(F.col('sex_ratio_at_birth_5y_f_per_1000_m')).rlike(r'^\([0-9.]+\)$'))
)
```

---

## Testing & Validation

### Test Cases for Parsing Function

| Input | Expected Output | Reliability Flag |
|-------|-----------------|------------------|
| `"(92.6)"` | 92.6 | TRUE (unreliable) |
| `"123.4 "` | 123.4 | FALSE (reliable) |
| `"*"` | NULL | N/A |
| `"na"` | NULL | N/A |
| `"(1261)"` | 1261 | TRUE (unreliable) |
| `NULL` | NULL | N/A |

### Validation Query

```sql
-- Test parsing on sample data
WITH test_data AS (
  SELECT '(92.6)' as test_val UNION ALL
  SELECT '123.4 ' UNION ALL
  SELECT '*' UNION ALL
  SELECT '(1261)'
)
SELECT 
  test_val,
  CASE 
    WHEN TRIM(test_val) RLIKE '^\\([0-9.]+\\)$' THEN 
      CAST(REGEXP_REPLACE(TRIM(test_val), '[()]', '') AS DOUBLE)
    WHEN TRIM(test_val) RLIKE '^[0-9.]+$' THEN 
      CAST(TRIM(test_val) AS DOUBLE)
    ELSE NULL
  END AS parsed_value,
  CASE 
    WHEN TRIM(test_val) RLIKE '^\\([0-9.]+\\)$' THEN TRUE
    ELSE FALSE
  END AS is_unreliable
FROM test_data;
```

Expected output:
```
test_val | parsed_value | is_unreliable
---------|--------------|---------------
(92.6)   | 92.6         | true
123.4    | 123.4        | false
*        | NULL         | false
(1261)   | 1261         | true
```

---

## References & Context

### Related Documents
- **Main EDA**: `/Workspace/Users/richthai92@gmail.com/DAIS-2026-AI-for-Good/virtue_foundation_eda_handoff.md`
- **Dashboard**: Virtue Foundation Healthcare Analysis (Lakeview)
- **Source Table**: `databricks_virtue_foundation_dataset_dais_2026.virtue_foundation_dataset.nfhs_5_district_health_indicators`

### NFHS-5 Survey Documentation
- Official website: [http://rchiips.org/nfhs/](http://rchiips.org/nfhs/)
- District factsheets: [http://rchiips.org/nfhs/districtfactsheet_NFHS-5.shtml](http://rchiips.org/nfhs/districtfactsheet_NFHS-5.shtml)
- Technical documentation explains bracket notation conventions

### Contact
For questions about this data quality issue, reference:
- Ticket ID: DQ-2026-BRACKETS
- Finding date: June 15, 2026
- Analyst: AI Agent (Genie Code)

---

## Change Log

**v1.0 - June 15, 2026**
- Initial discovery of bracket pattern in STRING columns
- Identified 28 affected districts across 3 primary columns
- Confirmed current dashboard is not affected
- Documented parsing logic and recommendations

---

*This is a living document. Update as new patterns are discovered or parsing logic is refined.*
