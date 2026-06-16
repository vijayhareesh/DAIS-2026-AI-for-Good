from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass(frozen=True)
class Facility:
    unique_id: str
    facility_name: str
    city: str
    state: str
    latitude: float
    longitude: float
    phone_number: str
    trust_score: float
    plausibility_status: str
    freshness_status: str
    risk_factors: tuple[str, ...]
    specialties: tuple[str, ...]
    capabilities: tuple[str, ...]
    verification_count: int = 0
    last_verified_date: datetime | None = None


@dataclass(frozen=True)
class ValidationResult:
    validation_id: str
    facility_id: str
    volunteer_id: str
    claims_checked: int
    claims_verified: int
    claims_failed: int
    old_trust_score: float
    new_trust_score: float
    details: dict[str, bool] = field(default_factory=dict)
    validated_at: datetime = field(default_factory=datetime.utcnow)
