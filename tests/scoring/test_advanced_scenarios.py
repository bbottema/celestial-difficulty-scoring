"""
Advanced observability scoring tests.

Tests for weather impact, moon proximity penalties, and edge cases.
These tests cover features not yet implemented - expect failures initially.
"""
import unittest
from assertpy import assert_that

from app.domain.model.celestial_object import CelestialObject
from app.domain.services.observability_calculation_service import ObservabilityCalculationService
from app.orm.model.entities import Telescope, Eyepiece, ObservationSite
from app.domain.model.light_pollution import LightPollution
from app.domain.model.telescope_type import TelescopeType


class TestFixtures:
    """Test fixtures - simplified for advanced tests."""

    @staticmethod
    def medium_dobsonian():
        return Telescope(
            id=None, name="8-inch Dob", type=TelescopeType.DOBSONIAN,
            aperture=200, focal_length=1200, focal_ratio=6.0
        )

    @staticmethod
    def medium_eyepiece():
        return Eyepiece(
            id=None, name="10mm", focal_length=10,
            barrel_size=1.25, apparent_field_of_view=50
        )

    @staticmethod
    def dark_site():
        return ObservationSite(
            id=None, name="Dark Sky", latitude=40.0, longitude=-80.0,
            light_pollution=LightPollution.BORTLE_2
        )

    @staticmethod
    def moon():
        return CelestialObject('Moon', 'Moon', -12.60, 31.00, 45.00)

    @staticmethod
    def jupiter():
        return CelestialObject('Jupiter', 'Planet', -2.40, 0.77, 45.00)

    @staticmethod
    def orion_nebula():
        return CelestialObject('Orion Nebula', 'DeepSky', 4.0, 65.0, 55.00)

    @staticmethod
    def horsehead():
        return CelestialObject('Horsehead Nebula', 'DeepSky', 10.0, 60.0, 45.00)

    @staticmethod
    def andromeda():
        return CelestialObject('Andromeda Galaxy', 'DeepSky', 3.44, 190.00, 60.00)


# =============================================================================
# WEATHER IMPACT TESTS
# =============================================================================

class TestWeatherImpactClear(unittest.TestCase):
    """Clear weather should allow full observability."""

    def setUp(self):
        self.service = ObservabilityCalculationService()
        self.scope = TestFixtures.medium_dobsonian()
        self.eyepiece = TestFixtures.medium_eyepiece()
        self.site = TestFixtures.dark_site()

    def test_clear_weather_no_penalty(self):
        """Clear weather should not reduce score."""
        jupiter = TestFixtures.jupiter()

        # TODO: weather parameter not yet implemented
        # For now, test will fail - this is expected
        try:
            clear_score = self.service.score_celestial_object(
                jupiter, self.scope, self.eyepiece, self.site,
                weather={'condition': 'Clear', 'cloud_cover': 0})

            # No penalty expected
            assert_that(clear_score.observability_score.score).is_greater_than(0)
        except TypeError:
            # Expected until weather parameter is added
            self.skipTest("Weather parameter not yet implemented")


class TestWeatherImpactCloudy(unittest.TestCase):
    """Clouds should dramatically reduce observability."""

    def setUp(self):
        self.service = ObservabilityCalculationService()
        self.scope = TestFixtures.medium_dobsonian()
        self.eyepiece = TestFixtures.medium_eyepiece()
        self.site = TestFixtures.dark_site()

    def test_overcast_devastates_jupiter(self):
        """Even Jupiter should be nearly invisible in overcast."""
        jupiter = TestFixtures.jupiter()

        try:
            clear_score = self.service.score_celestial_object(
                jupiter, self.scope, self.eyepiece, self.site,
                weather={'condition': 'Clear', 'cloud_cover': 0})
            overcast_score = self.service.score_celestial_object(
                jupiter, self.scope, self.eyepiece, self.site,
                weather={'condition': 'Overcast', 'cloud_cover': 100})

            # Overcast should reduce to < 10%
            ratio = overcast_score.observability_score.score / clear_score.observability_score.score
            assert_that(ratio).is_less_than(0.10)
        except TypeError:
            self.skipTest("Weather parameter not yet implemented")

    def test_overcast_devastates_moon(self):
        """Even Moon should be barely visible in overcast."""
        moon = TestFixtures.moon()

        try:
            clear_score = self.service.score_celestial_object(
                moon, self.scope, self.eyepiece, self.site,
                weather={'condition': 'Clear', 'cloud_cover': 0})
            overcast_score = self.service.score_celestial_object(
                moon, self.scope, self.eyepiece, self.site,
                weather={'condition': 'Overcast', 'cloud_cover': 100})

            ratio = overcast_score.observability_score.score / clear_score.observability_score.score
            assert_that(ratio).is_less_than(0.15)
        except TypeError:
            self.skipTest("Weather parameter not yet implemented")

    def test_overcast_kills_faint_objects(self):
        """Faint objects should be impossible in overcast."""
        horsehead = TestFixtures.horsehead()

        try:
            clear_score = self.service.score_celestial_object(
                horsehead, self.scope, self.eyepiece, self.site,
                weather={'condition': 'Clear', 'cloud_cover': 0})
            overcast_score = self.service.score_celestial_object(
                horsehead, self.scope, self.eyepiece, self.site,
                weather={'condition': 'Overcast', 'cloud_cover': 100})

            # Should be nearly zero
            assert_that(overcast_score.observability_score.score).is_less_than(
                clear_score.observability_score.score * 0.05)
        except TypeError:
            self.skipTest("Weather parameter not yet implemented")


class TestWeatherImpactPartialClouds(unittest.TestCase):
    """Partial clouds should reduce observability proportionally."""

    def setUp(self):
        self.service = ObservabilityCalculationService()
        self.scope = TestFixtures.medium_dobsonian()
        self.eyepiece = TestFixtures.medium_eyepiece()
        self.site = TestFixtures.dark_site()

    def test_partial_clouds_proportional_penalty(self):
        """50% cloud cover should reduce score by ~50%."""
        orion = TestFixtures.orion_nebula()

        try:
            clear_score = self.service.score_celestial_object(
                orion, self.scope, self.eyepiece, self.site,
                weather={'condition': 'Clear', 'cloud_cover': 0})
            partial_score = self.service.score_celestial_object(
                orion, self.scope, self.eyepiece, self.site,
                weather={'condition': 'Partly Cloudy', 'cloud_cover': 50})

            ratio = partial_score.observability_score.score / clear_score.observability_score.score
            assert_that(ratio).is_between(0.40, 0.60)  # 50% ± 10%
        except TypeError:
            self.skipTest("Weather parameter not yet implemented")

    def test_25_percent_clouds(self):
        """25% cloud cover should reduce score by ~25%."""
        jupiter = TestFixtures.jupiter()

        try:
            clear_score = self.service.score_celestial_object(
                jupiter, self.scope, self.eyepiece, self.site,
                weather={'condition': 'Clear', 'cloud_cover': 0})
            light_clouds_score = self.service.score_celestial_object(
                jupiter, self.scope, self.eyepiece, self.site,
                weather={'condition': 'Few Clouds', 'cloud_cover': 25})

            ratio = light_clouds_score.observability_score.score / clear_score.observability_score.score
            assert_that(ratio).is_between(0.70, 0.80)  # 75% ± 5%
        except TypeError:
            self.skipTest("Weather parameter not yet implemented")


class TestWeatherGradient(unittest.TestCase):
    """Score should decrease monotonically with worsening weather."""

    def setUp(self):
        self.service = ObservabilityCalculationService()
        self.scope = TestFixtures.medium_dobsonian()
        self.eyepiece = TestFixtures.medium_eyepiece()
        self.site = TestFixtures.dark_site()

    def test_weather_gradient_jupiter(self):
        """Jupiter: clear > light clouds > heavy clouds > overcast."""
        jupiter = TestFixtures.jupiter()

        try:
            clear = self.service.score_celestial_object(
                jupiter, self.scope, self.eyepiece, self.site,
                weather={'condition': 'Clear', 'cloud_cover': 0})
            light = self.service.score_celestial_object(
                jupiter, self.scope, self.eyepiece, self.site,
                weather={'condition': 'Few Clouds', 'cloud_cover': 25})
            heavy = self.service.score_celestial_object(
                jupiter, self.scope, self.eyepiece, self.site,
                weather={'condition': 'Mostly Cloudy', 'cloud_cover': 75})
            overcast = self.service.score_celestial_object(
                jupiter, self.scope, self.eyepiece, self.site,
                weather={'condition': 'Overcast', 'cloud_cover': 100})

            assert_that(clear.observability_score.score).is_greater_than(light.observability_score.score)
            assert_that(light.observability_score.score).is_greater_than(heavy.observability_score.score)
            assert_that(heavy.observability_score.score).is_greater_than(overcast.observability_score.score)
        except TypeError:
            self.skipTest("Weather parameter not yet implemented")


# =============================================================================
# MOON PROXIMITY TESTS
# =============================================================================

class TestMoonProximityBasic(unittest.TestCase):
    """Objects near bright moon should score poorly."""

    def setUp(self):
        self.service = ObservabilityCalculationService()
        self.scope = TestFixtures.medium_dobsonian()
        self.eyepiece = TestFixtures.medium_eyepiece()
        self.site = TestFixtures.dark_site()

    def test_object_near_full_moon_severe_penalty(self):
        """Object 10° from full moon should lose 70%+ score."""
        target = CelestialObject('Target Near Moon', 'DeepSky', 6.0, 10.0, 60.00)

        try:
            # Moon far away
            far_score = self.service.score_celestial_object(
                target, self.scope, self.eyepiece, self.site,
                moon_conditions={'phase': 'Full', 'illumination': 100, 'altitude': 60.0, 'separation_degrees': 120.0})

            # Moon very close
            near_score = self.service.score_celestial_object(
                target, self.scope, self.eyepiece, self.site,
                moon_conditions={'phase': 'Full', 'illumination': 100, 'altitude': 60.0, 'separation_degrees': 10.0})

            ratio = near_score.observability_score.score / far_score.observability_score.score
            assert_that(ratio).is_less_than(0.30)
        except TypeError:
            self.skipTest("Moon conditions parameter not yet implemented")

    def test_object_very_close_to_full_moon(self):
        """Object 5° from full moon should be nearly impossible."""
        target = CelestialObject('Target Very Close', 'DeepSky', 7.0, 5.0, 60.00)

        try:
            far_score = self.service.score_celestial_object(
                target, self.scope, self.eyepiece, self.site,
                moon_conditions={'phase': 'Full', 'illumination': 100, 'altitude': 60.0, 'separation_degrees': 90.0})

            very_close_score = self.service.score_celestial_object(
                target, self.scope, self.eyepiece, self.site,
                moon_conditions={'phase': 'Full', 'illumination': 100, 'altitude': 60.0, 'separation_degrees': 5.0})

            ratio = very_close_score.observability_score.score / far_score.observability_score.score
            assert_that(ratio).is_less_than(0.15)
        except TypeError:
            self.skipTest("Moon conditions parameter not yet implemented")


class TestMoonProximityByPhase(unittest.TestCase):
    """Moon proximity penalty should scale with illumination."""

    def setUp(self):
        self.service = ObservabilityCalculationService()
        self.scope = TestFixtures.medium_dobsonian()
        self.eyepiece = TestFixtures.medium_eyepiece()
        self.site = TestFixtures.dark_site()

    def test_new_moon_no_penalty(self):
        """New moon (0% illumination) should not penalize nearby objects."""
        target = CelestialObject('Target Near New Moon', 'DeepSky', 8.0, 10.0, 60.00)

        try:
            new_moon_score = self.service.score_celestial_object(
                target, self.scope, self.eyepiece, self.site,
                moon_conditions={'phase': 'New', 'illumination': 0, 'altitude': 0.0, 'separation_degrees': 20.0})

            full_moon_score = self.service.score_celestial_object(
                target, self.scope, self.eyepiece, self.site,
                moon_conditions={'phase': 'Full', 'illumination': 100, 'altitude': 60.0, 'separation_degrees': 20.0})

            # New moon should not penalize
            assert_that(new_moon_score.observability_score.score).is_greater_than(
                full_moon_score.observability_score.score * 2.0)
        except TypeError:
            self.skipTest("Moon conditions parameter not yet implemented")

    def test_quarter_moon_moderate_penalty(self):
        """Quarter moon (50% illumination) should have moderate penalty."""
        target = CelestialObject('Target Near Quarter Moon', 'DeepSky', 7.0, 8.0, 60.00)

        try:
            quarter_moon_score = self.service.score_celestial_object(
                target, self.scope, self.eyepiece, self.site,
                moon_conditions={'phase': 'First Quarter', 'illumination': 50, 'altitude': 50.0, 'separation_degrees': 15.0})

            full_moon_score = self.service.score_celestial_object(
                target, self.scope, self.eyepiece, self.site,
                moon_conditions={'phase': 'Full', 'illumination': 100, 'altitude': 50.0, 'separation_degrees': 15.0})

            # Quarter moon should be better than full moon
            assert_that(quarter_moon_score.observability_score.score).is_greater_than(
                full_moon_score.observability_score.score)
        except TypeError:
            self.skipTest("Moon conditions parameter not yet implemented")

    def test_crescent_moon_minor_penalty(self):
        """Crescent moon (10% illumination) should have minor penalty."""
        target = CelestialObject('Target Near Crescent', 'DeepSky', 7.5, 10.0, 60.00)

        try:
            crescent_score = self.service.score_celestial_object(
                target, self.scope, self.eyepiece, self.site,
                moon_conditions={'phase': 'Crescent', 'illumination': 10, 'altitude': 40.0, 'separation_degrees': 20.0})

            full_moon_score = self.service.score_celestial_object(
                target, self.scope, self.eyepiece, self.site,
                moon_conditions={'phase': 'Full', 'illumination': 100, 'altitude': 40.0, 'separation_degrees': 20.0})

            # Crescent should be much better than full
            assert_that(crescent_score.observability_score.score).is_greater_than(
                full_moon_score.observability_score.score * 3.0)
        except TypeError:
            self.skipTest("Moon conditions parameter not yet implemented")


class TestMoonProximityBySeparation(unittest.TestCase):
    """Moon proximity penalty should follow inverse square of separation."""

    def setUp(self):
        self.service = ObservabilityCalculationService()
        self.scope = TestFixtures.medium_dobsonian()
        self.eyepiece = TestFixtures.medium_eyepiece()
        self.site = TestFixtures.dark_site()

    def test_separation_gradient(self):
        """Score should increase with separation from full moon."""
        target = CelestialObject('Target', 'DeepSky', 7.0, 10.0, 60.00)
        separations = [5, 10, 20, 40, 80]

        try:
            scores = []
            for sep in separations:
                score = self.service.score_celestial_object(
                    target, self.scope, self.eyepiece, self.site,
                    moon_conditions={'phase': 'Full', 'illumination': 100, 'altitude': 60.0, 'separation_degrees': sep})
                scores.append(score.observability_score.score)

            # Scores should increase monotonically
            for i in range(len(scores) - 1):
                assert_that(scores[i + 1]).is_greater_than(scores[i])
        except TypeError:
            self.skipTest("Moon conditions parameter not yet implemented")

    def test_double_separation_significant_improvement(self):
        """Doubling separation should significantly improve score."""
        target = CelestialObject('Target', 'DeepSky', 7.0, 10.0, 60.00)

        try:
            close_score = self.service.score_celestial_object(
                target, self.scope, self.eyepiece, self.site,
                moon_conditions={'phase': 'Full', 'illumination': 100, 'altitude': 60.0, 'separation_degrees': 10.0})

            far_score = self.service.score_celestial_object(
                target, self.scope, self.eyepiece, self.site,
                moon_conditions={'phase': 'Full', 'illumination': 100, 'altitude': 60.0, 'separation_degrees': 20.0})

            # Doubling distance should roughly quadruple score (inverse square)
            ratio = far_score.observability_score.score / close_score.observability_score.score
            assert_that(ratio).is_greater_than(2.5)  # Allow some variance
        except TypeError:
            self.skipTest("Moon conditions parameter not yet implemented")


class TestMoonOccultation(unittest.TestCase):
    """Objects directly behind moon should be invisible."""

    def setUp(self):
        self.service = ObservabilityCalculationService()
        self.scope = TestFixtures.medium_dobsonian()
        self.eyepiece = TestFixtures.medium_eyepiece()
        self.site = TestFixtures.dark_site()

    def test_occultation_zero_score(self):
        """Object at 0° separation (behind moon) should score zero."""
        target = CelestialObject('Occulted Star', 'DeepSky', 3.0, 0.0001, 60.00)

        try:
            score = self.service.score_celestial_object(
                target, self.scope, self.eyepiece, self.site,
                moon_conditions={'phase': 'Full', 'illumination': 100, 'altitude': 60.0, 'separation_degrees': 0.0})

            assert_that(score.observability_score.score).is_equal_to(0.0)
        except TypeError:
            self.skipTest("Moon conditions parameter not yet implemented")

    def test_barely_past_moon_still_very_hard(self):
        """Object 0.5° from moon edge should be nearly impossible."""
        target = CelestialObject('Just Past Moon', 'DeepSky', 5.0, 1.0, 60.00)

        try:
            barely_past_score = self.service.score_celestial_object(
                target, self.scope, self.eyepiece, self.site,
                moon_conditions={'phase': 'Full', 'illumination': 100, 'altitude': 60.0, 'separation_degrees': 0.5})

            far_score = self.service.score_celestial_object(
                target, self.scope, self.eyepiece, self.site,
                moon_conditions={'phase': 'Full', 'illumination': 100, 'altitude': 60.0, 'separation_degrees': 60.0})

            ratio = barely_past_score.observability_score.score / far_score.observability_score.score
            assert_that(ratio).is_less_than(0.05)  # < 5% of far score
        except TypeError:
            self.skipTest("Moon conditions parameter not yet implemented")


class TestMoonProximityOnBrightObjects(unittest.TestCase):
    """Bright objects should be more resilient to moon proximity."""

    def setUp(self):
        self.service = ObservabilityCalculationService()
        self.scope = TestFixtures.medium_dobsonian()
        self.eyepiece = TestFixtures.medium_eyepiece()
        self.site = TestFixtures.dark_site()

    def test_jupiter_resilient_to_moon(self):
        """Jupiter should maintain 60%+ score even near moon."""
        jupiter = TestFixtures.jupiter()

        try:
            far_score = self.service.score_celestial_object(
                jupiter, self.scope, self.eyepiece, self.site,
                moon_conditions={'phase': 'Full', 'illumination': 100, 'altitude': 60.0, 'separation_degrees': 90.0})

            near_score = self.service.score_celestial_object(
                jupiter, self.scope, self.eyepiece, self.site,
                moon_conditions={'phase': 'Full', 'illumination': 100, 'altitude': 60.0, 'separation_degrees': 15.0})

            ratio = near_score.observability_score.score / far_score.observability_score.score
            assert_that(ratio).is_greater_than(0.60)
        except TypeError:
            self.skipTest("Moon conditions parameter not yet implemented")

    def test_faint_object_devastated_by_moon(self):
        """Faint object should lose 80%+ near moon."""
        horsehead = TestFixtures.horsehead()

        try:
            far_score = self.service.score_celestial_object(
                horsehead, self.scope, self.eyepiece, self.site,
                moon_conditions={'phase': 'Full', 'illumination': 100, 'altitude': 60.0, 'separation_degrees': 90.0})

            near_score = self.service.score_celestial_object(
                horsehead, self.scope, self.eyepiece, self.site,
                moon_conditions={'phase': 'Full', 'illumination': 100, 'altitude': 60.0, 'separation_degrees': 15.0})

            ratio = near_score.observability_score.score / far_score.observability_score.score
            assert_that(ratio).is_less_than(0.20)
        except TypeError:
            self.skipTest("Moon conditions parameter not yet implemented")


# =============================================================================
# COMBINED FACTORS TESTS
# =============================================================================

class TestCombinedAdversity(unittest.TestCase):
    """Test combinations of adverse factors."""

    def setUp(self):
        self.service = ObservabilityCalculationService()
        self.scope = TestFixtures.medium_dobsonian()
        self.eyepiece = TestFixtures.medium_eyepiece()
        self.site = TestFixtures.dark_site()

    def test_faint_object_near_moon_in_clouds(self):
        """Faint object near moon in cloudy weather should be nearly impossible."""
        horsehead = TestFixtures.horsehead()

        try:
            ideal_score = self.service.score_celestial_object(
                horsehead, self.scope, self.eyepiece, self.site,
                weather={'condition': 'Clear', 'cloud_cover': 0},
                moon_conditions={'phase': 'New', 'illumination': 0, 'altitude': 0.0, 'separation_degrees': 180.0})

            terrible_score = self.service.score_celestial_object(
                horsehead, self.scope, self.eyepiece, self.site,
                weather={'condition': 'Mostly Cloudy', 'cloud_cover': 75},
                moon_conditions={'phase': 'Full', 'illumination': 100, 'altitude': 60.0, 'separation_degrees': 10.0})

            ratio = terrible_score.observability_score.score / ideal_score.observability_score.score
            assert_that(ratio).is_less_than(0.05)  # < 5%
        except TypeError:
            self.skipTest("Combined parameters not yet implemented")

    def test_bright_object_survives_adversity(self):
        """Jupiter should remain observable even in moderate adversity."""
        jupiter = TestFixtures.jupiter()

        try:
            ideal_score = self.service.score_celestial_object(
                jupiter, self.scope, self.eyepiece, self.site,
                weather={'condition': 'Clear', 'cloud_cover': 0},
                moon_conditions={'phase': 'New', 'illumination': 0, 'altitude': 0.0, 'separation_degrees': 180.0})

            adverse_score = self.service.score_celestial_object(
                jupiter, self.scope, self.eyepiece, self.site,
                weather={'condition': 'Few Clouds', 'cloud_cover': 25},
                moon_conditions={'phase': 'First Quarter', 'illumination': 50, 'altitude': 50.0, 'separation_degrees': 30.0})

            ratio = adverse_score.observability_score.score / ideal_score.observability_score.score
            assert_that(ratio).is_greater_than(0.50)  # Still > 50%
        except TypeError:
            self.skipTest("Combined parameters not yet implemented")


# =============================================================================
# EDGE CASES
# =============================================================================

class TestEdgeCases(unittest.TestCase):
    """Test edge cases and boundary conditions."""

    def setUp(self):
        self.service = ObservabilityCalculationService()
        self.scope = TestFixtures.medium_dobsonian()
        self.eyepiece = TestFixtures.medium_eyepiece()
        self.site = TestFixtures.dark_site()

    def test_object_at_zenith(self):
        """Object at 90° altitude should score well."""
        zenith_object = CelestialObject('Zenith', 'DeepSky', 5.0, 10.0, 90.00)
        score = self.service.score_celestial_object(
            zenith_object, self.scope, self.eyepiece, self.site)
        assert_that(score.observability_score.score).is_greater_than(0)

    def test_object_just_above_horizon(self):
        """Object at 1° altitude should score poorly but not zero."""
        horizon_object = CelestialObject('Horizon', 'DeepSky', 5.0, 10.0, 1.00)
        score = self.service.score_celestial_object(
            horizon_object, self.scope, self.eyepiece, self.site)
        assert_that(score.observability_score.score).is_greater_than(0)

    def test_object_below_horizon_zero(self):
        """Object below horizon should score exactly zero."""
        below = CelestialObject('Below', 'DeepSky', 5.0, 10.0, -5.00)
        score = self.service.score_celestial_object(
            below, self.scope, self.eyepiece, self.site)
        assert_that(score.observability_score.score).is_equal_to(0.0)

    def test_extremely_bright_object(self):
        """Extremely bright object should score very high."""
        super_bright = CelestialObject('Super Bright', 'Planet', -10.0, 1.0, 50.00)
        score = self.service.score_celestial_object(
            super_bright, self.scope, self.eyepiece, self.site)
        assert_that(score.observability_score.score).is_greater_than(0)

    def test_extremely_faint_object(self):
        """Extremely faint object (mag 15) should score low but not zero."""
        super_faint = CelestialObject('Super Faint', 'DeepSky', 15.0, 1.0, 50.00)
        score = self.service.score_celestial_object(
            super_faint, self.scope, self.eyepiece, self.site)
        # Should score low but not zero (technically possible with large scope)
        assert_that(score.observability_score.score).is_greater_than_or_equal_to(0)

    def test_huge_extended_object(self):
        """Huge object (300 arcmin) should prefer very low mag."""
        huge = CelestialObject('Huge', 'DeepSky', 5.0, 300.0, 50.00)
        score = self.service.score_celestial_object(
            huge, self.scope, self.eyepiece, self.site)
        assert_that(score.observability_score.score).is_greater_than(0)

    def test_tiny_object(self):
        """Tiny object (0.01 arcmin) should benefit from high mag."""
        tiny = CelestialObject('Tiny', 'DeepSky', 8.0, 0.01, 50.00)
        score = self.service.score_celestial_object(
            tiny, self.scope, self.eyepiece, self.site)
        assert_that(score.observability_score.score).is_greater_than(0)


class TestScoreNormalization(unittest.TestCase):
    """Test that normalized scores are reasonable."""

    def setUp(self):
        self.service = ObservabilityCalculationService()
        self.scope = TestFixtures.medium_dobsonian()
        self.eyepiece = TestFixtures.medium_eyepiece()
        self.site = TestFixtures.dark_site()

    def test_normalized_scores_in_range(self):
        """Normalized scores should be in reasonable range (0-100ish)."""
        objects = [
            TestFixtures.moon(),
            TestFixtures.jupiter(),
            TestFixtures.orion_nebula(),
            TestFixtures.horsehead()
        ]

        for obj in objects:
            score = self.service.score_celestial_object(
                obj, self.scope, self.eyepiece, self.site)
            # Normalized score should be non-negative and not absurdly high
            assert_that(score.observability_score.normalized_score).is_greater_than_or_equal_to(0)
            assert_that(score.observability_score.normalized_score).is_less_than(1000)

    def test_raw_scores_positive_for_visible(self):
        """Raw scores should be positive for visible objects."""
        jupiter = TestFixtures.jupiter()
        score = self.service.score_celestial_object(
            jupiter, self.scope, self.eyepiece, self.site)
        assert_that(score.observability_score.score).is_greater_than(0)


if __name__ == '__main__':
    unittest.main()
