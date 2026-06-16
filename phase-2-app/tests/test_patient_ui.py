import unittest

from phase_2_app.patient_ui import result_heading


class PatientUiTest(unittest.TestCase):
    def test_result_heading_names_visible_subset(self):
        self.assertEqual(result_heading(total_count=100, visible_count=10), "Top 10 of 100 Matches")

    def test_result_heading_uses_total_when_all_visible(self):
        self.assertEqual(result_heading(total_count=7, visible_count=10), "Top Matches (7)")


if __name__ == "__main__":
    unittest.main()
