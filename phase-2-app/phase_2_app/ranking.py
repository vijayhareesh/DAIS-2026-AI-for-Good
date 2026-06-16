from __future__ import annotations

import re
from dataclasses import replace
from typing import Iterable

from .models import Facility


def normalize_medical_term(value: str) -> str:
    spaced = re.sub(r"(?<=[a-z])(?=[A-Z])", " ", str(value))
    return re.sub(r"[^a-z0-9]+", "", spaced.lower())


def display_medical_term(value: str) -> str:
    spaced = re.sub(r"(?<=[a-z])(?=[A-Z])", " ", str(value))
    return spaced.replace("_", " ").replace("-", " ").strip().title()


def unique_terms(values: Iterable[str]) -> tuple[str, ...]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        text = str(value).strip()
        key = normalize_medical_term(text)
        if not text or not key or key in seen:
            continue
        seen.add(key)
        result.append(text)
    return tuple(result)


def matched_terms(available: Iterable[str], requested: Iterable[str]) -> tuple[str, ...]:
    requested_by_key = {
        normalize_medical_term(value): str(value).strip()
        for value in requested
        if str(value).strip()
    }

    def matched_display_value(value: str) -> str | None:
        key = normalize_medical_term(value)
        for requested_key, requested_value in requested_by_key.items():
            if key == requested_key:
                return value
            if len(requested_key) >= 5 and requested_key in key:
                return requested_value if len(str(value)) > 24 else value
            if len(key) >= 5 and key in requested_key:
                return value
        return None

    return unique_terms(
        matched_value
        for value in available
        for matched_value in [matched_display_value(value)]
        if matched_value
    )


def rank_patient_facilities(
    facilities: Iterable[Facility],
    symptom_match: dict[str, list[str] | str],
) -> list[Facility]:
    requested_specialties = symptom_match.get("specialties", [])
    requested_capabilities = symptom_match.get("capabilities", [])

    ranked: list[Facility] = []
    for facility in facilities:
        specialty_hits = matched_terms(facility.specialties, requested_specialties)
        capability_hits = matched_terms(facility.capabilities, requested_capabilities)
        match_score = (
            len(specialty_hits) * 3.0
            + len(capability_hits) * 1.5
            + facility.trust_score * 0.25
        )
        ranked.append(
            replace(
                facility,
                match_score=match_score,
                matched_specialties=specialty_hits,
                matched_capabilities=capability_hits,
            )
        )

    return sorted(
        ranked,
        key=lambda facility: (facility.match_score, facility.trust_score),
        reverse=True,
    )


def volunteer_priority_key(facility: Facility) -> tuple[int, float, int, str]:
    if facility.trust_score < 0.70:
        priority_bucket = 0
    elif facility.trust_score < 0.80:
        priority_bucket = 1
    else:
        priority_bucket = 2
    return (
        priority_bucket,
        facility.trust_score,
        facility.verification_count,
        facility.facility_name.lower(),
    )


def rank_volunteer_facilities(facilities: Iterable[Facility]) -> list[Facility]:
    return sorted(facilities, key=volunteer_priority_key)
