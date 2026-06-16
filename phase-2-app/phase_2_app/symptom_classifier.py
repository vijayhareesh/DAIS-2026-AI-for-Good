from __future__ import annotations

import json
import os
import re
from typing import Any

import requests
from databricks.sdk.core import Config

from .ranking import display_medical_term, unique_terms


PROMPT = """Classify patient symptoms for healthcare facility search in India.
Return only valid compact JSON with these keys:
urgency: one of high, medium, routine
specialties: array of medical specialties
capabilities: array of facility capabilities
Use common English medical terms, not explanations."""


def normalize_classification(result: dict[str, Any]) -> dict[str, list[str] | str]:
    urgency = str(result.get("urgency", "routine")).strip().lower()
    if urgency not in {"high", "medium", "routine"}:
        urgency = "routine"

    specialties = [
        display_medical_term(value).lower()
        for value in unique_terms(result.get("specialties") or [])
    ]
    capabilities = [
        display_medical_term(value).lower()
        for value in unique_terms(result.get("capabilities") or [])
    ]

    if not specialties:
        specialties = ["general medicine"]
    if not capabilities:
        capabilities = ["outpatient care"]

    return {
        "urgency": urgency,
        "specialties": specialties,
        "capabilities": capabilities,
    }


def parse_model_response(payload: dict[str, Any]) -> dict[str, list[str] | str]:
    content = ""
    choices = payload.get("choices")
    if choices:
        message = choices[0].get("message", {})
        content = message.get("content") or choices[0].get("text") or ""
    elif "predictions" in payload:
        prediction = payload["predictions"][0]
        content = prediction if isinstance(prediction, str) else json.dumps(prediction)
    elif "content" in payload:
        content = str(payload["content"])

    if not content:
        raise ValueError("Model response did not include classification content")

    try:
        decoded = json.loads(content)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", content, re.S)
        if not match:
            raise
        decoded = json.loads(match.group(0))

    if not isinstance(decoded, dict):
        raise ValueError("Model response JSON must be an object")
    return normalize_classification(decoded)


class ModelServingSymptomClassifier:
    def __init__(self, endpoint_name: str, timeout_seconds: int = 20):
        self.endpoint_name = endpoint_name
        self.timeout_seconds = timeout_seconds

    @classmethod
    def from_env(cls) -> "ModelServingSymptomClassifier":
        endpoint_name = os.environ.get("HEALTHVERIFY_SYMPTOM_CLASSIFIER_ENDPOINT")
        if not endpoint_name:
            raise ValueError("HEALTHVERIFY_SYMPTOM_CLASSIFIER_ENDPOINT is not configured")
        return cls(endpoint_name)

    def classify(self, symptom_text: str) -> dict[str, list[str] | str]:
        cfg = Config()
        headers = cfg.authenticate()
        headers["Content-Type"] = "application/json"
        response = requests.post(
            f"{cfg.host.rstrip('/')}/serving-endpoints/{self.endpoint_name}/invocations",
            headers=headers,
            json={
                "messages": [
                    {"role": "system", "content": PROMPT},
                    {"role": "user", "content": symptom_text},
                ],
                "temperature": 0.0,
                "max_tokens": 250,
            },
            timeout=self.timeout_seconds,
        )
        response.raise_for_status()
        return parse_model_response(response.json())
