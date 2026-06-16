from __future__ import annotations

import os
import re

from .models import Facility
from .ranking import display_medical_term, normalize_medical_term, unique_terms
from .symptom_classifier import ModelServingSymptomClassifier, normalize_classification


SYMPTOM_RULES = [
    (
        re.compile(r"\b(heart|chest|cardiac|breath|breathing|shortness)\b", re.I),
        {
            "urgency": "high",
            "specialties": ["cardiology", "emergency medicine", "critical care"],
            "capabilities": ["icu", "oxygen support", "cardiac monitoring", "ambulance"],
        },
    ),
    (
        re.compile(r"\b(fracture|bone|joint|orthopedic|orthopaedic)\b", re.I),
        {
            "urgency": "medium",
            "specialties": ["orthopedics", "emergency medicine"],
            "capabilities": ["x-ray", "surgery"],
        },
    ),
]


def rule_based_match_symptoms(symptom_text: str) -> dict[str, list[str] | str]:
    text = symptom_text.strip()
    for pattern, result in SYMPTOM_RULES:
        if pattern.search(text):
            return {**result, "source": "rules"}

    return {
        "urgency": "routine",
        "specialties": ["general medicine"],
        "capabilities": ["outpatient care"],
        "source": "rules",
    }


def match_symptoms(symptom_text: str, classifier=None) -> dict[str, list[str] | str]:
    if classifier is None and os.environ.get("HEALTHVERIFY_USE_MODEL_SERVING", "").lower() == "true":
        try:
            classifier = ModelServingSymptomClassifier.from_env()
        except Exception:
            classifier = None

    if classifier is not None:
        try:
            result = normalize_classification(classifier.classify(symptom_text))
            return {**result, "source": "model_serving"}
        except Exception:
            return rule_based_match_symptoms(symptom_text)

    return rule_based_match_symptoms(symptom_text)


def facility_location(facility: Facility) -> str:
    parts = [part for part in (facility.city, facility.state) if part]
    return ", ".join(parts) if parts else "the listed location"


def public_phone(facility: Facility) -> str:
    return facility.official_phone or facility.phone_number


def summarize_terms(
    values: tuple[str, ...],
    limit: int = 4,
    excluded_context: tuple[str, ...] = (),
) -> str:
    excluded_keys = {
        normalize_medical_term(value)
        for value in excluded_context
        if normalize_medical_term(value)
    }
    terms: list[str] = []
    for value in unique_terms(values):
        text = str(value).strip()
        normalized = normalize_medical_term(text)
        if any(excluded_key and excluded_key in normalized for excluded_key in excluded_keys):
            continue
        if re.search(
            r"\b(is located|located in|listed among|top clinics|near me|doctors? on staff)\b",
            text,
            re.I,
        ):
            continue
        terms.append(display_medical_term(text))

    if len(terms) <= limit:
        return ", ".join(terms)
    return ", ".join(terms[:limit]) + f", and {len(terms) - limit} more"


def facility_claim_prompts(facility: Facility) -> list[str]:
    prompts: list[str] = []
    name = facility.facility_name
    location = facility_location(facility)
    phone = public_phone(facility)

    prompts.append(f"Is {name} currently operational in {location}?")

    if phone:
        prompts.append(f"Can you confirm that {name}'s public phone number {phone} reaches the facility?")
    else:
        prompts.append(f"What is the best official phone number for {name}?")

    prompts.append(f"What are {name}'s current operating hours?")

    if facility.specialties:
        prompts.append(
            f"Can you confirm {name} currently offers these listed specialties: "
            f"{summarize_terms(facility.specialties)}?"
        )

    if facility.capabilities:
        capabilities = summarize_terms(facility.capabilities, excluded_context=(name,))
        if capabilities:
            prompts.append(
                f"Can you confirm these listed capabilities at {name}: "
                f"{capabilities}?"
            )

    return prompts


def facility_gap_prompts(facility: Facility) -> list[str]:
    prompts: list[str] = []
    name = facility.facility_name
    location = facility_location(facility)
    phone = public_phone(facility)

    if not facility.official_phone and not facility.phone_number:
        prompts.append(f"What is the best official phone number for {name}?")
    elif not facility.official_phone:
        prompts.append(
            f"The record lists {phone}, but no separately verified official phone. "
            f"Can you confirm the official phone number for {name}?"
        )

    if not facility.official_website:
        prompts.append(
            f"No official website is listed for {name}. "
            "Is there a verified website or public page patients should use?"
        )

    if not facility.email:
        prompts.append(f"What official email address should patients use for {name}, if any?")

    if not facility.pincode:
        prompts.append(f"What is the correct pincode for {name} in {location}?")

    if not facility.specialties:
        prompts.append(f"Which specialties are currently available at {name}?")

    if not facility.capabilities:
        prompts.append(
            f"Which emergency, diagnostic, or inpatient capabilities are currently available at {name}?"
        )

    if facility.trust_score < 0.70:
        prompts.append(
            f"Because the confidence score is low ({facility.trust_score:.3f}), which listed details "
            f"for {name} are wrong or missing: name, address, phone, specialties, or capabilities?"
        )

    return prompts


def generate_verification_script(facility: Facility) -> list[dict[str, str]]:
    questions = [
        {"section": "basic", "prompt": prompt}
        for prompt in facility_claim_prompts(facility)
    ]

    questions.extend(
        {"section": "information gaps", "prompt": prompt}
        for prompt in facility_gap_prompts(facility)
    )

    if "SUSPICIOUS_VOLUME" in facility.risk_factors:
        name = facility.facility_name
        progressive_prompts = [
            f"Can you confirm whether cardiology services are currently available at {name}?",
            f"Can you confirm whether orthopedics services are currently available at {name}?",
            f"Can you confirm whether neurology services are currently available at {name}?",
            f"Does {name} have ICU beds as claimed?",
            f"Does {name} provide emergency medicine coverage?",
            f"Is oxygen support available for critical patients at {name}?",
            f"Is ambulance transfer available at {name}?",
        ]
        questions.extend(
            {"section": "progressive", "prompt": prompt} for prompt in progressive_prompts
        )

    if facility.freshness_status in {"STALE", "NO_DATE", "AGING"}:
        name = facility.facility_name
        stale_prompts = [
            f"Has {name}'s facility address changed recently?",
            f"Have any major specialties been added or removed at {name}?",
            f"Is {name}'s public website or listing still active?",
        ]
        questions.extend({"section": "staleness", "prompt": prompt} for prompt in stale_prompts)

    return questions[:13]
