# System Architecture

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│          DATABRICKS APP (Single Streamlit App)              │
├──────────────────────────┬──────────────────────────────────┤
│   VOLUNTEER PORTAL       │   PATIENT MATCHING APP           │
│   - Verification queue   │   - Symptom input (free text)    │
│   - Search facilities    │   - Interactive map view         │
│   - AI-generated script  │   - Top 3 highlighted facilities │
│   - Yes/No validation    │   - Trust badges                 │
│   - Submit & see impact  │   - Click for details            │
└────────────┬─────────────┴─────────────┬────────────────────┘
             │                            │
             │         Fast I/O via Lakebase
             ▼                            ▼
    ┌────────────────────────────────────────────────────────┐
    │         AI AGENT LAYER (MLflow Agents)                 │
    │  🤖 Script Generator Agent                             │
    │     - Analyzes facility risk profile                   │
    │     - Generates progressive validation questions       │
    │  🤖 Symptom Matcher Agent                              │
    │     - Interprets patient symptoms (NLU)                │
    │     - Maps to medical specialties/capabilities         │
    └────────────────────────┬──────────────────────────────┘
                             │
    ┌────────────────────────┴──────────────────────────────┐
    │      LAKEBASE (Operational Database)                   │
    │  💾 facilities_verified                                │
    │     - 10K facilities with trust scores                 │
    │     - Geospatial indexed (lat/lon)                     │
    │  💾 volunteer_validations                              │
    │     - Real-time validation submissions                 │
    │  💾 verification_queue                                 │
    │     - Facilities needing verification                  │
    │     - AI-generated scripts                             │
    │  ⚡ Score Recalculation Logic                          │
    │     - Incremental weighted average with decay          │
    │     - Triggered on volunteer submission                │
    └────────────────┬───────────────────────────────────────┘
                     │
                     │ 🔮 FUTURE: Scheduled Sync Pipeline
                     ▼
    ┌────────────────────────────────────────────────────────┐
    │      LAKEHOUSE (Unity Catalog - Analytical Layer)      │
    │  📊 BRONZE - dais2026.raw.*                            │
    │     - Raw facility data, pincode directory             │
    │  📊 SILVER - dais2026.virtue_foundation_cleaned.*      │
    │     - Cleaned facilities, validation scores            │
    │  📊 GOLD - dais2026.analytics.* (Future)               │
    │     - Historical validation trends                     │
    │     - ML training datasets for scoring model (Phase D) │
    │     - Audit trails & governance                        │
    └────────────────────────────────────────────────────────┘
```

---

## Data Flow Walkthrough

### Initial Setup (One-time)

1. Load existing facility data from `dais2026.virtue_foundation_cleaned.facilities` + validation scores → **Lakebase**
2. Script Generator Agent creates initial verification queue for high-risk facilities:
   - NO_DATE freshness status (64.5% of facilities)
   - SUSPICIOUS_VOLUME or INCOMPLETE_DATA plausibility
   - User-reported issues (future trigger)

---

## Operational Flow (Demo Journey)

### Demo Example Facility
- **Heritage Hospitals, Varanasi**
- Current trust score: **0.68** (SUSPICIOUS_VOLUME, STALE)
- 200 capability claims
- After volunteer validation → trust score improves to **0.88+**

### Volunteer Side

**1. Search & Select**
- Volunteer opens portal → searches "Heritage Hospitals"
- Finds "Heritage Hospitals, Varanasi" with:
  - Current trust score: 0.68
  - Status: SUSPICIOUS_VOLUME, STALE
  - 200 capability claims

**2. View AI-Generated Script**
- Opens verification task, sees script:
  - **Basic Questions** (all facilities):
    - "Is this facility currently operational?"
    - "Can you confirm this phone number is correct?"
  - **Progressive Questions** (high-risk facilities):
    - "Verify top claimed specialties: cardiology, orthopedics, neurology"
    - "Does facility have ICU capacity as claimed?"

**3. Call & Validate**
- Volunteer calls facility using provided phone number
- Fills yes/no form: 13 verified ✅, 2 not available ❌

**4. Submit & Recalculate**
- Submission writes to `volunteer_validations` table in Lakebase
- **Lakebase triggers score recalculation**:
  - Validation rate: 13/15 = 87% positive
  - New trust score: `(0.68 * 0.7) + (0.87 * 0.3) = 0.737`
  - After 2-3 validations: score reaches **0.88**
  - Freshness status: STALE → FRESH

### Patient Side

**5. Enter Symptoms**
- Patient enters: "Heart specialist near Varanasi"

**6. AI Interpretation**
- Symptom Matcher Agent interprets → ["cardiology", "internalMedicine"]

**7. Query & Rank**
- SQL query filters Lakebase:
  - Capability match (facilities with cardiology)
  - Trust score ≥ 0.75 threshold (filters out suspicious facilities)
  - Geospatial distance from Varanasi
- Ranks by: `(trust_score * 0.6) + (1 / distance * 0.4)`

**8. Display Results**

**BEFORE validation:**
- Heritage Hospitals ranked #8 (trust score 0.68)
- **Filtered out** due to threshold (< 0.75)
- Patient doesn't see it in results

**AFTER validation:**
- Heritage Hospitals ranked #2 (trust score 0.88, FRESH status)
- Shows in **top 3 with verified badge** 🟢
- Larger pin on map, highlighted in sidebar

**9. Patient Action**
- Patient clicks "Heritage Hospitals" → sees:
  - "Recently verified by volunteer"
  - "87% of claims confirmed"
  - Contact details, address, map

---

## Connected Flow Impact

**The Core Narrative:**

```
Volunteer validates (15 sec)
    ↓
Trust score updates (automatic)
    ↓
Patient sees better results (45 sec)
    ↓
RIGHT CARE, RIGHT PLACE, FIRST TIME
```

This demonstrates how volunteer validation directly protects patients and improves healthcare access.

---

## Future State Architecture

### Scheduled Sync Pipeline (Lakeflow)

**Purpose:** Sync operational data from Lakebase → Unity Catalog for governance and analytics

**Schedule:** Nightly (or hourly in production)

**Flow:**
```
Lakebase (volunteer_validations)
    ↓
Incremental CDC or full refresh
    ↓
Unity Catalog Gold Tables
    ↓
Available for:
  - ML model training (Phase D)
  - Audit trails
  - Trend analysis dashboards
  - Governance policies
```

### ML-Based Scoring (Phase D)

Instead of incremental weighted average, train a model to predict validation outcomes:

**Features:**
- Claim volume
- Social media engagement
- Facility age
- Location density
- Historical validation patterns

**Output:** Trust score + confidence interval

**Benefit:** More accurate prioritization, learns from patterns over time
