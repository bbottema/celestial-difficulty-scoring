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
        # Base score from object properties
        magnitude_score = self._normalize_magnitude(10 ** (-0.4 * (celestial_object.magnitude + 12)))
        size_score = self._normalize_size(celestial_object.size)
        base_score = (magnitude_score + size_score) / 2

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
            return EQUIPMENT_PENALTY_DEEPSKY

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
