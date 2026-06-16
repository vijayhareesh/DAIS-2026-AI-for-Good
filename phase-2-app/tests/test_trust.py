import unittest

from phase_2_app.trust import recalculate_trust_score


class TrustScoreTest(unittest.TestCase):
    def test_unchecked_validation_lowers_trust_score(self):
        self.assertLess(
            recalculate_trust_score(
                old_score=0.50,
                claims_checked=6,
                claims_verified=0,
                verification_count=0,
            ),
            0.50,
        )

    def test_all_checked_validation_still_increases_trust_score(self):
        self.assertGreater(
            recalculate_trust_score(
                old_score=0.50,
                claims_checked=6,
                claims_verified=6,
                verification_count=0,
            ),
            0.50,
        )


if __name__ == "__main__":
    unittest.main()
