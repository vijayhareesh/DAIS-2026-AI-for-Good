from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

# phase_2_app is now accessible from the parent directory
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from phase_2_app.agents import generate_verification_script
from phase_2_app.store import create_store


def get_store():
    if "healthverify_store" not in st.session_state:
        st.session_state.healthverify_store = create_store()
    return st.session_state.healthverify_store


def priority_label(facility) -> str:
    if facility.trust_score < 0.70:
        return "HIGH"
    if facility.trust_score < 0.80:
        return "MEDIUM"
    return "LOW"


st.set_page_config(page_title="Volunteer Portal", layout="wide")
st.title("Volunteer Verification Portal")

store = get_store()
query = st.text_input("Search by facility, city, state, or ID", value="")
rows = store.volunteer_queue(query, limit=20)

left, right = st.columns([0.48, 0.52])

with left:
    st.subheader(f"Verification Queue ({len(rows)} facilities)")
    for facility in rows:
        with st.container(border=True):
            cols = st.columns([0.18, 0.52, 0.15, 0.15])
            cols[0].write(priority_label(facility))
            cols[1].write(f"**{facility.facility_name}**")
            cols[1].caption(f"{facility.city}, {facility.state}")
            cols[2].metric("Trust", f"{facility.trust_score:.3f}")
            if cols[3].button("Verify", key=f"verify_{facility.unique_id}"):
                st.session_state.selected_facility_id = facility.unique_id

if rows:
    row_ids = {facility.unique_id for facility in rows}
    if st.session_state.get("selected_facility_id") not in row_ids:
        st.session_state.selected_facility_id = rows[0].unique_id
    selected_id = st.session_state.selected_facility_id
    facility = store.get_facility(selected_id)
    
    if facility:
        script = generate_verification_script(facility)

        with right:
            st.subheader(f"Verify: {facility.facility_name}")
            st.write(f"{facility.city}, {facility.state}")
            if facility.official_phone:
                st.write(f"Phone: {facility.official_phone}")
            st.progress(min(facility.trust_score, 1.0), text=f"Current trust score {facility.trust_score:.3f}")

            st.markdown("**Generated verification script**")
            for idx, item in enumerate(script, start=1):
                st.write(f"{idx}. {item['prompt']}")

            st.markdown("**Validation form**")
            responses = {}
            for idx, item in enumerate(script, start=1):
                responses[item["prompt"]] = st.checkbox(item["prompt"], value=idx <= 13, key=f"q_{idx}")

            notes = st.text_area("Volunteer notes", value="")
            if st.button("Submit Validation", type="primary"):
                checked = len(script)
                verified = sum(1 for value in responses.values() if value)
                result = store.submit_validation(
                    facility_id=facility.unique_id,
                    volunteer_id="demo_volunteer",
                    claims_checked=checked,
                    claims_verified=verified,
                    details=responses,
                )
                st.success(
                    f"✓ Validation saved! Trust score: "
                    f"{result.old_trust_score:.3f} → {result.new_trust_score:.3f}"
                )
                if notes:
                    st.caption(f"Notes: {notes}")
else:
    with right:
        st.info("Search for facilities to verify")
