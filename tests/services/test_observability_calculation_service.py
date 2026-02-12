import unittest

from assertpy import assert_that

from tests.test_helpers import create_test_celestial_object
from app.domain.services.observability_calculation_service import ObservabilityCalculationService


class TestObservabilityCalculationService(unittest.TestCase):

    def setUp(self):
        self.service = ObservabilityCalculationService()

    def test_calculate_observability(self):
        celestial_object = create_test_celestial_object("Test", "Planet", 1.0, 1.0, 1.0)
        assert_that(self.service.calculate_observability_score(celestial_object)).is_not_none()

    def test_relative_scoring_of_celestial_objects(self):
        objects = [
            create_test_celestial_object('Sun', 'Sun', -26.74, 31.00, 39.00),  # Example values
            create_test_celestial_object('Moon', 'Moon', -12.60, 31.00, 39.00),
            create_test_celestial_object('Jupiter', 'Planet', -2.40, 0.77, 43.00),
            create_test_celestial_object("Messier 1", "DeepSky", 8.4, 6.0, 50.0)
        ]

        scored_objects = [(obj.name, self.service.calculate_observability_score(obj).normalized_score) for obj in objects]
        # Sort by score in descending order
        scored_objects.sort(key=lambda x: x[1], reverse=True)

        # Now verify the order - expecting Sun > Moon > Jupiter > Messier 1
        expected_order = ["Sun", "Moon", "Jupiter", "Messier 1"]
        actual_order = [name for name, _ in scored_objects]

        assert_that(actual_order).is_equal_to(expected_order)

    def test_deep_sky_object_ranking(self):
        objects = [
            create_test_celestial_object("Very Large Bright", "DeepSky", magnitude=-1.0, size=30.0, altitude=45.0),
            create_test_celestial_object("Very Large Faint", "DeepSky", magnitude=10.0, size=30.0, altitude=45.0),
            create_test_celestial_object("Smaller Bright", "DeepSky", magnitude=-1.0, size=5.0, altitude=45.0),
            create_test_celestial_object("Small Faint", "DeepSky", magnitude=10.0, size=5.0, altitude=45.0),
            create_test_celestial_object("Medium Size Medium Bright", "DeepSky", magnitude=5.0, size=15.0, altitude=45.0),
        ]

        # Calculate scores
        scored_objects = [(obj.name, self.service.calculate_observability_score(obj).normalized_score) for obj in objects]
        # Sort by score in descending order (higher score = higher rank)
        scored_objects.sort(key=lambda x: x[1], reverse=True)

        expected_order = [
            "Very Large Bright",
            "Medium Size Medium Bright",
            "Smaller Bright",
            "Very Large Faint",
            "Small Faint"
        ]

        actual_order = [name for name, _ in scored_objects]

        # Assert that the actual ranking matches the expected ranking
        assert_that(actual_order).is_equal_to(expected_order)
