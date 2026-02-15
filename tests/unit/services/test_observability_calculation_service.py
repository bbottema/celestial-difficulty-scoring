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
        sun = create_test_celestial_object('Sun', 'Sun', -26.74, 31.00, 39.00)
        moon = create_test_celestial_object('Moon', 'Moon', -12.60, 31.00, 39.00)
        jupiter = create_test_celestial_object('Jupiter', 'Planet', -2.40, 0.77, 43.00)
        messier1 = create_test_celestial_object("Messier 1", "DeepSky", 8.4, 6.0, 50.0)

        sun_score = self.service.score_celestial_object(sun).observability_score.normalized_score
        moon_score = self.service.score_celestial_object(moon).observability_score.normalized_score
        jupiter_score = self.service.score_celestial_object(jupiter).observability_score.normalized_score
        m1_score = self.service.score_celestial_object(messier1).observability_score.normalized_score

        # Verify brightest objects score higher
        assert_that(sun_score).is_greater_than(m1_score)
        assert_that(moon_score).is_greater_than(m1_score)
        assert_that(jupiter_score).is_greater_than(m1_score)

    def test_deep_sky_object_ranking(self):
        """Test that magnitude has stronger influence than size on deep sky scoring."""
        very_bright = create_test_celestial_object("Very Bright", "DeepSky", magnitude=-1.0, size=30.0, altitude=45.0)
        faint = create_test_celestial_object("Faint", "DeepSky", magnitude=10.0, size=30.0, altitude=45.0)
        medium_bright = create_test_celestial_object("Medium Bright", "DeepSky", magnitude=5.0, size=15.0, altitude=45.0)

        very_bright_score = self.service.score_celestial_object(very_bright).observability_score.normalized_score
        faint_score = self.service.score_celestial_object(faint).observability_score.normalized_score
        medium_score = self.service.score_celestial_object(medium_bright).observability_score.normalized_score

        # Brighter objects should score higher
        assert_that(very_bright_score).is_greater_than(medium_score)
        assert_that(medium_score).is_greater_than(faint_score)
