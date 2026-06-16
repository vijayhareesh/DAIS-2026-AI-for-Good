import unittest
from pathlib import Path

from phase_2_app.home_content import project_summary


class HomeContentTest(unittest.TestCase):
    def test_project_summary_uses_project_description(self):
        summary = project_summary(Path(__file__).resolve().parents[2] / "PROJECT_DESCRIPTION.md")

        self.assertEqual(summary["title"], "HealthVerify India")
        self.assertIn("AI to cut through the noise", summary["what_it_does"])
        self.assertIn("Lakebase", summary["how_we_built_it"])

    def test_project_summary_does_not_include_facility_details(self):
        summary = project_summary(Path(__file__).resolve().parents[2] / "PROJECT_DESCRIPTION.md")
        text = "\n".join(summary.values())

        self.assertNotIn("Top Facility", text)
        self.assertNotIn("Trust Score", text)
        self.assertNotIn("Total Loaded", text)


if __name__ == "__main__":
    unittest.main()
