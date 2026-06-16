import unittest

from phase_2_app.agents import match_symptoms


class FakeClassifier:
    def classify(self, symptom_text: str):
        return {
            "urgency": "medium",
            "specialties": ["neurology", "emergencyMedicine"],
            "capabilities": ["ct scan"],
        }


class FailingClassifier:
    def classify(self, symptom_text: str):
        raise RuntimeError("endpoint unavailable")


class SymptomClassifierTest(unittest.TestCase):
    def test_match_symptoms_accepts_model_serving_classifier_result(self):
        result = match_symptoms("Severe headache with confusion", classifier=FakeClassifier())

        self.assertEqual(result["source"], "model_serving")
        self.assertEqual(result["urgency"], "medium")
        self.assertEqual(result["specialties"], ["neurology", "emergency medicine"])
        self.assertEqual(result["capabilities"], ["ct scan"])

    def test_match_symptoms_falls_back_to_rules_when_classifier_fails(self):
        result = match_symptoms("Heart pain, trouble breathing", classifier=FailingClassifier())

        self.assertEqual(result["source"], "rules")
        self.assertEqual(result["urgency"], "high")
        self.assertEqual(result["specialties"][:2], ["cardiology", "emergency medicine"])


if __name__ == "__main__":
    unittest.main()
