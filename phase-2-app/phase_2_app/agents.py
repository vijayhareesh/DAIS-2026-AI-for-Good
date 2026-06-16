from __future__ import annotations

import os
import re

from .models import Facility
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


def facility_gap_prompts(facility: Facility) -> list[str]:
    prompts: list[str] = []

    if not facility.official_phone and not facility.phone_number:
        prompts.append("What is the best official phone number for this facility?")
    elif not facility.official_phone:
        prompts.append("Can you confirm the official phone number for the public listing?")

    if not facility.official_website:
        prompts.append("Does the facility have an official website or verified public page?")

    if not facility.email:
        prompts.append("What official email address should patients use, if any?")

    if not facility.pincode:
        prompts.append("What is the correct pincode for the facility address?")

    if not facility.specialties:
        prompts.append("Which specialties are currently available at this facility?")

    if not facility.capabilities:
        prompts.append("Which emergency, diagnostic, or inpatient capabilities are currently available?")

    if facility.trust_score < 0.70:
        prompts.append(
            "Because the confidence score is low, can you confirm the facility name, "
            "address, phone, and currently available services?"
        )

    return prompts


def generate_verification_script(facility: Facility) -> list[dict[str, str]]:
    questions = [
        {"section": "basic", "prompt": "Is this facility currently operational?"},
        {"section": "basic", "prompt": "Can you confirm this phone number is correct?"},
        {"section": "basic", "prompt": "What are your current operating hours?"},
    ]

    questions.extend(
        {"section": "information gaps", "prompt": prompt}
        for prompt in facility_gap_prompts(facility)
    )

    if "SUSPICIOUS_VOLUME" in facility.risk_factors:
        progressive_prompts = [
            "Can you confirm cardiology services are currently available?",
            "Can you confirm orthopedics services are currently available?",
            "Can you confirm neurology services are currently available?",
            "Does the facility have ICU beds as claimed?",
            "Does the facility provide emergency medicine coverage?",
            "Is oxygen support available for critical patients?",
            "Is ambulance transfer available?",
        ]
        questions.extend(
            {"section": "progressive", "prompt": prompt} for prompt in progressive_prompts
        )

    if facility.freshness_status in {"STALE", "NO_DATE", "AGING"}:
        stale_prompts = [
            "Has the facility address changed recently?",
            "Have any major specialties been added or removed?",
            "Is the public website or listing still active?",
        ]
        questions.extend({"section": "staleness", "prompt": prompt} for prompt in stale_prompts)

    return questions[:13]
