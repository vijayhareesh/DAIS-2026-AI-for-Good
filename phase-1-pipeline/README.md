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
