# HealthVerify India - Hackathon Design Document

**Project:** Trusted Healthcare Access Through Community-Verified Facility Data  
**Hackathon:** Databricks Apps & Agents for Good 2026  
**Date:** 2026-06-15  
**Team:** [Your Team Name]

---

## Overview

HealthVerify India is an end-to-end system that ensures patients find trustworthy healthcare facilities through community-driven data validation powered by AI agents.

### The Problem

India has 10,000+ healthcare facilities with self-reported capabilities, specialties, and contact information. Current data quality issues:

- **Data quality concerns** including suspicious volume claims, incomplete data, and mismatched specialties
- **83% lack reliable freshness data** (64.5% have no update date, 18.2% are stale or aging)
- **Only 17.3% are recently validated as "FRESH"**
- **No verification mechanism** for patients to trust the information

### Real-World Impact

- Patients waste time and money traveling to facilities that don't have claimed capabilities
- Emergency cases risk dangerous delays when directed to inadequate facilities  
- Legitimate facilities lose trust due to ecosystem-wide data quality issues
- **Over 8,200 facilities** need verification or re-verification

### The Solution

A dual-platform system built on Databricks:

1. **Volunteer Verification Portal** - Community-driven data validation with AI-assisted script generation
2. **Patient Matching App** - Trust-scored facility recommendations based on symptoms and proximity

Both interfaces are combined in a single Databricks App, backed by Lakebase for operational performance and Unity Catalog for analytical governance.

---

## Documentation Structure

This design is split across multiple documents:

1. **[Architecture](./docs/architecture.md)** - System architecture, data flow, and component interaction
2. **[Components](./docs/components.md)** - Detailed specifications for Volunteer Portal, Patient App, and AI Agents
3. **[Data Schema](./docs/data-schema.md)** - Lakebase operational tables and Lakehouse analytical layer
4. **[Implementation Plan](./docs/implementation-plan.md)** - Build phases, tech stack, and future roadmap
5. **[Demo Script](./docs/demo-script.md)** - 3-minute pitch structure for hackathon judges

---

## Quick Start

### Data Sources
- Catalog: `dais2026`
- Schemas: `raw`, `virtue_foundation_cleaned`, `validation`
- Total Facilities: 10,088
- Validation Scores: 9,973 facilities scored

### Demo Facility Example
- **Heritage Hospitals, Varanasi**
- Current trust score: **0.68** (SUSPICIOUS_VOLUME, STALE)
- 200 capability claims
- After volunteer validation → trust score improves to **0.88+**
- **Impact:** Jumps from filtered out to top 3 results for patients

### Key Metrics
- 6,431 facilities with NO_DATE (64.5%)
- 1,815 facilities STALE or AGING (18.2%)
- 294 facilities SUSPICIOUS_VOLUME (2.9%)
- 269 facilities INCOMPLETE_DATA (2.7%)

---

## Success Criteria

**For Hackathon Demo:**
- ✅ Volunteer can search and verify a facility in <60 seconds
- ✅ Trust score updates in real-time after validation
- ✅ Patient sees different results before/after validation
- ✅ Top 3 facilities clearly highlighted on map
- ✅ Connected flow shows data quality → patient safety impact

**For Production (Future):**
- 1,000 volunteers verify entire database in 3 months
- 95% of facilities have trust score ≥ 0.80
- Patient satisfaction: 85%+ report finding appropriate care
- Reduce wasted travel by 40%

---

## Next Steps

1. Review [Architecture](./docs/architecture.md) document
2. Review [Components](./docs/components.md) specifications
3. Set up Lakebase schema per [Data Schema](./docs/data-schema.md)
4. Follow [Implementation Plan](./docs/implementation-plan.md)
5. Practice [Demo Script](./docs/demo-script.md) for 3-minute pitch
