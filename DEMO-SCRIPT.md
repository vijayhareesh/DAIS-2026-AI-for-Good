# HealthVerify India - Demo Script for DAIS 2026 Hackathon

**Total Time:** 3 minutes  
**Track:** Facility Trust Desk (Track 1)  
**Goal:** Show how AI-powered community verification builds trust in healthcare facility data

---

## 🎯 Demo Story Arc

### Hook (30 seconds) - The Crisis
> "64.9% of India's 10,000 healthcare facilities have NO DATE validation. A patient searching for cardiac care in Varanasi sees Heritage Hospitals claiming they can help. But should they trust it?"

**Show slide:** Map of India with 6,461 facilities highlighted red (missing dates)

---

### Problem (45 seconds) - Heritage Hospitals Example

**Open App: Facility Detail View**

Show Heritage Hospitals, Varanasi:
* **Facility Name:** Heritage Hospitals
* **Location:** Varanasi, Uttar Pradesh  
* **Trust Score:** 0.45 / 1.00
* **Status:** ⚠️ UNRELIABLE_DATA
* **Red Flags:**
  * ⚠️ Last updated 2+ years ago (STALE_DATA)
  * ⚠️ Claims 200+ services (OVERCLAIMING)  
  * ⚠️ Data shows clipping patterns (DATA_CLIPPED)
* **Result:** ❌ **HIDDEN from patient search results**

**Say:**
> "Our AI trust system analyzed this facility and found it UNRELIABLE. Trust score: 0.45. We HIDE it from patient search to protect them from wasting time and money traveling to a facility that may not deliver."

---

### Solution (60 seconds) - Volunteer Portal

**Switch to: Volunteer Portal**

**Step 1: Select Verification Task**
* Show list of facilities needing verification
* Select "Heritage Hospitals, Varanasi"
* Show priority: "HIGH - Hidden from 50+ patient searches this week"

**Step 2: AI-Generated Verification Script**
> "Our AI agent analyzes the facility's specific red flags and generates a custom verification script"

Show generated questions:
1. ✓ Do you currently provide cardiac care services?
2. ✓ When was your facility information last updated?
3. ✓ Can you confirm your current list of specialties? (We show 200+)
4. ✓ Do you have a cardiac catheterization lab? (claimed but suspicious)
5. ✓ What is your current bed capacity?

**Step 3: Record Verification**
* Volunteer calls facility
* Records answers: "Yes, we do provide cardiac care. Updated info 2 weeks ago. Confirmed 45 specialties (not 200)."
* Submit verification

**Step 4: Trust Score Update**
* Show real-time update animation
* **Before:** 0.45 (UNRELIABLE) → **After:** 0.88 (HIGH_RELIABILITY)
* **Status Change:** HIDDEN → ✅ VISIBLE IN SEARCH

**Say:**
> "One volunteer, 10 minutes, and now this facility is trusted. Let's see the patient impact..."

---

### Impact (45 seconds) - Patient Search

**Switch to: Patient Search**

**Show side-by-side comparison:**

| BEFORE Volunteer Verification | AFTER Volunteer Verification |
|-------------------------------|------------------------------|
| **Search:** "cardiac care Varanasi" | **Search:** "cardiac care Varanasi" |
| Heritage: ❌ HIDDEN (0.45) | Heritage: ✅ RANKED #11 (0.88) |
| Patient sees only 8 results | Patient sees 9 results including Heritage |
| Patient travels 50km to wrong facility | Patient finds right care 2km away |

**Say:**
> "Before verification, patients searching for cardiac care couldn't find Heritage - it was hidden for their protection. After verification, it appears in results and a family finds the care they need 2km from home instead of traveling 50km."

**Show final stats:**
* **10,039 facilities** across India analyzed
* **685 facilities (6.8%)** currently unreliable and hidden
* **6,461 facilities (64.9%)** missing validation dates
* **1,000 volunteers × 10 min each = 114 hours to verify entire database**

> "This is how we build trust at scale. Community-driven, AI-powered, saving patients from dangerous delays."

---

## 📊 Key Stats to Memorize

**Dataset:**
* 10,039 total facilities
* 236 states/regions covered
* 1,629 cities covered
* Average trust score: 0.744

**Data Quality Crisis:**
* 6,461 facilities (64.9%) - NO_DATE
* 4,999 facilities (50.2%) - POOR_DISTRICT_MATCH  
* 2,884 facilities (29.0%) - DATA_CLIPPED
* 2,207 facilities (22.2%) - TEMPLATE_CONTENT
* 949 facilities (9.5%) - STALE_DATA
* 685 facilities (6.8%) - UNRELIABLE (hidden from patients)

**Trust Score Distribution:**
* 1,542 facilities (15.4%) - HIGH_RELIABILITY (0.74-0.93)
* 7,809 facilities (77.8%) - MODERATE_RELIABILITY (0.58-0.83)
* 685 facilities (6.8%) - UNRELIABLE_DATA (0.39-0.81)

**Volunteer Impact:**
* 1 volunteer = 10 minutes per facility
* 685 urgent facilities ÷ 1,000 volunteers = 6,850 minutes = 114 hours
* Full database (10,039) ÷ 1,000 volunteers = ~3 months to 100% verified

---

## 🎬 Winning Pitch (30 seconds opening)

> "In India, 143 million people wait for surgery each year. They search for facilities like Heritage Hospitals in Varanasi, which claims cardiac care. But our AI trust system found this facility is UNRELIABLE - stale data, overclaiming 200+ services, suspicious patterns. Trust score: 0.45. We HIDE it from patient results to protect them.
>
> Here's the solution: A volunteer opens our app, gets an AI-generated verification script tailored to Heritage's suspicious claims, calls them, confirms they DO have cardiac care. Trust score jumps to 0.88 - now patients can find them.
>
> One volunteer, 10 minutes, one family saved from a wasted journey. We have 685 facilities like this. 1,000 volunteers can verify the entire database in 3 months. This is how we build trust at scale."

---

## 🚨 Demo Pitfalls to Avoid

**DON'T:**
* ❌ Explain the scoring algorithm math (too technical, wastes time)
* ❌ Show multiple facilities (confuses story - stick to Heritage)
* ❌ Show code, pipeline, or backend (judges don't care)
* ❌ Apologize for data quality (it's the PROBLEM we solve!)

**DO:**
* ✅ Show emotion - patient relief when they find trustworthy care
* ✅ Keep Heritage as the hero facility throughout
* ✅ Use "HIDDEN" vs "VISIBLE" language (clear patient safety message)
* ✅ Show real-time update animation (makes it feel alive)
* ✅ End with scale math: "1,000 volunteers = 3 months"

---

## 🔥 Differentiators vs Competition

**Why We Win Track 1 (Facility Trust Desk):**

1. **AI-Generated Custom Scripts** (not generic questions)
   * Adapts to each facility's specific red flags
   * Example: Heritage gets asked about "200+ services" because that's suspicious
   * Competitors use same questions for every facility

2. **Community-Driven at Scale**
   * 1,000 volunteers can verify 10K facilities in 3 months
   * Shows feasibility math clearly
   * Not just "we should crowdsource" - we show HOW

3. **Real-Time Patient Impact**
   * Volunteer verifies → Score updates → Search results change IMMEDIATELY
   * This is the "aha!" moment judges need to see
   * Not a theoretical system - it's LIVE

4. **Protective by Default**
   * LOW trust = HIDDEN from patients (safety-first)
   * Other solutions might show unreliable data with warnings
   * We PROTECT patients by hiding bad data

5. **Geospatial Evidence** (if time permits)
   * Show map with facilities appearing/disappearing based on trust
   * Visual > numbers for judges

---

## 🎥 Screen Flow Sequence

1. **Opening:** Slide with India map + problem stats
2. **Screen 1:** Heritage Hospitals detail (0.45, RED FLAGS, HIDDEN)
3. **Screen 2:** Volunteer portal - facility list
4. **Screen 3:** AI verification script generator
5. **Screen 4:** Verification form + submission
6. **Screen 5:** Real-time score update animation (0.45 → 0.88)
7. **Screen 6:** Patient search - side-by-side BEFORE/AFTER
8. **Screen 7:** Final impact stats dashboard

**Total screens:** 7-8 (30-40 seconds each)

---

## 💡 Backup Q&A Preparation

**Q: How do you prevent fake verifications?**
> A: Verification history is logged with volunteer ID and timestamp. Multiple verifications required for high-stakes changes. Phone verification cross-referenced with public records.

**Q: What if facility lies to volunteer?**
> A: We track verification accuracy over time. Volunteers with high dispute rates are flagged. Multiple volunteers verify high-impact facilities.

**Q: How do you scale beyond India?**
> A: System is geography-agnostic. Replace district health data with country-specific sources. Same trust scoring logic applies anywhere.

**Q: What's your business model?**
> A: This is a public good. Could monetize via: (1) API access for insurance companies, (2) Premium features for facility owners, (3) Government contracts for data quality.

**Q: Why not fully automate with AI?**
> A: Phone verification requires human judgment. AI generates the scripts but humans validate reality. Hybrid approach = accuracy + scale.

---

## ✅ Demo Checklist (Day Before)

**Data Prep:**
- [ ] Heritage Hospitals exists in database with 0.45 trust score
- [ ] Heritage has red flags: STALE_DATA, OVERCLAIMING, DATA_CLIPPED
- [ ] Varanasi has 10+ other facilities for search results
- [ ] Volunteer portal shows Heritage in "needs verification" queue
- [ ] Test data seed script runs successfully

**App Prep:**
- [ ] App deployed and accessible
- [ ] Volunteer portal loads within 2 seconds
- [ ] Patient search loads within 2 seconds
- [ ] Score update animation works smoothly
- [ ] Geospatial map renders correctly

**Technical Prep:**
- [ ] Internet connection stable
- [ ] Browser windows pre-opened to each screen
- [ ] Screen recording backup in case of crash
- [ ] Mobile hotspot ready as backup internet

**Presentation Prep:**
- [ ] Practice demo 10+ times at home
- [ ] Time each section (should be under 3 min)
- [ ] Memorize opening pitch (30 seconds verbatim)
- [ ] Memorize key stats (10,039 facilities, 64.9% missing dates, etc.)
- [ ] Prepare for 2 most likely questions

---

## 🏆 Closing Statement (15 seconds)

> "We've shown you one facility, one volunteer, 10 minutes. But this scales. 1,000 volunteers verifying 10,000 facilities means every patient in India can trust their search results. That's 143 million people waiting for surgery who won't waste another day traveling to the wrong place. That's AI for Good."

**END with:** Logo screen + "HealthVerify India - Trust Through Community"

---

## Notes

* Keep energy HIGH throughout demo
* Smile when showing the score go from 0.45 → 0.88 (this is the win!)
* Point at screen when showing HIDDEN → VISIBLE transition
* Make eye contact with judges during closing statement
* If demo crashes: pivot to screen recording backup immediately
