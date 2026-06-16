# Lakebase Integration Summary

## ✅ Completed

### 1. Infrastructure Prerequisites
- ✓ Change Data Feed enabled on `dais2026.dev_validation.integrated_facility_assessment`
- ✓ Lakebase project exists: `projects/dais2026`
- ✓ App scaffolded and deployed

### 2. App Code Updates
- ✓ Created `lakebase_store.py` - Production store with Postgres queries
- ✓ Updated `store.py` - Added `create_store()` factory (demo vs production)
- ✓ Updated `app.py` - Uses factory, shows real facility stats
- ✓ Updated `01_Volunteer_Portal.py` - Real facility search and validation
- ✓ Updated `02_Patient_Search.py` - Geospatial queries from Lakebase
- ✓ Updated `requirements.txt` - Added psycopg3 and databricks-sdk
- ✓ Updated `app.yaml` - Added database resource, set HEALTHVERIFY_MODE=production

## ⏳ Remaining Steps (Run in Terminal)

### Step 1: Register Lakebase Catalog (1 min)
```bash
databricks postgres create-catalog healthverify_lakebase \
  --json '{
    "spec": {
      "postgres_database": "databricks_postgres",
      "branch": "projects/dais2026/branches/production"
    }
  }'
```

### Step 2: Create Synced Table (5-10 mins)
```bash
databricks postgres create-synced-table healthverify_lakebase.public.facilities \
  --json '{
    "spec": {
      "source_table_full_name": "dais2026.dev_validation.integrated_facility_assessment",
      "primary_key_columns": ["unique_id"],
      "scheduling_policy": "TRIGGERED",
      "branch": "projects/dais2026/branches/production",
      "postgres_database": "databricks_postgres",
      "create_database_objects_if_missing": true,
      "new_pipeline_spec": {
        "storage_catalog": "dais2026",
        "storage_schema": "default"
      }
    }
  }'
```

### Step 3: Check Sync Status
```bash
databricks postgres get-synced-table "synced_tables/healthverify_lakebase.public.facilities"
```

Wait for `state: ONLINE` before proceeding.

### Step 4: Grant App Permissions
Get app Service Principal ID:
```bash
databricks apps get healthverify-india --output JSON | grep service_principal_client_id
```

Connect to Lakebase and grant permissions:
```sql
-- Connect to Lakebase
databricks postgres connect projects/dais2026/branches/production

-- Grant permissions (replace <SP_ID> with actual client ID)
GRANT USAGE ON SCHEMA public TO "<SP_ID>";
GRANT SELECT ON public.facilities TO "<SP_ID>";
GRANT INSERT, UPDATE, SELECT ON public.volunteer_validations TO "<SP_ID>";
```

### Step 5: Deploy App
```bash
cd /Workspace/Users/richthai92@gmail.com/DAIS-2026-AI-for-Good/phase-2-app
databricks apps deploy healthverify-india
```

### Step 6: Test
Visit: https://healthverify-india-3764736117518957.aws.databricksapps.com

Expected behavior:
- ✓ Home page shows top facility with real trust score
- ✓ Volunteer Portal lists 10K+ facilities
- ✓ Patient Search returns geospatial results
- ✓ Validations persist to Postgres
- ✓ Trust scores update in real-time

## Architecture

```
Pipeline (Batch)
  └── Gold: dais2026.dev_validation.integrated_facility_assessment
       │ (10,712 facilities with trust scores)
       ↓
  [Lakebase Synced Table] Triggered Mode
       ↓
Lakebase Postgres: healthverify_lakebase.public.facilities
       ↓
  [App Queries via psycopg3]
       ↓
Streamlit App: healthverify-india
  - Volunteer Portal: Validate facilities
  - Patient Search: Find care by location
  - Validations: Written to public.volunteer_validations
```

## Files Modified

* `phase-2-app/phase_2_app/lakebase_store.py` (new)
* `phase-2-app/phase_2_app/store.py` (updated)
* `phase-2-app/app.py` (updated)
* `phase-2-app/pages/01_Volunteer_Portal.py` (updated)
* `phase-2-app/pages/02_Patient_Search.py` (updated)
* `phase-2-app/requirements.txt` (updated)
* `phase-2-app/app.yaml` (updated)
* `lakebase-setup.sh` (new - automated setup script)

## Quick Start

```bash
cd ~/DAIS-2026-AI-for-Good
chmod +x lakebase-setup.sh
./lakebase-setup.sh
```

This script automates steps 1-3 and provides instructions for steps 4-6.
