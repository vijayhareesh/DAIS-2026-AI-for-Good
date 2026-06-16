from __future__ import annotations

import streamlit as st

from phase_2_app.store import create_store


def get_store():
    if "healthverify_store" not in st.session_state:
        st.session_state.healthverify_store = create_store()
    return st.session_state.healthverify_store


st.set_page_config(page_title="HealthVerify India", layout="wide")
st.title("HealthVerify India")
st.caption("Community-driven healthcare facility validation")

store = get_store()

# Show summary stats
facilities = store.list_facilities(limit=10)
if facilities:
    col1, col2, col3 = st.columns(3)
    col1.metric("Top Facility", facilities[0].facility_name)
    col2.metric("Trust Score", f"{facilities[0].trust_score:.3f}")
    col3.metric("Total Loaded", len(facilities))
    
    st.info(
        "✓ Connected to Lakebase with real facility data. "
        "Use **Volunteer Portal** to validate facilities, then use **Patient Search** "
        "to see updated trust scores."
    )
else:
    st.warning(
        "No facilities loaded. Check Lakebase sync status."
    )
