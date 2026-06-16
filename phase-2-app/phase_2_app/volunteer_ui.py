from __future__ import annotations


PRIORITY_STYLES = {
    "HIGH": ("#fee2e2", "#b91c1c", "#991b1b"),
    "MEDIUM": ("#fef3c7", "#b45309", "#92400e"),
    "LOW": ("#d1fae5", "#047857", "#065f46"),
}


def priority_label(trust_score: float) -> str:
    if trust_score < 0.70:
        return "HIGH"
    if trust_score < 0.80:
        return "MEDIUM"
    return "LOW"


def priority_badge_html(label: str) -> str:
    background, border, text = PRIORITY_STYLES[label]
    return (
        f"<span style='display:inline-block; min-width:4.8rem; text-align:center; "
        f"padding:0.28rem 0.45rem; border-radius:0.35rem; font-weight:700; "
        f"font-size:0.78rem; letter-spacing:0; color:{text}; background:{background}; "
        f"border:1px solid {border};'>{label}</span>"
    )


def verification_checkbox_key(facility_id: str, index: int) -> str:
    return f"q_{facility_id}_{index}"
