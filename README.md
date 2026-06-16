# HealthVerify India - DAIS 2026 AI for Good

**Hackathon:** Databricks Apps & Agents for Good 2026  
**Team:** [Your Team Name]  
**Track:** Facility Trust Desk (Track 1)

---

## Overview

End-to-end system ensuring patients find trustworthy healthcare facilities through community-driven data validation powered by AI agents.

### The Problem

India has 10,000+ healthcare facilities with self-reported capabilities, specialties, and contact information. Current data quality issues:

* **64.9% have missing validation dates** (6,461 facilities with NO_DATE)
* **Only 15.4% are HIGH_RELIABILITY** (1,542 facilities)
* **685 facilities (6.8%) are UNRELIABLE** and hidden from patient search
* No verification mechanism for patients to trust the information

### Real-World Impact

* Patients waste time and money traveling to facilities that don't have claimed capabilities
* Emergency cases risk dangerous delays when directed to inadequate facilities
* Legitimate facilities lose trust due to ecosystem-wide data quality issues
* **685 facilities currently hidden from search** to protect patients from unreliable data

---

## Solution Architecture

**Sequential Two-Phase Approach:**

### Phase 1: Batch Pipeline → Initial Trust Scoring
Lakeflow Spark Declarative Pipeline generates multi-dimensional trust scores for all 10K facilities using validation signals (freshness, plausibility, alignment, data quality).

**📁 [Go to Phase 1: Pipeline →](./phase-1-pipeline/)**

### Phase 2: Live App → Ongoing Validation
Databricks App with dual interfaces:
* **Volunteer Portal** - Community-driven verification with AI-generated scripts
* **Patient Search** - Trust-scored facility recommendations with geospatial matching

**📁 [Go to Phase 2: App →](./phase-2-app/)**

---

## Quick Start

1. **Start with Phase 1:** [Pipeline Implementation](./phase-1-pipeline/)
2. **Once pipeline completes:** [App Implementation](./phase-2-app/)
3. **Review design:** [HealthVerify India Design](./docs/design/2026-06-15-healthverify-india-design.md)
4. **Prepare for demo:** [Demo Script](./DEMO-SCRIPT.md) ⭐

### Local Verification

```bash
python3 -m unittest discover -s tests -v
PYTHONPYCACHEPREFIX=/private/tmp/healthverify_pycache python3 -m compileall phase_2_app phase-2-app jobs scripts
DATABRICKS_AUTH_STORAGE=plaintext databricks bundle validate -t dev
```

The `DATABRICKS_AUTH_STORAGE=plaintext` prefix is currently required for this workspace because the local Databricks CLI reported older secure-cache credentials for management APIs.

---

## Data Sources

* **Catalog:** `dais2026`
* **Schemas:** `raw`, `virtue_foundation_cleaned`, `validation`
* **Total Facilities:** 10,039
* **Validation Scores:** 10,039 facilities scored
* **States Covered:** 236
* **Cities Covered:** 1,629

---

## Data Quality Notes

Known data quality issues and remediation strategies:

* [NFHS Bracket Notation Issue](./docs/data-quality/nfhs-bracket-notation-issue.md) - STRING column parsing requirements
* [Virtue Foundation EDA](./docs/data-quality/virtue-foundation-eda.md) - Exploratory data analysis findings

---

## Project Status

### Phase 1: Pipeline
- [x] Architecture complete
- [x] Implementation plans complete (Bronze, Silver, Gold layers + Deployment)
- [x] Pipeline source implementation (`phase-1-pipeline/src/facility_validation_framework.sql`)
- [x] Pipeline quality checks (`phase-1-pipeline/src/quality_checks.sql`)
- [ ] Pipeline deployed to production

### Phase 2: App
- [x] Design complete
- [x] Component specifications complete
- [x] Deterministic demo agents and trust-score core (`phase_2_app/`)
- [x] Streamlit Databricks App scaffold (`phase-2-app/`)
- [x] Lakebase schema and sync scripts (`lakebase/`, `jobs/`, `scripts/`)
- [x] Demo script prepared
- [ ] Demo rehearsal

### Phase 3: Deployment Assets
- [x] Databricks Asset Bundle (`databricks.yml`)
- [x] Dev bundle validation
- [ ] Dev deployment
- [ ] Production deployment

---

## Key Metrics

### Current Data Quality (from validation.integrated_facility_assessment)
* 6,461 facilities with NO_DATE (64.9%)
* 949 facilities STALE_DATA (9.5%)
* 2,884 facilities DATA_CLIPPED (29.0%)
* 685 facilities UNRELIABLE_DATA (6.8%)

### Trust Score Distribution
* 1,542 facilities HIGH_RELIABILITY (15.4%) - avg score 0.821
* 7,809 facilities MODERATE_RELIABILITY (77.8%) - avg score 0.741
* 685 facilities UNRELIABLE_DATA (6.8%) - avg score 0.604

### Success Criteria (Target)
* **1,000 volunteers** verify entire database in **3 months** (114 hours for urgent 685)
* **95% of facilities** have trust score ≥ 0.80
* **Patient satisfaction:** 85%+ report finding appropriate care
* **Reduce wasted travel by 40%**

---

## Documentation Structure

```
DAIS-2026-AI-for-Good/
├── README.md (you are here)
├── DEMO-SCRIPT.md          # 3-minute hackathon demo script ⭐
├── databricks.yml          # Databricks Asset Bundle
├── docs/
│   ├── data-quality/       # Cross-phase data quality findings
│   ├── design/             # Overall system design
│   └── specs/              # Implementation specifications
├── jobs/                   # UC to Lakebase sync job
├── lakebase/               # Lakebase/Postgres schema
├── phase-1-pipeline/       # Batch pipeline for initial scoring
├── phase-2-app/            # Live app for ongoing validation
├── phase_2_app/            # Testable app/agent core
├── scripts/                # Demo data seed helpers
└── tests/                  # Local deterministic tests
```

---

## Databricks Deployment

### Prerequisites

* Databricks CLI authenticated as `richthai92@gmail.com`
* Workspace: `https://dbc-66fc0519-a852.cloud.databricks.com`
* Catalog/schema access to `dais2026.raw` and `dais2026.validation`
* Existing Lakeflow pipeline ID: `27fea50d-7b95-4540-b673-a0c8c92fe08d`
* Lakebase connection values available as job/app secrets or environment variables:
  * `LAKEBASE_JDBC_URL`
  * `LAKEBASE_USER`
  * `LAKEBASE_PASSWORD`

### Validate And Deploy

```bash
DATABRICKS_AUTH_STORAGE=plaintext databricks bundle validate -t dev
DATABRICKS_AUTH_STORAGE=plaintext databricks bundle deploy -t dev
DATABRICKS_AUTH_STORAGE=plaintext databricks bundle run facility_validation_pipeline -t dev
DATABRICKS_AUTH_STORAGE=plaintext databricks bundle run nightly_sync -t dev
```

Production deployment:

```bash
DATABRICKS_AUTH_STORAGE=plaintext databricks bundle validate -t prod
DATABRICKS_AUTH_STORAGE=plaintext databricks bundle deploy -t prod
```

### Pipeline Verification

After the pipeline run completes, execute the checks in:

```text
phase-1-pipeline/src/quality_checks.sql
```

Required evidence before demo:

* `validation.integrated_facility_assessment` has roughly 10K facilities
* No null final confidence, data quality, or combined scores
* Confidence tier distribution is within the expected range
* Heritage Hospitals demo data matches [DEMO-SCRIPT.md](./DEMO-SCRIPT.md) expectations

### Lakebase Demo Seed

Apply schema first:

```bash
psql "$LAKEBASE_DATABASE_URL" -f lakebase/schema.sql
```

Seed Heritage Hospitals:

```bash
LAKEBASE_DATABASE_URL="$LAKEBASE_DATABASE_URL" python3 scripts/seed_demo_data.py
```

Without `LAKEBASE_DATABASE_URL`, the seed script prints the SQL and parameters for manual application.

### Rollback

```bash
DATABRICKS_AUTH_STORAGE=plaintext databricks bundle deployment bind facility_validation_pipeline 27fea50d-7b95-4540-b673-a0c8c92fe08d
git checkout main -- databricks.yml phase-1-pipeline/src phase-2-app phase_2_app jobs lakebase scripts
DATABRICKS_AUTH_STORAGE=plaintext databricks bundle deploy -t dev
```

For app-only rollback, redeploy the previous Git commit with `databricks bundle deploy -t dev` after checking out that commit.

---

## Demo Facility Example

**Heritage Hospitals, Varanasi** (unique_id: `390fa6ee-297f-4063-8fbe-82f5e7db7258`)

* **Before volunteer verification:**
  * Trust score: **0.45** (UNRELIABLE_DATA)
  * Red flags: STALE_DATA, OVERCLAIMING, DATA_CLIPPED
  * Status: ❌ **HIDDEN from patient search results**
  * Impact: Patients searching "cardiac care Varanasi" cannot find this facility

* **After volunteer verification:**
  * Trust score: **0.88** (HIGH_RELIABILITY)
  * Red flags: None (FRESH data, verified claims)
  * Status: ✅ **VISIBLE in search results** - ranked #11 for cardiac care
  * Impact: Patients find trusted care 2km from home instead of traveling 50km

This demonstrates how volunteer validation with AI-generated verification scripts directly protects patients and improves healthcare access.

**For complete demo flow and judging presentation:** See [DEMO-SCRIPT.md](./DEMO-SCRIPT.md)

---

## Tech Stack

* **Pipeline:** Lakeflow Spark Declarative Pipelines (SQL, Serverless)
* **App:** Databricks Apps (Streamlit)
* **AI Agents:** MLflow Agents (Script Generator, Symptom Matcher)
* **Operational DB:** Lakebase (Postgres)
* **Analytics:** Unity Catalog (Delta Lake)
* **Geospatial:** Folium maps

---

## Contact & Support

**Repository:** `/Workspace/Users/richthai92@gmail.com/DAIS-2026-AI-for-Good`

For questions or contributions, see the [Design Document](./docs/design/2026-06-15-healthverify-india-design.md).
