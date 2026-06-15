# GOAL: Complete HealthVerify India Implementation - Pipeline to Demo-Ready App

**Project:** HealthVerify India - Community-Driven Healthcare Facility Validation  
**Hackathon:** Databricks Apps & Agents for Good 2026  
**Repository:** `/Workspace/Users/richthai92@gmail.com/DAIS-2026-AI-for-Good`

---

## Mission

Build a complete, demo-ready system for healthcare facility validation in India using:
* **Phase 1**: Lakeflow Spark Declarative Pipeline for batch trust scoring (10K facilities)
* **Phase 2**: Databricks App with volunteer verification + patient search interfaces
* **Deployment**: Declarative Automation Bundles (DABs) for production-ready deployment

**Success Criteria:** Working demo that shows volunteer → validation → patient impact cycle in <3 minutes

---

## Current State

✅ **Architecture & Design Complete:**
* System design finalized and documented
* Repository reorganized into phase-based structure
* Implementation plans written with step-by-step instructions
* Demo script prepared (3-minute pitch)

❌ **Implementation Needed:**
* Pipeline not yet built
* App not yet scaffolded
* DABs configuration not created
* Demo data not seeded

**You are starting from complete specifications. Your job: implement everything.**

---

## Quick Orientation

### Essential Documentation (Read First)

**Start Here:**
1. [Project README](./README.md) - Overview, problem statement, architecture
2. [System Design](./docs/design/2026-06-15-healthverify-india-design.md) - High-level design decisions

**Phase 1 - Pipeline:**
3. [Phase 1 README](./phase-1-pipeline/README.md) - Pipeline overview and quick start
4. [Pipeline Architecture](./phase-1-pipeline/architecture.md) - Medallion architecture, scoring formulas
5. Implementation Plans:
   * [Bronze Layer](./phase-1-pipeline/implementation-plans/bronze-layer.md)
   * [Silver Layer](./phase-1-pipeline/implementation-plans/silver-layer.md)
   * [Gold Layer](./phase-1-pipeline/implementation-plans/gold-layer.md)
   * [Deployment Guide](./phase-1-pipeline/implementation-plans/deployment.md)

**Phase 2 - App:**
6. [Phase 2 README](./phase-2-app/README.md) - App overview and demo script
7. [App Architecture](./phase-2-app/architecture.md) - Component design, data flow
8. [Components Spec](./phase-2-app/components.md) - Detailed component specifications
9. [Data Schema](./phase-2-app/data-schema.md) - Lakebase tables and sync logic
10. [Implementation Plan](./phase-2-app/implementation-plan.md) - Step-by-step app build

**Data Quality:**
11. [NFHS Bracket Notation Issue](./docs/data-quality/nfhs-bracket-notation-issue.md) - STRING column parsing requirements
12. [Virtue Foundation EDA](./docs/data-quality/virtue-foundation-eda.md) - Data quality analysis

---

## Execution Strategy

### Required Skills (Load These First)

**Before starting ANY implementation**, load these superpowers skills in order:

1. `skills/using-superpowers/SKILL.md` - Core framework (ALWAYS FIRST)
2. `skills/writing-plans/SKILL.md` - For creating detailed implementation plans
3. `skills/databricks-pipelines/SKILL.md` - For Phase 1 pipeline work
4. `skills/databricks-apps/SKILL.md` - For Phase 2 app work
5. `skills/databricks-lakebase/SKILL.md` - For operational database setup
6. `skills/test-driven-development/SKILL.md` - For testing as you build
7. `skills/verification-before-completion/SKILL.md` - Before marking anything complete
8. `skills/systematic-debugging/SKILL.md` - When things don't work

**Optional but Recommended:**
* `skills/subagent-driven-development/SKILL.md` - For complex multi-step work
* `skills/executing-plans/SKILL.md` - For batch execution of plans

---

## Phase 1: Lakeflow Spark Declarative Pipeline

### Objective
Build production batch pipeline to generate initial trust scores for 10,000 healthcare facilities.

### Implementation Sequence

**1. Setup & Verification (15 mins)**
* Verify pipeline exists: `27fea50d-7b95-4540-b673-a0c8c92fe08d`
* Verify source data exists:
  * `dais2026.raw.facilities` (~10K rows)
  * `dais2026.raw.india_post_pincode_directory` (~165K rows)
  * `dais2026.raw.nfhs_5_district_health_indicators` (~750 rows)
* Confirm `validation` schema is created or create it

**2. Bronze Layer Implementation (~2 hours)**
* Follow: `./phase-1-pipeline/implementation-plans/bronze-layer.md`
* **Critical**: Read the NFHS bracket notation issue doc first - STRING columns need special parsing
* Create 3 Bronze tables with type validation and geographic constraints
* Run initial data quality checks
* Verify row counts and schema

**3. Silver Layer Implementation (~3 hours)**
* Follow: `./phase-1-pipeline/implementation-plans/silver-layer.md`
* Parse JSON arrays (capabilities, specialties)
* Explode to ~460K rows
* Calculate percentile rankings
* Verify explosion logic produces expected row counts

**4. Gold Layer Implementation (~4 hours)**
* Follow: `./phase-1-pipeline/implementation-plans/gold-layer.md`
* Implement 6 validation scoring tables:
  * Freshness scores
  * Name-claim alignment
  * Plausibility scores
  * Data quality signals
  * Confidence scores
  * Integrated assessment (final output)
* **Critical**: Double-check scoring formulas match architecture doc
* Verify score distributions match expected tiers (HIGH 30-40%, MEDIUM 40-50%, LOW 10-20%)

**5. Pipeline Deployment (~1 hour)**
* Follow: `./phase-1-pipeline/implementation-plans/deployment.md`
* Switch to Production mode
* Configure monitoring and alerts
* Run full pipeline end-to-end
* Verify final table: `validation.integrated_facility_assessment` has ~10K rows with trust scores

**Phase 1 Success Criteria:**
* ✅ Pipeline runs successfully in Production mode
* ✅ All 13 tables created (3 Bronze + 4 Silver + 6 Gold)
* ✅ `validation.integrated_facility_assessment` contains trust scores for 9,973+ facilities
* ✅ Score distribution matches expectations
* ✅ No data quality issues in final output

---

## Phase 2: Databricks App (Volunteer + Patient Interfaces)

### Objective
Build real-time app with volunteer verification portal and patient search, powered by AI agents.

### Implementation Sequence

**1. Lakebase Setup (~30 mins)**
* Follow: `./phase-2-app/data-schema.md`
* Create Lakebase Postgres database (small instance)
* Create 3 tables:
  * `facilities_verified` (10K rows, geospatial indexed)
  * `volunteer_validations` (validation submissions)
  * `verification_queue` (facilities needing verification with AI scripts)
* Seed initial data from Phase 1 pipeline output
* Create PostGIS extension for geospatial queries
* Test geospatial query performance (<100ms for proximity search)

**2. Seed Demo Data (~15 mins)**
* Create "Heritage Hospitals, Varanasi" facility with:
  * Initial trust score: 0.68
  * Flags: SUSPICIOUS_VOLUME, STALE
  * 200 capability claims
* This is your demo facility for the 3-minute pitch

**3. MLflow AI Agents (~2 hours)**
* Follow: `./phase-2-app/components.md` (AI Agents section)

**Agent 1: Script Generator**
* Analyzes facility risk profile
* Generates progressive verification scripts
* Input: facility_id, trust_score, red_flags
* Output: JSON with basic + progressive questions
* Test with Heritage Hospitals demo facility

**Agent 2: Symptom Matcher**
* Interprets natural language symptoms
* Maps to specialties and capabilities
* Input: patient symptom text
* Output: ranked specialties + capability matches
* Test with "Heart pain, trouble breathing" → cardiology, emergency medicine, critical care

**Validation:**
* Test both agents independently
* Verify agent responses are sensible (not hallucinations)
* Measure response times (<2s for Script Generator, <1s for Symptom Matcher)

**4. Databricks App Scaffolding (~1 hour)**
* Follow: `./phase-2-app/components.md` (App Structure section)
* Create app with Streamlit multi-page architecture
* Setup Lakebase connection in app.yaml
* Configure MLflow agent endpoints
* Test basic app launch

**5. Volunteer Portal (~3 hours)**
* Follow: `./phase-2-app/components.md` (Volunteer Portal section)
* **Search & Browse:**
  * Search bar for facility names
  * Filter by city/state, trust score range, red flags
  * Results table with trust score badges
* **Verification Workflow:**
  * "Verify Now" button → calls Script Generator Agent
  * Display generated verification script
  * Yes/no checkbox form (13 questions for demo)
  * Submit → writes to `volunteer_validations` table
  * Real-time trust score recalculation
  * Success message with score change (0.68 → 0.737)
* **Testing:**
  * Walk through complete flow with Heritage Hospitals
  * Verify score updates in real-time
  * Test with multiple validation submissions

**6. Patient Search (~3 hours)**
* Follow: `./phase-2-app/components.md` (Patient Search section)
* **Symptom Input:**
  * Text area for natural language symptoms
  * City/state dropdown selector
  * "Find Care" button → calls Symptom Matcher Agent
* **Map Display:**
  * Folium map with facility markers
  * Color-coded by trust score (green ≥0.75, yellow 0.60-0.74, red <0.60)
  * Verify badge for recently validated facilities
  * Click marker → show facility details in sidebar
* **Results Sidebar:**
  * Top 5 facilities ranked by trust score + proximity
  * Facility cards with: name, address, phone, trust score, last validated
  * Filter threshold: only show facilities ≥0.75 trust score
* **Testing:**
  * Search for "Heart pain, trouble breathing" near Varanasi
  * Verify Heritage Hospitals appears after volunteer validation pushes it over 0.75 threshold
  * Test geospatial ranking (closer facilities rank higher)

**7. End-to-End Integration Test (~30 mins)**
* **Complete the demo cycle:**
  1. Start with Heritage Hospitals at trust score 0.68 (below 0.75 threshold)
  2. Patient searches → Heritage Hospitals NOT shown (filtered out)
  3. Volunteer verifies → trust score jumps to 0.737
  4. Patient searches again → Heritage Hospitals NOW appears (just below threshold)
  5. Second volunteer validation → trust score reaches 0.80
  6. Patient sees Heritage Hospitals ranked #2 for cardiology near Varanasi
* **Verify:**
  * All transitions happen in real-time
  * Trust score updates propagate immediately
  * No race conditions or data inconsistencies
  * App is responsive (<2s page loads)

**Phase 2 Success Criteria:**
* ✅ App launches successfully on Databricks Apps platform
* ✅ Both AI agents respond correctly
* ✅ Volunteer portal generates scripts and accepts validations
* ✅ Patient search returns geospatially-ranked results
* ✅ Trust scores update in real-time
* ✅ Demo cycle (volunteer → patient impact) works end-to-end
* ✅ Map visualization shows facilities with correct color coding

---

## Phase 3: Declarative Automation Bundles (DABs)

### Objective
Package everything for production deployment using DABs (formerly Databricks Asset Bundles).

### Implementation (~2 hours)

**1. DABs Structure**
Create `databricks.yml` in repository root:

```yaml
bundle:
  name: healthverify-india
  
variables:
  catalog: dais2026
  validation_schema: validation
  
resources:
  # Phase 1: Pipeline
  pipelines:
    facility_validation_pipeline:
      id: 27fea50d-7b95-4540-b673-a0c8c92fe08d
      name: "HealthVerify India - Facility Validation Pipeline"
      target: validation
      catalog: ${var.catalog}
      schema: ${var.validation_schema}
      channel: CURRENT
      photon: true
      serverless: true
      configuration:
        spark.databricks.delta.properties.defaults.enableChangeDataFeed: "true"
  
  # Phase 2: App
  apps:
    healthverify_app:
      name: "HealthVerify India"
      description: "Community-driven healthcare facility validation"
      resources:
        - name: lakebase_connection
          # Lakebase connection configuration
      config:
        app.yaml: ${workspace.file_path}/phase-2-app/app.yaml
  
  # Jobs for Data Sync
  jobs:
    nightly_sync:
      name: "HealthVerify - Nightly UC to Lakebase Sync"
      schedule:
        quartz_cron_expression: "0 0 2 * * ?" # 2 AM daily
        timezone_id: "America/Los_Angeles"
      tasks:
        - task_key: sync_facilities
          notebook_task:
            notebook_path: ${workspace.file_path}/jobs/sync_uc_to_lakebase.py
          job_cluster_key: serverless_cluster
      job_clusters:
        - job_cluster_key: serverless_cluster
          new_cluster:
            spark_version: "14.3.x-scala2.12"
            node_type_id: "Standard_DS3_v2"
            num_workers: 2
            
targets:
  dev:
    mode: development
    workspace:
      host: ${workspace.host}
    
  prod:
    mode: production
    workspace:
      host: ${workspace.host}
```

**2. Supporting Scripts**
* Create `jobs/sync_uc_to_lakebase.py` - nightly sync from Unity Catalog to Lakebase
* Create `.github/workflows/deploy.yml` - CI/CD for automated deployment (optional)

**3. Deployment**
```bash
# Validate bundle
databricks bundle validate -t dev

# Deploy to dev
databricks bundle deploy -t dev

# Run pipeline
databricks bundle run facility_validation_pipeline -t dev

# Deploy to prod
databricks bundle deploy -t prod
```

**4. Documentation**
* Update README with DABs deployment instructions
* Document environment variables and prerequisites
* Include rollback procedure

**DABs Success Criteria:**
* ✅ Bundle validates without errors
* ✅ Deploys successfully to dev environment
* ✅ Pipeline runs via bundle
* ✅ App deploys via bundle
* ✅ Nightly sync job configured and tested
* ✅ Documentation complete for deployment process

---

## Phase 4: Demo Preparation

### Objective
Prepare for 3-minute hackathon demo with smooth transitions and compelling narrative.

### Tasks (~1 hour)

**1. Demo Script Rehearsal**
* Read: `./phase-2-app/README.md` (Demo Script section)
* Practice 3-minute timing:
  * Hook: 30s
  * Architecture: 45s
  * Demo - Volunteer: 15s
  * Demo - Patient: 45s
  * ROI & Impact: 30s
  * Next Steps: 15s
* Memorize key metrics: 83%, 8,200 facilities, 0.68 → 0.88, 40% reduction

**2. Demo Data Prep**
* Ensure Heritage Hospitals is seeded at trust score 0.68
* Pre-load volunteer portal on one browser tab
* Pre-load patient search on another browser tab
* Test transitions between tabs
* Have architecture diagram ready to share screen

**3. Backup Plan**
* Take screenshots of each demo step
* Record a screen recording of the working demo
* Prepare to narrate from screenshots if live demo fails

**4. Judge Q&A Prep**
* Review Q&A section in demo script
* Key questions to prepare for:
  * How do you prevent malicious volunteers? → Account verification, multi-validation requirement, history tracking
  * What if facilities game the system? → Progressive questioning, cross-reference with external data, 0.75 threshold
  * Why not use Google Maps? → Healthcare requires domain-specific validation, consistent freshness
  * Cost to run? → $2K/month at scale = $0.02 per search vs $20-50 wasted travel cost
  * Privacy and governance? → Public facility data (not PHI), anonymous searches, Unity Catalog governance for audit trails

**5. Final Checklist**
* ✅ Pipeline deployed and running
* ✅ App running and accessible
* ✅ Demo facility (Heritage Hospitals) seeded correctly
* ✅ Both AI agents responding
* ✅ Volunteer validation flow works
* ✅ Patient search flow works
* ✅ Real-time score updates working
* ✅ Map visualization renders correctly
* ✅ Architecture diagram ready
* ✅ Backup screenshots/video prepared
* ✅ Demo script memorized
* ✅ Timer set for 3 minutes

---

## Critical Success Factors

### Must-Haves (Non-Negotiable)

1. **Pipeline Output Quality**
   * Trust scores for 9,973+ facilities
   * Score distribution matches expectations
   * No NULL scores or data quality issues

2. **Real-Time Updates**
   * Volunteer validation updates trust score immediately
   * Patient search reflects updated scores
   * No caching issues or stale data

3. **Demo Flow**
   * Complete volunteer → patient cycle works in <60 seconds
   * Heritage Hospitals transitions from invisible → visible → top-ranked
   * All transitions are smooth (no errors, no lag)

4. **AI Agent Reliability**
   * Script Generator produces sensible verification questions
   * Symptom Matcher maps symptoms to correct specialties
   * Both agents respond in <2 seconds

5. **Visual Polish**
   * Map renders cleanly with color-coded markers
   * Trust score badges are clear and professional
   * UI is intuitive (judges can understand without explanation)

### Nice-to-Haves (If Time Permits)

* Voice input for low-literacy users (Phase 2+ roadmap item)
* Multi-lingual support (Phase 2+ roadmap item)
* Advanced ML-based scoring (Phase 3 roadmap item)
* Mobile-responsive design
* Admin dashboard for monitoring

---

## Troubleshooting Guide

### Pipeline Issues

**Problem:** STRING columns not parsing correctly
* **Solution:** Review `./docs/data-quality/nfhs-bracket-notation-issue.md` and apply bracket notation parsing

**Problem:** Score distributions don't match expected tiers
* **Solution:** Check scoring formula weights in `./phase-1-pipeline/architecture.md` and verify calculations

**Problem:** Pipeline fails to run
* **Solution:** Check source tables exist and have data; verify permissions on `validation` schema

### App Issues

**Problem:** App won't start
* **Solution:** Check Lakebase connection credentials; verify app.yaml syntax

**Problem:** AI agents timeout or return errors
* **Solution:** Check MLflow endpoint status; verify agent model deployment; test agents independently

**Problem:** Trust scores don't update
* **Solution:** Check Lakebase write permissions; verify score recalculation logic; check for transaction conflicts

**Problem:** Map doesn't render
* **Solution:** Check Folium library import; verify geospatial coordinates are valid; test with simple hardcoded coordinates first

### DABs Issues

**Problem:** Bundle validation fails
* **Solution:** Check databricks.yml syntax; verify all referenced paths exist; check for circular dependencies

**Problem:** Deployment fails
* **Solution:** Check workspace permissions; verify cluster/warehouse availability; check resource quotas

---

## Execution Checklist (Use This to Track Progress)

### Phase 1: Pipeline
- [ ] Source data verified
- [ ] Bronze layer implemented and tested
- [ ] Silver layer implemented and tested
- [ ] Gold layer implemented and tested
- [ ] Pipeline deployed to Production
- [ ] Final output table verified (9,973+ rows with trust scores)

### Phase 2: App
- [ ] Lakebase database created and seeded
- [ ] Demo data (Heritage Hospitals) prepared
- [ ] Script Generator Agent deployed and tested
- [ ] Symptom Matcher Agent deployed and tested
- [ ] Databricks App scaffolded
- [ ] Volunteer Portal implemented
- [ ] Patient Search implemented
- [ ] End-to-end integration test passed

### Phase 3: DABs
- [ ] databricks.yml created
- [ ] Sync job script created
- [ ] Bundle validated
- [ ] Bundle deployed to dev
- [ ] Bundle deployed to prod
- [ ] Documentation updated

### Phase 4: Demo Prep
- [ ] Demo script rehearsed (3 minutes)
- [ ] Demo data prepared
- [ ] Backup screenshots/video created
- [ ] Judge Q&A prep complete
- [ ] Final pre-demo checklist completed

---

## Time Budget (Aggressive but Achievable)

| Phase | Estimated Time | Priority |
|-------|---------------|----------|
| Phase 1: Pipeline | 10 hours | CRITICAL |
| Phase 2: App | 10 hours | CRITICAL |
| Phase 3: DABs | 2 hours | HIGH |
| Phase 4: Demo Prep | 1 hour | HIGH |
| **Total** | **23 hours** | |

**Milestone Targets:**
* End of Day 1: Pipeline complete and deployed
* End of Day 2: App functional (both portals working)
* End of Day 3: DABs deployed, demo rehearsed, ready to present

---

## Final Verification Before Demo

**Run this checklist 1 hour before demo time:**

1. **Pipeline Verification**
   ```sql
   -- Check final output
   SELECT 
     COUNT(*) as total_facilities,
     AVG(combined_trust_score) as avg_trust_score,
     SUM(CASE WHEN combined_trust_score >= 0.80 THEN 1 ELSE 0 END) as high_trust_count,
     SUM(CASE WHEN combined_trust_score >= 0.60 AND combined_trust_score < 0.80 THEN 1 ELSE 0 END) as medium_trust_count,
     SUM(CASE WHEN combined_trust_score < 0.60 THEN 1 ELSE 0 END) as low_trust_count
   FROM validation.integrated_facility_assessment;
   
   -- Should show: ~10K total, ~30-40% HIGH, ~40-50% MEDIUM, ~10-20% LOW
   ```

2. **App Verification**
   * Open app in browser
   * Navigate to Volunteer Portal → Heritage Hospitals should show trust score 0.68
   * Navigate to Patient Search → Enter "Heart pain" near Varanasi → Heritage Hospitals should NOT appear (below 0.75 threshold)
   * Go back to Volunteer Portal → Submit validation for Heritage Hospitals
   * Return to Patient Search → Heritage Hospitals should NOW appear
   * Verify map markers are color-coded correctly
   * Click Heritage Hospitals marker → Detail card should show "Recently verified"

3. **Agent Verification**
   * Test Script Generator with Heritage Hospitals → Should return progressive questions
   * Test Symptom Matcher with "Heart pain, trouble breathing" → Should map to cardiology, emergency medicine

4. **Backup Materials**
   * Screenshots of each demo step saved
   * Screen recording of working demo saved
   * Architecture diagram ready to share
   * Demo script printed or accessible

5. **Environment Check**
   * App is running and accessible
   * Browser tabs are set up (Volunteer, Patient)
   * Timer is ready (3 minutes)
   * Presentation mode enabled (hide notifications, full screen)

---

## Post-Demo: Production Deployment (If Time Permits)

If the demo goes well and you have time, consider these production hardening steps:

1. **Security**
   * Enable authentication for volunteer portal
   * Implement rate limiting on AI agent endpoints
   * Add audit logging for all validation submissions

2. **Monitoring**
   * Set up pipeline monitoring alerts (data quality, row counts)
   * Add app performance monitoring (page load times, error rates)
   * Create dashboard for trust score distribution over time

3. **Scalability**
   * Test with concurrent users (10+ volunteers)
   * Optimize Lakebase queries (add indexes where needed)
   * Cache AI agent responses for common queries

4. **Documentation**
   * Write operational runbook
   * Document incident response procedures
   * Create user guides for volunteers and patients

---

## You've Got This! 🚀

You have complete specifications, detailed implementation plans, and a clear path from start to finish. Every decision has been made, every component designed. Your job is pure execution.

**Remember:**
* Load superpowers skills BEFORE starting each phase
* Follow the implementation plans step-by-step
* Test as you go (don't wait until the end)
* The demo flow is the north star - everything should work toward that 3-minute narrative
* When stuck, refer back to the documentation - the answers are there

**This is a winning project. Build it. Demo it. Ship it.**

---

**Last Updated:** June 15, 2026  
**Status:** Ready for Full Implementation  
**Estimated Completion:** 23 hours of focused work

Good luck! 🎯
