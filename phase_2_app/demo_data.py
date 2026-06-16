from __future__ import annotations

from .models import Facility


def heritage_hospitals() -> Facility:
    return Facility(
        unique_id="heritage-hospitals-varanasi",
        facility_name="Heritage Hospitals",
        city="Varanasi",
        state="Uttar Pradesh",
        latitude=25.3176,
        longitude=82.9739,
        phone_number="+91-542-XXX-XXXX",
        trust_score=0.68,
        plausibility_status="SUSPICIOUS_VOLUME",
        freshness_status="STALE",
        risk_factors=("SUSPICIOUS_VOLUME", "STALE", "HIGH_CLAIM_COUNT"),
        specialties=("cardiology", "orthopedics", "neurology"),
        capabilities=(
            "icu",
            "emergency medicine",
            "oxygen support",
            "cardiac monitoring",
            "ambulance",
        ),
        verification_count=0,
    )


def seeded_facilities() -> list[Facility]:
    return [
        heritage_hospitals(),
        Facility(
            unique_id="city-hospital-varanasi",
            facility_name="City Hospital Varanasi",
            city="Varanasi",
            state="Uttar Pradesh",
            latitude=25.323,
            longitude=82.986,
            phone_number="+91-542-YYY-YYYY",
            trust_score=0.85,
            plausibility_status="PLAUSIBLE",
            freshness_status="FRESH",
            risk_factors=(),
            specialties=("cardiology", "emergency medicine"),
            capabilities=("icu", "oxygen support", "ambulance"),
            verification_count=3,
        ),
        Facility(
            unique_id="regional-medical-center-varanasi",
            facility_name="Regional Medical Center",
            city="Varanasi",
            state="Uttar Pradesh",
            latitude=25.304,
            longitude=82.969,
            phone_number="+91-542-ZZZ-ZZZZ",
            trust_score=0.82,
            plausibility_status="PLAUSIBLE",
            freshness_status="AGING",
            risk_factors=("AGING",),
            specialties=("internal medicine", "critical care"),
            capabilities=("oxygen support", "emergency medicine"),
            verification_count=1,
        ),
    ]
