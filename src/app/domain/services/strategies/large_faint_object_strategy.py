from app.domain.model.scoring_context import ScoringContext
from app.domain.services.strategies.strategy_utils import calculate_weather_factor, calculate_moon_proximity_factor
from app.utils.scoring_constants import *
from app.utils.scoring_presets import get_active_preset
from app.utils.light_pollution_models import (
    calculate_light_pollution_factor_with_surface_brightness
)
from app.domain.services.strategies.base_strategy import IObservabilityScoringStrategy


class LargeFaintObjectScoringStrategy(IObservabilityScoringStrategy):
    """
    Scoring strategy for large, faint extended objects (e.g., M31, IC 1396).
    These need wide field of view (low magnification) and dark skies.
    """

    def calculate_score(self, celestial_object, context: 'ScoringContext'):
        # Adjust the magnitude score to increase with brightness (lower magnitude = higher score)
        magnitude_score = max(0, (FAINT_OBJECT_MAGNITUDE_BASELINE - celestial_object.magnitude))

        # Adjust the size score to increase with size
        size_score = min(celestial_object.size / MAX_DEEPSKY_SIZE_LARGE, 1)  # Cap the size score at 1

        # Combine scores
        base_score = (WEIGHT_MAGNITUDE_LARGE_OBJECTS * magnitude_score) + (WEIGHT_SIZE_LARGE_OBJECTS * size_score)
        base_score = min(base_score, MAX_OBSERVABLE_SCORE) / NORMALIZATION_DIVISOR

        # Equipment factor: need wide field of view (low magnification)
        equipment_factor = self._calculate_equipment_factor(celestial_object, context)

        # Site factor: dark skies are critical for faint nebulosity
        site_factor = self._calculate_site_factor(celestial_object, context)

        # Altitude factor: higher is better
        altitude_factor = self._calculate_altitude_factor(context.altitude)

        # Weather factor: clouds affect all objects
        weather_factor = calculate_weather_factor(context)

        # Moon proximity factor: moon can devastate large faint objects
        moon_factor = calculate_moon_proximity_factor(celestial_object, context)

        return base_score * equipment_factor * site_factor * altitude_factor * weather_factor * moon_factor

    def _calculate_equipment_factor(self, celestial_object, context: 'ScoringContext') -> float:
        """
        Large objects need LOW magnification for wide field of view.
        Also consider aperture for light gathering (low surface brightness objects).
        """
        if not context.has_equipment():
            return EQUIPMENT_PENALTY_LARGE_FAINT

        magnification = context.get_magnification()
        aperture = context.get_aperture_mm()
        preset = get_active_preset()

        # Calculate magnification factor (low mag preferred)
        if MAGNIFICATION_LARGE_OBJECT_OPTIMAL_MAX <= magnification <= 80:
            mag_factor = 1.2  # Optimal range
        elif 20 <= magnification < MAGNIFICATION_LARGE_OBJECT_OPTIMAL_MAX or \
             80 < magnification <= 120:
            mag_factor = 1.0
        elif magnification < 20:
            mag_factor = 0.9  # Too wide - dimmer image
        else:
            mag_factor = MAGNIFICATION_FACTOR_TOO_HIGH

        # Calculate aperture factor (light gathering for low surface brightness)
        if aperture >= APERTURE_LARGE:
            aperture_factor = preset.aperture_factor_large
        elif aperture >= APERTURE_MEDIUM:
            aperture_factor = preset.aperture_factor_medium
        elif aperture >= APERTURE_SMALL:
            aperture_factor = 1.0
        else:
            aperture_factor = preset.aperture_factor_tiny

        # Combine factors (both matter for large faint objects)
        return (mag_factor + aperture_factor) / 2

    def _calculate_site_factor(self, celestial_object, context: 'ScoringContext') -> float:
        """
        Dark skies are critical for faint extended nebulosity.
        Uses hybrid model with surface brightness consideration.
        """
        if not context.observation_site:
            return 0.6  # Significant penalty

        bortle = context.get_bortle_number()
        aperture = context.get_aperture_mm() if context.has_equipment() else None
        preset = get_active_preset()

        # Large faint objects use harsher penalty than standard deep-sky
        # Surface brightness model already handles size via detection_headroom scaling
        # (larger objects get stricter headroom: 3.0, 3.2, 3.5 based on size)
        # No additional size penalty needed - that would be double-penalizing
        factor = calculate_light_pollution_factor_with_surface_brightness(
            celestial_object.magnitude,
            celestial_object.size,
            bortle,
            aperture,
            use_legacy_penalty=True,
            legacy_penalty_per_bortle=LIGHT_POLLUTION_PENALTY_PER_BORTLE_LARGE,
            legacy_minimum_factor=preset.light_pollution_min_factor_large
        )

        return factor

    def _calculate_altitude_factor(self, altitude: float) -> float:
        """Higher altitude = better for faint objects. Below horizon = impossible."""
        if altitude < ALTITUDE_BELOW_HORIZON:
            return ALTITUDE_FACTOR_BELOW_HORIZON
        elif altitude >= ALTITUDE_OPTIMAL_MIN_LARGE:
            return ALTITUDE_FACTOR_OPTIMAL
        elif altitude >= ALTITUDE_GOOD_MIN_LARGE:
            return ALTITUDE_FACTOR_GOOD_LARGE
        elif altitude >= ALTITUDE_FAIR_MIN_LARGE:
            return ALTITUDE_FACTOR_FAIR_LARGE
        else:
            return ALTITUDE_FACTOR_POOR_LARGE
