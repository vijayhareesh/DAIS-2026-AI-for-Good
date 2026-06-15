# Data Schema

## Lakebase Tables (Operational)

Lakebase serves as the operational database for the application, handling real-time reads and writes from the Databricks App.

### Table: `facilities_verified`

**Purpose:** Core facility data with current trust scores and verification status

```sql
CREATE TABLE lakebase.healthverify.facilities_verified (
    -- Identifiers
    unique_id STRING PRIMARY KEY,
    facility_name STRING NOT NULL,
    
    -- Location
    state STRING,
    city STRING,
    address_line1 STRING,
    address_line2 STRING,
    address_line3 STRING,
    zip_code STRING,
    latitude DOUBLE,
    longitude DOUBLE,
    
    -- Contact Information
    phone_number STRING,
    email STRING,
    website STRING,
    social_media_links JSON,
    
    -- Capabilities (stored as JSON arrays)
    specialties ARRAY<STRING>,
    capabilities ARRAY<STRING>,
    equipment ARRAY<STRING>,
    procedures ARRAY<STRING>,
    
    -- Capacity
    bed_capacity INT,
    icu_capacity INT,
    doctor_count INT,
    
    -- Trust Scoring
    trust_score DECIMAL(5,2) NOT NULL DEFAULT 0.50,  -- 0.00 to 1.00
    plausibility_status STRING NOT NULL,  
        -- PLAUSIBLE, SUSPICIOUS_VOLUME, INCOMPLETE_DATA, LOW_MISMATCH, MODERATE_MISMATCH
    freshness_status STRING NOT NULL,
        -- FRESH, STALE, AGING, NO_DATE, FUTURE_DATE
    
    -- Verification Tracking
    last_verified_date TIMESTAMP,
    verification_count INT DEFAULT 0,
    total_claims_checked INT DEFAULT 0,
    total_claims_verified INT DEFAULT 0,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_source STRING
);

-- Indexes for performance
CREATE INDEX idx_facilities_location ON facilities_verified(latitude, longitude);
CREATE INDEX idx_facilities_city ON facilities_verified(city, state);
CREATE INDEX idx_facilities_trust ON facilities_verified(trust_score DESC);
CREATE INDEX idx_facilities_status ON facilities_verified(plausibility_status, freshness_status);
```

**Sample Data:**
```json
{
  "unique_id": "390fa6ee-297f-4063-8fbe-82f5e7db7258",
  "facility_name": "Heritage Hospitals",
  "state": "Uttar Pradesh",
  "city": "Varanasi",
  "latitude": 27.2106,
  "longitude": 77.9972,
  "phone_number": "+91-XXX-XXX-XXXX",
  "specialties": ["cardiology", "orthopedics", "neurology"],
  "trust_score": 0.68,
  "plausibility_status": "SUSPICIOUS_VOLUME",
  "freshness_status": "STALE",
  "verification_count": 0,
  "last_verified_date": null
}
```

---

### Table: `verification_queue`

**Purpose:** Facilities needing verification with AI-generated scripts

```sql
CREATE TABLE lakebase.healthverify.verification_queue (
    -- Identifiers
    queue_id STRING PRIMARY KEY,
    facility_id STRING NOT NULL,  -- FK to facilities_verified
    
    -- Facility Reference (denormalized for quick display)
    facility_name STRING NOT NULL,
    city STRING,
    state STRING,
    phone_number STRING,
    
    -- Risk Assessment
    priority_score INT NOT NULL,  -- 1-100, higher = more urgent
    risk_category STRING NOT NULL,  -- HIGH, MEDIUM, LOW
    risk_factors ARRAY<STRING>,  
        -- e.g., ["SUSPICIOUS_VOLUME", "NO_DATE", "HIGH_CLAIM_COUNT"]
    
    -- AI-Generated Script
    verification_script TEXT NOT NULL,  -- JSON array of questions
    script_version INT DEFAULT 1,
    script_generated_at TIMESTAMP,
    
    -- Assignment & Status
    status STRING NOT NULL DEFAULT 'PENDING',  
        -- PENDING, IN_PROGRESS, COMPLETED, SKIPPED
    assigned_volunteer_id STRING,
    assigned_at TIMESTAMP,
    completed_at TIMESTAMP,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_queue_priority ON verification_queue(priority_score DESC, created_at);
CREATE INDEX idx_queue_status ON verification_queue(status);
CREATE INDEX idx_queue_facility ON verification_queue(facility_id);
```

**Priority Calculation Logic:**
```python
def calculate_priority_score(facility):
    """
    Returns 1-100, higher = more urgent
    """
    score = 50  # baseline
    
    # Plausibility status
    if facility.plausibility_status == "SUSPICIOUS_VOLUME":
        score += 30
    elif facility.plausibility_status in ["INCOMPLETE_DATA", "MODERATE_MISMATCH"]:
        score += 20
    elif facility.plausibility_status == "LOW_MISMATCH":
        score += 10
    
    # Freshness status
    if facility.freshness_status == "NO_DATE":
        score += 15
    elif facility.freshness_status == "STALE":
        score += 20
    elif facility.freshness_status == "AGING":
        score += 10
    
    # User reports (future)
    score += min(facility.user_report_count * 5, 20)
    
    return min(score, 100)
```

**Sample Data:**
```json
{
  "queue_id": "q_390fa6ee",
  "facility_id": "390fa6ee-297f-4063-8fbe-82f5e7db7258",
  "facility_name": "Heritage Hospitals",
  "city": "Varanasi",
  "priority_score": 95,
  "risk_category": "HIGH",
  "risk_factors": ["SUSPICIOUS_VOLUME", "STALE", "HIGH_CLAIM_COUNT"],
  "verification_script": "[\"Is this facility operational?\", \"Verify cardiology services?\", ...]",
  "status": "PENDING",
  "created_at": "2026-06-15T10:00:00Z"
}
```

---

### Table: `volunteer_validations`

**Purpose:** Record of all volunteer verification submissions

```sql
CREATE TABLE lakebase.healthverify.volunteer_validations (
    -- Identifiers
    validation_id STRING PRIMARY KEY,
    facility_id STRING NOT NULL,  -- FK to facilities_verified
    volunteer_id STRING NOT NULL,
    queue_id STRING,  -- FK to verification_queue (optional)
    
    -- Validation Results
    claims_checked INT NOT NULL,
    claims_verified INT NOT NULL,
    claims_failed INT NOT NULL,
    validation_details JSON,  
        -- {"cardiology": true, "ICU": true, "neurology": false, ...}
    
    -- Score Impact
    old_trust_score DECIMAL(5,2),
    new_trust_score DECIMAL(5,2),
    score_change DECIMAL(5,2),
    
    -- Call Details
    volunteer_notes TEXT,
    call_duration_seconds INT,
    phone_answered BOOLEAN,
    
    -- Metadata
    validated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_validations_facility ON volunteer_validations(facility_id, validated_at);
CREATE INDEX idx_validations_volunteer ON volunteer_validations(volunteer_id, validated_at);
CREATE INDEX idx_validations_date ON volunteer_validations(validated_at);
```

**Sample Data:**
```json
{
  "validation_id": "val_abc123",
  "facility_id": "390fa6ee-297f-4063-8fbe-82f5e7db7258",
  "volunteer_id": "volunteer_001",
  "claims_checked": 15,
  "claims_verified": 13,
  "claims_failed": 2,
  "validation_details": {
    "operational": true,
    "phone_correct": true,
    "cardiology": true,
    "orthopedics": true,
    "neurology": false,
    "ICU_capacity": true
  },
  "old_trust_score": 0.68,
  "new_trust_score": 0.737,
  "score_change": 0.057,
  "volunteer_notes": "Facility confirmed most services. Neurology dept closed last year.",
  "call_duration_seconds": 240,
  "validated_at": "2026-06-15T14:30:00Z"
}
```

---

## Trust Score Recalculation Logic

### Incremental Update (MVP - Phase C)

Implemented as a Lakebase stored procedure or Python function called after validation submission:

```python
def recalculate_trust_score(facility_id, validation_result):
    """
    Weighted average with decay factor
    
    Args:
        facility_id: Unique facility identifier
        validation_result: Dict with claims_verified, claims_checked
    
    Returns:
        Updated facility record
    """
    # 1. Fetch current facility data
    facility = get_facility(facility_id)
    
    # 2. Calculate validation success rate
    validation_rate = (
        validation_result["claims_verified"] / 
        validation_result["claims_checked"]
    )
    
    # 3. Weighted average with decay
    decay_factor = 0.7  # Historical weight
    new_weight = 0.3    # New validation weight
    
    new_trust_score = (
        facility.trust_score * decay_factor + 
        validation_rate * new_weight
    )
    
    # 4. Boost for multiple validations (confidence grows)
    verification_count = facility.verification_count + 1
    if verification_count >= 3:
        confidence_boost = min(0.05 * (verification_count - 2), 0.10)
        new_trust_score = min(new_trust_score + confidence_boost, 1.0)
    
    # 5. Update cumulative stats
    total_claims_checked = (
        facility.total_claims_checked + 
        validation_result["claims_checked"]
    )
    total_claims_verified = (
        facility.total_claims_verified + 
        validation_result["claims_verified"]
    )
    
    # 6. Update freshness status
    freshness_status = "FRESH"
    
    # 7. Re-evaluate plausibility status
    overall_verification_rate = total_claims_verified / total_claims_checked
    if overall_verification_rate >= 0.85:
        plausibility_status = "PLAUSIBLE"
    elif overall_verification_rate >= 0.70:
        plausibility_status = "LOW_MISMATCH"
    else:
        plausibility_status = "INCOMPLETE_DATA"
    
    # 8. Return updated record
    return {
        "trust_score": round(new_trust_score, 2),
        "verification_count": verification_count,
        "total_claims_checked": total_claims_checked,
        "total_claims_verified": total_claims_verified,
        "freshness_status": freshness_status,
        "plausibility_status": plausibility_status,
        "last_verified_date": current_timestamp(),
        "updated_at": current_timestamp()
    }
```

**Example Calculation:**

**Initial State:**
- Heritage Hospitals: trust_score = 0.68, verification_count = 0

**Validation #1:**
- Claims checked: 15
- Claims verified: 13
- Validation rate: 13/15 = 0.867
- New score: (0.68 × 0.7) + (0.867 × 0.3) = 0.476 + 0.260 = **0.736**

**Validation #2:**
- Claims checked: 10
- Claims verified: 9
- Validation rate: 9/10 = 0.90
- New score: (0.736 × 0.7) + (0.90 × 0.3) = 0.515 + 0.270 = **0.785**

**Validation #3:**
- Claims checked: 12
- Claims verified: 11
- Validation rate: 11/12 = 0.917
- New score: (0.785 × 0.7) + (0.917 × 0.3) = 0.550 + 0.275 = **0.825**
- **Confidence boost**: +0.05 (3 validations reached)
- Final score: 0.825 + 0.05 = **0.875** ✓

---

## Lakehouse Tables (Analytical - Future)

### Bronze Layer: `dais2026.raw.*` (Already Exists)

**Tables:**
- `india_post_pincode_directory` - Postal codes for geospatial enrichment
- `facilities_capabilities_exploded` - Raw capability claims

---

### Silver Layer: `dais2026.virtue_foundation_cleaned.*` (Already Exists)

**Tables:**
- `facilities` - Cleaned facility master data
- Existing validation score tables (initial data source)

---

### Gold Layer: `dais2026.analytics.*` (Future Roadmap)

#### Table: `validation_history`

**Purpose:** Time-series tracking of trust score evolution

```sql
CREATE TABLE dais2026.analytics.validation_history (
    facility_id STRING,
    validation_date DATE,
    trust_score DECIMAL(5,2),
    plausibility_status STRING,
    freshness_status STRING,
    verification_count INT,
    volunteer_count INT,
    cumulative_claims_checked INT,
    cumulative_claims_verified INT
)
PARTITIONED BY (validation_date);
```

**Use Cases:**
- Trend analysis: "Which facilities are improving/declining?"
- Volunteer impact: "How many validations needed to reach trust threshold?"
- Dashboard: Line charts showing trust score over time

---

#### Table: `ml_training_features` (Phase D)

**Purpose:** Feature engineering for ML-based scoring model

```sql
CREATE TABLE dais2026.analytics.ml_training_features (
    facility_id STRING,
    
    -- Facility characteristics
    claim_count INT,
    social_followers INT,
    facility_age_years INT,
    location_density_score DECIMAL(5,2),
    
    -- Historical patterns
    avg_validation_rate DECIMAL(5,2),
    validation_consistency DECIMAL(5,2),
    time_since_last_update_days INT,
    
    -- Outcome labels
    trust_score_label DECIMAL(5,2),
    validation_success BOOLEAN,
    
    -- Metadata
    feature_snapshot_date DATE,
    created_at TIMESTAMP
)
PARTITIONED BY (feature_snapshot_date);
```

**ML Model Training:**
```python
# Pseudo-code for Phase D
from sklearn.ensemble import RandomForestRegressor

# Load training data
df = spark.table("dais2026.analytics.ml_training_features")

# Features
X = df.select("claim_count", "social_followers", ...).toPandas()

# Target
y = df.select("trust_score_label").toPandas()

# Train model
model = RandomForestRegressor()
model.fit(X, y)

# Predict trust scores for new facilities
predictions = model.predict(new_facilities)
```

---

#### Table: `audit_log`

**Purpose:** Compliance and debugging trail

```sql
CREATE TABLE dais2026.analytics.audit_log (
    event_id STRING PRIMARY KEY,
    event_type STRING,  
        -- VALIDATION_SUBMITTED, SCORE_UPDATED, PATIENT_SEARCH, ADMIN_ACTION
    facility_id STRING,
    user_id STRING,
    user_type STRING,  -- VOLUNTEER, PATIENT, ADMIN
    
    -- Event details (JSON)
    details JSON,
    
    -- Context
    ip_address STRING,
    user_agent STRING,
    
    -- Timestamp
    timestamp TIMESTAMP
)
PARTITIONED BY (DATE(timestamp));
```

**Sample Events:**
```json
{
  "event_type": "VALIDATION_SUBMITTED",
  "facility_id": "390fa6ee",
  "user_id": "volunteer_001",
  "details": {
    "claims_verified": 13,
    "claims_checked": 15,
    "old_score": 0.68,
    "new_score": 0.737
  },
  "timestamp": "2026-06-15T14:30:00Z"
}

{
  "event_type": "PATIENT_SEARCH",
  "user_id": "patient_xyz",
  "details": {
    "symptom_text": "heart pain near Varanasi",
    "results_count": 12,
    "top_result": "Heritage Hospitals"
  },
  "timestamp": "2026-06-15T15:45:00Z"
}
```

---

## Sync Pipeline (Lakebase → Lakehouse)

### Future Implementation

**Purpose:** Sync operational data to analytical layer for governance, ML, and reporting

**Frequency:** Nightly (or hourly in production)

**Pipeline Spec:**
```yaml
# Lakeflow Job Configuration
name: lakebase_to_lakehouse_sync
schedule: "0 2 * * *"  # 2 AM daily

tasks:
  - task_key: sync_validations
    notebook_task:
      notebook_path: /pipelines/sync_validations
      base_parameters:
        source: lakebase.healthverify.volunteer_validations
        target: dais2026.analytics.validation_history
        mode: incremental
        watermark_column: validated_at
  
  - task_key: update_ml_features
    depends_on:
      - sync_validations
    notebook_task:
      notebook_path: /pipelines/update_ml_features
      base_parameters:
        source: dais2026.virtue_foundation_cleaned.facilities
        target: dais2026.analytics.ml_training_features
```

**Incremental Sync Logic:**
```python
# Read new validations since last sync
last_sync = get_last_watermark("validation_history")
new_validations = spark.read \
    .format("postgresql") \
    .option("url", lakebase_url) \
    .option("dbtable", "volunteer_validations") \
    .load() \
    .filter(f"validated_at > '{last_sync}'")

# Aggregate by facility and date
daily_stats = new_validations.groupBy("facility_id", "validation_date").agg(
    avg("new_trust_score").alias("trust_score"),
    count("*").alias("validation_count"),
    countDistinct("volunteer_id").alias("volunteer_count")
)

# Append to Gold table
daily_stats.write \
    .format("delta") \
    .mode("append") \
    .partitionBy("validation_date") \
    .saveAsTable("dais2026.analytics.validation_history")
```

---

## Data Flow Summary

```
┌─────────────────────────────────────────┐
│  Databricks App                         │
│  - Volunteer Portal                     │
│  - Patient Matching App                 │
└──────────────┬──────────────────────────┘
               │
               │ Real-time reads/writes
               ▼
┌─────────────────────────────────────────┐
│  Lakebase (Operational)                 │
│  - facilities_verified                  │
│  - verification_queue                   │
│  - volunteer_validations                │
└──────────────┬──────────────────────────┘
               │
               │ Nightly sync (future)
               ▼
┌─────────────────────────────────────────┐
│  Lakehouse (Analytical)                 │
│  - Bronze: Raw data                     │
│  - Silver: Cleaned data                 │
│  - Gold: Analytics & ML                 │
└─────────────────────────────────────────┘
```
