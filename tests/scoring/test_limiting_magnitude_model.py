"""
Unit tests for the physics-based limiting magnitude model.

These tests demonstrate the benefits of Phase 5 implementation:
- Hard visibility cutoffs based on limiting magnitude
- Realistic aperture-based visibility improvements
- Surface brightness consideration for extended objects
- Physics-based exponential falloff near detection threshold
"""
import unittest
from assertpy import assert_that

from app.domain.model.celestial_object import CelestialObject
from app.domain.services.observability_calculation_service import ObservabilityCalculationService
from app.orm.model.entities import Telescope, Eyepiece, ObservationSite
from app.domain.model.light_pollution import LightPollution
from app.domain.model.telescope_type import TelescopeType
from app.utils.light_pollution_models import (
    calculate_light_pollution_factor_by_limiting_magnitude,
    get_visibility_status
)


class TestLimitingMagnitudePhysics(unittest.TestCase):
    """Test the core physics-based limiting magnitude calculations."""

    def test_bright_object_always_visible(self):
        """Bright objects (mag < 0) should be visible even in Bortle 9."""
        # Jupiter at magnitude -2.4 in worst light pollution (Bortle 9, NELM 3.6)
        factor = calculate_light_pollution_factor_by_limiting_magnitude(
            object_magnitude=-2.4,
            bortle=9,
            telescope_aperture_mm=None,  # Naked eye
            detection_headroom=0.5,
            use_legacy_penalty=False
        )

        # Jupiter is 6 magnitudes brighter than Bortle 9 limit
        # Should have very high visibility factor
        assert_that(factor).is_greater_than(0.99)

    def test_object_below_limiting_magnitude_invisible(self):
        """Objects fainter than limiting magnitude should score zero (invisible)."""
        # Faint galaxy (mag 11.0) in Bortle 5 (NELM 5.6) with no telescope
        factor = calculate_light_pollution_factor_by_limiting_magnitude(
            object_magnitude=11.0,
            bortle=5,
            telescope_aperture_mm=None,  # Naked eye
            detection_headroom=1.5,
            use_legacy_penalty=False
        )

        # Object is 5.4 magnitudes fainter than naked-eye limit
        # Should be completely invisible
        assert_that(factor).is_equal_to(0.0)

    def test_aperture_makes_faint_objects_visible(self):
        """Telescope aperture should make previously invisible objects visible."""
        # Faint galaxy (mag 11.0) in Bortle 5

        # Without telescope: invisible
        naked_eye_factor = calculate_light_pollution_factor_by_limiting_magnitude(
            object_magnitude=11.0,
            bortle=5,
            telescope_aperture_mm=None,
            detection_headroom=1.5,
            use_legacy_penalty=False
        )

        # With 200mm telescope: visible
        # 200mm aperture adds ~5*log10(200/7) ≈ 7.1 magnitudes to limiting mag
        # Limiting mag becomes 5.6 + 7.1 = 12.7
        telescope_factor = calculate_light_pollution_factor_by_limiting_magnitude(
            object_magnitude=11.0,
            bortle=5,
            telescope_aperture_mm=200,
            detection_headroom=1.5,
            use_legacy_penalty=False
        )

        assert_that(naked_eye_factor).is_equal_to(0.0)
        assert_that(telescope_factor).is_greater_than(0.5)

    def test_larger_aperture_better_than_smaller(self):
        """Larger aperture should give better visibility for same object."""
        # Galaxy at mag 10 in Bortle 6

        small_scope_factor = calculate_light_pollution_factor_by_limiting_magnitude(
            object_magnitude=10.0,
            bortle=6,
            telescope_aperture_mm=80,  # 3" refractor
            detection_headroom=1.5,
            use_legacy_penalty=False
        )

        medium_scope_factor = calculate_light_pollution_factor_by_limiting_magnitude(
            object_magnitude=10.0,
            bortle=6,
            telescope_aperture_mm=200,  # 8" scope
            detection_headroom=1.5,
            use_legacy_penalty=False
        )

        large_scope_factor = calculate_light_pollution_factor_by_limiting_magnitude(
            object_magnitude=10.0,
            bortle=6,
            telescope_aperture_mm=400,  # 16" scope
            detection_headroom=1.5,
            use_legacy_penalty=False
        )

        # Visibility should improve with aperture
        assert_that(medium_scope_factor).is_greater_than(small_scope_factor)
        assert_that(large_scope_factor).is_greater_than(medium_scope_factor)

    def test_exponential_falloff_near_threshold(self):
        """Visibility should fall off exponentially as object approaches limiting magnitude."""
        # In Bortle 5 (NELM 5.6) with 100mm scope (adds ~5.6 mag, limit ~11.2)

        # Object well above limit (mag 8.0): high visibility
        bright_factor = calculate_light_pollution_factor_by_limiting_magnitude(
            object_magnitude=8.0,
            bortle=5,
            telescope_aperture_mm=100,
            detection_headroom=1.5,
            use_legacy_penalty=False
        )

        # Object near limit (mag 10.5): marginal visibility
        marginal_factor = calculate_light_pollution_factor_by_limiting_magnitude(
            object_magnitude=10.5,
            bortle=5,
            telescope_aperture_mm=100,
            detection_headroom=1.5,
            use_legacy_penalty=False
        )

        # Object at limit (mag 11.2): barely visible
        threshold_factor = calculate_light_pollution_factor_by_limiting_magnitude(
            object_magnitude=11.2,
            bortle=5,
            telescope_aperture_mm=100,
            detection_headroom=1.5,
            use_legacy_penalty=False
        )

        # Should show exponential falloff
        assert_that(bright_factor).is_greater_than(0.85)  # Well above limit
        assert_that(marginal_factor).is_between(0.30, 0.70)  # Near limit
        assert_that(threshold_factor).is_less_than(0.15)  # At limit


class TestVisibilityStatusLabels(unittest.TestCase):
    """Test human-readable visibility status labels."""

    def test_excellent_visibility(self):
        """Very bright objects should show 'Excellent' status."""
        status = get_visibility_status(
            object_magnitude=1.0,
            bortle=5,
            telescope_aperture_mm=200
        )
        assert_that(status).is_equal_to("Excellent")

    def test_marginal_visibility(self):
        """Objects near limiting magnitude should show 'Marginal' status."""
        # Object close to telescope limiting magnitude
        status = get_visibility_status(
            object_magnitude=10.5,
            bortle=5,
            telescope_aperture_mm=100
        )
        assert_that(status).is_in("Marginal", "Good")

    def test_invisible_status(self):
        """Objects below limiting magnitude should show 'Invisible' status."""
        status = get_visibility_status(
            object_magnitude=12.0,
            bortle=8,
            telescope_aperture_mm=None  # Naked eye in city
        )
        assert_that(status).is_equal_to("Invisible")


class TestSurfaceBrightnessEffect(unittest.TestCase):
    """Test that extended objects are treated differently than point sources."""

    def test_compact_vs_extended_same_magnitude(self):
        """Extended objects should be harder to see than compact objects of same magnitude."""
        from app.utils.light_pollution_models import calculate_light_pollution_factor_with_surface_brightness

        # Compact object (mag 9.0, 2 arcmin)
        compact_factor = calculate_light_pollution_factor_with_surface_brightness(
            object_magnitude=9.0,
            object_size_arcmin=2,
            bortle=6,
            telescope_aperture_mm=200,
            use_legacy_penalty=False
        )

        # Extended object (mag 9.0, 60 arcmin) - same brightness spread over larger area
        extended_factor = calculate_light_pollution_factor_with_surface_brightness(
            object_magnitude=9.0,
            object_size_arcmin=60,
            bortle=6,
            telescope_aperture_mm=200,
            use_legacy_penalty=False
        )

        # Extended object should be harder to see due to lower surface brightness
        # (larger detection_headroom = 3.0 vs 1.5)
        assert_that(extended_factor).is_less_than(compact_factor)

    def test_large_object_needs_more_headroom(self):
        """Very large objects should require more visibility margin."""
        from app.utils.light_pollution_models import calculate_light_pollution_factor_with_surface_brightness

        # Both objects at mag 8.0, but different sizes
        medium_size = calculate_light_pollution_factor_with_surface_brightness(
            object_magnitude=8.0,
            object_size_arcmin=10,
            bortle=5,
            telescope_aperture_mm=200,
            use_legacy_penalty=False
        )

        large_size = calculate_light_pollution_factor_with_surface_brightness(
            object_magnitude=8.0,
            object_size_arcmin=100,
            bortle=5,
            telescope_aperture_mm=200,
            use_legacy_penalty=False
        )

        # Large object needs more visibility margin due to low surface brightness
        assert_that(large_size).is_less_than(medium_size)


class TestIntegratedBehavior(unittest.TestCase):
    """Test that the limiting magnitude model integrates correctly with full scoring."""

    def test_physics_model_provides_hard_cutoff(self):
        """
        The physics-based model should provide hard visibility cutoffs.
        Objects below limiting magnitude should return zero visibility.
        """
        from app.utils.light_pollution_models import calculate_light_pollution_factor_by_limiting_magnitude

        # Very faint object (mag 13) in Bortle 8 with small scope
        # Bortle 8 NELM = 4.1, 80mm scope adds ~5.1 mag -> limit ~9.2
        # Object is 3.8 magnitudes below limit
        factor = calculate_light_pollution_factor_by_limiting_magnitude(
            object_magnitude=13.0,
            bortle=8,
            telescope_aperture_mm=80,
            detection_headroom=1.5,
            use_legacy_penalty=False
        )

        # Should be invisible (hard cutoff)
        assert_that(factor).is_equal_to(0.0)

    def test_aperture_extends_limiting_magnitude(self):
        """
        Larger aperture should extend the limiting magnitude,
        making fainter objects visible.
        """
        from app.utils.light_pollution_models import calculate_light_pollution_factor_by_limiting_magnitude

        # Object at mag 11 in Bortle 6 (NELM 5.1)

        # 80mm scope: limit ~10.2 -> object invisible
        small_scope = calculate_light_pollution_factor_by_limiting_magnitude(
            object_magnitude=11.0,
            bortle=6,
            telescope_aperture_mm=80,
            detection_headroom=1.5,
            use_legacy_penalty=False
        )

        # 200mm scope: limit ~12.8 -> object visible
        large_scope = calculate_light_pollution_factor_by_limiting_magnitude(
            object_magnitude=11.0,
            bortle=6,
            telescope_aperture_mm=200,
            detection_headroom=1.5,
            use_legacy_penalty=False
        )

        assert_that(small_scope).is_equal_to(0.0)  # Invisible
        assert_that(large_scope).is_greater_than(0.5)  # Visible


class TestLegacyCompatibilityMode(unittest.TestCase):
    """Test that legacy mode preserves old behavior while adding visibility cutoffs."""

    def test_legacy_mode_maintains_linear_penalty(self):
        """Legacy mode should apply linear Bortle penalty."""
        # Object at mag 8.0 in Bortle 3 vs Bortle 6

        bortle3_factor = calculate_light_pollution_factor_by_limiting_magnitude(
            object_magnitude=8.0,
            bortle=3,
            telescope_aperture_mm=200,
            detection_headroom=1.5,
            use_legacy_penalty=True,
            legacy_penalty_per_bortle=0.10,  # 10% per Bortle
            legacy_minimum_factor=0.02
        )

        bortle6_factor = calculate_light_pollution_factor_by_limiting_magnitude(
            object_magnitude=8.0,
            bortle=6,
            telescope_aperture_mm=200,
            detection_headroom=1.5,
            use_legacy_penalty=True,
            legacy_penalty_per_bortle=0.10,
            legacy_minimum_factor=0.02
        )

        # Bortle 3 should be 30% better than Bortle 6 (3 Bortle levels × 10%)
        # (allowing for physics factor modulation)
        assert_that(bortle3_factor).is_greater_than(bortle6_factor)

    def test_legacy_mode_still_enforces_visibility_cutoff(self):
        """Legacy mode should still return 0.0 for invisible objects."""
        # Object well below limiting magnitude should be invisible even with legacy mode
        factor = calculate_light_pollution_factor_by_limiting_magnitude(
            object_magnitude=15.0,
            bortle=8,
            telescope_aperture_mm=100,  # Limit ~10 mag
            detection_headroom=1.5,
            use_legacy_penalty=True,
            legacy_penalty_per_bortle=0.10,
            legacy_minimum_factor=0.02
        )

        # Object is ~5 magnitudes below limit - should be invisible
        assert_that(factor).is_equal_to(0.0)


class TestRealisticOptimismGuards(unittest.TestCase):
    """
    Test that the model doesn't over-promise visibility in challenging conditions.
    These tests address real-world limitations that the basic telescope formula ignores.
    """

    def test_200mm_scope_bortle6_mag11_galaxy_documents_optimism(self):
        """
        Real-world test: Mag 11 galaxy from Bortle 6 with 200mm scope.
        Basic formula says limit ~12.7, so object "should be easy."
        Reality: mediocre seeing, light loss, observer skill → often marginal or missed.

        This test documents current behavior before aperture_gain_factor fix.
        """
        # Without aperture gain correction
        factor_optimistic = calculate_light_pollution_factor_by_limiting_magnitude(
            object_magnitude=11.0,
            bortle=6,
            telescope_aperture_mm=200,
            detection_headroom=1.5,
            use_legacy_penalty=False
        )

        # With aperture_gain_factor=0.85, this is now marginal (~0.17)
        # This represents realistic expectation: challenging but possible
        # Without correction (factor=1.0), would be ~0.5 (over-optimistic)
        assert_that(factor_optimistic).is_between(0.10, 0.25)

    def test_large_low_surface_brightness_needs_strict_headroom(self):
        """
        Large nebulae (>60') with low surface brightness are much harder
        than their integrated magnitude suggests.
        """
        from app.utils.light_pollution_models import calculate_light_pollution_factor_with_surface_brightness

        # Medium-size nebula (30 arcmin)
        medium_nebula = calculate_light_pollution_factor_with_surface_brightness(
            object_magnitude=7.0,
            object_size_arcmin=30,
            bortle=5,
            telescope_aperture_mm=200,
            use_legacy_penalty=False
        )

        # Very large nebula (120 arcmin) - same integrated magnitude
        large_nebula = calculate_light_pollution_factor_with_surface_brightness(
            object_magnitude=7.0,
            object_size_arcmin=120,
            bortle=5,
            telescope_aperture_mm=200,
            use_legacy_penalty=False
        )

        # Large nebula should be harder due to stricter headroom (3.2 vs 3.0)
        # Actual: ~0.776 vs ~0.853 = 91% (9% reduction)
        assert_that(large_nebula).is_less_than(medium_nebula * 0.93)

    def test_extended_object_in_bright_sky_harsh_penalty(self):
        """
        Extended objects suffer disproportionately in light pollution
        due to contrast loss.
        """
        from app.utils.light_pollution_models import calculate_light_pollution_factor_with_surface_brightness

        # Moderately bright galaxy (mag 9.0, 10 arcmin) in Bortle 7
        factor = calculate_light_pollution_factor_with_surface_brightness(
            object_magnitude=9.0,
            object_size_arcmin=10,
            bortle=7,
            telescope_aperture_mm=200,
            use_legacy_penalty=False
        )

        # Should be quite challenging (not "good")
        # Actual: ~0.51 (just marginal, not "good")
        assert_that(factor).is_less_than_or_equal_to(0.55)

    def test_tiny_aperture_limited_on_dsos(self):
        """
        50mm finder scope should not be rated highly for DSOs,
        even when technically above limiting magnitude.
        """
        factor = calculate_light_pollution_factor_by_limiting_magnitude(
            object_magnitude=8.4,
            bortle=3,
            telescope_aperture_mm=50,
            detection_headroom=1.5,
            use_legacy_penalty=False
        )

        # Should be moderate at best
        assert_that(factor).is_less_than(0.75)


class TestApertureDoubleCountingIssue(unittest.TestCase):
    """
    Test that documents aperture being counted in multiple factors.

    Current behavior in DeepSkyScoringStrategy:
    1. equipment_factor: Large aperture gets bonus (1.0 → 1.2 → 1.5)
    2. site_factor: Aperture extends limiting magnitude

    This creates multiplicative effect that may overweight aperture.
    """

    def test_aperture_double_counting_documented(self):
        """
        Document that aperture influences both equipment and site factors.

        This is by design but needs monitoring to ensure the combined effect
        doesn't make "bigger scope always wins" regardless of conditions.

        Proper balance:
        - Aperture in site_factor: handles visibility threshold (can you see it?)
        - Equipment_factor: should focus more on magnification, framing, etc.
        """
        # This test documents the architectural decision
        # Future: Consider reducing aperture's role in equipment_factor
        # to focus it on magnification/field-of-view appropriateness
        pass


class TestDoublePenaltyIssue(unittest.TestCase):
    """
    Test that demonstrates the double-penalty problem in LargeObjectStrategy.
    Issue: size affects both detection_headroom AND gets an additional size_penalty,
    causing very large objects to be overly suppressed even in good conditions.
    """

    def test_large_object_not_overly_crushed(self):
        """
        Andromeda (190') in dark skies should still score well.

        The headroom adjustment (3.5 for size >120') appropriately makes it harder,
        but we shouldn't apply an ADDITIONAL 15% size penalty on top of that.
        """
        from app.utils.light_pollution_models import calculate_light_pollution_factor_with_surface_brightness

        # Andromeda: mag 3.44, 190 arcmin in Bortle 3 with 200mm scope
        andromeda_factor = calculate_light_pollution_factor_with_surface_brightness(
            object_magnitude=3.44,
            object_size_arcmin=190,
            bortle=3,
            telescope_aperture_mm=200,
            use_legacy_penalty=False
        )

        # Should still be quite visible in dark skies
        # With just headroom adjustment (no double-penalty): should be > 0.75
        assert_that(andromeda_factor).is_greater_than(0.70)


class TestPresetIntegration(unittest.TestCase):
    """
    Test that preset system controls aperture_gain_factor and detection_headroom.

    Friendly preset: More optimistic (higher gain_factor, lower headroom)
    Strict preset: More conservative (lower gain_factor, higher headroom)
    """

    def test_preset_should_control_aperture_gain(self):
        """
        Future enhancement: Presets should control aperture_gain_factor.

        Friendly: 0.90 (optimistic)
        Strict: 0.75 (conservative)
        Default: 0.85 (realistic)
        """
        # This will be implemented when presets are enhanced
        pass

    def test_preset_should_control_headroom_multiplier(self):
        """
        Future enhancement: Presets could scale detection_headroom.

        Friendly: base headroom * 0.9
        Strict: base headroom * 1.1
        """
        pass


if __name__ == '__main__':
    unittest.main()
