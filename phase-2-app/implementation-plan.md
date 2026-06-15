# Implementation Plan

## Hackathon MVP Scope

**Goal:** Build an end-to-end demo showing volunteer validation → trust score update → patient benefit

**Timeline:** Hackathon duration (typically 24-48 hours)

**Success Criteria:**
- ✅ Volunteer can search and verify a facility
- ✅ Trust score updates in real-time
- ✅ Patient sees different results before/after validation
- ✅ 3-minute demo flows smoothly

---

## Phase 1: Data Setup (Pre-Demo)

### 1.1 Create Lakebase Database

```sql
-- Create Lakebase database
CREATE DATABASE lakebase.healthverify;

-- Set up tables (see data-schema.md for full DDL)
CREATE TABLE lakebase.healthverify.facilities_verified (...);
CREATE TABLE lakebase.healthverify.verification_queue (...);
CREATE TABLE lakebase.healthverify.volunteer_validations (...);
```

### 1.2 Seed Initial Data

**Script:** `scripts/seed_lakebase.py`

```python
# Load existing data from Unity Catalog
facilities_df = spark.table("dais2026.virtue_foundation_cleaned.facilities")
plausibility_df = spark.table("dais2026.validation.claim_plausibility_scores")
freshness_df = spark.table("dais2026.validation.claim_freshness_scores")

# Join and transform
seeded_facilities = facilities_df \
    .join(plausibility_df, "unique_id", "left") \
    .join(freshness_df, "unique_id", "left") \
    .select(
        col("unique_id"),
        col("name").alias("facility_name"),
        col("address_city").alias("city"),
        col("address_stateOrRegion").alias("state"),
        col("latitude"),
        col("longitude"),
        col("officialPhone").alias("phone_number"),
        col("email"),
        col("officialWebsite").alias("website"),
        col("specialties"),
        col("capability").alias("capabilities"),
        col("overall_plausibility_score").alias("trust_score"),
        col("plausibility_status"),
        col("freshness_status"),
        lit(0).alias("verification_count")
    )

# Write to Lakebase
seeded_facilities.write \
    .format("postgresql") \
    .option("url", lakebase_connection_string) \
    .option("dbtable", "facilities_verified") \
    .mode("overwrite") \
    .save()

print(f"Seeded {seeded_facilities.count()} facilities to Lakebase")
```

### 1.3 Generate Initial Verification Queue

**Script:** `scripts/generate_queue.py`

```python
# Identify high-priority facilities
high_priority = seeded_facilities.filter(
    (col("plausibility_status") == "SUSPICIOUS_VOLUME") |
    (col("freshness_status").isin(["STALE", "NO_DATE"])) |
    (col("trust_score") < 0.75)
)

# Calculate priority scores
from pyspark.sql.functions import when

queue_df = high_priority.withColumn(
    "priority_score",
    when(col("plausibility_status") == "SUSPICIOUS_VOLUME", 95)
    .when(col("plausibility_status") == "INCOMPLETE_DATA", 85)
    .when(col("freshness_status") == "STALE", 80)
    .when(col("freshness_status") == "NO_DATE", 75)
    .otherwise(50)
)

# Generate scripts using Script Generator Agent
# (Call agent for each facility - see components.md for logic)

queue_df.write \
    .format("postgresql") \
    .option("dbtable", "verification_queue") \
    .mode("overwrite") \
    .save()

print(f"Generated queue with {queue_df.count()} facilities")
```

**Expected Output:**
- ~8,200 facilities in verification queue
- Heritage Hospitals (Varanasi) with priority_score = 95

---

## Phase 2: Core Components

### 2.1 AI Agents (MLflow)

**Directory Structure:**
```
/agents/
  ├── script_generator/
  │   ├── agent.py
  │   ├── tools.py
  │   └── prompts.py
  └── symptom_matcher/
      ├── agent.py
      ├── tools.py
      └── prompts.py
```

**Script Generator Agent:**

`agents/script_generator/agent.py`:
```python
import mlflow
from databricks.agents import Agent

# Define tools
def analyze_facility_risk(facility_id: str) -> dict:
    """Query Lakebase for facility risk profile"""
    # Implementation: SQL query to Lakebase
    pass

def get_capability_claims(facility_id: str, limit: int = 10) -> list:
    """Get top capability claims for facility"""
    # Implementation: Parse capabilities JSON
    pass

# Create agent
script_generator = Agent(
    name="script_generator",
    model="databricks-dbrx-instruct",
    tools=[analyze_facility_risk, get_capability_claims],
    system_prompt="""
    You are a verification script generator for healthcare facilities.
    Generate progressive validation questions based on facility risk:
    - Basic questions for all facilities
    - Detailed questions for high-risk facilities
    Keep questions clear and actionable for volunteers.
    """
)

def generate_script(facility_id: str) -> str:
    """Generate verification script for facility"""
    response = script_generator.invoke(
        f"Generate verification script for facility {facility_id}"
    )
    return response.content
```

**Symptom Matcher Agent:**

`agents/symptom_matcher/agent.py`:
```python
def parse_symptoms(symptom_text: str) -> dict:
    """Extract symptoms, urgency, location via LLM"""
    # Implementation: LLM call to extract structured data
    pass

def map_to_specialties(symptoms: list) -> list:
    """Map symptoms to medical specialties"""
    # Implementation: Rule-based + LLM mapping
    pass

symptom_matcher = Agent(
    name="symptom_matcher",
    model="databricks-dbrx-instruct",
    tools=[parse_symptoms, map_to_specialties],
    system_prompt="""
    You are a medical symptom interpreter.
    Extract key symptoms, assess urgency, and map to specialties.
    Be conservative: if unclear, suggest multiple specialties.
    """
)

def match_patient(symptom_text: str, location: str) -> list:
    """Match patient to facilities"""
    # 1. Parse symptoms
    parsed = parse_symptoms(symptom_text)
    
    # 2. Map to specialties
    specialties = map_to_specialties(parsed["symptoms"])
    
    # 3. Query Lakebase (SQL)
    facilities = query_facilities(specialties, location)
    
    # 4. Rank and return
    return rank_facilities(facilities)
```

### 2.2 Databricks App (Streamlit)

**File:** `app.py`

```python
import streamlit as st
import folium
from streamlit_folium import st_folium
import psycopg2

# Page config
st.set_page_config(
    page_title="HealthVerify India",
    page_icon="🏥",
    layout="wide"
)

# Tabs
tab1, tab2 = st.tabs(["👥 Volunteer Portal", "🔍 Patient Search"])

# ==================== VOLUNTEER PORTAL ====================
with tab1:
    st.title("Volunteer Verification Portal")
    
    # Search bar
    search_query = st.text_input("Search facility by name or city", "")
    
    if search_query:
        # Query verification queue
        facilities = search_verification_queue(search_query)
    else:
        # Show top priority facilities
        facilities = get_top_priority_facilities(limit=20)
    
    # Display queue
    st.subheader(f"📋 Verification Queue ({len(facilities)} facilities)")
    
    for facility in facilities:
        with st.expander(
            f"{'🔴' if facility['priority_score'] > 85 else '🟡'} "
            f"{facility['name']} - {facility['city']} "
            f"(Trust: {facility['trust_score']})"
        ):
            # Display facility details
            st.write(f"**Phone:** {facility['phone_number']}")
            st.write(f"**Status:** {facility['plausibility_status']}, "
                     f"{facility['freshness_status']}")
            st.write(f"**Claims:** {facility['claim_count']}")
            
            # Show AI-generated script
            st.markdown("### 📝 Verification Script")
            st.text_area(
                "Questions to ask:",
                value=facility['verification_script'],
                height=200,
                disabled=True
            )
            
            # Validation form
            st.markdown("### ✓ Validation Form")
            
            claims = parse_claims(facility['capabilities'])
            validation_results = {}
            
            for i, claim in enumerate(claims[:10]):  # Top 10 claims
                validation_results[claim] = st.checkbox(
                    f"{claim} verified?",
                    key=f"{facility['id']}_{claim}"
                )
            
            notes = st.text_area("Notes (optional)")
            
            if st.button("Submit Validation", key=f"submit_{facility['id']}"):
                # Calculate results
                verified = sum(validation_results.values())
                checked = len(validation_results)
                
                # Submit to Lakebase
                submit_validation(
                    facility_id=facility['id'],
                    claims_checked=checked,
                    claims_verified=verified,
                    validation_details=validation_results,
                    notes=notes
                )
                
                # Show success
                st.success(
                    f"✅ Validation submitted! "
                    f"Trust score updated from {facility['trust_score']} "
                    f"to {recalculate_score(facility['id'])}"
                )
                st.balloons()

# ==================== PATIENT APP ====================
with tab2:
    st.title("Find Trusted Healthcare")
    
    # Search input
    col1, col2 = st.columns([3, 1])
    with col1:
        symptom_text = st.text_area(
            "Describe your symptoms or what care you need:",
            placeholder="e.g., Heart pain, trouble breathing",
            height=100
        )
    with col2:
        location = st.selectbox(
            "Location:",
            ["Varanasi", "Mumbai", "Delhi", "Bangalore", "Hyderabad", "Other"]
        )
    
    if st.button("Find Care", type="primary"):
        # Call Symptom Matcher Agent
        with st.spinner("Finding best matches..."):
            facilities = match_patient_to_facilities(symptom_text, location)
        
        if facilities:
            # Split screen: Map + List
            map_col, list_col = st.columns([3, 2])
            
            with map_col:
                # Create map
                m = folium.Map(
                    location=[facilities[0]['latitude'], facilities[0]['longitude']],
                    zoom_start=12
                )
                
                # Add markers
                for i, facility in enumerate(facilities):
                    # Top 3 get special markers
                    if i < 3:
                        icon_color = "green" if facility['trust_score'] >= 0.85 else "blue"
                        icon_size = 20
                    else:
                        icon_color = "gray"
                        icon_size = 10
                    
                    folium.Marker(
                        location=[facility['latitude'], facility['longitude']],
                        popup=facility['name'],
                        tooltip=f"{facility['name']} (Trust: {facility['trust_score']})",
                        icon=folium.Icon(color=icon_color, icon="info-sign")
                    ).add_to(m)
                
                st_folium(m, width=700, height=500)
            
            with list_col:
                st.subheader("🏆 Top Matches")
                
                for i, facility in enumerate(facilities[:10]):
                    # Top 3 highlighted
                    if i < 3:
                        with st.container():
                            st.markdown(f"### {i+1}. {facility['name']} 🟢")
                            st.markdown(f"⭐ Trust Score: **{facility['trust_score']}**")
                    else:
                        st.markdown(f"**{i+1}. {facility['name']}**")
                        st.markdown(f"⭐ {facility['trust_score']}")
                    
                    st.markdown(f"📍 {facility['distance_km']:.1f} km away")
                    st.markdown(f"🏥 {', '.join(facility['matched_specialties'][:3])}")
                    
                    if facility.get('recently_verified'):
                        st.success("✓ Recently verified by volunteer")
                    
                    if st.button("View Details", key=f"details_{facility['id']}"):
                        # Show full details modal
                        show_facility_details(facility)
                    
                    st.divider()
        else:
            st.warning("No facilities found. Try different symptoms or location.")
```

### 2.3 Score Recalculation Function

**File:** `utils/score_calculator.py`

```python
def recalculate_trust_score(facility_id, validation_result):
    """
    Incremental weighted average with decay
    See data-schema.md for full logic
    """
    # Fetch current facility
    conn = get_lakebase_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT trust_score, verification_count, 
               total_claims_checked, total_claims_verified
        FROM facilities_verified
        WHERE unique_id = %s
    """, (facility_id,))
    
    facility = cursor.fetchone()
    
    # Calculate new score
    validation_rate = (
        validation_result['claims_verified'] / 
        validation_result['claims_checked']
    )
    
    new_trust_score = (
        facility['trust_score'] * 0.7 + 
        validation_rate * 0.3
    )
    
    # Apply confidence boost for multiple validations
    verification_count = facility['verification_count'] + 1
    if verification_count >= 3:
        new_trust_score = min(new_trust_score * 1.05, 1.0)
    
    # Update database
    cursor.execute("""
        UPDATE facilities_verified
        SET 
            trust_score = %s,
            verification_count = %s,
            freshness_status = 'FRESH',
            last_verified_date = NOW(),
            updated_at = NOW()
        WHERE unique_id = %s
    """, (new_trust_score, verification_count, facility_id))
    
    conn.commit()
    
    return new_trust_score
```

---

## Phase 3: Testing & Demo Prep

### 3.1 Test Volunteer Flow

1. Search "Heritage Hospitals"
2. Verify facility with 13/15 claims verified
3. Confirm trust score updates from 0.68 → 0.73+

### 3.2 Test Patient Flow

**Before validation:**
- Search "heart specialist Varanasi"
- Verify Heritage Hospitals NOT in top 3

**After validation:**
- Same search
- Verify Heritage Hospitals IS in top 3 with verified badge

### 3.3 Prepare Demo Data

- Pre-seed specific facilities for demo
- Have Heritage Hospitals at 0.68 ready
- Practice timing: volunteer validation (15 sec) → patient search (45 sec)

---

## Tech Stack Summary

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **App Platform** | Databricks Apps (Streamlit) | Single UI for both portals |
| **Operational DB** | Lakebase (PostgreSQL-compatible) | Fast reads/writes, sub-second queries |
| **Analytical Layer** | Unity Catalog (Delta Lake) | Governance, historical data, ML training |
| **AI Agents** | MLflow Agents | Script generation, symptom matching |
| **LLM** | DBRX-Instruct or Llama | Foundation model for NLU |
| **Map Visualization** | Folium | Interactive maps in Streamlit |
| **Geospatial** | PostGIS (Lakebase) | Distance calculations |
| **Pipeline (Future)** | Lakeflow Jobs | Scheduled sync Lakebase→Lakehouse |

---

## Future Roadmap (Post-Hackathon)

### Phase D: ML-Based Scoring

**Timeline:** 1-2 months post-hackathon

**Goal:** Replace incremental scoring with ML model

**Steps:**
1. Sync historical validation data to Gold layer
2. Feature engineering (see data-schema.md)
3. Train RandomForest or XGBoost model
4. Deploy model endpoint
5. Update scoring logic to call model

**Expected Improvement:**
- More accurate risk assessment
- Better prioritization of verification queue
- Learn patterns over time

### Phase E: Multi-Modal Patient Interface

**Timeline:** 2-3 months post-hackathon

**Goal:** Voice input + multilingual support

**Features:**
- Speech-to-text for symptom input
- Hindi, Tamil, Telugu, Bengali language support
- Conversational agent for guided symptom collection
- SMS/WhatsApp integration

**Impact:**
- Reach low-literacy users
- Expand to rural areas
- Increase accessibility

### Phase F: Volunteer Mobile App

**Timeline:** 3-4 months post-hackathon

**Goal:** Native mobile app for volunteers

**Features:**
- Offline mode (download scripts, sync later)
- Push notifications for high-priority facilities
- Gamification (leaderboards, badges)
- Quick validation flow optimized for mobile

### Phase G: Integration & Scale

**Timeline:** 6-12 months post-hackathon

**Goal:** Public data platform

**Features:**
- Public API for verified facility data
- Government health department dashboard
- Partnership with Google Maps, Bing, etc.
- NGO/healthtech platform integrations

**Impact:**
- Verified data becomes standard across India
- Millions of patients benefit
- Sustainable volunteer ecosystem

---

## Success Metrics

### Hackathon Demo (Day 1)
- ✅ Complete volunteer validation in < 60 seconds
- ✅ Trust score updates in real-time
- ✅ Patient sees impact of validation immediately
- ✅ Judges understand the full cycle

### Production (6 months)
- 1,000 active volunteers
- 95% of facilities have trust score ≥ 0.80
- 100,000+ patient searches per month
- 85%+ patient satisfaction (survey)
- 40% reduction in wasted travel time

### Scale (12 months)
- 10,000+ volunteers across India
- All 10,000 facilities verified at least twice
- Integration with 5+ healthtech platforms
- Government partnership established
- Self-sustaining volunteer ecosystem
