import unittest

from phase_2_app.volunteer_ui import priority_badge_html, verification_checkbox_key


class VolunteerUiTest(unittest.TestCase):
    def test_priority_badges_have_distinct_colors(self):
        high = priority_badge_html("HIGH")
        medium = priority_badge_html("MEDIUM")
        low = priority_badge_html("LOW")

        self.assertIn("#b91c1c", high)
        self.assertIn("#b45309", medium)
        self.assertIn("#047857", low)
        self.assertNotEqual(high, medium)
        self.assertNotEqual(medium, low)

    def test_verification_checkbox_key_is_facility_scoped(self):
        self.assertEqual(verification_checkbox_key("facility-a", 3), "q_facility-a_3")


if __name__ == "__main__":
    unittest.main()
