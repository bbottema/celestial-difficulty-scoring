import unittest

from assertpy import assert_that

from test_helpers import create_test_celestial_object
from app.domain.services.observability_calculation_service import ObservabilityCalculationService


class TestObservabilityCalculationService(unittest.TestCase):

    def setUp(self):
        self.service = ObservabilityCalculationService()

    def test_calculate_observability(self):
        celestial_object = create_test_celestial_object("Test", "Planet", 1.0, 1.0, 1.0)
        assert_that(self.service.score_celestial_object(celestial_object)).is_not_none()

    def test_relative_scoring_of_celestial_objects(self):
        """Test that brighter objects score higher than fainter ones."""
        moon = create_test_celestial_object('Moon', 'Moon', -12.60, 31.00, 39.00)
        jupiter = create_test_celestial_object('Jupiter', 'Planet', -2.40, 0.77, 43.00)
        messier1 = create_test_celestial_object("Messier 1", "DeepSky", 8.4, 6.0, 50.0)

        moon_score = self.service.score_celestial_object(moon).observability_score.normalized_score
        jupiter_score = self.service.score_celestial_object(jupiter).observability_score.normalized_score
        m1_score = self.service.score_celestial_object(messier1).observability_score.normalized_score

        # Verify brightest objects score higher (Moon > Jupiter > Messier 1)
        assert_that(moon_score).is_greater_than(jupiter_score)
        assert_that(jupiter_score).is_greater_than(m1_score)

        # Verify all scores are in valid range 0-25
        assert_that(moon_score).is_between(0.0, 25.0)
        assert_that(jupiter_score).is_between(0.0, 25.0)
        assert_that(m1_score).is_between(0.0, 25.0)

    def test_deep_sky_object_ranking(self):
        """Test that deep sky scoring considers both magnitude and size."""
        # Test with same size - brightness wins
        bright_small = create_test_celestial_object("Bright Small", "DeepSky", magnitude=-1.0, size=10.0, altitude=45.0)
        faint_small = create_test_celestial_object("Faint Small", "DeepSky", magnitude=10.0, size=10.0, altitude=45.0)

        # Test with same brightness - size matters
        medium_small = create_test_celestial_object("Medium Small", "DeepSky", magnitude=5.0, size=5.0, altitude=45.0)
        medium_large = create_test_celestial_object("Medium Large", "DeepSky", magnitude=5.0, size=30.0, altitude=45.0)

        bright_small_score = self.service.score_celestial_object(bright_small).observability_score.normalized_score
        faint_small_score = self.service.score_celestial_object(faint_small).observability_score.normalized_score
        medium_small_score = self.service.score_celestial_object(medium_small).observability_score.normalized_score
        medium_large_score = self.service.score_celestial_object(medium_large).observability_score.normalized_score

        # When size is equal, brighter object scores higher
        assert_that(bright_small_score).is_greater_than(faint_small_score)

        # When brightness is equal, larger object scores higher
        assert_that(medium_large_score).is_greater_than(medium_small_score)

        # All scores in valid range 0-25
        assert_that(bright_small_score).is_between(0.0, 25.0)
        assert_that(medium_large_score).is_between(0.0, 25.0)
