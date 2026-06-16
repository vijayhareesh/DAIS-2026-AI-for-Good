from __future__ import annotations

from dataclasses import replace
from uuid import uuid4

from .demo_data import seeded_facilities
from .models import Facility, ValidationResult
from .trust import PATIENT_TRUST_THRESHOLD, recalculate_trust_score


class DemoStore:
    def __init__(self, facilities: list[Facility]):
        self._facilities = {facility.unique_id: facility for facility in facilities}
        self._validations: list[ValidationResult] = []

    @classmethod
    def seeded(cls) -> "DemoStore":
        return cls(seeded_facilities())

    def get_facility(self, facility_id: str) -> Facility:
        return self._facilities[facility_id]

    def list_facilities(self) -> list[Facility]:
        return list(self._facilities.values())

    def patient_visible(self, facility_id: str) -> bool:
        return self.get_facility(facility_id).trust_score >= PATIENT_TRUST_THRESHOLD

    def search_facilities(self, text: str = "", city: str | None = None) -> list[Facility]:
        needle = text.strip().lower()
        rows = self.list_facilities()
        if city:
            rows = [facility for facility in rows if facility.city.lower() == city.lower()]
        if needle:
            rows = [
                facility
                for facility in rows
                if needle in facility.facility_name.lower()
                or needle in facility.city.lower()
                or needle in facility.state.lower()
                or needle in facility.unique_id.lower()
            ]
        return sorted(rows, key=lambda facility: facility.trust_score)

    def submit_validation(
        self,
        facility_id: str,
        volunteer_id: str,
        claims_checked: int,
        claims_verified: int,
        details: dict[str, bool],
    ) -> ValidationResult:
        facility = self.get_facility(facility_id)
        new_score = recalculate_trust_score(
            old_score=facility.trust_score,
            claims_checked=claims_checked,
            claims_verified=claims_verified,
            verification_count=facility.verification_count,
        )
        validation = ValidationResult(
            validation_id=f"val_{uuid4().hex[:10]}",
            facility_id=facility_id,
            volunteer_id=volunteer_id,
            claims_checked=claims_checked,
            claims_verified=claims_verified,
            claims_failed=claims_checked - claims_verified,
            old_trust_score=facility.trust_score,
            new_trust_score=new_score,
            details=details,
        )
        self._validations.append(validation)
        self._facilities[facility_id] = replace(
            facility,
            trust_score=new_score,
            verification_count=facility.verification_count + 1,
            last_verified_date=validation.validated_at,
        )
        return validation

    def validations(self) -> list[ValidationResult]:
        return list(self._validations)
