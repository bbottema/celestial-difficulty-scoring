"""
Benchmark validation tests for Phase 5 limiting magnitude model.

These tests use real-world astronomical objects with actual catalog data
to validate that the scoring model produces realistic results across different
observing conditions (Bortle scales, apertures).

Data sources: Wikipedia, In-The-Sky.org, NASA/IPAC, SIMBAD
All coordinates are J2000 epoch in decimal degrees.

Note: CelestialObject in this codebase only has name, type, magnitude, size, altitude.
The RA/Dec data is preserved in comments for reference but not used in testing.
"""

import unittest
from assertpy import assert_that

from app.domain.model.celestial_object import CelestialObject
from app.domain.services.strategies.deep_sky_strategy import DeepSkyScoringStrategy
from app.domain.services.strategies.large_faint_object_strategy import LargeFaintObjectScoringStrategy
from app.orm.model.entities import Telescope, Eyepiece, ObservationSite
from app.domain.model.light_pollution import LightPollution
from app.domain.model.telescope_type import TelescopeType
from app.domain.model.scoring_context import ScoringContext


# ------------------------------------------------------------
# Real-world benchmark objects with catalog data
# Format: (name, magnitude, size_arcmin)
# Data sources: Wikipedia, In-The-Sky.org, NASA/IPAC, SIMBAD
# ------------------------------------------------------------

EASY_TIER = [
    ("M31 - Andromeda Galaxy", 3.44, 190.0, 10.6846, 41.2692),
    ("M42 - Orion Nebula", 4.00, 65.0, 83.7500, -5.3833),
    ("M45 - Pleiades", 1.6, 110.0, 56.8500, 24.1167),
    ("M13 - Hercules Globular Cluster", 5.80, 16.5, 250.2500, 36.4667),
]

MODERATE_TIER = [
    ("M51 - Whirlpool Galaxy", 8.40, 11.0, 202.2500, 47.1833),
    ("M33 - Triangulum Galaxy", 5.72, 73.0, 23.4584, 30.6602),
    ("M27 - Dumbbell Nebula", 7.4, 8.0, 299.9014, 22.7211),
    ("M57 - Ring Nebula", 8.8, 3.8, 283.3962, 33.0291),
]

CHALLENGING_TIER = [
    ("NGC 7000 - North America Nebula", 4.0, 120.0, 314.8213, 44.5289),
    ("IC 1396 - Elephant Trunk Region", 5.05, 14.0, 324.2500, 57.5000),
    ("Veil Nebula Complex (NGC 6960/6992)", 7.0, 180.0, 311.4083, 30.7317),
    ("NGC 1499 - California Nebula", 6.0, 150.0, 60.2917, 36.4600),
]

SANITY_TIER_COMPACT = [
    # Planetary nebulae (high surface brightness, tiny)
    ("NGC 7027 - Planetary Nebula", 8.50, 0.2, 316.7500, 42.2333),
    ("NGC 6572 - Planetary Nebula", 8.10, 0.2, 273.0000, 6.8500),
    ("IC 418 - Planetary Nebula", 9.44, 0.2, 81.7500, -12.6833),
    ("NGC 3242 - Ghost of Jupiter", 8.60, 0.4, 156.0000, -18.6333),
    # Compact galaxies
    ("M32 - Compact Elliptical Galaxy", 8.08, 8.7, 10.6742, 40.8653),
    ("M87 - Virgo A (Elliptical)", 8.6, 7.2, 187.7058, 12.3911),
    ("NGC 3115 - Spindle Galaxy", 9.10, 7.1, 151.2500, -7.7167),
    ("NGC 404 - Mirach's Ghost", 11.19, 3.6, 17.2500, 35.7167),
]


class TestEasyTierBenchmarks(unittest.TestCase):
    """
    Easy tier objects (M31, M42, M45, M13) should be:
    - Visible in moderate light pollution (Bortle 5-6) with small apertures
    - Excellent in dark skies (Bortle 3) with medium apertures
    """

    def test_m31_visible_in_bortle_5_with_small_scope(self):
        """M31 (mag 3.44, 190') should be visible in Bortle 5 with 80mm scope"""
        name, mag, size, ra, dec = EASY_TIER[0]  # M31
        m31 = create_object(name, mag, size, altitude=50.0, ra=ra, dec=dec)

        telescope = create_telescope(80, "Small Refractor")
        eyepiece = create_eyepiece(10)
        site = create_site(LightPollution.BORTLE_5, "Suburban Site")

        context = ScoringContext(
            telescope=telescope,
            eyepiece=eyepiece,
            observation_site=site,
            altitude=50.0
        )

        # M31 is huge and bright - should be visible even in moderate LP
        strategy = LargeFaintObjectScoringStrategy()
        factor = strategy._calculate_site_factor(m31, context)

        assert_that(factor).is_greater_than(0.5).described_as(
            f"M31 should be visible (>0.5) in Bortle 5 with 80mm, got {factor:.3f}"
        )

    def test_m42_excellent_in_bortle_3_with_medium_scope(self):
        """M42 (mag 4.0, 65') should score excellent in Bortle 3 with 200mm"""
        name, mag, size, ra, dec = EASY_TIER[1]  # M42
        m42 = create_object(name, mag, size, altitude=50.0, ra=ra, dec=dec)

        telescope = create_telescope(200, "Medium Dobsonian")
        eyepiece = create_eyepiece(10)
        site = create_site(LightPollution.BORTLE_3, "Dark Site")

        context = ScoringContext(
            telescope=telescope,
            eyepiece=eyepiece,
            observation_site=site,
            altitude=50.0
        )

        strategy = LargeFaintObjectScoringStrategy()
        factor = strategy._calculate_site_factor(m42, context)

        assert_that(factor).is_greater_than(0.80).described_as(
            f"M42 should score excellent (>0.80) in Bortle 3 with 200mm, got {factor:.3f}"
        )

    def test_m13_visible_in_bortle_6_with_medium_scope(self):
        """M13 (mag 5.8, 16.5') should be visible in Bortle 6 with 200mm"""
        name, mag, size, ra, dec = EASY_TIER[3]  # M13
        m13 = create_object(name, mag, size, altitude=50.0, ra=ra, dec=dec)

        telescope = create_telescope(200, "Medium Dobsonian")
        eyepiece = create_eyepiece(10)
        site = create_site(LightPollution.BORTLE_6, "Rural/Suburban")

        context = ScoringContext(
            telescope=telescope,
            eyepiece=eyepiece,
            observation_site=site,
            altitude=50.0
        )

        # M13 is compact with high surface brightness
        strategy = DeepSkyScoringStrategy()
        factor = strategy._calculate_site_factor(m13, context)

        assert_that(factor).is_greater_than(0.4).described_as(
            f"M13 should be visible (>0.4) in Bortle 6 with 200mm, got {factor:.3f}"
        )


class TestModerateTierBenchmarks(unittest.TestCase):
    """
    Moderate tier objects (M51, M33, M27, M57) should be:
    - Marginal/invisible in Bortle 6+ regardless of aperture
    - Good/visible in Bortle 4-5 with medium apertures
    - Excellent in Bortle 3 with large apertures
    """

    def test_m51_invisible_in_bortle_7(self):
        """M51 (mag 8.4, 11') should be invisible/marginal in Bortle 7"""
        name, mag, size, ra, dec = MODERATE_TIER[0]  # M51
        m51 = create_object(name, mag, size, altitude=50.0, ra=ra, dec=dec)

        telescope = create_telescope(200, "Medium Dobsonian")
        eyepiece = create_eyepiece(10)
        site = create_site(LightPollution.BORTLE_7, "Suburban/Urban")

        context = ScoringContext(
            telescope=telescope,
            eyepiece=eyepiece,
            observation_site=site,
            altitude=50.0
        )

        strategy = DeepSkyScoringStrategy()
        factor = strategy._calculate_site_factor(m51, context)

        assert_that(factor).is_less_than(0.3).described_as(
            f"M51 should be invisible/marginal (<0.3) in Bortle 7, got {factor:.3f}"
        )

    def test_m33_challenging_in_bortle_5(self):
        """M33 (mag 5.72, 73') has very low surface brightness - challenging even in Bortle 5"""
        name, mag, size, ra, dec = MODERATE_TIER[1]  # M33
        m33 = create_object(name, mag, size, altitude=50.0, ra=ra, dec=dec)

        telescope = create_telescope(200, "Medium Dobsonian")
        eyepiece = create_eyepiece(10)
        site = create_site(LightPollution.BORTLE_5, "Rural Site")

        context = ScoringContext(
            telescope=telescope,
            eyepiece=eyepiece,
            observation_site=site,
            altitude=50.0
        )

        # M33 is large and faint - needs dark skies
        strategy = LargeFaintObjectScoringStrategy()
        factor = strategy._calculate_site_factor(m33, context)

        # Should be visible but not excellent
        assert_that(factor).is_between(0.3, 0.7).described_as(
            f"M33 should be marginal/moderate (0.3-0.7) in Bortle 5, got {factor:.3f}"
        )

    def test_m27_good_in_bortle_4_with_large_scope(self):
        """M27 (mag 7.4, 8') should be good in Bortle 4 with large aperture"""
        name, mag, size, ra, dec = MODERATE_TIER[2]  # M27
        m27 = create_object(name, mag, size, altitude=50.0, ra=ra, dec=dec)

        telescope = create_telescope(300, "Large Dobsonian")
        eyepiece = create_eyepiece(10)
        site = create_site(LightPollution.BORTLE_4, "Rural Dark Site")

        context = ScoringContext(
            telescope=telescope,
            eyepiece=eyepiece,
            observation_site=site,
            altitude=50.0
        )

        strategy = DeepSkyScoringStrategy()
        factor = strategy._calculate_site_factor(m27, context)

        assert_that(factor).is_greater_than(0.6).described_as(
            f"M27 should be good (>0.6) in Bortle 4 with 300mm, got {factor:.3f}"
        )


class TestChallengingTierBenchmarks(unittest.TestCase):
    """
    Challenging tier objects (NGC 7000, IC 1396, Veil, California) should be:
    - Invisible in Bortle 5+ regardless of aperture
    - Marginal/visible in Bortle 4 with large apertures
    - Good in Bortle 3 with large apertures and filters (filter impact not modeled yet)
    """

    def test_north_america_nebula_invisible_in_bortle_5(self):
        """NGC 7000 (mag 4.0, 120') has extremely low surface brightness"""
        name, mag, size, ra, dec = CHALLENGING_TIER[0]  # NGC 7000
        ngc7000 = create_object(name, mag, size, altitude=50.0, ra=ra, dec=dec)

        telescope = create_telescope(300, "Large Dobsonian")
        eyepiece = create_eyepiece(10)
        site = create_site(LightPollution.BORTLE_5, "Rural Site")

        context = ScoringContext(
            telescope=telescope,
            eyepiece=eyepiece,
            observation_site=site,
            altitude=50.0
        )

        strategy = LargeFaintObjectScoringStrategy()
        factor = strategy._calculate_site_factor(ngc7000, context)

        assert_that(factor).is_less_than(0.4).described_as(
            f"NGC 7000 should be invisible/marginal (<0.4) in Bortle 5, got {factor:.3f}"
        )

    def test_veil_nebula_needs_dark_skies(self):
        """Veil Nebula (mag 7.0, 180') needs Bortle 3 to be visible"""
        name, mag, size, ra, dec = CHALLENGING_TIER[2]  # Veil
        veil = create_object(name, mag, size, altitude=50.0, ra=ra, dec=dec)

        telescope = create_telescope(300, "Large Dobsonian")
        eyepiece = create_eyepiece(10)
        site_dark = create_site(LightPollution.BORTLE_3, "Dark Site")
        site_rural = create_site(LightPollution.BORTLE_5, "Rural Site")

        context_dark = ScoringContext(
            telescope=telescope,
            eyepiece=eyepiece,
            observation_site=site_dark,
            altitude=50.0
        )
        context_rural = ScoringContext(
            telescope=telescope,
            eyepiece=eyepiece,
            observation_site=site_rural,
            altitude=50.0
        )

        strategy = LargeFaintObjectScoringStrategy()
        factor_dark = strategy._calculate_site_factor(veil, context_dark)
        factor_rural = strategy._calculate_site_factor(veil, context_rural)

        # Should be significantly better in dark skies
        assert_that(factor_dark).is_greater_than(factor_rural * 1.5).described_as(
            f"Veil should be much better in Bortle 3 ({factor_dark:.3f}) vs Bortle 5 ({factor_rural:.3f})"
        )
        assert_that(factor_dark).is_greater_than(0.5).described_as(
            f"Veil should be visible (>0.5) in Bortle 3, got {factor_dark:.3f}"
        )

    def test_california_nebula_requires_excellent_conditions(self):
        """California Nebula (mag 6.0, 150') is extremely challenging"""
        name, mag, size, ra, dec = CHALLENGING_TIER[3]  # California
        california = create_object(name, mag, size, altitude=50.0, ra=ra, dec=dec)

        telescope = create_telescope(300, "Large Dobsonian")
        eyepiece = create_eyepiece(10)
        site = create_site(LightPollution.BORTLE_3, "Dark Site")

        context = ScoringContext(
            telescope=telescope,
            eyepiece=eyepiece,
            observation_site=site,
            altitude=50.0
        )

        strategy = LargeFaintObjectScoringStrategy()
        factor = strategy._calculate_site_factor(california, context)

        # Should be visible but not excellent even in Bortle 3
        assert_that(factor).is_between(0.4, 0.8).described_as(
            f"California Nebula should be challenging (0.4-0.8) even in Bortle 3, got {factor:.3f}"
        )


class TestCompactHighSurfaceBrightness(unittest.TestCase):
    """
    Planetary nebulae (NGC 7027, NGC 6572, IC 418, NGC 3242) should be:
    - Much easier than extended objects at the same magnitude
    - Visible in moderate light pollution with medium apertures

    CAVEAT: Current model doesn't differentiate by object type, so these
    may be slightly over-penalized due to generic "DeepSky" classification.
    This is a known limitation documented in Phase 5 and addressed in Phase 7.
    """

    def test_planetary_nebula_easier_than_galaxy_same_magnitude(self):
        """NGC 6572 (mag 8.1, 0.2') should be easier than M51 (mag 8.4, 11') despite similar magnitude"""
        pn_name, pn_mag, pn_size, pn_ra, pn_dec = SANITY_TIER_COMPACT[1]  # NGC 6572
        galaxy_name, galaxy_mag, galaxy_size, galaxy_ra, galaxy_dec = MODERATE_TIER[0]  # M51

        pn = create_object(pn_name, pn_mag, pn_size, altitude=50.0, ra=pn_ra, dec=pn_dec)
        galaxy = create_object(galaxy_name, galaxy_mag, galaxy_size, altitude=50.0, ra=galaxy_ra, dec=galaxy_dec)

        telescope = create_telescope(200, "Medium Dobsonian")
        eyepiece = create_eyepiece(10)
        site = create_site(LightPollution.BORTLE_5, "Rural Site")

        context = ScoringContext(
            telescope=telescope,
            eyepiece=eyepiece,
            observation_site=site,
            altitude=50.0
        )

        strategy = DeepSkyScoringStrategy()
        factor_pn = strategy._calculate_site_factor(pn, context)
        factor_galaxy = strategy._calculate_site_factor(galaxy, context)

        # Compact object should score better
        assert_that(factor_pn).is_greater_than(factor_galaxy).described_as(
            f"Planetary nebula ({factor_pn:.3f}) should be easier than galaxy ({factor_galaxy:.3f})"
        )

    def test_compact_galaxies_benefit_from_concentration(self):
        """M32 (mag 8.08, 8.7') should be visible in Bortle 6 despite moderate magnitude"""
        name, mag, size, ra, dec = SANITY_TIER_COMPACT[4]  # M32
        m32 = create_object(name, mag, size, altitude=50.0, ra=ra, dec=dec)

        telescope = create_telescope(200, "Medium Dobsonian")
        eyepiece = create_eyepiece(10)
        site = create_site(LightPollution.BORTLE_6, "Suburban")

        context = ScoringContext(
            telescope=telescope,
            eyepiece=eyepiece,
            observation_site=site,
            altitude=50.0
        )

        strategy = DeepSkyScoringStrategy()
        factor = strategy._calculate_site_factor(m32, context)

        # Compact elliptical should be visible
        assert_that(factor).is_greater_than(0.3).described_as(
            f"M32 should be visible (>0.3) in Bortle 6 with 200mm, got {factor:.3f}"
        )


class TestApertureImpactOnBenchmarks(unittest.TestCase):
    """
    Verify that aperture makes a realistic difference for faint objects
    but doesn't over-promise visibility in bright skies.
    """

    def test_large_aperture_helps_faint_galaxy_in_dark_skies(self):
        """M51 should be significantly better with 300mm vs 150mm in Bortle 4"""
        name, mag, size, ra, dec = MODERATE_TIER[0]  # M51
        m51 = create_object(name, mag, size, altitude=50.0, ra=ra, dec=dec)

        telescope_small = create_telescope(150, "Small Dob")
        telescope_large = create_telescope(300, "Large Dob")
        eyepiece = create_eyepiece(10)
        site = create_site(LightPollution.BORTLE_4, "Rural Dark Site")

        context_small = ScoringContext(
            telescope=telescope_small,
            eyepiece=eyepiece,
            observation_site=site,
            altitude=50.0
        )
        context_large = ScoringContext(
            telescope=telescope_large,
            eyepiece=eyepiece,
            observation_site=site,
            altitude=50.0
        )

        strategy = DeepSkyScoringStrategy()
        factor_small = strategy._calculate_site_factor(m51, context_small)
        factor_large = strategy._calculate_site_factor(m51, context_large)

        # Large aperture should provide noticeable improvement
        assert_that(factor_large).is_greater_than(factor_small * 1.2).described_as(
            f"300mm ({factor_large:.3f}) should be >20% better than 150mm ({factor_small:.3f})"
        )

    def test_aperture_does_not_overcome_terrible_light_pollution(self):
        """Even 300mm shouldn't make M51 excellent in Bortle 8"""
        name, mag, size, ra, dec = MODERATE_TIER[0]  # M51
        m51 = create_object(name, mag, size, altitude=50.0, ra=ra, dec=dec)

        telescope = create_telescope(300, "Large Dobsonian")
        eyepiece = create_eyepiece(10)
        site = create_site(LightPollution.BORTLE_8, "Urban")

        context = ScoringContext(
            telescope=telescope,
            eyepiece=eyepiece,
            observation_site=site,
            altitude=50.0
        )

        strategy = DeepSkyScoringStrategy()
        factor = strategy._calculate_site_factor(m51, context)

        # Should remain poor/invisible
        assert_that(factor).is_less_than(0.2).described_as(
            f"M51 should remain poor (<0.2) in Bortle 8 even with 300mm, got {factor:.3f}"
        )




def create_object(name: str, magnitude: float, size: float, altitude: float = 45.0,
                  ra: float = 0.0, dec: float = 0.0) -> CelestialObject:
    """Helper to create CelestialObject for testing"""
    return CelestialObject(
        name=name,
        object_type="DeepSky",
        magnitude=magnitude,
        size=size,
        altitude=altitude,
        ra=ra,
        dec=dec
    )


def create_telescope(aperture_mm: int, name: str = "Test Telescope") -> Telescope:
    """Helper to create Telescope for testing"""
    # Telescope needs: name, type, aperture, focal_length, focal_ratio
    focal_length = aperture_mm * 5  # f/5 ratio
    return Telescope(
        id=None,
        name=name,
        type=TelescopeType.NEWTONIAN,
        aperture=aperture_mm,
        focal_length=focal_length,
        focal_ratio=5.0
    )


def create_eyepiece(focal_length_mm: int = 10) -> Eyepiece:
    """Helper to create Eyepiece for testing"""
    return Eyepiece(
        id=None,
        name="Test Eyepiece",
        focal_length=focal_length_mm
    )


def create_site(bortle: LightPollution, name: str = "Test Site") -> ObservationSite:
    """Helper to create ObservationSite for testing"""
    return ObservationSite(
        id=None,
        name=name,
        latitude=40.0,
        longitude=-80.0,
        light_pollution=bortle
    )

if __name__ == '__main__':
    unittest.main()
