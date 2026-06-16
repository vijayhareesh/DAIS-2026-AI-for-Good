from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

# phase_2_app is now accessible from the parent directory
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from phase_2_app.agents import generate_verification_script
from phase_2_app.app_style import apply_app_style
from phase_2_app.store import create_store
from phase_2_app.volunteer_ui import (
    compact_trust_html,
    priority_badge_html,
    priority_label,
    verification_checkbox_key,
)


def get_store():
    if "healthverify_store" not in st.session_state:
        st.session_state.healthverify_store = create_store()
    return st.session_state.healthverify_store


st.set_page_config(page_title="Volunteer Portal", layout="wide")
apply_app_style()
st.title("Volunteer Verification Portal")

store = get_store()
query = st.text_input("Search by facility, city, state, or ID", value="")
rows = store.volunteer_queue(query, limit=20)

left, right = st.columns([0.48, 0.52])

with left:
    st.subheader(f"Verification Queue ({len(rows)} facilities)")
    for facility in rows:
        with st.container(border=True):
            cols = st.columns([0.18, 0.48, 0.18, 0.16])
            priority = priority_label(facility.trust_score)
            cols[0].markdown(priority_badge_html(priority), unsafe_allow_html=True)
            cols[1].write(f"**{facility.facility_name}**")
            cols[1].caption(f"{facility.city}, {facility.state}")
            cols[2].markdown(compact_trust_html(facility.trust_score), unsafe_allow_html=True)
            if cols[3].button("Verify", key=f"verify_{facility.unique_id}", use_container_width=True):
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
            st.subheader(facility.facility_name)
            st.write(f"{facility.city}, {facility.state}")
            if facility.official_phone:
                st.write(f"Phone: {facility.official_phone}")
            st.progress(min(facility.trust_score, 1.0), text=f"Current trust score {facility.trust_score:.3f}")

            st.markdown("**Verification checklist**")
            responses = {}
            for idx, item in enumerate(script, start=1):
                prompt = item["prompt"]
                responses[prompt] = st.checkbox(
                    f"{idx}. {prompt}",
                    value=False,
                    key=verification_checkbox_key(facility.unique_id, idx),
                )

            notes = st.text_area("Volunteer notes", value="", key=f"notes_{facility.unique_id}")
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
