from app.domain.model.scoring_context import ScoringContext
from app.domain.services.strategies.strategy_utils import calculate_weather_factor, calculate_moon_proximity_factor
from app.utils.scoring_constants import *
from app.utils.light_pollution_models import (
    calculate_light_pollution_factor_by_limiting_magnitude
)
from app.domain.services.strategies.base_strategy import IObservabilityScoringStrategy


class SolarSystemScoringStrategy(IObservabilityScoringStrategy):
    """
    Scoring strategy for solar system objects (planets, moon, sun).
    These objects are bright, so light pollution has minimal impact.
    Magnification is key to seeing details (cloud bands, rings, moons).
    """

    def calculate_score(self, celestial_object, context: 'ScoringContext'):
        # Base score from object properties
        magnitude_score = self._normalize_magnitude(10 ** (-0.4 * celestial_object.magnitude))
        size_score = self._normalize_size(celestial_object.size)
        base_score = (magnitude_score + size_score) / 2

        # Equipment factor: magnification matters for seeing details
        equipment_factor = self._calculate_equipment_factor(celestial_object, context)

        # Site factor: light pollution barely affects bright objects
        site_factor = self._calculate_site_factor(celestial_object, context)

        # Altitude factor: atmosphere matters more for planets
        altitude_factor = self._calculate_altitude_factor(context.altitude)

        # Weather factor: clouds affect all objects
        weather_factor = calculate_weather_factor(context)

        # Moon proximity factor: moon doesn't affect bright solar system objects
        moon_factor = calculate_moon_proximity_factor(celestial_object, context)

        return base_score * equipment_factor * site_factor * altitude_factor * weather_factor * moon_factor

    def _calculate_equipment_factor(self, celestial_object, context: 'ScoringContext') -> float:
        """
        For planets: higher magnification = better (see more detail)
        Target: 150-300x for planets
        """
        if not context.has_equipment():
            return EQUIPMENT_PENALTY_SOLAR_SYSTEM

        magnification = context.get_magnification()

        # Optimal magnification range for planets
        if MAGNIFICATION_PLANETARY_OPTIMAL_MIN <= magnification <= MAGNIFICATION_PLANETARY_OPTIMAL_MAX:
            return MAGNIFICATION_FACTOR_OPTIMAL
        elif 100 <= magnification < MAGNIFICATION_PLANETARY_OPTIMAL_MIN or \
             MAGNIFICATION_PLANETARY_OPTIMAL_MAX < magnification <= 400:
            return MAGNIFICATION_FACTOR_ACCEPTABLE
        elif MAGNIFICATION_PLANETARY_TOO_LOW <= magnification < 100:
            return 0.8  # Moderate penalty
        else:
            return MAGNIFICATION_FACTOR_TOO_HIGH

    def _calculate_site_factor(self, celestial_object, context: 'ScoringContext') -> float:
        """
        Light pollution barely affects bright solar system objects.
        Uses hybrid model: legacy linear penalty with physics-based visibility check.
        """
        if not context.observation_site:
            return 0.9  # Small penalty for unknown site

        bortle = context.get_bortle_number()
        aperture = context.get_aperture_mm() if context.has_equipment() else None

        # Use hybrid model that blends legacy penalty with physics-based visibility
        # This maintains test compatibility while adding hard visibility cutoffs
        factor = calculate_light_pollution_factor_by_limiting_magnitude(
            celestial_object.magnitude,
            bortle,
            aperture,
            detection_headroom=0.5,
            use_legacy_penalty=True,
            legacy_penalty_per_bortle=LIGHT_POLLUTION_PENALTY_PER_BORTLE_SOLAR,
            legacy_minimum_factor=0.90  # Solar system objects stay very visible
        )

        return factor

    def _calculate_altitude_factor(self, altitude: float) -> float:
        """
        Atmospheric distortion affects planets significantly
        Optimal: 30-80 degrees
        Below horizon: impossible to observe
        """
        if altitude < ALTITUDE_BELOW_HORIZON:
            return ALTITUDE_FACTOR_BELOW_HORIZON
        elif altitude >= ALTITUDE_ZENITH_MAX:
            return ALTITUDE_FACTOR_NEAR_ZENITH
        elif altitude >= ALTITUDE_OPTIMAL_MIN_SOLAR:
            return ALTITUDE_FACTOR_OPTIMAL
        elif altitude >= ALTITUDE_GOOD_MIN_SOLAR:
            return ALTITUDE_FACTOR_GOOD_SOLAR
        elif altitude >= ALTITUDE_POOR_MIN_SOLAR:
            return ALTITUDE_FACTOR_POOR_SOLAR
        else:
            return ALTITUDE_FACTOR_VERY_POOR_SOLAR

    # normalize to 0-10 scale
    @staticmethod
    def _normalize_magnitude(score) -> float:
        return (score / SUN_MAGNITUDE_SCORE) * MAX_OBSERVABLE_SCORE

    @staticmethod
    def _normalize_size(score) -> float:
        return (score / MAX_SOLAR_SIZE) * MAX_OBSERVABLE_SCORE
