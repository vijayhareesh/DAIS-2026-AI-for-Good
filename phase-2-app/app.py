from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

# phase_2_app is now in the same directory as app.py, no sys.path manipulation needed

from phase_2_app.store import DemoStore


def get_store() -> DemoStore:
    if "healthverify_store" not in st.session_state:
        st.session_state.healthverify_store = DemoStore.seeded()
    return st.session_state.healthverify_store


st.set_page_config(page_title="HealthVerify India", layout="wide")
st.title("HealthVerify India")
st.caption("Community-driven healthcare facility validation")

store = get_store()
heritage = store.get_facility("heritage-hospitals-varanasi")

col1, col2, col3 = st.columns(3)
col1.metric("Demo Facility", heritage.facility_name)
col2.metric("Trust Score", f"{heritage.trust_score:.3f}")
col3.metric("Validations", heritage.verification_count)

st.write(
    "Use the Volunteer Portal page to validate Heritage Hospitals, then use "
    "Patient Search to see how the updated trust score changes patient results."
)
