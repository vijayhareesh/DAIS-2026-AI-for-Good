# HealthVerify India Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the HealthVerify India demo system described in `EXECUTION-PROMPT.md`: Lakeflow pipeline source, Databricks App, demo agents, Lakebase schema/sync, DAB deployment assets, and verification evidence.

**Architecture:** The repo will contain deployable source artifacts for a medallion Lakeflow pipeline, a Streamlit Databricks App, deterministic agent helpers for demo reliability, Lakebase/Postgres schema and sync scripts, and a Databricks Asset Bundle that wires those assets to the existing workspace resources. Databricks deployment and runtime verification remain separate gates because they require live workspace access.

**Tech Stack:** Databricks Lakeflow Spark Declarative Pipelines SQL, Databricks Asset Bundles, Streamlit, Folium, Python 3.11, pytest, Lakebase/Postgres-compatible SQL, MLflow-compatible Python agent wrappers.

---

### Task 1: Repository Scaffold And Tests

**Files:**
- Create: `tests/test_agents.py`
- Create: `tests/test_trust_scoring.py`
- Create: `tests/test_demo_store.py`
- Create: `pyproject.toml`

- [ ] **Step 1: Write failing tests for symptom matching, script generation, trust-score updates, and demo data invariants**

Run: `python3 -m pytest tests -q`

Expected before implementation: import failures for `phase_2_app`.

- [ ] **Step 2: Add minimal Python package metadata**

Create `pyproject.toml` with pytest configuration and dependencies documented for Streamlit app runtime.

- [ ] **Step 3: Re-run tests**

Run: `python3 -m pytest tests -q`

Expected after package scaffold only: failures move from missing package to missing functions/classes.

### Task 2: Phase 2 Deterministic Demo Core

**Files:**
- Create: `phase_2_app/__init__.py`
- Create: `phase_2_app/agents.py`
- Create: `phase_2_app/trust.py`
- Create: `phase_2_app/store.py`
- Create: `phase_2_app/demo_data.py`

- [ ] **Step 1: Implement symptom matcher**

Expose `match_symptoms(symptom_text: str) -> dict` returning ranked specialties and capability matches. The required demo input `Heart pain, trouble breathing` must rank cardiology, emergency medicine, and critical care.

- [ ] **Step 2: Implement script generator**

Expose `generate_verification_script(facility: Facility) -> list[dict]` with basic and progressive questions. Heritage Hospitals must receive 13 demo questions.

- [ ] **Step 3: Implement score recalculation**

Expose `recalculate_trust_score(old_score: float, claims_checked: int, claims_verified: int, verification_count: int) -> float`. The first Heritage validation must move `0.68` to `0.737`; the second must reach at least `0.80`.

- [ ] **Step 4: Implement demo store**

Expose an in-memory/SQLite-compatible store used by local tests and the Streamlit fallback mode. It must seed Heritage Hospitals at trust score `0.68`, below patient threshold `0.75`.

- [ ] **Step 5: Run tests**

Run: `python3 -m pytest tests -q`

Expected: all deterministic core tests pass.

### Task 3: Databricks App Source

**Files:**
- Create: `phase-2-app/app.py`
- Create: `phase-2-app/app.yaml`
- Create: `phase-2-app/requirements.txt`
- Create: `phase-2-app/pages/01_Volunteer_Portal.py`
- Create: `phase-2-app/pages/02_Patient_Search.py`

- [ ] **Step 1: Build Streamlit entrypoint**

The app must provide Volunteer Portal and Patient Search pages without a marketing landing page.

- [ ] **Step 2: Build Volunteer Portal**

The page must search/filter facilities, show queue priority, generate a verification script, accept yes/no validation responses, write a validation event, and show score movement.

- [ ] **Step 3: Build Patient Search**

The page must accept symptom text and location, call symptom matching, filter facilities below `0.75`, rank by trust/proximity, and render a Folium map with green/yellow/red markers.

- [ ] **Step 4: Run import/syntax verification**

Run: `python3 -m compileall phase_2_app phase-2-app`

Expected: no syntax errors.

### Task 4: Phase 1 Pipeline Source

**Files:**
- Create: `phase-1-pipeline/src/facility_validation_framework.sql`
- Create: `phase-1-pipeline/src/quality_checks.sql`

- [ ] **Step 1: Add Bronze SQL**

Create the 3 Bronze materialized views from the implementation plan with constraints and NFHS bracket-notation awareness.

- [ ] **Step 2: Add Silver SQL**

Create the 4 Silver materialized views for array parsing, explosion, specialty indexing, and district baselines.

- [ ] **Step 3: Add Gold SQL**

Create the 6 Gold materialized views for freshness, name-claim alignment, plausibility, data quality, confidence, and integrated assessment.

- [ ] **Step 4: Add SQL quality checks**

Create verification queries for row counts, tier distribution, null score detection, and Heritage Hospitals lookup.

### Task 5: Lakebase Schema And Sync

**Files:**
- Create: `lakebase/schema.sql`
- Create: `jobs/sync_uc_to_lakebase.py`
- Create: `scripts/seed_demo_data.py`

- [ ] **Step 1: Add Postgres-compatible schema**

Create `facilities_verified`, `verification_queue`, and `volunteer_validations` tables with indexes.

- [ ] **Step 2: Add Unity Catalog to Lakebase sync script**

Read `dais2026.validation.integrated_facility_assessment`, transform into app schema, and upsert facilities and verification queue rows.

- [ ] **Step 3: Add demo data seed script**

Ensure Heritage Hospitals, Varanasi is present with trust score `0.68`, risk flags `SUSPICIOUS_VOLUME` and `STALE`, and high-priority queue entry.

### Task 6: Databricks Asset Bundle

**Files:**
- Create: `databricks.yml`
- Modify: `README.md`

- [ ] **Step 1: Add bundle resources**

Define the existing pipeline ID `27fea50d-7b95-4540-b673-a0c8c92fe08d`, Databricks App resource, sync job, and dev/prod targets.

- [ ] **Step 2: Add deployment docs**

Document authentication, validation, deployment, pipeline run, app run, rollback, and final verification commands.

- [ ] **Step 3: Validate bundle locally**

Run: `DATABRICKS_AUTH_STORAGE=plaintext databricks bundle validate -t dev`

Expected: bundle configuration validates.

### Task 7: Workspace Deployment Gates

**Files:**
- No new files unless deployment output requires docs updates.

- [ ] **Step 1: Verify source data**

Run Databricks queries proving `dais2026.raw.facilities`, `dais2026.raw.india_post_pincode_directory`, and `dais2026.raw.nfhs_5_district_health_indicators` row counts match expectations.

- [ ] **Step 2: Deploy bundle to dev**

Run: `DATABRICKS_AUTH_STORAGE=plaintext databricks bundle deploy -t dev`

- [ ] **Step 3: Run pipeline**

Run the bundle pipeline resource and verify all 13 tables exist.

- [ ] **Step 4: Deploy app**

Run the Databricks App resource and verify the Volunteer and Patient flows.

- [ ] **Step 5: Complete final audit**

Use `EXECUTION-PROMPT.md` checklist requirement-by-requirement. Do not mark the goal complete unless every required Databricks runtime and demo artifact is verified with current evidence.
