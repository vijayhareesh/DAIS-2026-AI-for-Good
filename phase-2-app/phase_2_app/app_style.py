from __future__ import annotations

import streamlit as st


APP_CSS = """
<style>
  .block-container {
    max-width: 1280px;
    padding-top: 1.4rem;
    padding-left: 1.5rem;
    padding-right: 1.5rem;
  }

  div[data-testid="stVerticalBlock"] {
    gap: 0.65rem;
  }

  div[data-testid="stHorizontalBlock"] {
    gap: 0.75rem;
  }

  .stButton > button {
    width: 100%;
    min-height: 2.35rem;
    padding: 0.35rem 0.5rem;
    white-space: normal;
    line-height: 1.15;
  }

  div[data-testid="stMetric"] {
    background: transparent;
  }

  div[data-testid="stMetricValue"] {
    font-size: 1.08rem;
    overflow-wrap: anywhere;
  }

  p, li, label, span {
    overflow-wrap: anywhere;
  }

  h1 {
    font-size: clamp(1.9rem, 2.8vw, 2.55rem);
  }

  h2, h3 {
    line-height: 1.18;
  }
</style>
"""


def apply_app_style() -> None:
    st.markdown(APP_CSS, unsafe_allow_html=True)
