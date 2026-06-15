# Repository Reorganization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reorganize DAIS-2026-AI-for-Good repository into phase-based structure (Pipeline → App)

**Architecture:** Sequential implementation across 5 phases (Directory Setup, README Creation, File Moves, Cleanup, Verification). Each phase is independently verifiable before proceeding to next.

**Tech Stack:** Databricks workspace file tools (createAsset, workspaceUpdateFile), markdown

**Design Reference:** [Repository Reorganization Design](./2026-06-15-repository-reorganization-design.md)

---

## File Structure Overview

### Directories to Create
* `docs/data-quality/` — Cross-phase data quality documentation
* `docs/design/` — Overall system design documents
* `phase-1-pipeline/` — Pipeline implementation docs
* `phase-1-pipeline/implementation-plans/` — Layer-specific plans
* `phase-2-app/` — App implementation docs

### Files to Create (READMEs with new content)
* `README.md` (root) — Project overview + navigation
* `phase-1-pipeline/README.md` — Pipeline quick start
* `phase-2-app/README.md` — App overview + demo

### Files to Move
* 2 data quality files → `docs/data-quality/`
* 1 design file → `docs/design/`
* 5 pipeline files → `phase-1-pipeline/`
* 4 app files → `phase-2-app/`

### Files to Delete
* 4 obsolete files (empty or consolidated)
* 2 empty directories

---

## Phase A: Directory Setup

### Task 1: Create Data Quality Directory

**Files:**
* Create: `/Users/richthai92@gmail.com/DAIS-2026-AI-for-Good/docs/data-quality/`

- [ ] **Step 1: Create docs/data-quality directory**

Using Databricks workspace tools:

```python
# Will use createAsset tool with assetType="directory"
```

- [ ] **Step 2: Verify directory created**

Expected: Directory exists at `/Users/richthai92@gmail.com/DAIS-2026-AI-for-Good/docs/data-quality/`

---

### Task 2: Create Design Directory

**Files:**
* Create: `/Users/richthai92@gmail.com/DAIS-2026-AI-for-Good/docs/design/`

- [ ] **Step 1: Create docs/design directory**

Using Databricks workspace tools:

```python
# Will use createAsset tool with assetType="directory"
```

- [ ] **Step 2: Verify directory created**

Expected: Directory exists at `/Users/richthai92@gmail.com/DAIS-2026-AI-for-Good/docs/design/`

---

### Task 3: Create Phase 1 Pipeline Directory

**Files:**
* Create: `/Users/richthai92@gmail.com/DAIS-2026-AI-for-Good/phase-1-pipeline/`

- [ ] **Step 1: Create phase-1-pipeline directory**

Using Databricks workspace tools:

```python
# Will use createAsset tool with assetType="directory"
```

- [ ] **Step 2: Verify directory created**

Expected: Directory exists at `/Users/richthai92@gmail.com/DAIS-2026-AI-for-Good/phase-1-pipeline/`

---

### Task 4: Create Implementation Plans Directory

**Files:**
* Create: `/Users/richthai92@gmail.com/DAIS-2026-AI-for-Good/phase-1-pipeline/implementation-plans/`

- [ ] **Step 1: Create implementation-plans subdirectory**

Using Databricks workspace tools:

```python
# Will use createAsset tool with assetType="directory"
```

- [ ] **Step 2: Verify directory created**

Expected: Directory exists at `/Users/richthai92@gmail.com/DAIS-2026-AI-for-Good/phase-1-pipeline/implementation-plans/`

---

### Task 5: Create Phase 2 App Directory

**Files:**
* Create: `/Users/richthai92@gmail.com/DAIS-2026-AI-for-Good/phase-2-app/`

- [ ] **Step 1: Create phase-2-app directory**

Using Databricks workspace tools:

```python
# Will use createAsset tool with assetType="directory"
```

- [ ] **Step 2: Verify directory created**

Expected: Directory exists at `/Users/richthai92@gmail.com/DAIS-2026-AI-for-Good/phase-2-app/`

---

## Phase B: Create New READMEs

### Task 6: Write Root README

**Files:**
* Create: `/Users/richthai92@gmail.com/DAIS-2026-AI-for-Good/README.md`

- [ ] **Step 1: Create root README file**

Using createAsset with assetType="file"

- [ ] **Step 2: Write README content**

Content to write:

```markdown
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
- [ ] Pipeline implementation
- [ ] Pipeline deployed to production

### Phase 2: App
- [x] Design complete
- [x] Component specifications complete
- [ ] App implementation
- [ ] Demo preparation

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
├── docs/
│   ├── data-quality/       # Cross-phase data quality findings
│   ├── design/             # Overall system design
│   └── specs/              # Implementation specifications
├── phase-1-pipeline/       # Batch pipeline for initial scoring
└── phase-2-app/            # Live app for ongoing validation
```

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
```

- [ ] **Step 3: Verify README created and content correct**

Expected: Root README exists with complete content (project overview, phase links, status checklist)

---

### Task 7: Write Phase 1 Pipeline README

**Files:**
* Create: `/Users/richthai92@gmail.com/DAIS-2026-AI-for-Good/phase-1-pipeline/README.md`
* Reference: `docs/superpowers/plans/README-facility-validation-pipeline.md` (to consolidate content)

- [ ] **Step 1: Read source README for consolidation**

Read `/Users/richthai92@gmail.com/DAIS-2026-AI-for-Good/docs/superpowers/plans/README-facility-validation-pipeline.md` to extract key content

- [ ] **Step 2: Create phase-1-pipeline README file**

Using createAsset with assetType="file"

- [ ] **Step 3: Write README content (consolidated)**

Content to write:

```markdown
# Phase 1: Facility Validation Pipeline

**← [Back to Project Overview](../README.md)**

---

## Overview

Production batch pipeline for initial trust scoring of 10,000 facilities using multi-dimensional validation and external reference data (geographic, health outcomes).

**Pipeline ID:** `27fea50d-7b95-4540-b673-a0c8c92fe08d`

**Architecture:** Medallion (Bronze → Silver → Gold) using Lakeflow Spark Declarative Pipelines

**Output:** Trust scores and validation signals for Phase 2 app consumption

---

## Purpose

Generate initial trust scores for all facilities to seed the real-time validation app (Phase 2). The pipeline:

1. Validates and cleanses raw facility data
2. Parses and explodes capability claims
3. Computes multi-dimensional scoring (freshness, plausibility, alignment, quality)
4. Produces production-ready tables for filtering and ranking

**This pipeline MUST complete before Phase 2 app can launch.**

---

## Architecture Summary

### Source Data
* `dais2026.raw.facilities` (~10K facilities with capability claims)
* `dais2026.raw.india_post_pincode_directory` (~165K pincodes for geographic validation)
* `dais2026.raw.nfhs_5_district_health_indicators` (~750 districts for outcome correlation)

### Output Schema
* **Bronze:** 3 tables - Type-validated copies with geographic constraints
* **Silver:** 4 tables - Transformed data (~460K exploded rows)
* **Gold:** 6 tables - Validation scoring (~10K scored facilities)

### Target Tables
* `validation.claim_freshness_scores`
* `validation.name_claim_alignment_scores`
* `validation.claim_plausibility_scores`
* `validation.data_quality_signals`
* `validation.facility_confidence_scores`
* `validation.integrated_facility_assessment`

**Full architecture:** [architecture.md](./architecture.md)

---

## Implementation Plans

Follow these plans sequentially. Each layer builds on the previous:

1. **[Bronze Layer](./implementation-plans/bronze-layer.md)** - ~2 hours
   * 3 Bronze tables
   * Type validation and geographic constraints
   * Schema verification

2. **[Silver Layer](./implementation-plans/silver-layer.md)** - ~3 hours
   * 4 Silver tables
   * JSON array parsing and explosion
   * Percentile ranking calculations

3. **[Gold Layer](./implementation-plans/gold-layer.md)** - ~4 hours
   * 6 Gold tables
   * Multi-dimensional scoring formulas
   * Red flag detection logic

4. **[Deployment Guide](./implementation-plans/deployment.md)** - ~1 hour
   * Production mode setup
   * Post-deployment monitoring
   * Alert thresholds

**Total estimated time:** ~10 hours

---

## Quick Reference

### Tech Stack
* **Platform:** Lakeflow Spark Declarative Pipelines (formerly Delta Live Tables)
* **Language:** SQL
* **Compute:** Serverless
* **Schema:** `validation.*` (Gold tables for production)

### Key Metrics
* **Confidence tiers:** HIGH 30-40%, MEDIUM 40-50%, LOW 10-20%
* **Production ready:** ≥70% facilities in HIGH/MODERATE reliability
* **Red flags:** FUTURE_DATE <1%, OVERCLAIMING 5-10%, MISMATCH 2-5%

### Scoring Formula
```
Combined Score = (Confidence × 60%) + (Data Quality × 40%)

Where Confidence = 
  (Plausibility × 45%) + 
  (District Outcomes × 30%) + 
  (Freshness × 15%) + 
  (Geographic Match × 10%)

And Plausibility = 
  (Name-Claim Alignment × 20%) + 
  (Volume × 25%) + 
  (Balance × 15%) + 
  (Social × 15%) + 
  (Location × 15%) + 
  (Contact × 10%)
```

---

## Data Quality Considerations

**NFHS-5 Data Issue:** The district health indicators table contains STRING columns with bracket notation indicating unreliable estimates. See [NFHS Bracket Notation Issue](../docs/data-quality/nfhs-bracket-notation-issue.md) for parsing requirements.

**Facility Data Quality:** 83% of facilities lack reliable freshness data. See [Virtue Foundation EDA](../docs/data-quality/virtue-foundation-eda.md) for complete analysis.

---

## Implementation Status

- [x] Architecture specification complete
- [x] Bronze layer plan complete
- [x] Silver layer plan complete
- [x] Gold layer plan complete
- [x] Deployment guide complete
- [ ] Bronze layer implemented
- [ ] Silver layer implemented
- [ ] Gold layer implemented
- [ ] Pipeline deployed to production
- [ ] Monitoring configured

---

## Next Steps

### For Implementers

1. Navigate to pipeline notebook: `/Workspace/Users/richthai92@gmail.com/DAIS-2026-AI-for-Good/facility_validation_framework`
2. Start with [Bronze Layer Plan](./implementation-plans/bronze-layer.md)
3. Follow step-by-step implementation
4. Test and validate each layer before proceeding
5. Deploy using [Deployment Guide](./implementation-plans/deployment.md)

### After Pipeline Deployment

**→ [Proceed to Phase 2: App Implementation](../phase-2-app/)**

The app depends on this pipeline's output tables in the `validation` schema.

---

## Support & Resources

**Pipeline Editor:** `/editor/pipelines/27fea50d-7b95-4540-b673-a0c8c92fe08d`

**Documentation Location:** `/Workspace/Users/richthai92@gmail.com/DAIS-2026-AI-for-Good/phase-1-pipeline/`

**For detailed architecture and scoring logic, see [architecture.md](./architecture.md)**
```

- [ ] **Step 4: Verify README created and content correct**

Expected: Phase 1 README exists with consolidated content from old README

---

### Task 8: Write Phase 2 App README

**Files:**
* Create: `/Users/richthai92@gmail.com/DAIS-2026-AI-for-Good/phase-2-app/README.md`
* Reference: `docs/demo-script.md` (to consolidate demo content)

- [ ] **Step 1: Read demo script for consolidation**

Read `/Users/richthai92@gmail.com/DAIS-2026-AI-for-Good/docs/demo-script.md` to extract demo content

- [ ] **Step 2: Create phase-2-app README file**

Using createAsset with assetType="file"

- [ ] **Step 3: Write README content (with demo script)**

Content to write:

```markdown
# Phase 2: Live Validation App

**← [Back to Project Overview](../README.md)**

---

## Overview

Real-time volunteer verification and patient matching app using trust scores from Phase 1 pipeline.

**App Type:** Databricks App (Streamlit)

**Prerequisites:** Phase 1 pipeline must be complete and deployed

---

## Purpose

Ongoing data validation through community volunteers, paired with intelligent patient matching:

1. **Volunteer Portal** - Verify facility data using AI-generated scripts
2. **Patient Search** - Match patients to trustworthy facilities based on symptoms and proximity

**Phase 1 provides the initial scores; Phase 2 keeps them current through continuous validation.**

---

## Architecture Summary

### Components

**Volunteer Portal:**
* Search and browse facilities needing verification
* AI-generated verification scripts (progressive based on risk)
* Yes/no validation forms
* Real-time trust score updates

**Patient Search:**
* Natural language symptom input
* AI-powered symptom → specialty matching
* Geospatial facility ranking
* Interactive map + results sidebar

**AI Agents (MLflow):**
* **Script Generator** - Analyzes facility risk, creates custom verification questions
* **Symptom Matcher** - Interprets symptoms, maps to specialties and capabilities

**Operational Database (Lakebase):**
* `facilities_verified` - 10K facilities with trust scores (geospatially indexed)
* `volunteer_validations` - Real-time validation submissions
* `verification_queue` - Facilities needing verification with AI scripts

**Full architecture:** [architecture.md](./architecture.md)

---

## Component Specifications

* **[Components](./components.md)** - Detailed specs for Volunteer Portal, Patient App, and AI Agents
* **[Data Schema](./data-schema.md)** - Lakebase operational tables and score recalculation logic
* **[Implementation Plan](./implementation-plan.md)** - Step-by-step build phases

---

## Demo Script (3-Minute Pitch)

### Pre-Demo Checklist

- [ ] Databricks App running and loaded
- [ ] Demo data seeded (Heritage Hospitals at trust score 0.68)
- [ ] Browser window maximized
- [ ] Volunteer tab open first

### The Hook (30 seconds)

> "Imagine you're having chest pain in Varanasi. You search online for a cardiologist and find Heritage Hospitals claiming to have top cardiac care. You travel 2 hours to get there. When you arrive, you discover they closed their cardiology department last year. You've wasted time, money, and in an emergency, this delay could cost your life.
> 
> **This is the reality for millions in India today.**
>
> We have 10,000 healthcare facilities with self-reported capabilities. **83% lack reliable freshness data.** Only 17% have been recently validated. Over 8,200 facilities need verification right now.
>
> **HealthVerify India solves this through community-driven validation powered by AI agents.**"

### Architecture (45 seconds)

> "Here's how it works. We built a single Databricks App with two interfaces.
> 
> **Volunteer Portal** - where volunteers verify facility data using AI-generated scripts.
> 
> **Patient Search** - where patients find trustworthy care based on symptoms and proximity.
> 
> The operational layer is **Lakebase** - handling real-time reads and writes for 10,000 facilities with sub-second geospatial queries. Two **MLflow AI agents** power the intelligence: one generates smart verification scripts based on facility risk, the other interprets patient symptoms in natural language.
> 
> In the future, we'll sync data back to **Unity Catalog** for governance, ML model training, and historical analytics.
> 
> Now let me show you the complete cycle in action."

### Part 1: Volunteer Validation (15 seconds)

**Switch to Volunteer Portal tab**

> "I'm a volunteer. Let me search for Heritage Hospitals in Varanasi."

**Action:** Type "Heritage Hospitals" in search bar

> "Here it is - **trust score 0.68, flagged as SUSPICIOUS** with 200 capability claims. Let me verify this facility."

**Action:** Click "Verify Now"

> "Look at this - our AI agent analyzed the facility's risk profile and generated a **custom verification script**. Basic questions for everyone, but because this facility has suspicious volume claims, we get progressive questions about their top specialties."

**Action:** Scroll through the script (3 seconds)

> "As a volunteer, I call the facility, verify the claims, and fill out this simple yes/no form."

**Action:** Check 13 boxes (quickly), uncheck 2, click "Submit Validation"

> "Submitted. Watch the trust score update in real time..."

**Visual:** Show success message with score change: 0.68 → 0.737

> "**0.68 to 0.74!** This facility is now marked as FRESH."

### Part 2: Patient Impact (45 seconds)

**Switch to Patient Search tab**

> "Now here's the impact. I'm a patient with heart pain near Varanasi."

**Action:** Type "Heart pain, trouble breathing" in text area, select "Varanasi" location

> "Our **Symptom Matcher Agent** interprets this in natural language and maps it to cardiology, emergency medicine, critical care."

**Action:** Click "Find Care"

**Visual:** Map loads with facility markers

> "Look at the map - facilities appear, but Heritage Hospitals is **now in the top 3** with this big green verified badge."

**Action:** Highlight the top 3 pins, point to Heritage Hospitals

> "**Before our volunteer's validation 30 seconds ago**, Heritage Hospitals had a trust score of 0.68 - it was **filtered out entirely** because we don't show facilities below our 0.75 safety threshold. Patients never saw it.
>
> **After validation**, trust score jumped to 0.74, and with one more validation it crosses the threshold. By the third validation, it reaches 0.88 and ranks #2 for cardiology near Varanasi."

**Action:** Click on Heritage Hospitals marker/card

> "When I click, I see: 'Recently verified by volunteer, 87% of claims confirmed.' I can call them, get directions, and trust I'm going to the right place.
>
> **This is how volunteer validation directly protects patients and saves lives.**"

### ROI & Impact (30 seconds)

> "Let's talk impact.
>
> **Operational Efficiency:** Our AI pre-validation means volunteers don't waste time calling dead numbers. We've reduced validation time by 60% compared to manual processes.
>
> **Scale:** With 1,000 volunteers using this system, we can verify the entire database of 10,000 facilities in just 3 months. Each volunteer verifies 3-4 facilities per week.
>
> **Patient Outcomes:** Patients get the right care, at the right place, the first time. We project a 40% reduction in wasted travel time and significantly improved emergency response.
>
> **Data Quality:** We're building toward the gold standard - 95% of facilities with trust scores above 0.80, continuously maintained through recurring verification cycles."

### Next Steps (15 seconds)

> "Our roadmap is clear.
>
> **Phase 1** - Production deployment: Lakeflow pipeline syncs Lakebase to Unity Catalog nightly for governance and audit trails.
>
> **Phase 2** - Multi-modal interface: Voice input in Hindi, Tamil, Telugu, Bengali - reaching low-literacy users in rural areas.
>
> **Phase 3** - ML-based scoring: Train models on historical validation patterns to improve risk assessment and prioritization.
>
> This is HealthVerify India - **trusted healthcare access through community-verified data, powered by Databricks.**
>
> Thank you."

### Timing Breakdown

| Section | Time | Cumulative |
|---------|------|------------|
| Hook | 30s | 0:30 |
| Architecture | 45s | 1:15 |
| Demo - Volunteer | 15s | 1:30 |
| Demo - Patient | 45s | 2:15 |
| ROI & Impact | 30s | 2:45 |
| Next Steps | 15s | 3:00 |

---

## Implementation Status

- [x] Architecture design complete
- [x] Component specifications complete
- [x] Data schema defined
- [x] Demo script written
- [ ] AI agents implemented (Script Generator, Symptom Matcher)
- [ ] Databricks App scaffolding
- [ ] Volunteer Portal implemented
- [ ] Patient Search implemented
- [ ] Lakebase schema setup
- [ ] Data seeding (Phase 1 → Lakebase sync)
- [ ] Demo data preparation

---

## Prerequisites

**Phase 1 must be complete:**
* Pipeline deployed and running
* Gold tables populated in `validation` schema
* Trust scores computed for all facilities

**Before starting Phase 2 implementation:**
1. Verify Phase 1 pipeline has run successfully
2. Confirm `validation.*` tables exist and contain data
3. Review [Data Schema](./data-schema.md) for Lakebase sync requirements

---

## Next Steps

### For Implementation

Follow the [Implementation Plan](./implementation-plan.md) step-by-step:

1. Set up Lakebase database
2. Seed initial data from Phase 1 tables
3. Build AI agents (MLflow)
4. Develop Databricks App (Streamlit)
5. Test end-to-end flow
6. Prepare demo

### For Demo Preparation

1. Practice demo script (3 minutes)
2. Prepare Heritage Hospitals as demo facility
3. Test volunteer → patient flow
4. Have backup screenshots ready
5. Review judge Q&A prep (see full demo script)

---

## Support & Resources

**App Location:** `/Workspace/Users/richthai92@gmail.com/DAIS-2026-AI-for-Good/` (future)

**Documentation Location:** `/Workspace/Users/richthai92@gmail.com/DAIS-2026-AI-for-Good/phase-2-app/`

**← [Return to Phase 1: Pipeline](../phase-1-pipeline/) if pipeline not yet complete**
```

- [ ] **Step 4: Verify README created and content correct**

Expected: Phase 2 README exists with demo script consolidated

---

## Phase C: Move Files

### Task 9: Move Data Quality File (NFHS)

**Files:**
* Source: `/Users/richthai92@gmail.com/DAIS-2026-AI-for-Good/virtue_foundation_data_quality_addendum.md`
* Destination: `/Users/richthai92@gmail.com/DAIS-2026-AI-for-Good/docs/data-quality/nfhs-bracket-notation-issue.md`

- [ ] **Step 1: Read source file content**

Read `/Users/richthai92@gmail.com/DAIS-2026-AI-for-Good/virtue_foundation_data_quality_addendum.md`

- [ ] **Step 2: Create destination file**

Using createAsset with assetType="file", name="docs/data-quality/nfhs-bracket-notation-issue.md"

- [ ] **Step 3: Write content to destination**

Using workspaceUpdateFile with exact content from source file

- [ ] **Step 4: Verify file moved correctly**

Expected: New file exists at `docs/data-quality/nfhs-bracket-notation-issue.md` with identical content

- [ ] **Step 5: Delete source file**

Delete `/Users/richthai92@gmail.com/DAIS-2026-AI-for-Good/virtue_foundation_data_quality_addendum.md`

---

### Task 10: Move Data Quality File (EDA)

**Files:**
* Source: `/Users/richthai92@gmail.com/DAIS-2026-AI-for-Good/virtue_foundation_eda_handoff.md`
* Destination: `/Users/richthai92@gmail.com/DAIS-2026-AI-for-Good/docs/data-quality/virtue-foundation-eda.md`

- [ ] **Step 1: Read source file content**

Read `/Users/richthai92@gmail.com/DAIS-2026-AI-for-Good/virtue_foundation_eda_handoff.md`

- [ ] **Step 2: Create destination file**

Using createAsset with assetType="file", name="docs/data-quality/virtue-foundation-eda.md"

- [ ] **Step 3: Write content to destination**

Using workspaceUpdateFile with exact content from source file

- [ ] **Step 4: Verify file moved correctly**

Expected: New file exists at `docs/data-quality/virtue-foundation-eda.md` with identical content

- [ ] **Step 5: Delete source file**

Delete `/Users/richthai92@gmail.com/DAIS-2026-AI-for-Good/virtue_foundation_eda_handoff.md`

---

### Task 11: Move Design File

**Files:**
* Source: `/Users/richthai92@gmail.com/DAIS-2026-AI-for-Good/2026-06-15-healthverify-india-design.md`
* Destination: `/Users/richthai92@gmail.com/DAIS-2026-AI-for-Good/docs/design/2026-06-15-healthverify-india-design.md`

- [ ] **Step 1: Read source file content**

Read `/Users/richthai92@gmail.com/DAIS-2026-AI-for-Good/2026-06-15-healthverify-india-design.md`

- [ ] **Step 2: Create destination file**

Using createAsset with assetType="file", name="docs/design/2026-06-15-healthverify-india-design.md"

- [ ] **Step 3: Write content to destination**

Using workspaceUpdateFile with exact content from source file

- [ ] **Step 4: Verify file moved correctly**

Expected: New file exists at `docs/design/2026-06-15-healthverify-india-design.md` with identical content

- [ ] **Step 5: Delete source file**

Delete `/Users/richthai92@gmail.com/DAIS-2026-AI-for-Good/2026-06-15-healthverify-india-design.md`

---

### Task 12: Move Pipeline Architecture File

**Files:**
* Source: `/Users/richthai92@gmail.com/DAIS-2026-AI-for-Good/docs/superpowers/plans/2025-01-15-facility-validation-pipeline-architecture.md`
* Destination: `/Users/richthai92@gmail.com/DAIS-2026-AI-for-Good/phase-1-pipeline/architecture.md`

- [ ] **Step 1: Read source file content**

Read `/Users/richthai92@gmail.com/DAIS-2026-AI-for-Good/docs/superpowers/plans/2025-01-15-facility-validation-pipeline-architecture.md`

- [ ] **Step 2: Create destination file**

Using createAsset with assetType="file", name="phase-1-pipeline/architecture.md"

- [ ] **Step 3: Write content to destination**

Using workspaceUpdateFile with exact content from source file

- [ ] **Step 4: Verify file moved correctly**

Expected: New file exists at `phase-1-pipeline/architecture.md` with identical content (date prefix removed from filename)

- [ ] **Step 5: Delete source file**

Delete `/Users/richthai92@gmail.com/DAIS-2026-AI-for-Good/docs/superpowers/plans/2025-01-15-facility-validation-pipeline-architecture.md`

---

### Task 13: Move Pipeline Bronze Layer Plan

**Files:**
* Source: `/Users/richthai92@gmail.com/DAIS-2026-AI-for-Good/docs/superpowers/plans/2025-01-15-facility-validation-bronze-layer.md`
* Destination: `/Users/richthai92@gmail.com/DAIS-2026-AI-for-Good/phase-1-pipeline/implementation-plans/bronze-layer.md`

- [ ] **Step 1: Read source file content**

Read `/Users/richthai92@gmail.com/DAIS-2026-AI-for-Good/docs/superpowers/plans/2025-01-15-facility-validation-bronze-layer.md`

- [ ] **Step 2: Create destination file**

Using createAsset with assetType="file", name="phase-1-pipeline/implementation-plans/bronze-layer.md"

- [ ] **Step 3: Write content to destination**

Using workspaceUpdateFile with exact content from source file

- [ ] **Step 4: Verify file moved correctly**

Expected: New file exists at `phase-1-pipeline/implementation-plans/bronze-layer.md` with identical content

- [ ] **Step 5: Delete source file**

Delete `/Users/richthai92@gmail.com/DAIS-2026-AI-for-Good/docs/superpowers/plans/2025-01-15-facility-validation-bronze-layer.md`

---

### Task 14: Move Pipeline Silver Layer Plan

**Files:**
* Source: `/Users/richthai92@gmail.com/DAIS-2026-AI-for-Good/docs/superpowers/plans/2025-01-15-facility-validation-silver-layer.md`
* Destination: `/Users/richthai92@gmail.com/DAIS-2026-AI-for-Good/phase-1-pipeline/implementation-plans/silver-layer.md`

- [ ] **Step 1: Read source file content**

Read `/Users/richthai92@gmail.com/DAIS-2026-AI-for-Good/docs/superpowers/plans/2025-01-15-facility-validation-silver-layer.md`

- [ ] **Step 2: Create destination file**

Using createAsset with assetType="file", name="phase-1-pipeline/implementation-plans/silver-layer.md"

- [ ] **Step 3: Write content to destination**

Using workspaceUpdateFile with exact content from source file

- [ ] **Step 4: Verify file moved correctly**

Expected: New file exists at `phase-1-pipeline/implementation-plans/silver-layer.md` with identical content

- [ ] **Step 5: Delete source file**

Delete `/Users/richthai92@gmail.com/DAIS-2026-AI-for-Good/docs/superpowers/plans/2025-01-15-facility-validation-silver-layer.md`

---

### Task 15: Move Pipeline Gold Layer Plan

**Files:**
* Source: `/Users/richthai92@gmail.com/DAIS-2026-AI-for-Good/docs/superpowers/plans/2025-01-15-facility-validation-gold-layer.md`
* Destination: `/Users/richthai92@gmail.com/DAIS-2026-AI-for-Good/phase-1-pipeline/implementation-plans/gold-layer.md`

- [ ] **Step 1: Read source file content**

Read `/Users/richthai92@gmail.com/DAIS-2026-AI-for-Good/docs/superpowers/plans/2025-01-15-facility-validation-gold-layer.md`

- [ ] **Step 2: Create destination file**

Using createAsset with assetType="file", name="phase-1-pipeline/implementation-plans/gold-layer.md"

- [ ] **Step 3: Write content to destination**

Using workspaceUpdateFile with exact content from source file

- [ ] **Step 4: Verify file moved correctly**

Expected: New file exists at `phase-1-pipeline/implementation-plans/gold-layer.md` with identical content

- [ ] **Step 5: Delete source file**

Delete `/Users/richthai92@gmail.com/DAIS-2026-AI-for-Good/docs/superpowers/plans/2025-01-15-facility-validation-gold-layer.md`

---

### Task 16: Move Pipeline Deployment Guide

**Files:**
* Source: `/Users/richthai92@gmail.com/DAIS-2026-AI-for-Good/docs/superpowers/plans/2025-01-15-facility-validation-deployment.md`
* Destination: `/Users/richthai92@gmail.com/DAIS-2026-AI-for-Good/phase-1-pipeline/implementation-plans/deployment.md`

- [ ] **Step 1: Read source file content**

Read `/Users/richthai92@gmail.com/DAIS-2026-AI-for-Good/docs/superpowers/plans/2025-01-15-facility-validation-deployment.md`

- [ ] **Step 2: Create destination file**

Using createAsset with assetType="file", name="phase-1-pipeline/implementation-plans/deployment.md"

- [ ] **Step 3: Write content to destination**

Using workspaceUpdateFile with exact content from source file

- [ ] **Step 4: Verify file moved correctly**

Expected: New file exists at `phase-1-pipeline/implementation-plans/deployment.md` with identical content

- [ ] **Step 5: Delete source file**

Delete `/Users/richthai92@gmail.com/DAIS-2026-AI-for-Good/docs/superpowers/plans/2025-01-15-facility-validation-deployment.md`

---

### Task 17: Move App Architecture File

**Files:**
* Source: `/Users/richthai92@gmail.com/DAIS-2026-AI-for-Good/docs/architecture.md`
* Destination: `/Users/richthai92@gmail.com/DAIS-2026-AI-for-Good/phase-2-app/architecture.md`

- [ ] **Step 1: Read source file content**

Read `/Users/richthai92@gmail.com/DAIS-2026-AI-for-Good/docs/architecture.md`

- [ ] **Step 2: Create destination file**

Using createAsset with assetType="file", name="phase-2-app/architecture.md"

- [ ] **Step 3: Write content to destination**

Using workspaceUpdateFile with exact content from source file

- [ ] **Step 4: Verify file moved correctly**

Expected: New file exists at `phase-2-app/architecture.md` with identical content

- [ ] **Step 5: Delete source file**

Delete `/Users/richthai92@gmail.com/DAIS-2026-AI-for-Good/docs/architecture.md`

---

### Task 18: Move App Components File

**Files:**
* Source: `/Users/richthai92@gmail.com/DAIS-2026-AI-for-Good/docs/components.md`
* Destination: `/Users/richthai92@gmail.com/DAIS-2026-AI-for-Good/phase-2-app/components.md`

- [ ] **Step 1: Read source file content**

Read `/Users/richthai92@gmail.com/DAIS-2026-AI-for-Good/docs/components.md`

- [ ] **Step 2: Create destination file**

Using createAsset with assetType="file", name="phase-2-app/components.md"

- [ ] **Step 3: Write content to destination**

Using workspaceUpdateFile with exact content from source file

- [ ] **Step 4: Verify file moved correctly**

Expected: New file exists at `phase-2-app/components.md` with identical content

- [ ] **Step 5: Delete source file**

Delete `/Users/richthai92@gmail.com/DAIS-2026-AI-for-Good/docs/components.md`

---

### Task 19: Move App Data Schema File

**Files:**
* Source: `/Users/richthai92@gmail.com/DAIS-2026-AI-for-Good/docs/data-schema.md`
* Destination: `/Users/richthai92@gmail.com/DAIS-2026-AI-for-Good/phase-2-app/data-schema.md`

- [ ] **Step 1: Read source file content**

Read `/Users/richthai92@gmail.com/DAIS-2026-AI-for-Good/docs/data-schema.md`

- [ ] **Step 2: Create destination file**

Using createAsset with assetType="file", name="phase-2-app/data-schema.md"

- [ ] **Step 3: Write content to destination**

Using workspaceUpdateFile with exact content from source file

- [ ] **Step 4: Verify file moved correctly**

Expected: New file exists at `phase-2-app/data-schema.md` with identical content

- [ ] **Step 5: Delete source file**

Delete `/Users/richthai92@gmail.com/DAIS-2026-AI-for-Good/docs/data-schema.md`

---

### Task 20: Move App Implementation Plan File

**Files:**
* Source: `/Users/richthai92@gmail.com/DAIS-2026-AI-for-Good/docs/implementation-plan.md`
* Destination: `/Users/richthai92@gmail.com/DAIS-2026-AI-for-Good/phase-2-app/implementation-plan.md`

- [ ] **Step 1: Read source file content**

Read `/Users/richthai92@gmail.com/DAIS-2026-AI-for-Good/docs/implementation-plan.md`

- [ ] **Step 2: Create destination file**

Using createAsset with assetType="file", name="phase-2-app/implementation-plan.md"

- [ ] **Step 3: Write content to destination**

Using workspaceUpdateFile with exact content from source file

- [ ] **Step 4: Verify file moved correctly**

Expected: New file exists at `phase-2-app/implementation-plan.md` with identical content

- [ ] **Step 5: Delete source file**

Delete `/Users/richthai92@gmail.com/DAIS-2026-AI-for-Good/docs/implementation-plan.md`

---

## Phase D: Cleanup

### Task 21: Delete Obsolete README (Pipeline)

**Files:**
* Delete: `/Users/richthai92@gmail.com/DAIS-2026-AI-for-Good/docs/superpowers/plans/README-facility-validation-pipeline.md`

- [ ] **Step 1: Verify content was merged into phase-1-pipeline/README.md**

Confirm phase-1-pipeline/README.md exists and contains consolidated content

- [ ] **Step 2: Delete obsolete file**

Delete `/Users/richthai92@gmail.com/DAIS-2026-AI-for-Good/docs/superpowers/plans/README-facility-validation-pipeline.md`

- [ ] **Step 3: Verify file deleted**

Expected: File no longer exists

---

### Task 22: Delete Obsolete Demo Script

**Files:**
* Delete: `/Users/richthai92@gmail.com/DAIS-2026-AI-for-Good/docs/demo-script.md`

- [ ] **Step 1: Verify content was merged into phase-2-app/README.md**

Confirm phase-2-app/README.md exists and contains demo script content

- [ ] **Step 2: Delete obsolete file**

Delete `/Users/richthai92@gmail.com/DAIS-2026-AI-for-Good/docs/demo-script.md`

- [ ] **Step 3: Verify file deleted**

Expected: File no longer exists

---

### Task 23: Delete Empty Python File

**Files:**
* Delete: `/Users/richthai92@gmail.com/DAIS-2026-AI-for-Good/New File 2026-06-15 16_04_34.py`

- [ ] **Step 1: Verify file is empty**

Read file to confirm it contains no meaningful content

- [ ] **Step 2: Delete empty file**

Delete `/Users/richthai92@gmail.com/DAIS-2026-AI-for-Good/New File 2026-06-15 16_04_34.py`

- [ ] **Step 3: Verify file deleted**

Expected: File no longer exists

---

### Task 24: Delete Empty Pipeline File

**Files:**
* Delete: `/Users/richthai92@gmail.com/DAIS-2026-AI-for-Good/docs/superpowers/plans/2026-06-15-facility-validation-pipeline.md`

- [ ] **Step 1: Verify file is empty**

Read file to confirm it contains no meaningful content

- [ ] **Step 2: Delete empty file**

Delete `/Users/richthai92@gmail.com/DAIS-2026-AI-for-Good/docs/superpowers/plans/2026-06-15-facility-validation-pipeline.md`

- [ ] **Step 3: Verify file deleted**

Expected: File no longer exists

---

### Task 25: Delete Empty Plans Directory

**Files:**
* Delete: `/Users/richthai92@gmail.com/DAIS-2026-AI-for-Good/docs/superpowers/plans/`

- [ ] **Step 1: List directory contents**

List files in `/Users/richthai92@gmail.com/DAIS-2026-AI-for-Good/docs/superpowers/plans/` to confirm it's empty

- [ ] **Step 2: Delete empty directory**

Delete directory `/Users/richthai92@gmail.com/DAIS-2026-AI-for-Good/docs/superpowers/plans/`

- [ ] **Step 3: Verify directory deleted**

Expected: Directory no longer exists

---

### Task 26: Delete Empty Superpowers Directory

**Files:**
* Delete: `/Users/richthai92@gmail.com/DAIS-2026-AI-for-Good/docs/superpowers/`

- [ ] **Step 1: List directory contents**

List files in `/Users/richthai92@gmail.com/DAIS-2026-AI-for-Good/docs/superpowers/` to confirm it's empty

- [ ] **Step 2: Delete empty directory**

Delete directory `/Users/richthai92@gmail.com/DAIS-2026-AI-for-Good/docs/superpowers/`

- [ ] **Step 3: Verify directory deleted**

Expected: Directory no longer exists

---

## Phase E: Verification

### Task 27: Verify All Links in Root README

**Files:**
* Verify: `/Users/richthai92@gmail.com/DAIS-2026-AI-for-Good/README.md`

- [ ] **Step 1: Read root README**

Read `/Users/richthai92@gmail.com/DAIS-2026-AI-for-Good/README.md`

- [ ] **Step 2: Check all markdown links**

Verify each link points to an existing file or directory:
* `./phase-1-pipeline/` → should exist
* `./phase-2-app/` → should exist
* `./docs/design/2026-06-15-healthverify-india-design.md` → should exist
* `./docs/data-quality/` → should exist

- [ ] **Step 3: Document any broken links**

Expected: All links work, no 404s

---

### Task 28: Verify All Links in Phase 1 README

**Files:**
* Verify: `/Users/richthai92@gmail.com/DAIS-2026-AI-for-Good/phase-1-pipeline/README.md`

- [ ] **Step 1: Read Phase 1 README**

Read `/Users/richthai92@gmail.com/DAIS-2026-AI-for-Good/phase-1-pipeline/README.md`

- [ ] **Step 2: Check all markdown links**

Verify each link points to an existing file:
* `./architecture.md` → should exist
* `./implementation-plans/bronze-layer.md` → should exist
* `./implementation-plans/silver-layer.md` → should exist
* `./implementation-plans/gold-layer.md` → should exist
* `./implementation-plans/deployment.md` → should exist
* `../phase-2-app/` → should exist
* `../docs/data-quality/nfhs-bracket-notation-issue.md` → should exist
* `../docs/data-quality/virtue-foundation-eda.md` → should exist

- [ ] **Step 3: Document any broken links**

Expected: All links work, no 404s

---

### Task 29: Verify All Links in Phase 2 README

**Files:**
* Verify: `/Users/richthai92@gmail.com/DAIS-2026-AI-for-Good/phase-2-app/README.md`

- [ ] **Step 1: Read Phase 2 README**

Read `/Users/richthai92@gmail.com/DAIS-2026-AI-for-Good/phase-2-app/README.md`

- [ ] **Step 2: Check all markdown links**

Verify each link points to an existing file:
* `./architecture.md` → should exist
* `./components.md` → should exist
* `./data-schema.md` → should exist
* `./implementation-plan.md` → should exist
* `../phase-1-pipeline/` → should exist

- [ ] **Step 3: Document any broken links**

Expected: All links work, no 404s

---

### Task 30: Test Navigation Flow

**Files:**
* Navigate: Root → Phase 1 → Phase 2

- [ ] **Step 1: Start at root README**

Open `/Users/richthai92@gmail.com/DAIS-2026-AI-for-Good/README.md`

- [ ] **Step 2: Navigate to Phase 1**

Follow link to `./phase-1-pipeline/` and open README

- [ ] **Step 3: Navigate to implementation plan**

From Phase 1 README, follow link to `./implementation-plans/bronze-layer.md`

- [ ] **Step 4: Navigate back to Phase 1 README**

Verify breadcrumb or back navigation works

- [ ] **Step 5: Navigate to Phase 2**

From Phase 1 README, follow link to `../phase-2-app/`

- [ ] **Step 6: Navigate to architecture**

From Phase 2 README, follow link to `./architecture.md`

- [ ] **Step 7: Navigate back to root**

From Phase 2 README, follow link to `../README.md`

Expected: All navigation paths work smoothly, no dead ends

---

### Task 31: Verify Content Preservation

**Files:**
* Verify: All moved files

- [ ] **Step 1: Compare file counts**

Original file count: 17 files
New structure file count: Should be 17+ (includes new READMEs)

- [ ] **Step 2: Spot-check moved file content**

Pick 3 random moved files, verify content matches source

- [ ] **Step 3: Verify no truncation**

Check file sizes - moved files should be same size as originals

- [ ] **Step 4: Document any issues**

Expected: All content preserved, no information loss

---

### Task 32: Final Directory Structure Verification

**Files:**
* Verify: Entire repository structure

- [ ] **Step 1: List root directory**

List `/Users/richthai92@gmail.com/DAIS-2026-AI-for-Good/` to verify structure

Expected structure:
```
DAIS-2026-AI-for-Good/
├── README.md
├── docs/
│   ├── data-quality/
│   ├── design/
│   └── specs/
├── phase-1-pipeline/
│   ├── README.md
│   ├── architecture.md
│   └── implementation-plans/
└── phase-2-app/
    ├── README.md
    ├── architecture.md
    ├── components.md
    ├── data-schema.md
    └── implementation-plan.md
```

- [ ] **Step 2: Verify all expected directories exist**

* docs/data-quality/ ✓
* docs/design/ ✓
* docs/specs/ ✓
* phase-1-pipeline/ ✓
* phase-1-pipeline/implementation-plans/ ✓
* phase-2-app/ ✓

- [ ] **Step 3: Verify obsolete directories deleted**

* docs/superpowers/plans/ ✗ (should not exist)
* docs/superpowers/ ✗ (should not exist)

- [ ] **Step 4: Verify all expected files exist**

Check file counts per directory match expectations

- [ ] **Step 5: Document final structure**

Expected: Clean phase-based structure, no orphaned files, all obsolete content removed

---

## Success Criteria

### Structure
* ✅ 6 directories created successfully
* ✅ 3 new READMEs created with consolidated content
* ✅ 12 files moved to new locations
* ✅ 4 obsolete files deleted
* ✅ 2 empty directories deleted

### Documentation
* ✅ Root README provides project overview and navigation
* ✅ Phase 1 README consolidates pipeline documentation
* ✅ Phase 2 README includes demo script
* ✅ All cross-references updated and working

### Verification
* ✅ All links verified (root, phase-1, phase-2)
* ✅ Navigation flow tested end-to-end
* ✅ Content preservation confirmed
* ✅ Final structure matches design spec

---

## Post-Implementation Notes

After completing all tasks, the repository will have a clear phase-based structure that:

* Communicates sequential dependency (Phase 1 → Phase 2)
* Provides self-contained phase documentation
* Consolidates related content
* Eliminates orphaned files
* Maintains complete content history (via git)

**Total Tasks:** 32
**Total Steps:** 143
**Estimated Time:** 3-4 hours (with verification)

---

**Plan created with superpowers:writing-plans skill**
