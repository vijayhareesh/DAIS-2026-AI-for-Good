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
echo "  ✓ Gold table CDF enabled: dais2026.dev_validation.integrated_facility_assessment"
echo "  ✓ App code updated for Lakebase"
echo ""
echo "This script will:"
echo "  1. Register Lakebase database as Unity Catalog"
echo "  2. Create synced table (10,712 facilities)"
echo "  3. Grant app permissions"
echo ""
read -p "Press Enter to continue..."

# Step 1: Register Lakebase as UC Catalog
echo ""
echo "[1/4] Registering Lakebase database as Unity Catalog..."
echo "------------------------------------------------------------------------"

databricks postgres create-catalog healthverify_lakebase \
  --json '{
    "spec": {
      "postgres_database": "databricks_postgres",
      "branch": "projects/dais2026/branches/production"
    }
  }' --output JSON

if [ $? -eq 0 ]; then
    echo "✓ Catalog 'healthverify_lakebase' registered"
else
    echo "⚠ If catalog already exists, this is OK - continuing..."
fi

sleep 2

# Step 2: Create synced table
echo ""
echo "[2/4] Creating synced table for facilities (this may take 5-10 mins)..."
echo "------------------------------------------------------------------------"

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
  }' --output JSON

if [ $? -eq 0 ]; then
    echo "✓ Synced table created - syncing 10,712 facilities from gold layer"
else
    echo "⚠ If table already exists, this is OK - continuing..."
fi

# Step 3: Wait for sync to complete
echo ""
echo "[3/4] Checking sync status..."
echo "------------------------------------------------------------------------"
echo "Waiting for initial sync to complete (this takes 5-10 minutes)..."
echo ""

for i in {1..30}; do
    STATUS=$(databricks postgres get-synced-table "synced_tables/healthverify_lakebase.public.facilities" \
      --output JSON 2>/dev/null | python3 -c "import json,sys; print(json.load(sys.stdin).get('status', {}).get('state', 'UNKNOWN'))" || echo "PENDING")
    
    echo "  [$i/30] Sync status: $STATUS"
    
    if [ "$STATUS" = "ONLINE" ]; then
        echo "✓ Sync completed! Facilities are available in Lakebase"
        break
    fi
    
    if [ $i -eq 30 ]; then
        echo "⚠ Sync still in progress. Check status manually with:"
        echo "  databricks postgres get-synced-table 'synced_tables/healthverify_lakebase.public.facilities'"
    fi
    
    sleep 20
done

# Step 4: Grant permissions
echo ""
echo "[4/4] Setting up app permissions..."
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
    echo "-- Connect to Lakebase Postgres:"
    echo "databricks postgres connect projects/dais2026/branches/production"
    echo ""
    echo "-- Grant SELECT on facilities (synced table):"
    echo "GRANT USAGE ON SCHEMA public TO \"$APP_SP\";"
    echo "GRANT SELECT ON public.facilities TO \"$APP_SP\";"
    echo ""
    echo "-- Grant CRUD on validations (created by app on first run):"
    echo "GRANT INSERT, UPDATE, SELECT ON public.volunteer_validations TO \"$APP_SP\";"
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
echo "  ✓ Query 10,712 real facilities from Lakebase"
echo "  ✓ Show geospatial search results"
echo "  ✓ Persist validation submissions to Postgres"
echo "  ✓ Update trust scores in real-time"
echo ""
