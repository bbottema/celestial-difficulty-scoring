"""
Unit tests for celestial observability scoring.

These tests focus on pairwise comparisons and quick sanity checks to pinpoint logical mistakes.
Each test compares exactly two objects or tests one external factor at a time.

Most tests will initially fail as features are not yet implemented - this is expected.
"""
import unittest
from assertpy import assert_that

from app.domain.model.celestial_object import CelestialObject
from app.domain.services.observability_calculation_service import ObservabilityCalculationService
from app.orm.model.entities import Telescope, Eyepiece, ObservationSite
from app.domain.model.light_pollution import LightPollution
from app.domain.model.telescope_type import TelescopeType


class TestFixtures:
    """Test fixtures for equipment and celestial objects."""

    # Equipment
    @staticmethod
    def small_refractor():
        return Telescope(
            id=None,
            name="80mm Refractor",
            type=TelescopeType.REFRACTOR,
            aperture=80,
            focal_length=600,
            focal_ratio=7.5
        )

    @staticmethod
    def medium_dobsonian():
        return Telescope(
            id=None,
            name="8-inch Dob",
            type=TelescopeType.DOBSONIAN,
            aperture=200,
            focal_length=1200,
            focal_ratio=6.0
        )

    @staticmethod
    def large_dobsonian():
        return Telescope(
            id=None,
            name="16-inch Dob",
            type=TelescopeType.DOBSONIAN,
            aperture=400,
            focal_length=1800,
            focal_ratio=4.5
        )

    @staticmethod
    def wide_eyepiece():
        return Eyepiece(
            id=None,
            name="25mm Wide",
            focal_length=25,
            barrel_size=1.25,
            apparent_field_of_view=68
        )

    @staticmethod
    def medium_eyepiece():
        return Eyepiece(
            id=None,
            name="10mm Medium",
            focal_length=10,
            barrel_size=1.25,
            apparent_field_of_view=50
        )

    @staticmethod
    def planetary_eyepiece():
        return Eyepiece(
            id=None,
            name="5mm Planetary",
            focal_length=5,
            barrel_size=1.25,
            apparent_field_of_view=50
        )

    @staticmethod
    def widefield_eyepiece():
        return Eyepiece(
            id=None,
            name="30mm Widefield",
            focal_length=30,
            barrel_size=2.0,
            apparent_field_of_view=82
        )

    # Sites
    @staticmethod
    def dark_site():
        return ObservationSite(
            id=None,
            name="Dark Sky Reserve",
            latitude=40.0,
            longitude=-80.0,
            light_pollution=LightPollution.BORTLE_2
        )

    @staticmethod
    def suburban_site():
        return ObservationSite(
            id=None,
            name="Suburban Backyard",
            latitude=40.0,
            longitude=-80.0,
            light_pollution=LightPollution.BORTLE_6
        )

    @staticmethod
    def city_site():
        return ObservationSite(
            id=None,
            name="City Center",
            latitude=40.0,
            longitude=-80.0,
            light_pollution=LightPollution.BORTLE_8
        )

    # Solar System Objects
    @staticmethod
    def sun():
        return CelestialObject('Sun', 'Sun', -26.74, 31.00, 45.00)

    @staticmethod
    def moon():
        return CelestialObject('Moon', 'Moon', -12.60, 31.00, 45.00)

    @staticmethod
    def jupiter():
        return CelestialObject('Jupiter', 'Planet', -2.40, 0.77, 45.00)

    @staticmethod
    def saturn():
        return CelestialObject('Saturn', 'Planet', 0.50, 0.27, 45.00)

    @staticmethod
    def mars():
        return CelestialObject('Mars', 'Planet', -1.00, 0.15, 45.00)

    @staticmethod
    def venus():
        return CelestialObject('Venus', 'Planet', -4.00, 0.20, 45.00)

    @staticmethod
    def uranus():
        return CelestialObject('Uranus', 'Planet', 5.70, 0.058, 45.00)

    @staticmethod
    def neptune():
        return CelestialObject('Neptune', 'Planet', 7.80, 0.037, 45.00)

    # Bright Stars
    @staticmethod
    def sirius():
        return CelestialObject('Sirius', 'DeepSky', -1.46, 0.0001, 60.00)

    @staticmethod
    def vega():
        return CelestialObject('Vega', 'DeepSky', 0.03, 0.0001, 70.00)

    @staticmethod
    def betelgeuse():
        return CelestialObject('Betelgeuse', 'DeepSky', 0.50, 0.0001, 50.00)

    # Bright Deep-Sky Objects
    @staticmethod
    def orion_nebula():
        return CelestialObject('Orion Nebula', 'DeepSky', 4.0, 65.0, 55.00)

    @staticmethod
    def andromeda():
        return CelestialObject('Andromeda Galaxy', 'DeepSky', 3.44, 190.00, 60.00)

    @staticmethod
    def pleiades():
        return CelestialObject('Pleiades', 'DeepSky', 1.6, 110.0, 65.00)

    # Medium Deep-Sky Objects
    @staticmethod
    def ring_nebula():
        return CelestialObject('Ring Nebula', 'DeepSky', 8.8, 1.4, 60.00)

    @staticmethod
    def whirlpool():
        return CelestialObject('Whirlpool Galaxy', 'DeepSky', 8.4, 11.0, 55.00)

    @staticmethod
    def dumbbell_nebula():
        return CelestialObject('Dumbbell Nebula', 'DeepSky', 7.5, 8.0, 58.00)

    # Faint Deep-Sky Objects
    @staticmethod
    def veil_nebula():
        return CelestialObject('Veil Nebula', 'DeepSky', 7.0, 180.00, 55.00)

    @staticmethod
    def horsehead():
        return CelestialObject('Horsehead Nebula', 'DeepSky', 10.0, 60.0, 45.00)

    @staticmethod
    def ic_1396():
        return CelestialObject('IC 1396', 'DeepSky', 9.5, 170.0, 50.00)


# =============================================================================
# SOLAR SYSTEM BRIGHTNESS COMPARISONS
# =============================================================================

class TestSolarSystemBrightnessOrdering(unittest.TestCase):
    """Tests that solar system objects rank by brightness."""

    def setUp(self):
        self.service = ObservabilityCalculationService()
        self.medium_scope = TestFixtures.medium_dobsonian()
        self.medium_eyepiece = TestFixtures.medium_eyepiece()
        self.dark_site = TestFixtures.dark_site()

    def test_sun_beats_moon(self):
        """Sun should always score higher than Moon (both at same altitude)."""
        sun = TestFixtures.sun()
        moon = TestFixtures.moon()

        sun_score = self.service.score_celestial_object(
            sun, self.medium_scope, self.medium_eyepiece, self.dark_site)
        moon_score = self.service.score_celestial_object(
            moon, self.medium_scope, self.medium_eyepiece, self.dark_site)

        assert_that(sun_score.observability_score.normalized_score).is_greater_than(
            moon_score.observability_score.normalized_score)

    def test_moon_beats_jupiter(self):
        """Moon should always score higher than Jupiter."""
        moon = TestFixtures.moon()
        jupiter = TestFixtures.jupiter()

        moon_score = self.service.score_celestial_object(
            moon, self.medium_scope, self.medium_eyepiece, self.dark_site)
        jupiter_score = self.service.score_celestial_object(
            jupiter, self.medium_scope, self.medium_eyepiece, self.dark_site)

        assert_that(moon_score.observability_score.normalized_score).is_greater_than(
            jupiter_score.observability_score.normalized_score)

    def test_moon_beats_venus(self):
        """Moon should score higher than Venus."""
        moon = TestFixtures.moon()
        venus = TestFixtures.venus()

        moon_score = self.service.score_celestial_object(
            moon, self.medium_scope, self.medium_eyepiece, self.dark_site)
        venus_score = self.service.score_celestial_object(
            venus, self.medium_scope, self.medium_eyepiece, self.dark_site)

        assert_that(moon_score.observability_score.normalized_score).is_greater_than(
            venus_score.observability_score.normalized_score)

    def test_venus_beats_jupiter(self):
        """Venus (mag -4) should score higher than Jupiter (mag -2.4)."""
        venus = TestFixtures.venus()
        jupiter = TestFixtures.jupiter()

        venus_score = self.service.score_celestial_object(
            venus, self.medium_scope, self.medium_eyepiece, self.dark_site)
        jupiter_score = self.service.score_celestial_object(
            jupiter, self.medium_scope, self.medium_eyepiece, self.dark_site)

        assert_that(venus_score.observability_score.normalized_score).is_greater_than(
            jupiter_score.observability_score.normalized_score)

    def test_jupiter_beats_saturn(self):
        """Jupiter (mag -2.4) should score higher than Saturn (mag 0.5)."""
        jupiter = TestFixtures.jupiter()
        saturn = TestFixtures.saturn()

        jupiter_score = self.service.score_celestial_object(
            jupiter, self.medium_scope, self.medium_eyepiece, self.dark_site)
        saturn_score = self.service.score_celestial_object(
            saturn, self.medium_scope, self.medium_eyepiece, self.dark_site)

        assert_that(jupiter_score.observability_score.normalized_score).is_greater_than(
            saturn_score.observability_score.normalized_score)

    def test_mars_beats_saturn(self):
        """Mars (mag -1.0) should score higher than Saturn (mag 0.5)."""
        mars = TestFixtures.mars()
        saturn = TestFixtures.saturn()

        mars_score = self.service.score_celestial_object(
            mars, self.medium_scope, self.medium_eyepiece, self.dark_site)
        saturn_score = self.service.score_celestial_object(
            saturn, self.medium_scope, self.medium_eyepiece, self.dark_site)

        assert_that(mars_score.observability_score.normalized_score).is_greater_than(
            saturn_score.observability_score.normalized_score)

    def test_saturn_beats_uranus(self):
        """Saturn (mag 0.5) should score higher than Uranus (mag 5.7)."""
        saturn = TestFixtures.saturn()
        uranus = TestFixtures.uranus()

        saturn_score = self.service.score_celestial_object(
            saturn, self.medium_scope, self.medium_eyepiece, self.dark_site)
        uranus_score = self.service.score_celestial_object(
            uranus, self.medium_scope, self.medium_eyepiece, self.dark_site)

        assert_that(saturn_score.observability_score.normalized_score).is_greater_than(
            uranus_score.observability_score.normalized_score)

    def test_uranus_beats_neptune(self):
        """Uranus (mag 5.7) should score higher than Neptune (mag 7.8)."""
        uranus = TestFixtures.uranus()
        neptune = TestFixtures.neptune()

        uranus_score = self.service.score_celestial_object(
            uranus, self.medium_scope, self.medium_eyepiece, self.dark_site)
        neptune_score = self.service.score_celestial_object(
            neptune, self.medium_scope, self.medium_eyepiece, self.dark_site)

        assert_that(uranus_score.observability_score.normalized_score).is_greater_than(
            neptune_score.observability_score.normalized_score)


# =============================================================================
# MOON VS OTHER OBJECT TYPES
# =============================================================================

class TestMoonVsOtherObjectTypes(unittest.TestCase):
    """Moon should beat nearly everything except Sun."""

    def setUp(self):
        self.service = ObservabilityCalculationService()
        self.medium_scope = TestFixtures.medium_dobsonian()
        self.medium_eyepiece = TestFixtures.medium_eyepiece()
        self.dark_site = TestFixtures.dark_site()

    def test_moon_beats_brightest_star(self):
        """Moon should score higher than Sirius (brightest star)."""
        moon = TestFixtures.moon()
        sirius = TestFixtures.sirius()

        moon_score = self.service.score_celestial_object(
            moon, self.medium_scope, self.medium_eyepiece, self.dark_site)
        sirius_score = self.service.score_celestial_object(
            sirius, self.medium_scope, self.medium_eyepiece, self.dark_site)

        assert_that(moon_score.observability_score.normalized_score).is_greater_than(
            sirius_score.observability_score.normalized_score)

    def test_moon_beats_vega(self):
        """Moon should score higher than Vega."""
        moon = TestFixtures.moon()
        vega = TestFixtures.vega()

        moon_score = self.service.score_celestial_object(
            moon, self.medium_scope, self.medium_eyepiece, self.dark_site)
        vega_score = self.service.score_celestial_object(
            vega, self.medium_scope, self.medium_eyepiece, self.dark_site)

        assert_that(moon_score.observability_score.normalized_score).is_greater_than(
            vega_score.observability_score.normalized_score)

    def test_moon_beats_orion_nebula(self):
        """Moon should score higher than Orion Nebula."""
        moon = TestFixtures.moon()
        orion = TestFixtures.orion_nebula()

        moon_score = self.service.score_celestial_object(
            moon, self.medium_scope, self.medium_eyepiece, self.dark_site)
        orion_score = self.service.score_celestial_object(
            orion, self.medium_scope, self.medium_eyepiece, self.dark_site)

        assert_that(moon_score.observability_score.normalized_score).is_greater_than(
            orion_score.observability_score.normalized_score)

    def test_moon_beats_andromeda(self):
        """Moon should score higher than Andromeda Galaxy."""
        moon = TestFixtures.moon()
        andromeda = TestFixtures.andromeda()

        moon_score = self.service.score_celestial_object(
            moon, self.medium_scope, self.medium_eyepiece, self.dark_site)
        andromeda_score = self.service.score_celestial_object(
            andromeda, self.medium_scope, self.medium_eyepiece, self.dark_site)

        assert_that(moon_score.observability_score.normalized_score).is_greater_than(
            andromeda_score.observability_score.normalized_score)

    def test_moon_beats_pleiades(self):
        """Moon should score higher than Pleiades."""
        moon = TestFixtures.moon()
        pleiades = TestFixtures.pleiades()

        moon_score = self.service.score_celestial_object(
            moon, self.medium_scope, self.medium_eyepiece, self.dark_site)
        pleiades_score = self.service.score_celestial_object(
            pleiades, self.medium_scope, self.medium_eyepiece, self.dark_site)

        assert_that(moon_score.observability_score.normalized_score).is_greater_than(
            pleiades_score.observability_score.normalized_score)

    def test_moon_beats_ring_nebula(self):
        """Moon should score higher than Ring Nebula."""
        moon = TestFixtures.moon()
        ring = TestFixtures.ring_nebula()

        moon_score = self.service.score_celestial_object(
            moon, self.medium_scope, self.medium_eyepiece, self.dark_site)
        ring_score = self.service.score_celestial_object(
            ring, self.medium_scope, self.medium_eyepiece, self.dark_site)

        assert_that(moon_score.observability_score.normalized_score).is_greater_than(
            ring_score.observability_score.normalized_score)

    def test_moon_beats_horsehead(self):
        """Moon should score higher than Horsehead Nebula (very faint)."""
        moon = TestFixtures.moon()
        horsehead = TestFixtures.horsehead()

        moon_score = self.service.score_celestial_object(
            moon, self.medium_scope, self.medium_eyepiece, self.dark_site)
        horsehead_score = self.service.score_celestial_object(
            horsehead, self.medium_scope, self.medium_eyepiece, self.dark_site)

        assert_that(moon_score.observability_score.normalized_score).is_greater_than(
            horsehead_score.observability_score.normalized_score)


# =============================================================================
# PLANETS VS STARS
# =============================================================================

class TestPlanetsVsStars(unittest.TestCase):
    """Brightness-based comparisons between planets and stars."""

    def setUp(self):
        self.service = ObservabilityCalculationService()
        self.medium_scope = TestFixtures.medium_dobsonian()
        self.medium_eyepiece = TestFixtures.medium_eyepiece()
        self.dark_site = TestFixtures.dark_site()

    def test_jupiter_beats_sirius(self):
        """Jupiter (mag -2.4) should score higher than Sirius (mag -1.46)."""
        jupiter = TestFixtures.jupiter()
        sirius = TestFixtures.sirius()

        jupiter_score = self.service.score_celestial_object(
            jupiter, self.medium_scope, self.medium_eyepiece, self.dark_site)
        sirius_score = self.service.score_celestial_object(
            sirius, self.medium_scope, self.medium_eyepiece, self.dark_site)

        assert_that(jupiter_score.observability_score.normalized_score).is_greater_than(
            sirius_score.observability_score.normalized_score)

    def test_jupiter_beats_vega(self):
        """Jupiter (mag -2.4) should score higher than Vega (mag 0.03)."""
        jupiter = TestFixtures.jupiter()
        vega = TestFixtures.vega()

        jupiter_score = self.service.score_celestial_object(
            jupiter, self.medium_scope, self.medium_eyepiece, self.dark_site)
        vega_score = self.service.score_celestial_object(
            vega, self.medium_scope, self.medium_eyepiece, self.dark_site)

        assert_that(jupiter_score.observability_score.normalized_score).is_greater_than(
            vega_score.observability_score.normalized_score)

    def test_sirius_beats_saturn(self):
        """Sirius (mag -1.46) should score higher than Saturn (mag 0.5)."""
        sirius = TestFixtures.sirius()
        saturn = TestFixtures.saturn()

        sirius_score = self.service.score_celestial_object(
            sirius, self.medium_scope, self.medium_eyepiece, self.dark_site)
        saturn_score = self.service.score_celestial_object(
            saturn, self.medium_scope, self.medium_eyepiece, self.dark_site)

        assert_that(sirius_score.observability_score.normalized_score).is_greater_than(
            saturn_score.observability_score.normalized_score)

    def test_vega_beats_saturn(self):
        """Vega (mag 0.03) should score higher than Saturn (mag 0.5)."""
        vega = TestFixtures.vega()
        saturn = TestFixtures.saturn()

        vega_score = self.service.score_celestial_object(
            vega, self.medium_scope, self.medium_eyepiece, self.dark_site)
        saturn_score = self.service.score_celestial_object(
            saturn, self.medium_scope, self.medium_eyepiece, self.dark_site)

        assert_that(vega_score.observability_score.normalized_score).is_greater_than(
            saturn_score.observability_score.normalized_score)


# =============================================================================
# BRIGHT STARS VS DEEP-SKY OBJECTS
# =============================================================================

class TestStarsVsDeepSkyObjects(unittest.TestCase):
    """Bright stars should generally beat deep-sky objects."""

    def setUp(self):
        self.service = ObservabilityCalculationService()
        self.medium_scope = TestFixtures.medium_dobsonian()
        self.medium_eyepiece = TestFixtures.medium_eyepiece()
        self.dark_site = TestFixtures.dark_site()

    def test_sirius_beats_orion_nebula(self):
        """Sirius (mag -1.46) should beat Orion Nebula (mag 4.0)."""
        sirius = TestFixtures.sirius()
        orion = TestFixtures.orion_nebula()

        sirius_score = self.service.score_celestial_object(
            sirius, self.medium_scope, self.medium_eyepiece, self.dark_site)
        orion_score = self.service.score_celestial_object(
            orion, self.medium_scope, self.medium_eyepiece, self.dark_site)

        assert_that(sirius_score.observability_score.normalized_score).is_greater_than(
            orion_score.observability_score.normalized_score)

    def test_vega_beats_andromeda(self):
        """Vega (mag 0.03) should beat Andromeda (mag 3.44)."""
        vega = TestFixtures.vega()
        andromeda = TestFixtures.andromeda()

        vega_score = self.service.score_celestial_object(
            vega, self.medium_scope, self.medium_eyepiece, self.dark_site)
        andromeda_score = self.service.score_celestial_object(
            andromeda, self.medium_scope, self.medium_eyepiece, self.dark_site)

        assert_that(vega_score.observability_score.normalized_score).is_greater_than(
            andromeda_score.observability_score.normalized_score)

    def test_sirius_beats_ring_nebula(self):
        """Sirius (mag -1.46) should beat Ring Nebula (mag 8.8)."""
        sirius = TestFixtures.sirius()
        ring = TestFixtures.ring_nebula()

        sirius_score = self.service.score_celestial_object(
            sirius, self.medium_scope, self.medium_eyepiece, self.dark_site)
        ring_score = self.service.score_celestial_object(
            ring, self.medium_scope, self.medium_eyepiece, self.dark_site)

        assert_that(sirius_score.observability_score.normalized_score).is_greater_than(
            ring_score.observability_score.normalized_score)

    def test_vega_beats_horsehead(self):
        """Vega should beat Horsehead Nebula (very faint)."""
        vega = TestFixtures.vega()
        horsehead = TestFixtures.horsehead()

        vega_score = self.service.score_celestial_object(
            vega, self.medium_scope, self.medium_eyepiece, self.dark_site)
        horsehead_score = self.service.score_celestial_object(
            horsehead, self.medium_scope, self.medium_eyepiece, self.dark_site)

        assert_that(vega_score.observability_score.normalized_score).is_greater_than(
            horsehead_score.observability_score.normalized_score)


# =============================================================================
# DEEP-SKY MAGNITUDE COMPARISONS
# =============================================================================

class TestDeepSkyMagnitudeOrdering(unittest.TestCase):
    """Brighter deep-sky objects should score higher than fainter ones."""

    def setUp(self):
        self.service = ObservabilityCalculationService()
        self.medium_scope = TestFixtures.medium_dobsonian()
        self.medium_eyepiece = TestFixtures.medium_eyepiece()
        self.dark_site = TestFixtures.dark_site()

    def test_pleiades_beats_andromeda(self):
        """Pleiades (mag 1.6) should beat Andromeda (mag 3.44)."""
        pleiades = TestFixtures.pleiades()
        andromeda = TestFixtures.andromeda()

        pleiades_score = self.service.score_celestial_object(
            pleiades, self.medium_scope, self.medium_eyepiece, self.dark_site)
        andromeda_score = self.service.score_celestial_object(
            andromeda, self.medium_scope, self.medium_eyepiece, self.dark_site)

        assert_that(pleiades_score.observability_score.normalized_score).is_greater_than(
            andromeda_score.observability_score.normalized_score)

    def test_andromeda_beats_orion_nebula(self):
        """Andromeda (mag 3.44) should beat Orion Nebula (mag 4.0)."""
        andromeda = TestFixtures.andromeda()
        orion = TestFixtures.orion_nebula()

        andromeda_score = self.service.score_celestial_object(
            andromeda, self.medium_scope, self.medium_eyepiece, self.dark_site)
        orion_score = self.service.score_celestial_object(
            orion, self.medium_scope, self.medium_eyepiece, self.dark_site)

        assert_that(andromeda_score.observability_score.normalized_score).is_greater_than(
            orion_score.observability_score.normalized_score)

    def test_orion_nebula_beats_veil_nebula(self):
        """Orion Nebula (mag 4.0) should beat Veil Nebula (mag 7.0)."""
        orion = TestFixtures.orion_nebula()
        veil = TestFixtures.veil_nebula()

        orion_score = self.service.score_celestial_object(
            orion, self.medium_scope, self.medium_eyepiece, self.dark_site)
        veil_score = self.service.score_celestial_object(
            veil, self.medium_scope, self.medium_eyepiece, self.dark_site)

        assert_that(orion_score.observability_score.normalized_score).is_greater_than(
            veil_score.observability_score.normalized_score)

    def test_dumbbell_beats_ring_nebula(self):
        """Dumbbell (mag 7.5) should beat Ring Nebula (mag 8.8)."""
        dumbbell = TestFixtures.dumbbell_nebula()
        ring = TestFixtures.ring_nebula()

        dumbbell_score = self.service.score_celestial_object(
            dumbbell, self.medium_scope, self.medium_eyepiece, self.dark_site)
        ring_score = self.service.score_celestial_object(
            ring, self.medium_scope, self.medium_eyepiece, self.dark_site)

        assert_that(dumbbell_score.observability_score.normalized_score).is_greater_than(
            ring_score.observability_score.normalized_score)

    def test_whirlpool_beats_ic_1396(self):
        """Whirlpool (mag 8.4) should beat IC 1396 (mag 9.5)."""
        whirlpool = TestFixtures.whirlpool()
        ic = TestFixtures.ic_1396()

        whirlpool_score = self.service.score_celestial_object(
            whirlpool, self.medium_scope, self.medium_eyepiece, self.dark_site)
        ic_score = self.service.score_celestial_object(
            ic, self.medium_scope, self.medium_eyepiece, self.dark_site)

        assert_that(whirlpool_score.observability_score.normalized_score).is_greater_than(
            ic_score.observability_score.normalized_score)

    def test_ic_1396_beats_horsehead(self):
        """IC 1396 (mag 9.5) should beat Horsehead (mag 10.0)."""
        ic = TestFixtures.ic_1396()
        horsehead = TestFixtures.horsehead()

        ic_score = self.service.score_celestial_object(
            ic, self.medium_scope, self.medium_eyepiece, self.dark_site)
        horsehead_score = self.service.score_celestial_object(
            horsehead, self.medium_scope, self.medium_eyepiece, self.dark_site)

        assert_that(ic_score.observability_score.normalized_score).is_greater_than(
            horsehead_score.observability_score.normalized_score)


# =============================================================================
# APERTURE IMPACT TESTS (Pairwise)
# =============================================================================

class TestApertureImpactOnFaintObjects(unittest.TestCase):
    """Large aperture should dramatically improve faint object scores."""

    def setUp(self):
        self.service = ObservabilityCalculationService()
        self.small_scope = TestFixtures.small_refractor()
        self.large_scope = TestFixtures.large_dobsonian()
        self.medium_eyepiece = TestFixtures.medium_eyepiece()
        self.dark_site = TestFixtures.dark_site()

    def test_aperture_helps_horsehead(self):
        """Horsehead (mag 10) should score much higher with large aperture."""
        horsehead = TestFixtures.horsehead()

        small_score = self.service.score_celestial_object(
            horsehead, self.small_scope, self.medium_eyepiece, self.dark_site)
        large_score = self.service.score_celestial_object(
            horsehead, self.large_scope, self.medium_eyepiece, self.dark_site)

        # Large aperture should be 2x+ better for very faint object
        assert_that(large_score.observability_score.score).is_greater_than(
            small_score.observability_score.score * 2.0)

    def test_aperture_helps_ring_nebula(self):
        """Ring Nebula (mag 8.8) should score higher with large aperture."""
        ring = TestFixtures.ring_nebula()

        small_score = self.service.score_celestial_object(
            ring, self.small_scope, self.medium_eyepiece, self.dark_site)
        large_score = self.service.score_celestial_object(
            ring, self.large_scope, self.medium_eyepiece, self.dark_site)

        assert_that(large_score.observability_score.score).is_greater_than(
            small_score.observability_score.score)

    def test_aperture_helps_whirlpool(self):
        """Whirlpool Galaxy should benefit from large aperture."""
        whirlpool = TestFixtures.whirlpool()

        small_score = self.service.score_celestial_object(
            whirlpool, self.small_scope, self.medium_eyepiece, self.dark_site)
        large_score = self.service.score_celestial_object(
            whirlpool, self.large_scope, self.medium_eyepiece, self.dark_site)

        assert_that(large_score.observability_score.score).is_greater_than(
            small_score.observability_score.score * 1.5)

    def test_aperture_minor_impact_on_jupiter(self):
        """Jupiter should only slightly benefit from aperture (already bright)."""
        jupiter = TestFixtures.jupiter()

        small_score = self.service.score_celestial_object(
            jupiter, self.small_scope, self.medium_eyepiece, self.dark_site)
        large_score = self.service.score_celestial_object(
            jupiter, self.large_scope, self.medium_eyepiece, self.dark_site)

        # Should improve, but not dramatically (already very bright)
        ratio = large_score.observability_score.score / small_score.observability_score.score
        assert_that(ratio).is_less_than(1.5)  # Less than 50% improvement

    def test_aperture_minor_impact_on_moon(self):
        """Moon should barely benefit from aperture."""
        moon = TestFixtures.moon()

        small_score = self.service.score_celestial_object(
            moon, self.small_scope, self.medium_eyepiece, self.dark_site)
        large_score = self.service.score_celestial_object(
            moon, self.large_scope, self.medium_eyepiece, self.dark_site)

        # Moon so bright that aperture barely matters
        ratio = large_score.observability_score.score / small_score.observability_score.score
        assert_that(ratio).is_less_than(1.3)  # Less than 30% improvement


# =============================================================================
# MAGNIFICATION IMPACT TESTS (Pairwise)
# =============================================================================

class TestMagnificationImpactOnPlanets(unittest.TestCase):
    """Planets should benefit from higher magnification in optimal range."""

    def setUp(self):
        self.service = ObservabilityCalculationService()
        self.medium_scope = TestFixtures.medium_dobsonian()
        self.dark_site = TestFixtures.dark_site()

    def test_jupiter_prefers_medium_magnification_over_low(self):
        """Jupiter should score better with medium magnification than low."""
        jupiter = TestFixtures.jupiter()

        wide_eyepiece = TestFixtures.wide_eyepiece()  # 1200/25 = 48x
        medium_eyepiece = TestFixtures.medium_eyepiece()  # 1200/10 = 120x

        low_mag_score = self.service.score_celestial_object(
            jupiter, self.medium_scope, wide_eyepiece, self.dark_site)
        medium_mag_score = self.service.score_celestial_object(
            jupiter, self.medium_scope, medium_eyepiece, self.dark_site)

        assert_that(medium_mag_score.observability_score.score).is_greater_than(
            low_mag_score.observability_score.score)

    def test_saturn_prefers_high_magnification(self):
        """Saturn should score better with higher magnification."""
        saturn = TestFixtures.saturn()

        medium_eyepiece = TestFixtures.medium_eyepiece()  # 1200/10 = 120x
        planetary_eyepiece = TestFixtures.planetary_eyepiece()  # 1200/5 = 240x

        medium_mag_score = self.service.score_celestial_object(
            saturn, self.medium_scope, medium_eyepiece, self.dark_site)
        high_mag_score = self.service.score_celestial_object(
            saturn, self.medium_scope, planetary_eyepiece, self.dark_site)

        assert_that(high_mag_score.observability_score.score).is_greater_than(
            medium_mag_score.observability_score.score)


class TestMagnificationImpactOnLargeObjects(unittest.TestCase):
    """Large extended objects should prefer low magnification."""

    def setUp(self):
        self.service = ObservabilityCalculationService()
        self.large_scope = TestFixtures.large_dobsonian()
        self.dark_site = TestFixtures.dark_site()

    def test_andromeda_prefers_low_magnification(self):
        """Andromeda (190 arcmin) should prefer low magnification."""
        andromeda = TestFixtures.andromeda()

        widefield_eyepiece = TestFixtures.widefield_eyepiece()  # 1800/30 = 60x
        planetary_eyepiece = TestFixtures.planetary_eyepiece()  # 1800/5 = 360x

        low_mag_score = self.service.score_celestial_object(
            andromeda, self.large_scope, widefield_eyepiece, self.dark_site)
        high_mag_score = self.service.score_celestial_object(
            andromeda, self.large_scope, planetary_eyepiece, self.dark_site)

        assert_that(low_mag_score.observability_score.score).is_greater_than(
            high_mag_score.observability_score.score)

    def test_pleiades_prefers_low_magnification(self):
        """Pleiades (110 arcmin) should prefer very low magnification."""
        pleiades = TestFixtures.pleiades()

        widefield_eyepiece = TestFixtures.widefield_eyepiece()  # 60x
        medium_eyepiece = TestFixtures.medium_eyepiece()  # 180x

        low_mag_score = self.service.score_celestial_object(
            pleiades, self.large_scope, widefield_eyepiece, self.dark_site)
        medium_mag_score = self.service.score_celestial_object(
            pleiades, self.large_scope, medium_eyepiece, self.dark_site)

        assert_that(low_mag_score.observability_score.score).is_greater_than(
            medium_mag_score.observability_score.score)

    def test_veil_nebula_prefers_low_magnification(self):
        """Veil Nebula (180 arcmin) should prefer low magnification."""
        veil = TestFixtures.veil_nebula()

        widefield_eyepiece = TestFixtures.widefield_eyepiece()  # 60x
        planetary_eyepiece = TestFixtures.planetary_eyepiece()  # 360x

        low_mag_score = self.service.score_celestial_object(
            veil, self.large_scope, widefield_eyepiece, self.dark_site)
        high_mag_score = self.service.score_celestial_object(
            veil, self.large_scope, planetary_eyepiece, self.dark_site)

        assert_that(low_mag_score.observability_score.score).is_greater_than(
            high_mag_score.observability_score.score)


# =============================================================================
# LIGHT POLLUTION IMPACT TESTS (Pairwise)
# =============================================================================

class TestLightPollutionImpactOnPlanets(unittest.TestCase):
    """Planets should be minimally affected by light pollution."""

    def setUp(self):
        self.service = ObservabilityCalculationService()
        self.medium_scope = TestFixtures.medium_dobsonian()
        self.medium_eyepiece = TestFixtures.medium_eyepiece()
        self.dark_site = TestFixtures.dark_site()
        self.city_site = TestFixtures.city_site()

    def test_jupiter_resilient_to_light_pollution(self):
        """Jupiter should be 90%+ visible even in city."""
        jupiter = TestFixtures.jupiter()

        dark_score = self.service.score_celestial_object(
            jupiter, self.medium_scope, self.medium_eyepiece, self.dark_site)
        city_score = self.service.score_celestial_object(
            jupiter, self.medium_scope, self.medium_eyepiece, self.city_site)

        ratio = city_score.observability_score.score / dark_score.observability_score.score
        assert_that(ratio).is_greater_than(0.90)

    def test_saturn_resilient_to_light_pollution(self):
        """Saturn should remain visible in city."""
        saturn = TestFixtures.saturn()

        dark_score = self.service.score_celestial_object(
            saturn, self.medium_scope, self.medium_eyepiece, self.dark_site)
        city_score = self.service.score_celestial_object(
            saturn, self.medium_scope, self.medium_eyepiece, self.city_site)

        ratio = city_score.observability_score.score / dark_score.observability_score.score
        assert_that(ratio).is_greater_than(0.85)

    def test_moon_unaffected_by_light_pollution(self):
        """Moon should be essentially unaffected by light pollution."""
        moon = TestFixtures.moon()

        dark_score = self.service.score_celestial_object(
            moon, self.medium_scope, self.medium_eyepiece, self.dark_site)
        city_score = self.service.score_celestial_object(
            moon, self.medium_scope, self.medium_eyepiece, self.city_site)

        ratio = city_score.observability_score.score / dark_score.observability_score.score
        assert_that(ratio).is_greater_than(0.95)


class TestLightPollutionImpactOnDeepSky(unittest.TestCase):
    """Deep-sky objects should be severely affected by light pollution."""

    def setUp(self):
        self.service = ObservabilityCalculationService()
        self.large_scope = TestFixtures.large_dobsonian()
        self.medium_eyepiece = TestFixtures.medium_eyepiece()
        self.dark_site = TestFixtures.dark_site()
        self.suburban_site = TestFixtures.suburban_site()
        self.city_site = TestFixtures.city_site()

    def test_horsehead_devastated_by_city_light(self):
        """Horsehead (very faint) should lose 70%+ in city."""
        horsehead = TestFixtures.horsehead()

        dark_score = self.service.score_celestial_object(
            horsehead, self.large_scope, self.medium_eyepiece, self.dark_site)
        city_score = self.service.score_celestial_object(
            horsehead, self.large_scope, self.medium_eyepiece, self.city_site)

        ratio = city_score.observability_score.score / dark_score.observability_score.score
        assert_that(ratio).is_less_than(0.30)

    def test_ring_nebula_hurt_by_city_light(self):
        """Ring Nebula should lose 50%+ score in city."""
        ring = TestFixtures.ring_nebula()

        dark_score = self.service.score_celestial_object(
            ring, self.large_scope, self.medium_eyepiece, self.dark_site)
        city_score = self.service.score_celestial_object(
            ring, self.large_scope, self.medium_eyepiece, self.city_site)

        ratio = city_score.observability_score.score / dark_score.observability_score.score
        assert_that(ratio).is_less_than(0.50)

    def test_andromeda_hurt_by_suburbs(self):
        """Andromeda should lose 30-50% in suburbs."""
        andromeda = TestFixtures.andromeda()

        dark_score = self.service.score_celestial_object(
            andromeda, self.large_scope, self.medium_eyepiece, self.dark_site)
        suburban_score = self.service.score_celestial_object(
            andromeda, self.large_scope, self.medium_eyepiece, self.suburban_site)

        ratio = suburban_score.observability_score.score / dark_score.observability_score.score
        assert_that(ratio).is_between(0.50, 0.70)

    def test_orion_nebula_moderately_affected(self):
        """Orion Nebula (bright DSO) should be moderately affected."""
        orion = TestFixtures.orion_nebula()

        dark_score = self.service.score_celestial_object(
            orion, self.large_scope, self.medium_eyepiece, self.dark_site)
        suburban_score = self.service.score_celestial_object(
            orion, self.large_scope, self.medium_eyepiece, self.suburban_site)

        ratio = suburban_score.observability_score.score / dark_score.observability_score.score
        assert_that(ratio).is_between(0.60, 0.85)


class TestLightPollutionGradient(unittest.TestCase):
    """Scores should decrease monotonically with worsening light pollution."""

    def setUp(self):
        self.service = ObservabilityCalculationService()
        self.medium_scope = TestFixtures.medium_dobsonian()
        self.medium_eyepiece = TestFixtures.medium_eyepiece()
        self.dark_site = TestFixtures.dark_site()
        self.suburban_site = TestFixtures.suburban_site()
        self.city_site = TestFixtures.city_site()

    def test_orion_nebula_gradient(self):
        """Orion Nebula: dark > suburban > city."""
        orion = TestFixtures.orion_nebula()

        dark_score = self.service.score_celestial_object(
            orion, self.medium_scope, self.medium_eyepiece, self.dark_site)
        suburban_score = self.service.score_celestial_object(
            orion, self.medium_scope, self.medium_eyepiece, self.suburban_site)
        city_score = self.service.score_celestial_object(
            orion, self.medium_scope, self.medium_eyepiece, self.city_site)

        assert_that(dark_score.observability_score.score).is_greater_than(
            suburban_score.observability_score.score)
        assert_that(suburban_score.observability_score.score).is_greater_than(
            city_score.observability_score.score)

    def test_whirlpool_gradient(self):
        """Whirlpool Galaxy: dark > suburban > city."""
        whirlpool = TestFixtures.whirlpool()

        dark_score = self.service.score_celestial_object(
            whirlpool, self.medium_scope, self.medium_eyepiece, self.dark_site)
        suburban_score = self.service.score_celestial_object(
            whirlpool, self.medium_scope, self.medium_eyepiece, self.suburban_site)
        city_score = self.service.score_celestial_object(
            whirlpool, self.medium_scope, self.medium_eyepiece, self.city_site)

        assert_that(dark_score.observability_score.score).is_greater_than(
            suburban_score.observability_score.score)
        assert_that(suburban_score.observability_score.score).is_greater_than(
            city_score.observability_score.score)


# =============================================================================
# ALTITUDE IMPACT TESTS (Pairwise)
# =============================================================================

class TestAltitudeImpact(unittest.TestCase):
    """Objects at higher altitudes should score better."""

    def setUp(self):
        self.service = ObservabilityCalculationService()
        self.medium_scope = TestFixtures.medium_dobsonian()
        self.medium_eyepiece = TestFixtures.medium_eyepiece()
        self.dark_site = TestFixtures.dark_site()

    def test_jupiter_high_beats_low(self):
        """Jupiter at 70° should beat Jupiter at 15°."""
        jupiter_high = CelestialObject('Jupiter High', 'Planet', -2.40, 0.77, 70.00)
        jupiter_low = CelestialObject('Jupiter Low', 'Planet', -2.40, 0.77, 15.00)

        high_score = self.service.score_celestial_object(
            jupiter_high, self.medium_scope, self.medium_eyepiece, self.dark_site)
        low_score = self.service.score_celestial_object(
            jupiter_low, self.medium_scope, self.medium_eyepiece, self.dark_site)

        assert_that(high_score.observability_score.score).is_greater_than(
            low_score.observability_score.score * 1.3)  # At least 30% better

    def test_andromeda_high_beats_low(self):
        """Andromeda at 60° should beat Andromeda at 20°."""
        andromeda_high = CelestialObject('Andromeda High', 'DeepSky', 3.44, 190.00, 60.00)
        andromeda_low = CelestialObject('Andromeda Low', 'DeepSky', 3.44, 190.00, 20.00)

        high_score = self.service.score_celestial_object(
            andromeda_high, self.medium_scope, self.medium_eyepiece, self.dark_site)
        low_score = self.service.score_celestial_object(
            andromeda_low, self.medium_scope, self.medium_eyepiece, self.dark_site)

        assert_that(high_score.observability_score.score).is_greater_than(
            low_score.observability_score.score)

    def test_below_horizon_is_zero(self):
        """Objects below horizon should score zero."""
        below_horizon = CelestialObject('Below', 'Planet', -2.0, 0.5, -10.00)

        score = self.service.score_celestial_object(
            below_horizon, self.medium_scope, self.medium_eyepiece, self.dark_site)

        assert_that(score.observability_score.score).is_equal_to(0.0)

    def test_moon_high_beats_low(self):
        """Moon at 80° should beat Moon at 10°."""
        moon_high = CelestialObject('Moon High', 'Moon', -12.60, 31.00, 80.00)
        moon_low = CelestialObject('Moon Low', 'Moon', -12.60, 31.00, 10.00)

        high_score = self.service.score_celestial_object(
            moon_high, self.medium_scope, self.medium_eyepiece, self.dark_site)
        low_score = self.service.score_celestial_object(
            moon_low, self.medium_scope, self.medium_eyepiece, self.dark_site)

        assert_that(high_score.observability_score.score).is_greater_than(
            low_score.observability_score.score)


# =============================================================================
# NO EQUIPMENT PENALTY TESTS
# =============================================================================

class TestNoEquipmentPenalty(unittest.TestCase):
    """Observing without equipment should severely penalize faint objects."""

    def setUp(self):
        self.service = ObservabilityCalculationService()
        self.medium_scope = TestFixtures.medium_dobsonian()
        self.medium_eyepiece = TestFixtures.medium_eyepiece()
        self.dark_site = TestFixtures.dark_site()

    def test_horsehead_needs_equipment(self):
        """Horsehead should score < 30% without equipment."""
        horsehead = TestFixtures.horsehead()

        with_equipment = self.service.score_celestial_object(
            horsehead, self.medium_scope, self.medium_eyepiece, self.dark_site)
        no_equipment = self.service.score_celestial_object(
            horsehead, None, None, self.dark_site)

        ratio = no_equipment.observability_score.score / with_equipment.observability_score.score
        assert_that(ratio).is_less_than(0.30)

    def test_ring_nebula_needs_equipment(self):
        """Ring Nebula should score much lower without equipment."""
        ring = TestFixtures.ring_nebula()

        with_equipment = self.service.score_celestial_object(
            ring, self.medium_scope, self.medium_eyepiece, self.dark_site)
        no_equipment = self.service.score_celestial_object(
            ring, None, None, self.dark_site)

        ratio = no_equipment.observability_score.score / with_equipment.observability_score.score
        assert_that(ratio).is_less_than(0.40)

    def test_jupiter_okay_without_equipment(self):
        """Jupiter should still be visible naked eye (> 70% score)."""
        jupiter = TestFixtures.jupiter()

        with_equipment = self.service.score_celestial_object(
            jupiter, self.medium_scope, self.medium_eyepiece, self.dark_site)
        no_equipment = self.service.score_celestial_object(
            jupiter, None, None, self.dark_site)

        ratio = no_equipment.observability_score.score / with_equipment.observability_score.score
        assert_that(ratio).is_greater_than(0.70)

    def test_moon_excellent_without_equipment(self):
        """Moon should be 90%+ visible naked eye."""
        moon = TestFixtures.moon()

        with_equipment = self.service.score_celestial_object(
            moon, self.medium_scope, self.medium_eyepiece, self.dark_site)
        no_equipment = self.service.score_celestial_object(
            moon, None, None, self.dark_site)

        ratio = no_equipment.observability_score.score / with_equipment.observability_score.score
        assert_that(ratio).is_greater_than(0.90)

    def test_sirius_visible_naked_eye(self):
        """Sirius should be 80%+ visible naked eye."""
        sirius = TestFixtures.sirius()

        with_equipment = self.service.score_celestial_object(
            sirius, self.medium_scope, self.medium_eyepiece, self.dark_site)
        no_equipment = self.service.score_celestial_object(
            sirius, None, None, self.dark_site)

        ratio = no_equipment.observability_score.score / with_equipment.observability_score.score
        assert_that(ratio).is_greater_than(0.80)


# =============================================================================
# COMPREHENSIVE SANITY TESTS
# =============================================================================

class TestComprehensiveSanityChecks(unittest.TestCase):
    """High-level sanity tests to catch major logic errors."""

    def setUp(self):
        self.service = ObservabilityCalculationService()
        self.medium_scope = TestFixtures.medium_dobsonian()
        self.medium_eyepiece = TestFixtures.medium_eyepiece()
        self.dark_site = TestFixtures.dark_site()

    def test_sun_always_highest(self):
        """Sun should rank highest among all objects."""
        objects = [
            TestFixtures.sun(),
            TestFixtures.moon(),
            TestFixtures.jupiter(),
            TestFixtures.sirius(),
            TestFixtures.orion_nebula()
        ]

        scores = [self.service.score_celestial_object(obj, self.medium_scope, self.medium_eyepiece, self.dark_site)
                  for obj in objects]
        scores.sort(key=lambda s: s.observability_score.normalized_score, reverse=True)

        assert_that(scores[0].name).is_equal_to('Sun')

    def test_positive_scores(self):
        """All visible objects should have positive scores."""
        objects = [
            TestFixtures.moon(),
            TestFixtures.jupiter(),
            TestFixtures.saturn(),
            TestFixtures.orion_nebula(),
            TestFixtures.horsehead()
        ]

        for obj in objects:
            score = self.service.score_celestial_object(
                obj, self.medium_scope, self.medium_eyepiece, self.dark_site)
            assert_that(score.observability_score.score).is_greater_than(0.0)

    def test_brighter_always_better(self):
        """For same object type/size, brighter magnitude should always win."""
        bright_dso = CelestialObject('Bright', 'DeepSky', 5.0, 10.0, 50.0)
        faint_dso = CelestialObject('Faint', 'DeepSky', 9.0, 10.0, 50.0)

        bright_score = self.service.score_celestial_object(
            bright_dso, self.medium_scope, self.medium_eyepiece, self.dark_site)
        faint_score = self.service.score_celestial_object(
            faint_dso, self.medium_scope, self.medium_eyepiece, self.dark_site)

        assert_that(bright_score.observability_score.score).is_greater_than(
            faint_score.observability_score.score)


if __name__ == '__main__':
    unittest.main()
