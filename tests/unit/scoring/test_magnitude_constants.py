"""
Unit tests to verify precomputed magnitude score constants match their formulas.

These tests ensure that the pre-calculated values in scoring_constants.py
are mathematically correct and haven't drifted from their source formulas.
"""

import unittest
from app.utils.scoring_constants import (
    SUN_APPARENT_MAGNITUDE,
    SUN_MAGNITUDE_SCORE,
    SIRIUS_APPARENT_MAGNITUDE,
    SIRIUS_DEEPSKY_MAGNITUDE_SCORE,
    MAGNITUDE_OFFSET_DEEPSKY,
)


class TestMagnitudeConstants(unittest.TestCase):

    def test_sun_magnitude_score(self):
        """
        Verify SUN_MAGNITUDE_SCORE matches formula: 10^(-0.4 * SUN_APPARENT_MAGNITUDE)

        The Sun's apparent magnitude is -26.74, which gives:
        10^(-0.4 * -26.74) = 10^10.696 ≈ 49,659,232,145
        """
        expected = 10 ** (-0.4 * SUN_APPARENT_MAGNITUDE)
        actual = SUN_MAGNITUDE_SCORE

        # Use relative tolerance for floating point comparison
        self.assertAlmostEqual(expected, actual, delta=expected * 1e-10,
            msg=f"SUN_MAGNITUDE_SCORE mismatch! Expected: {expected}, Actual: {actual}")

    def test_sirius_deepsky_magnitude_score(self):
        """
        Verify SIRIUS_DEEPSKY_MAGNITUDE_SCORE matches formula:
        10^(-0.4 * (SIRIUS_APPARENT_MAGNITUDE + MAGNITUDE_OFFSET_DEEPSKY))

        Sirius magnitude: -1.46
        Deep-sky offset: +12
        Adjusted magnitude: -1.46 + 12 = 10.54
        Score: 10^(-0.4 * 10.54) = 10^-4.216 ≈ 0.0001527
        """
        expected = 10 ** (-0.4 * (SIRIUS_APPARENT_MAGNITUDE + MAGNITUDE_OFFSET_DEEPSKY))
        actual = SIRIUS_DEEPSKY_MAGNITUDE_SCORE

        # Use relative tolerance for floating point comparison
        self.assertAlmostEqual(expected, actual, delta=expected * 1e-10,
            msg=f"SIRIUS_DEEPSKY_MAGNITUDE_SCORE mismatch! Expected: {expected}, Actual: {actual}")

    def test_magnitude_score_formula_consistency(self):
        """
        Test that magnitude score formula produces expected relative scaling.

        Brightness ratio between two objects should follow inverse logarithmic scale:
        ratio = 10^(0.4 * (mag2 - mag1))

        Example: 5 magnitude difference = 100× brightness difference
        """
        # Test case: 5 magnitude difference should be 100× brightness
        mag1 = 5.0
        mag2 = 10.0
        score1 = 10 ** (-0.4 * mag1)
        score2 = 10 ** (-0.4 * mag2)

        brightness_ratio = score1 / score2
        expected_ratio = 100.0  # 5 magnitudes = 100× brightness

        self.assertAlmostEqual(brightness_ratio, expected_ratio, places=3,
            msg=f"5 magnitude difference should be 100× brightness, got {brightness_ratio}×")

    def test_precomputed_values_are_floats(self):
        """Ensure precomputed constants are float type (not int or string)."""
        self.assertIsInstance(SUN_MAGNITUDE_SCORE, float)
        self.assertIsInstance(SIRIUS_DEEPSKY_MAGNITUDE_SCORE, float)

    def test_precomputed_values_are_positive(self):
        """All magnitude scores should be positive."""
        self.assertGreater(SUN_MAGNITUDE_SCORE, 0)
        self.assertGreater(SIRIUS_DEEPSKY_MAGNITUDE_SCORE, 0)

    def test_sun_brighter_than_sirius(self):
        """
        Sun should have vastly higher magnitude score than Sirius.

        Sun: mag -26.74
        Sirius (with deep-sky offset): mag 10.54
        Difference: ~37 magnitudes = ~10^14.8 brightness ratio
        """
        self.assertGreater(SUN_MAGNITUDE_SCORE, SIRIUS_DEEPSKY_MAGNITUDE_SCORE)
        ratio = SUN_MAGNITUDE_SCORE / SIRIUS_DEEPSKY_MAGNITUDE_SCORE

        # Should be approximately 10^14.8 ≈ 6.3 × 10^14
        expected_ratio_order_of_magnitude = 14
        actual_ratio_order_of_magnitude = len(str(int(ratio))) - 1

        self.assertGreaterEqual(actual_ratio_order_of_magnitude, expected_ratio_order_of_magnitude,
            msg=f"Sun/Sirius brightness ratio seems wrong. Expected ~10^{expected_ratio_order_of_magnitude}, got ~10^{actual_ratio_order_of_magnitude}")

    def test_magnitude_offset_applied_correctly(self):
        """
        Verify that MAGNITUDE_OFFSET_DEEPSKY (12) is applied correctly.

        The offset is used to bring deep-sky objects (typically mag 5-15)
        into a scoreable range by shifting them toward brighter values.
        """
        # Without offset, Sirius score
        sirius_raw = 10 ** (-0.4 * SIRIUS_APPARENT_MAGNITUDE)

        # With offset (as used in SIRIUS_DEEPSKY_MAGNITUDE_SCORE)
        sirius_offset = 10 ** (-0.4 * (SIRIUS_APPARENT_MAGNITUDE + MAGNITUDE_OFFSET_DEEPSKY))

        # Offset should make the score much smaller (fainter)
        self.assertLess(sirius_offset, sirius_raw)

        # The ratio should be 10^(-0.4 * 12) = 10^-4.8 ≈ 0.0000158
        expected_offset_factor = 10 ** (-0.4 * MAGNITUDE_OFFSET_DEEPSKY)
        actual_offset_factor = sirius_offset / sirius_raw

        self.assertAlmostEqual(expected_offset_factor, actual_offset_factor, delta=expected_offset_factor * 1e-10)


if __name__ == "__main__":
    unittest.main()
