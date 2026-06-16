from __future__ import annotations

import math
import sys
from pathlib import Path

import streamlit as st

# phase_2_app is now accessible from the parent directory
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from phase_2_app.agents import match_symptoms
from phase_2_app.store import DemoStore
from phase_2_app.trust import PATIENT_TRUST_THRESHOLD

try:
    import folium
    from streamlit_folium import st_folium
except ImportError:  # pragma: no cover - exercised only in minimal local envs.
    folium = None
    st_folium = None


CITY_COORDS = {
    "Varanasi": (25.3176, 82.9739),
}


def get_store() -> DemoStore:
    if "healthverify_store" not in st.session_state:
        st.session_state.healthverify_store = DemoStore.seeded()
    return st.session_state.healthverify_store


def distance_km(a_lat: float, a_lon: float, b_lat: float, b_lon: float) -> float:
    earth_radius_km = 6371.0
    d_lat = math.radians(b_lat - a_lat)
    d_lon = math.radians(b_lon - a_lon)
    lat1 = math.radians(a_lat)
    lat2 = math.radians(b_lat)
    h = (
        math.sin(d_lat / 2) ** 2
        + math.cos(lat1) * math.cos(lat2) * math.sin(d_lon / 2) ** 2
    )
    return 2 * earth_radius_km * math.asin(math.sqrt(h))


def marker_color(score: float) -> str:
    if score >= 0.75:
        return "green"
    if score >= 0.60:
        return "orange"
    return "red"


st.set_page_config(page_title="Patient Search", layout="wide")
st.title("Patient Search")

store = get_store()
symptoms = st.text_area("Describe symptoms or care needed", value="Heart pain, trouble breathing")
city = st.selectbox("Location", sorted(CITY_COORDS), index=0)

if st.button("Find Care", type="primary"):
    st.session_state.patient_search_submitted = True

if st.session_state.get("patient_search_submitted", True):
    match = match_symptoms(symptoms)
    origin = CITY_COORDS[city]
    candidates = [
        facility
        for facility in store.list_facilities()
        if facility.city == city and facility.trust_score >= PATIENT_TRUST_THRESHOLD
    ]
    ranked = sorted(
        candidates,
        key=lambda facility: (
            -facility.trust_score,
            distance_km(origin[0], origin[1], facility.latitude, facility.longitude),
        ),
    )

    st.caption(
        "Matched specialties: "
        + ", ".join(match["specialties"])
        + " | Required trust threshold: "
        + f"{PATIENT_TRUST_THRESHOLD:.2f}"
    )

    map_col, results_col = st.columns([0.6, 0.4])
    with map_col:
        if folium and st_folium:
            fmap = folium.Map(location=origin, zoom_start=13)
            for facility in store.list_facilities():
                color = marker_color(facility.trust_score)
                popup = f"{facility.facility_name} ({facility.trust_score:.3f})"
                folium.Marker(
                    location=(facility.latitude, facility.longitude),
                    popup=popup,
                    icon=folium.Icon(color=color),
                ).add_to(fmap)
            st_folium(fmap, height=520, use_container_width=True)
        else:
            st.info("Map libraries are optional locally. Databricks app installs Folium.")

    with results_col:
        st.subheader(f"Top Matches ({len(ranked)})")
        if not ranked:
            st.warning("No facilities meet the trust threshold yet.")
        for idx, facility in enumerate(ranked[:5], start=1):
            km = distance_km(origin[0], origin[1], facility.latitude, facility.longitude)
            with st.container(border=True):
                st.write(f"**{idx}. {facility.facility_name}**")
                st.write(f"Trust score: {facility.trust_score:.3f} | {km:.1f} km away")
                st.caption(", ".join(facility.specialties + facility.capabilities))
                if facility.last_verified_date:
                    st.success("Recently verified")
