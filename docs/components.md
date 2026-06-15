# Component Specifications

## 1. Volunteer Portal

### Purpose
Provide volunteers with an interface to search, view, and validate facilities in need of verification.

### Features

#### 1.1 Search & Browse Interface
- **Search Bar**: Search by facility name, city, state, or unique_id
- **Queue View**: Table showing facilities needing verification
- **Sorting Options**: 
  - Priority (SUSPICIOUS > STALE > NO_DATE)
  - Location (alphabetical by city/state)
  - Trust score (lowest first)
- **Visual Indicators**:
  - 🔴 High priority (SUSPICIOUS_VOLUME, trust < 0.70)
  - 🟡 Medium priority (STALE, AGING, trust 0.70-0.80)
  - 🟢 Low priority (NO_DATE, trust > 0.80)

#### 1.2 Verification Task Screen
Opens when volunteer clicks "Verify Now" button

**Displays:**
- Facility details: name, address, contact info
- Current trust score and status
- AI-generated verification script (text display, copyable)
- List of capability claims to verify

**Validation Form:**
- Simple yes/no checkboxes for each claim
- Optional text field for volunteer notes
- Phone call duration tracker (optional)
- Submit button

**After Submission:**
- Show before/after trust scores
- Display "Your validation helped X patients today!"
- Automatically return to queue view

#### 1.3 Impact Dashboard (Sidebar)
Motivates volunteers by showing impact metrics:
- "You've verified 12 facilities this week"
- "Your validations improved data quality for 3,450 patients"
- Leaderboard (optional, for gamification)

### UI Mock Structure

```
┌────────────────────────────────────────────────────────┐
│  Volunteer Portal                                      │
├────────────────────────────────────────────────────────┤
│  [Search: Heritage Hospitals           🔍] [Filter ▼] │
├────────────────────────────────────────────────────────┤
│  📋 Verification Queue (234 pending)                   │
│                                                        │
│  Priority | Facility Name         | City    | Trust  │
│  🔴       | Heritage Hospitals    | Varanasi| 0.68   │
│           | 200 claims | STALE    |[Verify]│        │
│  🔴       | Aravind Eye Hospital  | Hyderabad| 0.56  │
│           | 200 claims | SUSPICIOUS|[Verify]│        │
│  🟡       | Fortis Hospital       | Gurgaon | 0.75   │
│           | 180 claims | AGING    |[Verify]│        │
└────────────────────────────────────────────────────────┘

When "Verify" clicked:

┌────────────────────────────────────────────────────────┐
│  Verify: Heritage Hospitals, Varanasi                  │
├────────────────────────────────────────────────────────┤
│  📍 Address: XYZ Road, Varanasi, UP                    │
│  📞 Phone: +91-XXX-XXX-XXXX                            │
│  📊 Current Trust Score: 0.68 (SUSPICIOUS_VOLUME)      │
├────────────────────────────────────────────────────────┤
│  📝 AI-Generated Verification Script:                  │
│  ┌────────────────────────────────────────────────┐   │
│  │ Basic Questions:                               │   │
│  │ 1. Is this facility currently operational?     │   │
│  │ 2. Can you confirm this phone number?          │   │
│  │                                                 │   │
│  │ Progressive Questions (High Priority):         │   │
│  │ 3. Verify specialty: Cardiology?               │   │
│  │ 4. Verify specialty: Orthopedics?              │   │
│  │ 5. Does facility have ICU as claimed?          │   │
│  └────────────────────────────────────────────────┘   │
├────────────────────────────────────────────────────────┤
│  ✓ Validation Form:                                    │
│  ☐ Facility operational                                │
│  ☐ Phone number correct                                │
│  ☐ Cardiology available                                │
│  ☐ Orthopedics available                               │
│  ☐ ICU capacity confirmed                              │
│  ...                                                   │
│  Notes: [Optional text field]                          │
│  [Submit Validation]                                   │
└────────────────────────────────────────────────────────┘
```

---

## 2. Patient Matching App

### Purpose
Help patients find trustworthy healthcare facilities based on symptoms and proximity.

### Features

#### 2.1 Simple Search Interface
- **Text Area**: "Describe your symptoms or what care you need"
  - Placeholder: "e.g., Heart pain, trouble breathing"
  - Multi-line input supported
- **Location Input**: 
  - Dropdown with major cities OR
  - Auto-detect from user location (if available)
- **Search Button**: "Find Care"

#### 2.2 Interactive Map View
- **Map Library**: Folium (recommended for Streamlit) or Plotly
- **Facility Markers**:
  - **Top 3**: Large pins with bold colors (green for verified, blue for high trust)
  - **Others**: Smaller gray pins
- **Trust Badges**:
  - 🟢 Verified (recently validated by volunteer)
  - 🟡 Partially Verified (older validation)
  - ⚪ Unverified (below threshold, shown with warning)
- **Interaction**: Click pin → highlight in sidebar, scroll to facility card

#### 2.3 Results Sidebar
Displays ranked list of facilities

**Facility Card Layout:**
```
┌─────────────────────────────────┐
│ 1. Heritage Hospitals 🟢        │
│    ⭐⭐⭐⭐ (0.88)                 │
│    📍 2.3 km away                │
│    🏥 Cardiology, ICU, Emergency │
│    📞 +91-XXX-XXX-XXXX           │
│    ✓ Recently verified (87%)    │
│    [View Details]                │
└─────────────────────────────────┘
```

**Top 3 Cards**: Bold border, highlighted background  
**Others**: Standard styling

#### 2.4 Facility Detail View
Opens when user clicks "View Details"

**Displays:**
- Full facility information
- Complete list of specialties and capabilities
- Trust score with explanation:
  - "Recently verified by volunteer on [date]"
  - "87% of claims confirmed"
- Map showing exact location
- Contact details with click-to-call/email
- Directions link (Google Maps integration)

### UI Mock Structure

```
┌─────────────────────────────────────────────────────────────┐
│  Patient Search                                             │
├─────────────────────────────────────────────────────────────┤
│  Describe your symptoms:                                    │
│  ┌───────────────────────────────────────────────────────┐ │
│  │ Heart pain, trouble breathing                         │ │
│  └───────────────────────────────────────────────────────┘ │
│  Location: [Varanasi ▼]          [Find Care]               │
├──────────────────────────┬──────────────────────────────────┤
│  🗺️ MAP (60% width)      │  📋 RESULTS (40% width)          │
│                          │                                  │
│  ┌────────────────────┐  │  Top Matches (3 of 12):          │
│  │    🟢 2            │  │                                  │
│  │  🟢 1      🟢 3    │  │  🟢 1. Heritage Hospitals       │
│  │                    │  │     ⭐⭐⭐⭐ (0.88) | 2.3 km     │
│  │         ⚪ 4       │  │     Cardiology, ICU             │
│  │                    │  │     ✓ Recently verified         │
│  │  ⚪ 5     ⚪ 6      │  │     [View Details]              │
│  │                    │  │                                  │
│  └────────────────────┘  │  🟢 2. City Hospital            │
│                          │     ⭐⭐⭐⭐ (0.85) | 3.1 km     │
│                          │     Cardiology, Emergency       │
│                          │     [View Details]              │
│                          │                                  │
│                          │  🟢 3. Medical Center           │
│                          │     ⭐⭐⭐ (0.82) | 4.5 km       │
│                          │     Internal Medicine           │
│                          │     [View Details]              │
│                          │                                  │
│                          │  ─────────────────────          │
│                          │  4. Regional Hospital           │
│                          │     ⭐⭐ (0.78) | 5.2 km         │
│                          │     ...                          │
└──────────────────────────┴──────────────────────────────────┘
```

---

## 3. AI Agents (MLflow)

### 3.1 Script Generator Agent

**Purpose:** Generate custom verification scripts based on facility risk profile

**Tools:**
1. `analyze_facility_risk(facility_id)` - Query Lakebase for risk indicators
2. `get_capability_claims(facility_id, limit)` - Retrieve specific claims
3. `llm_generate_questions(context)` - Generate natural language questions

**Logic Flow:**

```python
def generate_verification_script(facility_id):
    """
    Progressive validation: basic questions for all,
    detailed questions for high-risk facilities
    """
    # 1. Get facility data
    facility = analyze_facility_risk(facility_id)
    
    # 2. Basic questions (all facilities)
    script = [
        "Is this facility currently operational?",
        "Can you confirm this phone number is correct?",
        "What are your operating hours?"
    ]
    
    # 3. Progressive questions based on risk
    if facility.plausibility_status == "SUSPICIOUS_VOLUME":
        # High claim volume - verify top claims
        top_claims = get_capability_claims(facility_id, limit=10)
        script += [
            f"Do you have {specialty} services?" 
            for specialty in top_claims[:5]
        ]
        script.append("Can you confirm ICU capacity?")
    
    if facility.freshness_status in ["STALE", "NO_DATE"]:
        # Old data - verify basics haven't changed
        script += [
            "Has your facility address changed recently?",
            "Have any major specialties been added or removed?",
            "Is the website still active?"
        ]
    
    if facility.plausibility_status in ["INCOMPLETE_DATA", "LOW_MISMATCH"]:
        # Data quality issues - fill gaps
        script += [
            "What is your bed capacity?",
            "Do you have 24/7 emergency services?",
            "What are your main specialties?"
        ]
    
    # 4. LLM polish for natural language
    context = {
        "facility_name": facility.name,
        "city": facility.city,
        "risk_factors": facility.risk_summary
    }
    polished_script = llm_generate_questions(script, context)
    
    return polished_script
```

**Example Output:**
```
Heritage Hospitals, Varanasi - Verification Script

Basic Questions:
1. Is Heritage Hospitals currently operational?
2. Can you confirm the phone number +91-XXX-XXX-XXXX is correct?
3. What are your operating hours?

High-Priority Questions (200 claims flagged):
4. Do you provide cardiology services?
5. Do you provide orthopedic services?
6. Do you provide neurology services?
7. Can you confirm ICU capacity as claimed?
8. Is emergency care available 24/7?

Data Quality Questions (last update 8 months ago):
9. Has your facility address changed?
10. Have any specialties been discontinued?
```

### 3.2 Symptom Matcher Agent

**Purpose:** Interpret patient symptoms and map to medical specialties

**Tools:**
1. `parse_symptoms(text)` - Extract symptoms, urgency, location via LLM
2. `map_to_specialties(symptoms)` - Convert to specialty codes
3. `query_facilities(specialties, location, filters)` - SQL query Lakebase

**Logic Flow:**

```python
def match_patient_to_facilities(symptom_text, location):
    """
    NLU-based symptom interpretation → specialty mapping → SQL ranking
    """
    # 1. Extract intent via LLM
    parsed = parse_symptoms(symptom_text)
    # Example output:
    # {
    #   "symptoms": ["chest pain", "breathing difficulty"],
    #   "urgency": "high",
    #   "location": "Varanasi"
    # }
    
    # 2. Map symptoms to medical specialties
    specialties = map_to_specialties(parsed["symptoms"])
    # Example output:
    # ["cardiology", "emergencyMedicine", "criticalCareMedicine"]
    
    # 3. SQL query with filters
    facilities = query_facilities(
        specialties=specialties,
        location=parsed.get("location", location),
        min_trust_score=0.75,  # Filter threshold
        max_distance_km=50,
        limit=20
    )
    
    # 4. Rank by weighted score
    ranked_facilities = []
    for facility in facilities:
        # Distance score (inverse, normalized)
        distance_score = 1.0 / (1.0 + facility.distance_km / 10)
        
        # Trust score (already 0-1)
        trust_score = facility.trust_score
        
        # Weighted final score
        final_score = (trust_score * 0.6) + (distance_score * 0.4)
        
        ranked_facilities.append({
            **facility,
            "match_score": final_score,
            "matched_specialties": specialties
        })
    
    # Sort by score descending
    ranked_facilities.sort(key=lambda x: x["match_score"], reverse=True)
    
    return ranked_facilities[:10]  # Top 10
```

**Example Input/Output:**

**Input:**
```
symptom_text = "Heart pain, trouble breathing, near Varanasi"
location = "Varanasi"
```

**LLM Parse Output:**
```json
{
  "symptoms": ["heart pain", "breathing difficulty"],
  "urgency": "high",
  "body_part": "chest",
  "duration": null,
  "location": "Varanasi"
}
```

**Specialty Mapping:**
```python
["cardiology", "emergencyMedicine", "criticalCareMedicine", "internalMedicine"]
```

**SQL Query:**
```sql
SELECT * FROM facilities_verified
WHERE 
  (specialties LIKE '%cardiology%' 
   OR specialties LIKE '%emergencyMedicine%')
  AND trust_score >= 0.75
  AND city = 'Varanasi'
  AND distance_km(latitude, longitude, user_lat, user_lon) < 50
ORDER BY trust_score DESC, distance_km ASC
LIMIT 20
```

**Ranked Output (Top 3):**
```python
[
  {
    "facility_id": "39dd607d",
    "name": "Heritage Hospitals",
    "trust_score": 0.88,
    "distance_km": 2.3,
    "match_score": 0.87,
    "matched_specialties": ["cardiology", "emergencyMedicine"],
    "badge": "VERIFIED"
  },
  {
    "facility_id": "d8d93d78",
    "name": "City Hospital",
    "trust_score": 0.85,
    "distance_km": 3.1,
    "match_score": 0.82,
    "matched_specialties": ["cardiology"],
    "badge": "VERIFIED"
  },
  ...
]
```

---

## Integration Points

### Volunteer Portal ↔ Lakebase
- **Read**: Query `verification_queue` for facilities needing validation
- **Read**: Fetch facility details from `facilities_verified`
- **Write**: Submit validation results to `volunteer_validations`
- **Trigger**: Score recalculation stored procedure

### Patient App ↔ Lakebase
- **Read**: Query `facilities_verified` with filters
- **Write**: Log search queries for analytics (optional)

### AI Agents ↔ Lakebase
- **Script Generator**: Read facility risk profile, write script to `verification_queue`
- **Symptom Matcher**: Read facility capabilities for matching

### Lakebase ↔ Lakehouse (Future)
- **Scheduled sync**: Lakeflow job runs nightly
- **CDC**: Capture changes from `volunteer_validations`
- **Write to Gold**: Append to `dais2026.analytics.validation_history`
