from app.domain.model.scoring_context import ScoringContext
from app.domain.services.strategies.strategy_utils import calculate_weather_factor, calculate_moon_proximity_factor, get_size_arcmin
from app.utils.scoring_constants import *
from app.utils.scoring_presets import get_active_preset
from app.utils.light_pollution_models import (
    calculate_light_pollution_factor_with_surface_brightness
)
from app.domain.services.strategies.base_strategy import IObservabilityScoringStrategy


class DeepSkyScoringStrategy(IObservabilityScoringStrategy):
    """
    Scoring strategy for standard deep-sky objects (galaxies, nebulae, clusters).

    HIERARCHICAL MODEL (Phase 6.5 refactor):
    1. Detection: Can object be detected? (uses aperture via limiting magnitude)
    2. Quality: How good is the viewing experience? (independent factors)

    This eliminates double-counting of aperture benefits.
    """

    def calculate_score(self, celestial_object, context: 'ScoringContext'):
        # Base score from object properties using SAME approach as ReflectedLightStrategy
        # This ensures cross-strategy comparisons are calibrated correctly
        flux = 10 ** (-0.4 * celestial_object.magnitude)
        # Sirius: mag -1.46 → flux = 3.72
        # Vega: mag 0.03 → flux = 1.01
        # M42: mag 4.0 → flux = 0.04

        # For point sources (stars), size=0, so base score is just flux-based
        # For extended objects (>= 1 arcmin), add size contribution
        # Use same threshold as ReflectedLight: only add size if >= 1 arcmin
        size_arcmin = get_size_arcmin(celestial_object)
        size_contribution = (size_arcmin / 10.0) * 0.20 if size_arcmin >= 1.0 else 0.0
        base_score = (flux / 100.0) * 0.80 + size_contribution

        # HIERARCHICAL FACTORS (Phase 6.5 refactor):

        # 1. DETECTION: Can we detect this object at all?
        #    Uses limiting magnitude (includes aperture via physics)
        detection_factor = self._calculate_detection_factor(celestial_object, context)

        # 2. MAGNIFICATION: Is magnification appropriate for this object?
        #    (No aperture dependency - only mag/size matching)
        magnification_factor = self._calculate_magnification_factor(celestial_object, context)

        # 3. SKY DARKNESS: Light pollution penalty
        #    (No aperture dependency - only Bortle scale)
        sky_darkness_factor = self._calculate_sky_darkness_factor(celestial_object, context)

        # 4. ALTITUDE: Atmospheric clarity
        #    (No aperture dependency)
        altitude_factor = self._calculate_altitude_factor(context.altitude)

        # 5. WEATHER: Cloud cover
        weather_factor = calculate_weather_factor(context)

        # 6. MOON: Moon proximity
        moon_factor = calculate_moon_proximity_factor(celestial_object, context)

        return base_score * detection_factor * magnification_factor * sky_darkness_factor * altitude_factor * weather_factor * moon_factor

    def _calculate_detection_factor(self, celestial_object, context: 'ScoringContext') -> float:
        """
        DETECTION FACTOR: Can the object be detected above the noise floor?

        Uses physics-based limiting magnitude model (Phase 5):
        - Includes aperture via limiting magnitude formula
        - Considers light pollution (Bortle scale)
        - Returns 0.0 if below detection threshold
        - Returns 0-1 exponential falloff near threshold
        - Returns ~1.0 if well above threshold

        This is the ONLY factor that considers aperture (via limiting magnitude).
        All other factors are independent of aperture.
        """
        if not context.observation_site:
            return 0.7  # Moderate penalty for unknown site

        bortle = context.get_bortle_number()
        aperture = context.get_aperture_mm() if context.has_equipment() else None
        telescope_type = context.telescope.type if context.has_equipment() else None

        # Use limiting magnitude model with surface brightness consideration
        # Phase 6.5: Pass telescope_type and altitude for split aperture gain
        # Phase 7: Pass object_classification for type-aware headroom
        # NOTE: We set use_legacy_penalty=False to get PURE limiting magnitude model
        # The sky_darkness_factor will handle Bortle penalties separately
        size_arcmin = get_size_arcmin(celestial_object)
        factor = calculate_light_pollution_factor_with_surface_brightness(
            celestial_object.magnitude,
            size_arcmin,
            bortle,
            aperture,
            telescope_type=telescope_type,
            altitude=celestial_object.altitude,
            observer_skill='intermediate',  # TODO: Make configurable in user settings
            object_classification=celestial_object.classification,  # Phase 7: Type-aware headroom
            use_legacy_penalty=False,  # Pure physics model, no legacy blending
            legacy_penalty_per_bortle=0.0,  # Not used
            legacy_minimum_factor=0.0  # Not used
        )

        return factor

    def _calculate_magnification_factor(self, celestial_object, context: 'ScoringContext') -> float:
        """
        MAGNIFICATION FACTOR: Is magnification appropriate for this object?

        Large extended objects need LOW magnification (wide field of view).
        Small compact objects can handle HIGHER magnification.

        NO APERTURE DEPENDENCY - only considers magnification and object size.

        For FAINT objects (mag > 9), magnification matching is less critical than detection.
        We're more forgiving because any equipment that can detect it is valuable.
        """
        if not context.has_equipment():
            # Naked eye viewing
            # Bright stars/objects: great naked-eye
            # Faint objects: significant penalty
            if celestial_object.magnitude < 1.0:
                return 0.95  # Bright stars easily visible
            elif celestial_object.magnitude < 4.0:
                return 0.70  # Moderate stars visible
            else:
                return 0.40  # Faint objects hard without equipment

        magnification = context.get_magnification()
        size_arcmin = get_size_arcmin(celestial_object)

        # For very faint objects, magnification matching is less critical
        # Detection is paramount - if you can see it at all, that's what matters
        # We progressively care less about magnification as objects get fainter
        if celestial_object.magnitude > 9:
            leniency = 1.5  # Very faint: detection >> magnification matching
        elif celestial_object.magnitude > 7:
            leniency = 1.3  # Faint: detection > magnification matching
        else:
            leniency = 1.0  # Bright: magnification matching matters

        # Magnification matching based on object size
        # For faint objects (leniency > 1), we're very forgiving - just don't be extreme
        if size_arcmin > 60:  # Very large (Andromeda, Pleiades, etc.)
            # Need very low magnification, but faint ones are forgiving
            if magnification < 100:
                return 1.0  # Good enough for very large objects
            elif magnification < 200:
                return min(0.85 * leniency, 1.0)  # Acceptable for faint
            else:
                return min(0.7 * leniency, 1.0)  # Too high but tolerable if faint

        elif size_arcmin > 20:  # Large (many nebulae)
            # Need low-moderate magnification
            if magnification < 150:
                return 1.0  # Wide acceptable range
            elif magnification < 200:
                return min(0.9 * leniency, 1.0)
            else:
                return min(0.8 * leniency, 1.0)

        elif size_arcmin > 5:  # Medium (many galaxies)
            # Moderate magnification best
            if 50 <= magnification <= 150:
                return min(1.0 * leniency, 1.0)
            elif 30 <= magnification < 50 or 150 < magnification <= 200:
                return min(0.9 * leniency, 1.0)
            else:
                return min(0.8 * leniency, 1.0)

        else:  # Small/compact (planetary nebulae, globular clusters)
            # Can handle higher magnification
            if 100 <= magnification <= 200:
                return min(1.0 * leniency, 1.0)
            elif 50 <= magnification < 100 or 200 < magnification <= 250:
                return min(0.9 * leniency, 1.0)
            else:
                return min(0.85 * leniency, 1.0)

    def _calculate_sky_darkness_factor(self, celestial_object, context: 'ScoringContext') -> float:
        """
        SKY DARKNESS FACTOR: Light pollution penalty based on Bortle scale.

        NO APERTURE DEPENDENCY - only considers Bortle scale and object brightness.
        Aperture's effect on visibility is handled by detection_factor.

        Fainter objects suffer more from light pollution.
        """
        if not context.observation_site:
            return 0.8  # Moderate penalty for unknown site

        bortle = context.get_bortle_number()
        preset = get_active_preset()

        # Determine penalty based on object brightness
        if celestial_object.magnitude <= 6:  # Bright deep-sky
            penalty_per_bortle = 0.06  # Less affected by light pollution
        elif celestial_object.magnitude <= 9:  # Medium faint
            penalty_per_bortle = LIGHT_POLLUTION_PENALTY_PER_BORTLE_DEEPSKY
        else:  # Very faint
            penalty_per_bortle = 0.13  # Heavily affected by light pollution

        # Linear Bortle penalty
        factor = 1.0 - ((bortle - 1) * penalty_per_bortle)
        factor = max(factor, preset.light_pollution_min_factor_deepsky)

        return factor

    # Backward compatibility aliases for tests
    def _calculate_site_factor(self, celestial_object, context: 'ScoringContext') -> float:
        """DEPRECATED: Use _calculate_detection_factor() instead. Kept for test compatibility."""
        return self._calculate_detection_factor(celestial_object, context)

    def _calculate_equipment_factor(self, celestial_object, context: 'ScoringContext') -> float:
        """DEPRECATED: Use _calculate_magnification_factor() instead. Kept for test compatibility."""
        return self._calculate_magnification_factor(celestial_object, context)

    def _calculate_altitude_factor(self, altitude: float) -> float:
        """Higher altitude = less atmosphere to penetrate. Below horizon = impossible."""
        if altitude < ALTITUDE_BELOW_HORIZON:
            return ALTITUDE_FACTOR_BELOW_HORIZON
        elif altitude >= ALTITUDE_OPTIMAL_MIN_DEEPSKY:
            return ALTITUDE_FACTOR_OPTIMAL
        elif altitude >= ALTITUDE_GOOD_MIN_DEEPSKY:
            return ALTITUDE_FACTOR_GOOD_DEEPSKY
        elif altitude >= ALTITUDE_FAIR_MIN_DEEPSKY:
            return ALTITUDE_FACTOR_FAIR_DEEPSKY
        elif altitude >= ALTITUDE_POOR_MIN_DEEPSKY:
            return ALTITUDE_FACTOR_POOR_DEEPSKY
        else:
            preset = get_active_preset()
            return preset.altitude_factor_very_poor_deepsky

    @staticmethod
    def _normalize_magnitude(score) -> float:
        return (score / SIRIUS_DEEPSKY_MAGNITUDE_SCORE) * MAX_OBSERVABLE_SCORE

    @staticmethod
    def _normalize_size(score) -> float:
        return (score / MAX_DEEPSKY_SIZE_COMPACT) * MAX_OBSERVABLE_SCORE

    def normalize_score(self, raw_score: float) -> float:
        """
        Normalize deep-sky scores to 0-25 scale.

        After unifying base score calculation with ReflectedLightStrategy,
        use the SAME normalization formula to preserve magnitude ordering.

        Typical raw scores (after factors):
        - Sirius: ~0.0275
        - Vega: ~0.007
        - M42: ~0.001-0.003
        - Faint galaxies: ~0.0001-0.0005
        """
        # Use same hybrid normalization as ReflectedLightStrategy
        if raw_score <= 0:
            return 0.0
        elif raw_score > 10:
            # Logarithmic for very bright objects
            import math
            return min(15 + math.log10(raw_score), 25.0)
        else:
            # Power scaling for normal objects
            compressed = raw_score ** 0.35
            return min(compressed * 15.0, 25.0)
