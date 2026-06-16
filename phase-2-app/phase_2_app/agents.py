from __future__ import annotations

import re

from .models import Facility


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


def match_symptoms(symptom_text: str) -> dict[str, list[str] | str]:
    text = symptom_text.strip()
    for pattern, result in SYMPTOM_RULES:
        if pattern.search(text):
            return result

    return {
        "urgency": "routine",
        "specialties": ["general medicine"],
        "capabilities": ["outpatient care"],
    }


def generate_verification_script(facility: Facility) -> list[dict[str, str]]:
    questions = [
        {"section": "basic", "prompt": "Is this facility currently operational?"},
        {"section": "basic", "prompt": "Can you confirm this phone number is correct?"},
        {"section": "basic", "prompt": "What are your current operating hours?"},
    ]

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
