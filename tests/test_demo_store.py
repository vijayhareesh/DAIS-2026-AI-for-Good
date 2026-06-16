import unittest


from phase_2_app.demo_data import heritage_hospitals
from phase_2_app.store import DemoStore


class DemoStoreTest(unittest.TestCase):
    def test_demo_store_starts_heritage_below_patient_threshold(self):
        store = DemoStore.seeded()
        heritage = store.get_facility("heritage-hospitals-varanasi")

        self.assertEqual(heritage, heritage_hospitals())
        self.assertEqual(heritage.trust_score, 0.68)
        self.assertFalse(store.patient_visible("heritage-hospitals-varanasi"))

    def test_demo_store_validation_makes_patient_search_visibility_change(self):
        store = DemoStore.seeded()

        first = store.submit_validation(
            facility_id="heritage-hospitals-varanasi",
            volunteer_id="volunteer_001",
            claims_checked=15,
            claims_verified=13,
            details={"cardiology": True, "ICU": True, "neurology": False},
        )
        self.assertEqual(first.old_trust_score, 0.68)
        self.assertEqual(first.new_trust_score, 0.737)
        self.assertFalse(store.patient_visible("heritage-hospitals-varanasi"))

        second = store.submit_validation(
            facility_id="heritage-hospitals-varanasi",
            volunteer_id="volunteer_002",
            claims_checked=15,
            claims_verified=14,
            details={"cardiology": True, "ICU": True, "emergency": True},
        )

        self.assertEqual(second.new_trust_score, 0.808)
        self.assertTrue(store.patient_visible("heritage-hospitals-varanasi"))
