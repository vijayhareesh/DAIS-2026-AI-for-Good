# HealthVerify India - DAIS 2026 AI for Good

**Hackathon:** Databricks Apps & Agents for Good 2026  
**Team:** [Your Team Name]

---

## Overview

End-to-end system ensuring patients find trustworthy healthcare facilities through community-driven data validation powered by AI agents.

### The Problem

India has 10,000+ healthcare facilities with self-reported capabilities, specialties, and contact information. Current data quality issues:

* **83% lack reliable freshness data** (64.5% have no update date, 18.2% are stale or aging)
* **Only 17.3% are recently validated as "FRESH"**
* **Over 8,200 facilities** need verification or re-verification
* No verification mechanism for patients to trust the information

### Real-World Impact

* Patients waste time and money traveling to facilities that don't have claimed capabilities
* Emergency cases risk dangerous delays when directed to inadequate facilities
* Legitimate facilities lose trust due to ecosystem-wide data quality issues

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
* **Total Facilities:** 10,088
* **Validation Scores:** 9,973 facilities scored

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
- [ ] Demo preparation

### Phase 3: Deployment Assets
- [x] Databricks Asset Bundle (`databricks.yml`)
- [x] Dev bundle validation
- [ ] Dev deployment
- [ ] Production deployment

---

## Key Metrics

### Current Data Quality
* 6,431 facilities with NO_DATE (64.5%)
* 1,815 facilities STALE or AGING (18.2%)
* 294 facilities SUSPICIOUS_VOLUME (2.9%)
* 269 facilities INCOMPLETE_DATA (2.7%)

### Success Criteria (Future)
* 1,000 volunteers verify entire database in 3 months
* 95% of facilities have trust score ≥ 0.80
* Patient satisfaction: 85%+ report finding appropriate care
* Reduce wasted travel by 40%

---

## Documentation Structure

```
DAIS-2026-AI-for-Good/
├── README.md (you are here)
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
* Heritage Hospitals demo data is present or seeded into Lakebase

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

**Heritage Hospitals, Varanasi**
* **Before:** Trust score 0.68 (SUSPICIOUS_VOLUME, STALE) - filtered out from patient results
* **After volunteer validation:** Trust score 0.88+ (FRESH) - ranks #2 for cardiology
* **Impact:** Jumps from invisible to top 3 results for patients

This demonstrates how volunteer validation directly protects patients and improves healthcare access.

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
