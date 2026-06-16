#!/bin/bash
# HealthVerify India - Lakebase Setup Commands
# Run these commands in your terminal with databricks CLI configured

set -e

echo "========================================================================"
echo "HealthVerify India - Lakebase Integration Setup"
echo "========================================================================"
echo ""
echo "Prerequisites:"
echo "  ✓ Lakebase project: projects/dais2026"
echo "  ✓ Gold table: dais2026.dev_validation.integrated_facility_assessment"
echo "  ✓ App code updated for Lakebase"
echo ""
echo "This script will:"
echo "  1. Register Lakebase database as Unity Catalog"
echo "  2. Create deduped sync source view"
echo "  3. Create synced table (10,019 unique facilities) using SNAPSHOT sync"
echo "  4. Wait for the initial sync"
echo "  5. Grant app permissions"
echo ""
read -p "Press Enter to continue..."

# Step 1: Register Lakebase as UC Catalog
echo ""
echo "[1/5] Registering Lakebase database as Unity Catalog..."
echo "------------------------------------------------------------------------"

if CATALOG_OUTPUT=$(databricks postgres create-catalog healthverify_lakebase \
  --json '{
    "spec": {
      "postgres_database": "databricks_postgres",
      "branch": "projects/dais2026/branches/production"
    }
  }' --output JSON 2>&1); then
    echo "$CATALOG_OUTPUT"
    echo "✓ Catalog 'healthverify_lakebase' registered"
else
    if [[ "$CATALOG_OUTPUT" == *"already exists"* ]]; then
        echo "⚠ Catalog already exists - continuing..."
    else
        echo "$CATALOG_OUTPUT"
        exit 1
    fi
fi

sleep 2

# Step 2: Create deduped sync source view
echo ""
echo "[2/5] Creating deduped UC source view..."
echo "------------------------------------------------------------------------"

databricks experimental aitools tools query "
CREATE OR REPLACE VIEW dais2026.dev_validation.integrated_facility_assessment_deduped AS
SELECT
  replace(unique_id, chr(0), '') AS unique_id,
  replace(facility_name, chr(0), '') AS facility_name,
  replace(state, chr(0), '') AS state,
  replace(city, chr(0), '') AS city,
  replace(pincode, chr(0), '') AS pincode,
  latitude,
  longitude,
  replace(phone_numbers, chr(0), '') AS phone_numbers,
  replace(officialPhone, chr(0), '') AS officialPhone,
  replace(email, chr(0), '') AS email,
  replace(officialWebsite, chr(0), '') AS officialWebsite,
  replace(specialties, chr(0), '') AS specialties,
  replace(capability, chr(0), '') AS capability,
  total_capability_claims,
  final_confidence_score,
  data_quality_score,
  combined_quality_confidence_score,
  replace(overall_reliability, chr(0), '') AS overall_reliability,
  replace(delivery_likelihood, chr(0), '') AS delivery_likelihood,
  replace(confidence_tier, chr(0), '') AS confidence_tier,
  transform(red_flags, x -> replace(x, chr(0), '')) AS red_flags,
  replace(data_quality_status, chr(0), '') AS data_quality_status,
  assessment_generated_at
FROM (
  SELECT
    *,
    ROW_NUMBER() OVER (
      PARTITION BY unique_id
      ORDER BY
        combined_quality_confidence_score DESC NULLS LAST,
        final_confidence_score DESC NULLS LAST,
        data_quality_score DESC NULLS LAST,
        assessment_generated_at DESC NULLS LAST
    ) AS rn
  FROM dais2026.dev_validation.integrated_facility_assessment
)
WHERE rn = 1
" --output JSON

echo "✓ Deduped view ready: dais2026.dev_validation.integrated_facility_assessment_deduped"

# Step 3: Create synced table
echo ""
echo "[3/5] Creating synced table for facilities (this may take 5-10 mins)..."
echo "------------------------------------------------------------------------"
echo "Note: Using SNAPSHOT scheduling (full refresh) instead of TRIGGERED (incremental)"
echo "      to avoid Auto CDF preview channel requirement"
echo ""

if SYNCED_TABLE_OUTPUT=$(databricks postgres create-synced-table healthverify_lakebase.public.facilities \
  --json '{
    "spec": {
      "source_table_full_name": "dais2026.dev_validation.integrated_facility_assessment_deduped",
      "primary_key_columns": ["unique_id"],
      "scheduling_policy": "SNAPSHOT",
      "branch": "projects/dais2026/branches/production",
      "postgres_database": "databricks_postgres",
      "create_database_objects_if_missing": true,
      "new_pipeline_spec": {
        "storage_catalog": "dais2026",
        "storage_schema": "default"
      }
    }
  }' --output JSON 2>&1); then
    echo "$SYNCED_TABLE_OUTPUT"
    if [[ "$SYNCED_TABLE_OUTPUT" == *"FAILED"* ]]; then
        echo "⚠ Synced table resource exists, but sync is currently failed - checking status..."
    else
        echo "✓ Synced table created - syncing 10,019 unique facilities from gold layer"
    fi
else
    if [[ "$SYNCED_TABLE_OUTPUT" == *"already exists"* ]]; then
        echo "⚠ Synced table already exists - continuing..."
    else
        echo "$SYNCED_TABLE_OUTPUT"
        exit 1
    fi
fi

# Step 4: Wait for sync to complete
echo ""
echo "[4/5] Checking sync status..."
echo "------------------------------------------------------------------------"
echo "Waiting for initial sync to complete (this takes 5-10 minutes)..."
echo ""

for i in {1..30}; do
    SYNCED_TABLE_JSON=$(databricks postgres get-synced-table "synced_tables/healthverify_lakebase.public.facilities" \
      --output JSON 2>/dev/null || true)

    if [ -z "$SYNCED_TABLE_JSON" ]; then
        STATUS="PENDING"
        PIPELINE_ID="UNKNOWN"
        STATUS_MESSAGE=""
    else
        STATUS=$(printf "%s" "$SYNCED_TABLE_JSON" | python3 -c "import json,sys; status=json.load(sys.stdin).get('status', {}); print(status.get('state') or status.get('detailed_state') or 'UNKNOWN')")
        PIPELINE_ID=$(printf "%s" "$SYNCED_TABLE_JSON" | python3 -c "import json,sys; print(json.load(sys.stdin).get('status', {}).get('pipeline_id', 'UNKNOWN'))")
        STATUS_MESSAGE=$(printf "%s" "$SYNCED_TABLE_JSON" | python3 -c "import json,sys; print(json.load(sys.stdin).get('status', {}).get('message', ''))")
    fi
    
    echo "  [$i/30] Sync status: $STATUS"
    
    if [[ "$STATUS" == *"ONLINE"* ]]; then
        echo "✓ Sync completed! Facilities are available in Lakebase"
        break
    fi

    if [[ "$STATUS" == *"FAILED"* ]]; then
        if [ -n "$STATUS_MESSAGE" ]; then
            echo "  $STATUS_MESSAGE"
        fi
        echo "✗ Sync failed. Inspect the managed Lakeflow pipeline events with:"
        echo "  databricks pipelines list-pipeline-events $PIPELINE_ID"
        exit 1
    fi
    
    if [ $i -eq 30 ]; then
        echo "⚠ Sync still in progress. Check status manually with:"
        echo "  databricks postgres get-synced-table 'synced_tables/healthverify_lakebase.public.facilities'"
    fi
    
    sleep 20
done

# Step 5: Grant permissions
echo ""
echo "[5/5] Setting up app permissions..."
echo "------------------------------------------------------------------------"

# Get app Service Principal client ID
APP_SP=$(databricks apps get healthverify-india --output JSON 2>/dev/null \
  | python3 -c "import json,sys; print(json.load(sys.stdin).get('service_principal_client_id', 'UNKNOWN'))" || echo "UNKNOWN")

if [ "$APP_SP" = "UNKNOWN" ]; then
    echo "⚠ Could not get app Service Principal ID"
    echo "  Run manually after app is deployed:"
    echo "  1. Get SP ID: databricks apps get healthverify-india"
    echo "  2. Connect to Lakebase and run grants (see below)"
else
    echo "App Service Principal: $APP_SP"
    echo ""
    echo "Run these SQL commands to grant permissions:"
    echo "------------------------------------------------------------------------"
    echo "-- If the app Postgres role does not exist yet, create it first:"
    echo "databricks postgres create-role projects/dais2026/branches/production \\"
    echo "  --role-id app-healthverify-india \\"
    echo "  --json '{\"spec\": {\"identity_type\": \"SERVICE_PRINCIPAL\", \"postgres_role\": \"$APP_SP\", \"auth_method\": \"LAKEBASE_OAUTH_V1\"}}'"
    echo ""
    echo "-- Connect to Lakebase Postgres:"
    echo "databricks psql projects/dais2026/branches/production/endpoints/primary -- -d databricks_postgres"
    echo ""
    echo "-- Grant SELECT on facilities (synced table):"
    echo "GRANT USAGE, CREATE ON SCHEMA public TO \"$APP_SP\";"
    echo "GRANT SELECT ON public.facilities TO \"$APP_SP\";"
    echo "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO \"$APP_SP\";"
    echo ""
    echo "-- Grant CRUD on validations (created by app on first run):"
    echo "GRANT INSERT, UPDATE, DELETE, SELECT ON public.volunteer_validations TO \"$APP_SP\";"
    echo "------------------------------------------------------------------------"
fi

echo ""
echo "========================================================================"
echo "Setup Complete!"
echo "========================================================================"
echo ""
echo "Next steps:"
echo "  1. Grant permissions (see SQL above)"
echo "  2. Deploy app: databricks apps deploy healthverify-india"
echo "  3. Visit: https://healthverify-india-3764736117518957.aws.databricksapps.com"
echo ""
echo "The app will:"
echo "  ✓ Query 10,019 unique real facilities from Lakebase"
echo "  ✓ Show geospatial search results"
echo "  ✓ Persist validation submissions to Postgres"
echo "  ✓ Update trust scores in real-time"
echo ""
