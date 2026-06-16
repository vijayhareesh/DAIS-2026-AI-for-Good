from __future__ import annotations

import math
import re
import sys
from pathlib import Path

import streamlit as st

# phase_2_app is now accessible from the parent directory
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from phase_2_app.agents import match_symptoms
from phase_2_app.app_style import apply_app_style
from phase_2_app.patient_ui import result_heading
from phase_2_app.ranking import rank_patient_facilities
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


CITY_ALL = "All cities"


def format_medical_term(value: str) -> str:
    spaced = re.sub(r"(?<=[a-z])(?=[A-Z])", " ", value)
    return spaced.replace("_", " ").replace("-", " ").strip().title()


def display_key(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", format_medical_term(value).lower())


def format_terms(values: tuple[str, ...] | list[str], limit: int = 6) -> str:
    if not values:
        return ""
    unique_values = []
    seen = set()
    for value in values:
        key = display_key(value)
        if not key or key in seen:
            continue
        seen.add(key)
        unique_values.append(value)
    visible = [format_medical_term(value) for value in unique_values[:limit]]
    remaining = len(unique_values) - limit
    suffix = f" +{remaining} more" if remaining > 0 else ""
    return ", ".join(visible) + suffix


def marker_style(rank: int, is_selected: bool) -> tuple[str, str, str]:
    if is_selected:
        return "red", "star", "Selected"
    if rank == 1:
        return "orange", "star", "Top match"
    if rank <= 3:
        return "green", "ok-sign", "Top 3"
    if rank <= 10:
        return "blue", "info-sign", "Top 10"
    return "gray", "plus", "Additional"


def has_coordinates(facility) -> bool:
    return facility.latitude is not None and facility.longitude is not None


st.set_page_config(page_title="Patient Search", layout="wide")
apply_app_style()
st.title("Patient Search")

store = get_store()
symptoms = st.text_area("Describe symptoms or care needed", value="Heart pain, trouble breathing")

if "patient_search_cities" not in st.session_state:
    st.session_state.patient_search_cities = store.list_cities(limit=500)

city_options = [CITY_ALL] + st.session_state.patient_search_cities
selected_city_label = st.selectbox("City", city_options, index=0)
selected_city = None if selected_city_label == CITY_ALL else selected_city_label

if st.button("Find Care", type="primary"):
    st.session_state.patient_search_submitted = True

if st.session_state.get("patient_search_submitted", True):
    match = match_symptoms(symptoms)
    
    # Search facilities by city
    candidates = [
        facility
        for facility in store.search_facilities(text="", city=selected_city, limit=100)
        if facility.trust_score >= PATIENT_TRUST_THRESHOLD
    ]
    
    ranked = rank_patient_facilities(candidates, match)

    st.caption(
        "Matched specialties: "
        + format_terms(match["specialties"])
        + f" | Classifier: {str(match.get('source', 'rules')).replace('_', ' ').title()}"
        + " | Required trust threshold: "
        + f"{PATIENT_TRUST_THRESHOLD:.2f}"
    )

    selected_id = None
    if ranked:
        ranked_ids = [facility.unique_id for facility in ranked]
        if st.session_state.get("patient_selected_facility_id") not in ranked_ids:
            st.session_state.patient_selected_facility_id = ranked[0].unique_id

        top_ids = [facility.unique_id for facility in ranked[:10]]
        rank_lookup = {facility.unique_id: index for index, facility in enumerate(ranked, start=1)}
        facility_lookup = {facility.unique_id: facility for facility in ranked}
        selected_id = st.selectbox(
            "Highlight match on map",
            top_ids,
            index=top_ids.index(st.session_state.patient_selected_facility_id)
            if st.session_state.patient_selected_facility_id in top_ids
            else 0,
            format_func=lambda facility_id: (
                f"#{rank_lookup[facility_id]} {facility_lookup[facility_id].facility_name}"
            ),
            key="patient_selected_facility_id",
        )

    visible_results = min(len(ranked), 10)
    map_col, results_col = st.columns([0.55, 0.45])
    with map_col:
        mapped_facilities = [facility for facility in ranked[:20] if has_coordinates(facility)]
        selected_facility = next(
            (facility for facility in ranked if facility.unique_id == selected_id),
            ranked[0] if ranked else None,
        )
        center_facility = (
            selected_facility
            if selected_facility and has_coordinates(selected_facility)
            else mapped_facilities[0] if mapped_facilities else None
        )

        if folium and st_folium and center_facility:
            center = (center_facility.latitude, center_facility.longitude)
            fmap = folium.Map(location=center, zoom_start=12)
            
            for rank, facility in enumerate(ranked[:20], start=1):
                if has_coordinates(facility):
                    is_selected = facility.unique_id == selected_id
                    color, icon, priority = marker_style(rank, is_selected)
                    popup = (
                        f"#{rank} {facility.facility_name}<br>"
                        f"{priority}<br>"
                        f"Trust score: {facility.trust_score:.3f}"
                    )
                    folium.Marker(
                        location=(facility.latitude, facility.longitude),
                        popup=popup,
                        tooltip=f"#{rank} {facility.facility_name}",
                        icon=folium.Icon(color=color, icon=icon),
                    ).add_to(fmap)
            st_folium(fmap, height=520, use_container_width=True)
            st.caption("Marker priority: selected red, top match orange, top 3 green, top 10 blue, additional gray.")
        else:
            st.info("Map requires valid facility coordinates. Search for facilities with location data.")

    with results_col:
        st.subheader(result_heading(total_count=len(ranked), visible_count=10))
        if len(ranked) > visible_results:
            st.caption(f"Showing the first {visible_results} ranked facilities. Use city or symptoms to narrow results.")
        if not ranked:
            st.warning("No facilities meet the trust threshold in this area.")
        for idx, facility in enumerate(ranked[:10], start=1):
            with st.container(border=True):
                st.write(f"**{idx}. {facility.facility_name}**")
                score_cols = st.columns(2)
                score_cols[0].caption(f"Trust score: {facility.trust_score:.3f}")
                score_cols[1].caption(f"Match score: {facility.match_score:.2f}")
                st.caption(f"{facility.city}, {facility.state}")
                if facility.unique_id == selected_id:
                    st.success("Highlighted on map")
                if facility.matched_specialties or facility.matched_capabilities:
                    st.caption(
                        "Matched: "
                        + format_terms(facility.matched_specialties + facility.matched_capabilities)
                    )
                if facility.specialties:
                    st.caption(f"Specialties: {format_terms(facility.specialties)}")
                if facility.last_verified_date:
                    st.success(f"✓ Last verified: {facility.last_verified_date.strftime('%Y-%m-%d')}")
