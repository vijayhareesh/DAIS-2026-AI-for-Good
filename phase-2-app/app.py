from __future__ import annotations

from pathlib import Path

import streamlit as st

from phase_2_app.app_style import apply_app_style
from phase_2_app.home_content import project_summary


PROJECT_DESCRIPTION_PATH = Path(__file__).resolve().parent / "PROJECT_DESCRIPTION.md"


st.set_page_config(page_title="Home", layout="wide")
apply_app_style()

summary = project_summary(PROJECT_DESCRIPTION_PATH)

st.title(summary["title"])
st.caption("Community-driven healthcare facility validation")

st.markdown(summary["inspiration"])

left, right = st.columns([0.52, 0.48])

with left:
    st.subheader("What It Does")
    st.markdown(summary["what_it_does"])

with right:
    st.subheader("How We Built It")
    st.markdown(summary["how_we_built_it"])

st.subheader("What's Next")
st.markdown(summary["next_steps"])
