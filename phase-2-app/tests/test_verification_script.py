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

    def test_script_uses_facility_specific_context(self):
        facility = Facility(
            unique_id="metro-hospital",
            facility_name="Metro Heart Hospital",
            city="Lucknow",
            state="Uttar Pradesh",
            latitude=26.8,
            longitude=80.9,
            phone_number="+91 55555 00000",
            trust_score=0.42,
            plausibility_status="UNKNOWN",
            freshness_status="UNKNOWN",
            risk_factors=(),
            specialties=("cardiology", "pulmonology"),
            capabilities=("icu", "oxygen support"),
        )

        prompts = [item["prompt"] for item in generate_verification_script(facility)]
        prompt_text = "\n".join(prompts).lower()

        self.assertIn("metro heart hospital", prompt_text)
        self.assertIn("lucknow", prompt_text)
        self.assertIn("+91 55555 00000", prompt_text)
        self.assertIn("cardiology", prompt_text)
        self.assertIn("pulmonology", prompt_text)
        self.assertIn("icu", prompt_text)
        self.assertIn("oxygen support", prompt_text)
        self.assertIn("0.420", prompt_text)

    def test_scripts_for_different_facilities_are_not_interchangeable(self):
        first = Facility(
            unique_id="heart-hospital",
            facility_name="Heart Care Centre",
            city="Patna",
            state="Bihar",
            latitude=25.6,
            longitude=85.1,
            phone_number="111",
            trust_score=0.41,
            plausibility_status="UNKNOWN",
            freshness_status="UNKNOWN",
            risk_factors=(),
            specialties=("cardiology",),
            capabilities=("icu",),
        )
        second = Facility(
            unique_id="bone-hospital",
            facility_name="Bone Clinic",
            city="Jaipur",
            state="Rajasthan",
            latitude=26.9,
            longitude=75.8,
            phone_number="222",
            trust_score=0.39,
            plausibility_status="UNKNOWN",
            freshness_status="UNKNOWN",
            risk_factors=(),
            specialties=("orthopedics",),
            capabilities=("x-ray",),
        )

        first_prompts = "\n".join(item["prompt"] for item in generate_verification_script(first))
        second_prompts = "\n".join(item["prompt"] for item in generate_verification_script(second))

        self.assertNotEqual(first_prompts, second_prompts)
        self.assertIn("Heart Care Centre", first_prompts)
        self.assertIn("Bone Clinic", second_prompts)
        self.assertIn("cardiology", first_prompts.lower())
        self.assertIn("orthopedics", second_prompts.lower())

    def test_script_filters_listing_boilerplate_from_capability_questions(self):
        facility = Facility(
            unique_id="dental-center",
            facility_name="Smile Architect Orthodontic Center And Dental Clinic",
            city="Nashik",
            state="Maharashtra",
            latitude=20.0,
            longitude=73.7,
            phone_number="+919545455007",
            trust_score=0.388,
            plausibility_status="UNKNOWN",
            freshness_status="UNKNOWN",
            risk_factors=(),
            specialties=("orthodontics", "dentistry"),
            capabilities=(
                "Smile Architect Orthodontic Center & Dental Clinic Is Located In Govind Nagar, Nashik",
                "Smile Architect Orthodontic Center & Dental Clinic Is Listed Among Top Clinics In Nashik",
                "located in Nashik, Maharashtra, India",
                "outpatient dental clinic",
                "orthodontic center",
                "has 2 doctors on staff",
            ),
        )

        prompts = [item["prompt"] for item in generate_verification_script(facility)]
        capability_prompt = next(prompt for prompt in prompts if "listed capabilities" in prompt)

        self.assertIn("Outpatient Dental Clinic", capability_prompt)
        self.assertIn("Orthodontic Center", capability_prompt)
        self.assertNotIn("Is Located", capability_prompt)
        self.assertNotIn("Is Listed Among", capability_prompt)
        self.assertNotIn("Located In", capability_prompt)
        self.assertNotIn("Doctors On Staff", capability_prompt)


if __name__ == "__main__":
    unittest.main()
