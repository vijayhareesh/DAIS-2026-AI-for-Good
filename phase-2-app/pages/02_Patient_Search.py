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
from phase_2_app.store import create_store
from phase_2_app.trust import PATIENT_TRUST_THRESHOLD

try:
    import folium
    from streamlit_folium import st_folium
except ImportError:
    folium = None
    st_folium = None


def get_store():
    if "healthverify_store" not in st.session_state:
        st.session_state.healthverify_store = create_store()
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
city = st.text_input("City", value="")

if st.button("Find Care", type="primary"):
    st.session_state.patient_search_submitted = True

if st.session_state.get("patient_search_submitted", True):
    match = match_symptoms(symptoms)
    
    # Search facilities by city
    candidates = [
        facility
        for facility in store.search_facilities(text="", city=city if city else None, limit=100)
        if facility.trust_score >= PATIENT_TRUST_THRESHOLD
    ]
    
    # Sort by trust score (distance requires valid lat/lon)
    ranked = sorted(candidates, key=lambda f: -f.trust_score)

    st.caption(
        "Matched specialties: "
        + ", ".join(match["specialties"])
        + " | Required trust threshold: "
        + f"{PATIENT_TRUST_THRESHOLD:.2f}"
    )

    map_col, results_col = st.columns([0.6, 0.4])
    with map_col:
        if folium and st_folium and ranked and ranked[0].latitude and ranked[0].longitude:
            # Center on first result
            center = (ranked[0].latitude, ranked[0].longitude)
            fmap = folium.Map(location=center, zoom_start=12)
            
            for facility in ranked[:20]:  # Show top 20 on map
                if facility.latitude and facility.longitude:
                    color = marker_color(facility.trust_score)
                    popup = f"{facility.facility_name} ({facility.trust_score:.3f})"
                    folium.Marker(
                        location=(facility.latitude, facility.longitude),
                        popup=popup,
                        icon=folium.Icon(color=color),
                    ).add_to(fmap)
            st_folium(fmap, height=520, use_container_width=True)
        else:
            st.info("Map requires valid facility coordinates. Search for facilities with location data.")

    with results_col:
        st.subheader(f"Top Matches ({len(ranked)})" )
        if not ranked:
            st.warning("No facilities meet the trust threshold in this area.")
        for idx, facility in enumerate(ranked[:10], start=1):
            with st.container(border=True):
                st.write(f"**{idx}. {facility.facility_name}**")
                st.write(f"Trust score: {facility.trust_score:.3f}")
                st.caption(f"{facility.city}, {facility.state}")
                if facility.specialties:
                    st.caption(f"Specialties: {facility.specialties}")
                if facility.last_verified_date:
                    st.success(f"✓ Last verified: {facility.last_verified_date.strftime('%Y-%m-%d')}")
