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
