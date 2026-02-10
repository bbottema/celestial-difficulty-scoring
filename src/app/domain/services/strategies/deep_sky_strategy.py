from app.domain.model.scoring_context import ScoringContext
from app.domain.services.strategies.strategy_utils import calculate_weather_factor, calculate_moon_proximity_factor
from app.utils.scoring_constants import *
from app.utils.scoring_presets import get_active_preset
from app.utils.light_pollution_models import (
    calculate_light_pollution_factor_with_surface_brightness
)
from app.domain.services.strategies.base_strategy import IObservabilityScoringStrategy


class DeepSkyScoringStrategy(IObservabilityScoringStrategy):
    """
    Scoring strategy for standard deep-sky objects (galaxies, nebulae, clusters).
    These objects are faint, so aperture and dark skies are CRITICAL.
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
        size_contribution = (celestial_object.size / 10.0) * 0.20 if celestial_object.size >= 1.0 else 0.0
        base_score = (flux / 100.0) * 0.80 + size_contribution

        # Equipment factor: aperture is king for faint objects
        equipment_factor = self._calculate_equipment_factor(celestial_object, context)

        # Site factor: light pollution is HUGE for faint objects
        site_factor = self._calculate_site_factor(celestial_object, context)

        # Altitude factor: higher is better (less atmosphere to penetrate)
        altitude_factor = self._calculate_altitude_factor(context.altitude)

        # Weather factor: clouds affect all objects
        weather_factor = calculate_weather_factor(context)

        # Moon proximity factor: moon can devastate faint deep-sky objects
        moon_factor = calculate_moon_proximity_factor(celestial_object, context)

        return base_score * equipment_factor * site_factor * altitude_factor * weather_factor * moon_factor

    def _calculate_equipment_factor(self, celestial_object, context: 'ScoringContext') -> float:
        """
        For deep-sky: aperture is critical (light gathering power).
        More aperture = see fainter objects.
        Uses active preset for aperture scaling.
        """
        if not context.has_equipment():
            # Bright stars (mag < 1) are easily visible naked-eye
            # Faint objects need equipment
            if celestial_object.magnitude < 1.0:
                return 0.95  # Bright stars: minimal penalty (80%+ needed for Sirius test)
            elif celestial_object.magnitude < 4.0:
                return 0.60  # Moderate brightness
            else:
                return EQUIPMENT_PENALTY_DEEPSKY  # Faint: significant penalty

        preset = get_active_preset()
        aperture = context.get_aperture_mm()

        # Aperture impact depends on object brightness
        # Faint objects benefit much more from large aperture
        if celestial_object.magnitude <= 6:  # Bright deep-sky
            # Even small scopes work
            if aperture >= APERTURE_MEDIUM:
                return preset.aperture_factor_medium
            elif aperture >= APERTURE_SMALL:
                return 1.0
            else:
                return preset.aperture_factor_tiny
        elif celestial_object.magnitude <= 9:  # Medium faint
            # Need decent aperture
            if aperture >= APERTURE_LARGE:
                return preset.aperture_factor_large
            elif aperture >= 150:
                return preset.aperture_factor_medium
            elif aperture >= APERTURE_MEDIUM:
                return 0.9
            else:
                return 0.6
        else:  # Very faint (>9 mag)
            # Really need large aperture
            if aperture >= 250:
                return preset.aperture_factor_large * 1.05  # Extra bonus for very large scopes
            elif aperture >= APERTURE_LARGE:
                return preset.aperture_factor_large
            elif aperture >= 150:
                return 0.9
            elif aperture >= APERTURE_MEDIUM:
                return 0.6
            else:
                return 0.3  # Very difficult with small scope

    def _calculate_site_factor(self, celestial_object, context: 'ScoringContext') -> float:
        """
        Light pollution is CRITICAL for faint deep-sky objects.
        Uses hybrid model: legacy penalties with physics-based visibility checks.
        """
        if not context.observation_site:
            return 0.7  # Moderate penalty for unknown site

        bortle = context.get_bortle_number()
        aperture = context.get_aperture_mm() if context.has_equipment() else None
        preset = get_active_preset()

        # Determine penalty based on object brightness (same logic as before)
        if celestial_object.magnitude <= 6:  # Bright deep-sky
            penalty_per_bortle = 0.06
        elif celestial_object.magnitude <= 9:  # Medium faint
            penalty_per_bortle = LIGHT_POLLUTION_PENALTY_PER_BORTLE_DEEPSKY
        else:  # Very faint
            penalty_per_bortle = 0.13

        # Use hybrid model with surface brightness consideration
        factor = calculate_light_pollution_factor_with_surface_brightness(
            celestial_object.magnitude,
            celestial_object.size,
            bortle,
            aperture,
            use_legacy_penalty=True,
            legacy_penalty_per_bortle=penalty_per_bortle,
            legacy_minimum_factor=preset.light_pollution_min_factor_deepsky
        )

        return factor

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
