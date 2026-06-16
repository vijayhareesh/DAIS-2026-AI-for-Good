import unittest

from phase_2_app.agents import generate_verification_script
from phase_2_app.models import Facility


class VerificationScriptTest(unittest.TestCase):
    def test_script_includes_questions_for_facility_information_gaps(self):
        facility = Facility(
            unique_id="gap-hospital",
            facility_name="Gap Hospital",
            city="Nedumangadu",
            state="Trivandrum",
            latitude=8.6,
            longitude=77.0,
            phone_number="",
            trust_score=0.42,
            plausibility_status="UNKNOWN",
            freshness_status="UNKNOWN",
            risk_factors=(),
            specialties=(),
            capabilities=(),
        )

        prompts = [item["prompt"] for item in generate_verification_script(facility)]

        self.assertTrue(any("official phone" in prompt.lower() for prompt in prompts))
        self.assertTrue(any("specialties" in prompt.lower() for prompt in prompts))
        self.assertTrue(any("capabilities" in prompt.lower() for prompt in prompts))
        self.assertTrue(any("confidence score is low" in prompt.lower() for prompt in prompts))


if __name__ == "__main__":
    unittest.main()
