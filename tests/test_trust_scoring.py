import unittest


from phase_2_app.trust import recalculate_trust_score


class TrustScoringTest(unittest.TestCase):
    def test_first_heritage_validation_moves_score_to_demo_checkpoint(self):
        new_score = recalculate_trust_score(
            old_score=0.68,
            claims_checked=15,
            claims_verified=13,
            verification_count=0,
        )

        self.assertEqual(new_score, 0.737)

    def test_second_heritage_validation_pushes_score_above_patient_threshold(self):
        first_score = recalculate_trust_score(
            old_score=0.68,
            claims_checked=15,
            claims_verified=13,
            verification_count=0,
        )
        second_score = recalculate_trust_score(
            old_score=first_score,
            claims_checked=15,
            claims_verified=14,
            verification_count=1,
        )

        self.assertGreaterEqual(second_score, 0.80)
        self.assertEqual(second_score, 0.808)
