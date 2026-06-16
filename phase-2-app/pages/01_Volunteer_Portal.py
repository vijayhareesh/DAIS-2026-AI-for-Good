from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from phase_2_app.agents import generate_verification_script
from phase_2_app.store import DemoStore


def get_store() -> DemoStore:
    if "healthverify_store" not in st.session_state:
        st.session_state.healthverify_store = DemoStore.seeded()
    return st.session_state.healthverify_store


def priority_label(facility) -> str:
    if facility.trust_score < 0.70 or "SUSPICIOUS_VOLUME" in facility.risk_factors:
        return "HIGH"
    if facility.trust_score < 0.80 or facility.freshness_status in {"STALE", "AGING"}:
        return "MEDIUM"
    return "LOW"


st.set_page_config(page_title="Volunteer Portal", layout="wide")
st.title("Volunteer Verification Portal")

store = get_store()
query = st.text_input("Search by facility, city, state, or ID", value="Heritage")
rows = store.search_facilities(query)

left, right = st.columns([0.48, 0.52])

with left:
    st.subheader("Verification Queue")
    for facility in rows:
        with st.container(border=True):
            cols = st.columns([0.18, 0.52, 0.15, 0.15])
            cols[0].write(priority_label(facility))
            cols[1].write(f"**{facility.facility_name}**")
            cols[1].caption(f"{facility.city}, {facility.state}")
            cols[2].metric("Trust", f"{facility.trust_score:.3f}")
            if cols[3].button("Verify", key=f"verify_{facility.unique_id}"):
                st.session_state.selected_facility_id = facility.unique_id

selected_id = st.session_state.get("selected_facility_id", "heritage-hospitals-varanasi")
facility = store.get_facility(selected_id)
script = generate_verification_script(facility)

with right:
    st.subheader(f"Verify: {facility.facility_name}")
    st.write(f"{facility.city}, {facility.state}")
    st.write(f"Phone: {facility.phone_number}")
    st.progress(min(facility.trust_score, 1.0), text=f"Current trust score {facility.trust_score:.3f}")

    st.markdown("**Generated verification script**")
    for idx, item in enumerate(script, start=1):
        st.write(f"{idx}. {item['prompt']}")

    st.markdown("**Validation form**")
    responses = {}
    for idx, item in enumerate(script, start=1):
        responses[item["prompt"]] = st.checkbox(item["prompt"], value=idx <= 13, key=f"q_{idx}")

    notes = st.text_area("Volunteer notes", value="Facility confirmed most services. Neurology needs follow-up.")
    if st.button("Submit Validation", type="primary"):
        checked = 15
        verified = min(14, sum(1 for value in responses.values() if value) + facility.verification_count)
        result = store.submit_validation(
            facility_id=facility.unique_id,
            volunteer_id="demo_volunteer",
            claims_checked=checked,
            claims_verified=verified,
            details=responses,
        )
        st.success(
            f"Validation saved. Trust score moved from "
            f"{result.old_trust_score:.3f} to {result.new_trust_score:.3f}."
        )
        st.caption(notes)
