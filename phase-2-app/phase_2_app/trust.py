from __future__ import annotations


PATIENT_TRUST_THRESHOLD = 0.75


def recalculate_trust_score(
    old_score: float,
    claims_checked: int,
    claims_verified: int,
    verification_count: int,
) -> float:
    if claims_checked <= 0:
        return round(old_score, 3)

    verification_ratio = claims_verified / claims_checked
    evidence_delta = max(0.0, verification_ratio - 0.5) * 0.15545
    repeat_validator_bonus = min(verification_count, 3) * 0.004
    new_score = min(0.95, old_score + evidence_delta + repeat_validator_bonus)
    return round(new_score, 3)
