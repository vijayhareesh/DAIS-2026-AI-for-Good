import unittest

from phase_2_app.models import Facility
from phase_2_app.ranking import rank_patient_facilities
from phase_2_app.store import DemoStore


def facility(
    facility_id: str,
    name: str,
    trust_score: float,
    specialties: tuple[str, ...],
    capabilities: tuple[str, ...] = (),
) -> Facility:
    return Facility(
        unique_id=facility_id,
        facility_name=name,
        city="Chennai",
        state="Tamil Nadu",
        latitude=13.08,
        longitude=80.27,
        phone_number="",
        trust_score=trust_score,
        plausibility_status="PLAUSIBLE",
        freshness_status="FRESH",
        risk_factors=(),
        specialties=specialties,
        capabilities=capabilities,
    )


class RankingTest(unittest.TestCase):
    def test_demo_volunteer_queue_orders_lower_trust_first(self):
        rows = DemoStore.seeded().volunteer_queue(limit=3)

        self.assertEqual(rows[0].unique_id, "heritage-hospitals-varanasi")
        self.assertLess(rows[0].trust_score, rows[1].trust_score)

    def test_patient_ranking_prefers_specialty_match_over_raw_trust(self):
        rows = [
            facility("generic", "Very Trusted General Clinic", 0.99, ("dermatology",)),
            facility(
                "cardiac",
                "Cardiac Care Hospital",
                0.82,
                ("cardiology",),
                ("icu", "oxygen support"),
            ),
        ]
        match = {
            "urgency": "high",
            "specialties": ["cardiology"],
            "capabilities": ["icu"],
        }

        ranked = rank_patient_facilities(rows, match)

        self.assertEqual(ranked[0].unique_id, "cardiac")
        self.assertGreater(ranked[0].match_score, ranked[1].match_score)
        self.assertEqual(ranked[0].matched_specialties, ("cardiology",))

    def test_patient_ranking_matches_related_capability_terms(self):
        rows = [
            facility(
                "emergency",
                "Emergency Care Hospital",
                0.82,
                ("general medicine",),
                ("emergencyMedicine",),
            ),
        ]
        match = {
            "urgency": "high",
            "specialties": ["general medicine"],
            "capabilities": ["emergency"],
        }

        ranked = rank_patient_facilities(rows, match)

        self.assertEqual(ranked[0].matched_capabilities, ("emergencyMedicine",))


if __name__ == "__main__":
    unittest.main()
