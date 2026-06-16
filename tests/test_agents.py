import unittest


from phase_2_app.agents import generate_verification_script, match_symptoms
from phase_2_app.demo_data import heritage_hospitals


class AgentsTest(unittest.TestCase):
    def test_symptom_matcher_maps_heart_pain_to_cardiology_and_emergency_care(self):
        result = match_symptoms("Heart pain, trouble breathing")

        self.assertEqual(result["urgency"], "high")
        self.assertEqual(
            result["specialties"][:3],
            ["cardiology", "emergency medicine", "critical care"],
        )
        self.assertIn("icu", result["capabilities"])
        self.assertIn("oxygen support", result["capabilities"])

    def test_script_generator_produces_heritage_progressive_demo_script(self):
        script = generate_verification_script(heritage_hospitals())

        self.assertEqual(len(script), 13)
        self.assertEqual(script[0]["section"], "basic")
        self.assertEqual(script[0]["prompt"], "Is this facility currently operational?")
        self.assertTrue(any("cardiology" in item["prompt"].lower() for item in script))
        self.assertTrue(any("ICU" in item["prompt"] for item in script))
        self.assertTrue(any(item["section"] == "staleness" for item in script))
