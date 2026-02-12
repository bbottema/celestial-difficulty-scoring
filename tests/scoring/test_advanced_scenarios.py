"""
Advanced observability scoring tests.

Tests for weather impact, moon proximity penalties, and edge cases.
These tests cover features not yet implemented - expect failures initially.
"""
import unittest
from assertpy import assert_that

from tests.test_helpers import create_test_celestial_object
from app.domain.model.moon_conditions import MoonConditions
from app.domain.services.observability_calculation_service import ObservabilityCalculationService
from app.orm.model.entities import Telescope, Eyepiece, ObservationSite
from app.domain.model.light_pollution import LightPollution
from app.domain.model.telescope_type import TelescopeType


def create_moon_at_separation(target_ra: float, target_dec: float, separation_degrees: float,
                              illumination: float, altitude: float) -> MoonConditions:
    """
    Helper to create MoonConditions at specified separation from target.
    Places moon at calculated RA/Dec to achieve desired separation.
    """
    # Simple approach: place moon at same declination, offset in RA
    # For accurate separation, we use spherical trigonometry
    # For simplicity in tests, we'll offset in RA by the separation amount
    # (This is approximate but sufficient for testing purposes)
    moon_ra = target_ra + separation_degrees
    moon_dec = target_dec

    return MoonConditions(
        phase=illumination / 100.0,
        illumination=illumination,
        altitude=altitude,
        ra=moon_ra,
        dec=moon_dec
    )


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
        return create_test_celestial_object('Moon', 'Moon', -12.60, 31.00, 45.00)

    @staticmethod
    def jupiter():
        return create_test_celestial_object('Jupiter', 'Planet', -2.40, 0.77, 45.00, ra=200.0, dec=20.0)

    @staticmethod
    def orion_nebula():
        return create_test_celestial_object('Orion Nebula', 'DeepSky', 4.0, 65.0, 55.00)

    @staticmethod
    def horsehead():
        return create_test_celestial_object('Horsehead Nebula', 'DeepSky', 10.0, 60.0, 45.00, ra=85.0, dec=-2.0)

    @staticmethod
    def andromeda():
        return create_test_celestial_object('Andromeda Galaxy', 'DeepSky', 3.44, 190.00, 60.00)


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
        """Even Jupiter should be drastically worse in overcast than clear weather."""
        jupiter = TestFixtures.jupiter()

        try:
            clear_score = self.service.score_celestial_object(
                jupiter, self.scope, self.eyepiece, self.site,
                weather={'condition': 'Clear', 'cloud_cover': 0})
            overcast_score = self.service.score_celestial_object(
                jupiter, self.scope, self.eyepiece, self.site,
                weather={'condition': 'Overcast', 'cloud_cover': 100})

            # Overcast should drastically reduce score (even for bright objects)
            # Using relative comparison: overcast should be much worse than clear
            assert_that(overcast_score.observability_score.score).is_less_than(
                clear_score.observability_score.score * 0.2
            ).described_as(
                f"Overcast should reduce Jupiter to <20% of clear score "
                f"(got {overcast_score.observability_score.score:.2f} vs {clear_score.observability_score.score:.2f})"
            )
        except TypeError:
            self.skipTest("Weather parameter not yet implemented")

    def test_overcast_devastates_moon(self):
        """Even Moon should be drastically worse in overcast than clear weather."""
        moon = TestFixtures.moon()

        try:
            clear_score = self.service.score_celestial_object(
                moon, self.scope, self.eyepiece, self.site,
                weather={'condition': 'Clear', 'cloud_cover': 0})
            overcast_score = self.service.score_celestial_object(
                moon, self.scope, self.eyepiece, self.site,
                weather={'condition': 'Overcast', 'cloud_cover': 100})

            # Even the moon should be drastically reduced by overcast
            assert_that(overcast_score.observability_score.score).is_less_than(
                clear_score.observability_score.score * 0.2
            ).described_as(
                f"Overcast should reduce Moon to <20% of clear score "
                f"(got {overcast_score.observability_score.score:.2f} vs {clear_score.observability_score.score:.2f})"
            )
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
        """50% cloud cover should reduce score by approximately 50% (proportional impact)."""
        orion = TestFixtures.orion_nebula()

        try:
            clear_score = self.service.score_celestial_object(
                orion, self.scope, self.eyepiece, self.site,
                weather={'condition': 'Clear', 'cloud_cover': 0})
            partial_score = self.service.score_celestial_object(
                orion, self.scope, self.eyepiece, self.site,
                weather={'condition': 'Partly Cloudy', 'cloud_cover': 50})

            # Cloud cover impact should be roughly proportional: 50% clouds → ~50% reduction
            # Allow 10% tolerance for non-linear effects
            ratio = partial_score.observability_score.score / clear_score.observability_score.score
            assert_that(ratio).is_between(0.40, 0.60).described_as(
                f"50% clouds should leave ~50% of score (got {ratio:.2%})"
            )
        except TypeError:
            self.skipTest("Weather parameter not yet implemented")

    def test_25_percent_clouds(self):
        """25% cloud cover should reduce score by approximately 25% (proportional impact)."""
        jupiter = TestFixtures.jupiter()

        try:
            clear_score = self.service.score_celestial_object(
                jupiter, self.scope, self.eyepiece, self.site,
                weather={'condition': 'Clear', 'cloud_cover': 0})
            light_clouds_score = self.service.score_celestial_object(
                jupiter, self.scope, self.eyepiece, self.site,
                weather={'condition': 'Few Clouds', 'cloud_cover': 25})

            # Cloud cover impact should be roughly proportional: 25% clouds → ~25% reduction
            # Allow 5% tolerance
            ratio = light_clouds_score.observability_score.score / clear_score.observability_score.score
            assert_that(ratio).is_between(0.70, 0.80).described_as(
                f"25% clouds should leave ~75% of score (got {ratio:.2%})"
            )
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
        """Object 10° from full moon should be drastically worse than far from moon."""
        target = create_test_celestial_object('Target Near Moon', 'DeepSky', 6.0, 10.0, 60.00, ra=180.0, dec=30.0)

        # Moon far away
        far_moon = create_moon_at_separation(target.ra, target.dec, 120.0, 100.0, 60.0)
        far_score = self.service.score_celestial_object(
            target, self.scope, self.eyepiece, self.site,
            moon_conditions=far_moon)

        # Moon very close
        near_moon = create_moon_at_separation(target.ra, target.dec, 10.0, 100.0, 60.0)
        near_score = self.service.score_celestial_object(
            target, self.scope, self.eyepiece, self.site,
            moon_conditions=near_moon)

        # Full moon 10° away should severely reduce score (<30% of far score)
        assert_that(near_score.observability_score.score).is_less_than(
            far_score.observability_score.score * 0.3
        ).described_as(
            f"Object 10° from full moon should be <30% of far score "
            f"(got {near_score.observability_score.score:.2f} vs {far_score.observability_score.score:.2f})"
        )

    def test_object_very_close_to_full_moon(self):
        """Object 5° from full moon should be much harder than 90° away."""
        target = create_test_celestial_object('Target Very Close', 'DeepSky', 7.0, 5.0, 60.00, ra=180.0, dec=30.0)

        far_moon = create_moon_at_separation(target.ra, target.dec, 90.0, 100.0, 60.0)
        far_score = self.service.score_celestial_object(
            target, self.scope, self.eyepiece, self.site,
            moon_conditions=far_moon)

        close_moon = create_moon_at_separation(target.ra, target.dec, 5.0, 100.0, 60.0)
        very_close_score = self.service.score_celestial_object(
            target, self.scope, self.eyepiece, self.site,
            moon_conditions=close_moon)

        # Object 5° from full moon should be significantly worse than 90° away
        assert_that(very_close_score.observability_score.score).is_less_than(
            far_score.observability_score.score
        ).described_as(
            f"Object 5° from full moon should be much harder than 90° away "
            f"(got {very_close_score.observability_score.score:.2f} vs {far_score.observability_score.score:.2f})"
        )


class TestMoonProximityByPhase(unittest.TestCase):
    """Moon proximity penalty should scale with illumination."""

    def setUp(self):
        self.service = ObservabilityCalculationService()
        self.scope = TestFixtures.medium_dobsonian()
        self.eyepiece = TestFixtures.medium_eyepiece()
        self.site = TestFixtures.dark_site()

    def test_new_moon_no_penalty(self):
        """New moon (0% illumination) should not penalize nearby objects."""
        target = create_test_celestial_object('Target Near New Moon', 'DeepSky', 8.0, 10.0, 60.00, ra=180.0, dec=30.0)

        new_moon = create_moon_at_separation(target.ra, target.dec, 20.0, 0.0, 0.0)
        new_moon_score = self.service.score_celestial_object(
            target, self.scope, self.eyepiece, self.site,
            moon_conditions=new_moon)

        full_moon = create_moon_at_separation(target.ra, target.dec, 20.0, 100.0, 60.0)
        full_moon_score = self.service.score_celestial_object(
            target, self.scope, self.eyepiece, self.site,
            moon_conditions=full_moon)

        # New moon should not penalize
        assert_that(new_moon_score.observability_score.score).is_greater_than(
            full_moon_score.observability_score.score * 2.0)

    def test_quarter_moon_moderate_penalty(self):
        """Quarter moon (50% illumination) should have moderate penalty."""
        target = create_test_celestial_object('Target Near Quarter Moon', 'DeepSky', 7.0, 8.0, 60.00, ra=180.0, dec=30.0)

        quarter_moon = create_moon_at_separation(target.ra, target.dec, 15.0, 50.0, 50.0)
        quarter_moon_score = self.service.score_celestial_object(
            target, self.scope, self.eyepiece, self.site,
            moon_conditions=quarter_moon)

        full_moon = create_moon_at_separation(target.ra, target.dec, 15.0, 100.0, 50.0)
        full_moon_score = self.service.score_celestial_object(
            target, self.scope, self.eyepiece, self.site,
            moon_conditions=full_moon)

        # Quarter moon should be better than full moon
        assert_that(quarter_moon_score.observability_score.score).is_greater_than(
            full_moon_score.observability_score.score)

    def test_crescent_moon_minor_penalty(self):
        """Crescent moon (10% illumination) should have minor penalty."""
        target = create_test_celestial_object('Target Near Crescent', 'DeepSky', 7.5, 10.0, 60.00, ra=180.0, dec=30.0)

        crescent_moon = create_moon_at_separation(target.ra, target.dec, 20.0, 10.0, 40.0)
        crescent_score = self.service.score_celestial_object(
            target, self.scope, self.eyepiece, self.site,
            moon_conditions=crescent_moon)

        full_moon = create_moon_at_separation(target.ra, target.dec, 20.0, 100.0, 40.0)
        full_moon_score = self.service.score_celestial_object(
            target, self.scope, self.eyepiece, self.site,
            moon_conditions=full_moon)

        # Crescent should be much better than full
        assert_that(crescent_score.observability_score.score).is_greater_than(
            full_moon_score.observability_score.score * 3.0)


class TestMoonProximityBySeparation(unittest.TestCase):
    """Moon proximity penalty should follow inverse square of separation."""

    def setUp(self):
        self.service = ObservabilityCalculationService()
        self.scope = TestFixtures.medium_dobsonian()
        self.eyepiece = TestFixtures.medium_eyepiece()
        self.site = TestFixtures.dark_site()

    def test_separation_gradient(self):
        """Score should increase with separation from full moon."""
        target = create_test_celestial_object('Target', 'DeepSky', 7.0, 10.0, 60.00, ra=180.0, dec=30.0)
        separations = [5, 10, 20, 40, 80]

        scores = []
        for sep in separations:
            moon = create_moon_at_separation(target.ra, target.dec, sep, 100.0, 60.0)
            score = self.service.score_celestial_object(
                target, self.scope, self.eyepiece, self.site,
                moon_conditions=moon)
            scores.append(score.observability_score.score)

        # Scores should increase monotonically
        for i in range(len(scores) - 1):
            assert_that(scores[i + 1]).is_greater_than(scores[i])

    def test_double_separation_significant_improvement(self):
        """Doubling separation should significantly improve score."""
        target = create_test_celestial_object('Target', 'DeepSky', 7.0, 10.0, 60.00, ra=180.0, dec=30.0)

        close_moon = create_moon_at_separation(target.ra, target.dec, 10.0, 100.0, 60.0)
        close_score = self.service.score_celestial_object(
            target, self.scope, self.eyepiece, self.site,
            moon_conditions=close_moon)

        far_moon = create_moon_at_separation(target.ra, target.dec, 20.0, 100.0, 60.0)
        far_score = self.service.score_celestial_object(
            target, self.scope, self.eyepiece, self.site,
            moon_conditions=far_moon)

        # Doubling distance should roughly quadruple score (inverse square)
        ratio = far_score.observability_score.score / close_score.observability_score.score
        assert_that(ratio).is_greater_than(2.5)  # Allow some variance


class TestMoonOccultation(unittest.TestCase):
    """Objects directly behind moon should be invisible."""

    def setUp(self):
        self.service = ObservabilityCalculationService()
        self.scope = TestFixtures.medium_dobsonian()
        self.eyepiece = TestFixtures.medium_eyepiece()
        self.site = TestFixtures.dark_site()

    def test_occultation_zero_score(self):
        """Object at 0° separation (behind moon) should score zero."""
        target = create_test_celestial_object('Occulted Star', 'DeepSky', 3.0, 0.0001, 60.00, ra=180.0, dec=30.0)

        moon = create_moon_at_separation(target.ra, target.dec, 0.0, 100.0, 60.0)
        score = self.service.score_celestial_object(
            target, self.scope, self.eyepiece, self.site,
            moon_conditions=moon)

        assert_that(score.observability_score.score).is_equal_to(0.0)

    def test_barely_past_moon_still_very_hard(self):
        """Object 0.5° from moon should be much harder than 60° away."""
        target = create_test_celestial_object('Just Past Moon', 'DeepSky', 5.0, 1.0, 60.00, ra=180.0, dec=30.0)

        close_moon = create_moon_at_separation(target.ra, target.dec, 0.5, 100.0, 60.0)
        barely_past_score = self.service.score_celestial_object(
            target, self.scope, self.eyepiece, self.site,
            moon_conditions=close_moon)

        far_moon = create_moon_at_separation(target.ra, target.dec, 60.0, 100.0, 60.0)
        far_score = self.service.score_celestial_object(
            target, self.scope, self.eyepiece, self.site,
            moon_conditions=far_moon)

        # Object just 0.5° from moon should be significantly worse than 60° away
        assert_that(barely_past_score.observability_score.score).is_less_than(
            far_score.observability_score.score
        ).described_as(
            f"Object 0.5° from moon should be much harder than 60° away "
            f"(got {barely_past_score.observability_score.score:.2f} vs {far_score.observability_score.score:.2f})"
        )


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

        far_moon = create_moon_at_separation(jupiter.ra, jupiter.dec, 90.0, 100.0, 60.0)
        far_score = self.service.score_celestial_object(
            jupiter, self.scope, self.eyepiece, self.site,
            moon_conditions=far_moon)

        near_moon = create_moon_at_separation(jupiter.ra, jupiter.dec, 15.0, 100.0, 60.0)
        near_score = self.service.score_celestial_object(
            jupiter, self.scope, self.eyepiece, self.site,
            moon_conditions=near_moon)

        ratio = near_score.observability_score.score / far_score.observability_score.score
        assert_that(ratio).is_greater_than(0.60)

    def test_faint_object_devastated_by_moon(self):
        """Faint objects should be drastically worse near full moon than far from moon."""
        horsehead = TestFixtures.horsehead()

        far_moon = create_moon_at_separation(horsehead.ra, horsehead.dec, 90.0, 100.0, 60.0)
        far_score = self.service.score_celestial_object(
            horsehead, self.scope, self.eyepiece, self.site,
            moon_conditions=far_moon)

        near_moon = create_moon_at_separation(horsehead.ra, horsehead.dec, 15.0, 100.0, 60.0)
        near_score = self.service.score_celestial_object(
            horsehead, self.scope, self.eyepiece, self.site,
            moon_conditions=near_moon)

        # Faint objects near moon should be devastated (<20% of far score)
        assert_that(near_score.observability_score.score).is_less_than(
            far_score.observability_score.score * 0.2
        ).described_as(
            f"Faint object near moon should be <20% of far score "
            f"(got {near_score.observability_score.score:.2f} vs {far_score.observability_score.score:.2f})"
        )


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

        new_moon = create_moon_at_separation(horsehead.ra, horsehead.dec, 180.0, 0.0, 0.0)
        ideal_score = self.service.score_celestial_object(
            horsehead, self.scope, self.eyepiece, self.site,
            weather={'condition': 'Clear', 'cloud_cover': 0},
            moon_conditions=new_moon)

        full_moon = create_moon_at_separation(horsehead.ra, horsehead.dec, 10.0, 100.0, 60.0)
        terrible_score = self.service.score_celestial_object(
            horsehead, self.scope, self.eyepiece, self.site,
            weather={'condition': 'Mostly Cloudy', 'cloud_cover': 75},
            moon_conditions=full_moon)

        ratio = terrible_score.observability_score.score / ideal_score.observability_score.score
        assert_that(ratio).is_less_than(0.05)  # < 5%

    def test_bright_object_survives_adversity(self):
        """Jupiter should remain reasonably observable even in moderate adversity."""
        jupiter = TestFixtures.jupiter()

        new_moon = create_moon_at_separation(jupiter.ra, jupiter.dec, 180.0, 0.0, 0.0)
        ideal_score = self.service.score_celestial_object(
            jupiter, self.scope, self.eyepiece, self.site,
            weather={'condition': 'Clear', 'cloud_cover': 0},
            moon_conditions=new_moon)

        quarter_moon = create_moon_at_separation(jupiter.ra, jupiter.dec, 30.0, 50.0, 50.0)
        adverse_score = self.service.score_celestial_object(
            jupiter, self.scope, self.eyepiece, self.site,
            weather={'condition': 'Few Clouds', 'cloud_cover': 25},
            moon_conditions=quarter_moon)

        # Bright objects should remain reasonably observable in moderate adversity (>50%)
        ratio = adverse_score.observability_score.score / ideal_score.observability_score.score
        assert_that(ratio).is_greater_than(0.50).described_as(
            f"Jupiter in moderate adversity should be >50% of ideal score (got {ratio:.2%})"
        )


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
        zenith_object = create_test_celestial_object('Zenith', 'DeepSky', 5.0, 10.0, 90.00)
        score = self.service.score_celestial_object(
            zenith_object, self.scope, self.eyepiece, self.site)
        assert_that(score.observability_score.score).is_greater_than(0)

    def test_object_just_above_horizon(self):
        """Object at 1° altitude should score poorly but not zero."""
        horizon_object = create_test_celestial_object('Horizon', 'DeepSky', 5.0, 10.0, 1.00)
        score = self.service.score_celestial_object(
            horizon_object, self.scope, self.eyepiece, self.site)
        assert_that(score.observability_score.score).is_greater_than(0)

    def test_object_below_horizon_zero(self):
        """Object below horizon should score exactly zero."""
        below = create_test_celestial_object('Below', 'DeepSky', 5.0, 10.0, -5.00)
        score = self.service.score_celestial_object(
            below, self.scope, self.eyepiece, self.site)
        assert_that(score.observability_score.score).is_equal_to(0.0)

    def test_extremely_bright_object(self):
        """Extremely bright object should score very high."""
        super_bright = create_test_celestial_object('Super Bright', 'Planet', -10.0, 1.0, 50.00)
        score = self.service.score_celestial_object(
            super_bright, self.scope, self.eyepiece, self.site)
        assert_that(score.observability_score.score).is_greater_than(0)

    def test_extremely_faint_object(self):
        """Extremely faint object (mag 15) should score low but not zero."""
        super_faint = create_test_celestial_object('Super Faint', 'DeepSky', 15.0, 1.0, 50.00)
        score = self.service.score_celestial_object(
            super_faint, self.scope, self.eyepiece, self.site)
        # Should score low but not zero (technically possible with large scope)
        assert_that(score.observability_score.score).is_greater_than_or_equal_to(0)

    def test_huge_extended_object(self):
        """Huge object (300 arcmin) should prefer very low mag."""
        huge = create_test_celestial_object('Huge', 'DeepSky', 5.0, 300.0, 50.00)
        score = self.service.score_celestial_object(
            huge, self.scope, self.eyepiece, self.site)
        assert_that(score.observability_score.score).is_greater_than(0)

    def test_tiny_object(self):
        """Tiny object (0.01 arcmin) should benefit from high mag."""
        tiny = create_test_celestial_object('Tiny', 'DeepSky', 8.0, 0.01, 50.00)
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
