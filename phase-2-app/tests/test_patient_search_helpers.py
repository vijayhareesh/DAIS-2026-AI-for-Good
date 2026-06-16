import unittest

from phase_2_app.lakebase_store import _as_tuple
from phase_2_app.store import DemoStore


class PatientSearchHelpersTest(unittest.TestCase):
    def test_as_tuple_dedupes_list_values_preserving_order(self):
        self.assertEqual(
            _as_tuple(
                '["cardiology", "cardiology", "emergencyMedicine", '
                '"Emergency Medicine", ""]'
            ),
            ("cardiology", "emergencyMedicine"),
        )

    def test_demo_store_lists_unique_cities_for_dropdown(self):
        store = DemoStore.seeded()

        self.assertEqual(store.list_cities(), ["Varanasi"])


if __name__ == "__main__":
    unittest.main()
