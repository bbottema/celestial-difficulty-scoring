"""
Scoring strategy for the Sun.

The Sun is a special case:
- Always the brightest object when visible (magnitude -26.7)
- REQUIRES solar filter for safe observation
- Only visible during daytime (altitude > 0)
- Weather is the main limiting factor

Safety is paramount - score is 0 without proper solar filter.
"""

from app.domain.model.scoring_context import ScoringContext
from app.domain.services.strategies.strategy_utils import calculate_weather_factor, get_size_arcmin
from app.utils.scoring_constants import *
from app.domain.services.strategies.base_strategy import IObservabilityScoringStrategy


class SunStrategy(IObservabilityScoringStrategy):
    """
    Scoring strategy for the Sun.

    Always brightest object when above horizon, but requires safety equipment.
    """

    def calculate_score(self, celestial_object, context: 'ScoringContext'):
        # Base score using unified flux formula (same as other strategies)
        flux = 10 ** (-0.4 * celestial_object.magnitude)
        # Sun: mag -26.74 → flux = 49,659,232,145
        # Use same formula: flux/100 * 0.80 + size/10 * 0.20
        size_arcmin = get_size_arcmin(celestial_object)
        base_score = (flux / 100.0) * 0.80 + (size_arcmin / 10.0) * 0.20

        # Equipment factor: MUST have solar filter (safety!)
        equipment_factor = self._calculate_equipment_factor(celestial_object, context)

        # Site factor: Light pollution doesn't affect the Sun
        site_factor = 1.0

        # Altitude factor: Only visible above horizon (obviously!)
        altitude_factor = self._calculate_altitude_factor(context.altitude)

        # Weather factor: Clouds significantly affect Sun viewing
        weather_factor = calculate_weather_factor(context)

        # Moon factor: N/A for Sun
        moon_factor = 1.0

        return base_score * equipment_factor * site_factor * altitude_factor * weather_factor * moon_factor

    def _calculate_equipment_factor(self, celestial_object, context: 'ScoringContext') -> float:
        """
        Equipment factor for Sun observation.

        TODO: When we add solar filter tracking to equipment, check for it here.
        For now, we return a reasonable value assuming proper equipment.
        """
        if not context.has_equipment():
            # NEVER observe Sun without equipment - extremely dangerous!
            # Return 0 for safety (though realistically Sun should never be
            # in a target list for naked-eye observation)
            return 0.0

        # TODO: Check for solar filter in equipment
        # if not context.has_solar_filter():
        #     return 0.0

        # Assume proper solar filter present if equipment exists
        # Magnification doesn't matter much for Sun (just seeing detail vs full disk)
        return 1.0

    def _calculate_altitude_factor(self, altitude: float) -> float:
        """
        Altitude factor for Sun.

        Sun is only visible above horizon (daytime).
        """
        if altitude < ALTITUDE_BELOW_HORIZON:
            return ALTITUDE_FACTOR_BELOW_HORIZON
        elif altitude >= ALTITUDE_OPTIMAL_MIN_SOLAR:
            return ALTITUDE_FACTOR_OPTIMAL
        elif altitude >= ALTITUDE_GOOD_MIN_SOLAR:
            return ALTITUDE_FACTOR_GOOD_SOLAR
        elif altitude >= ALTITUDE_POOR_MIN_SOLAR:
            return ALTITUDE_FACTOR_POOR_SOLAR
        else:
            return ALTITUDE_FACTOR_VERY_POOR_SOLAR

    def normalize_score(self, raw_score: float) -> float:
        """
        Normalize Sun scores to 0-25 scale.

        After unifying base score calculation with other strategies,
        use the SAME normalization formula to preserve magnitude ordering.

        Sun raw scores are MUCH higher due to extreme brightness (mag -26.74).
        """
        # Use same hybrid normalization as other strategies
        if raw_score <= 0:
            return 0.0
        elif raw_score > 10:
            # Logarithmic for Sun (extremely bright)
            # Sun (raw=397M): 15 + log10(397M) = 23.60
            import math
            return min(15 + math.log10(raw_score), 25.0)
        else:
            # Power scaling (unlikely for Sun, but for consistency)
            compressed = raw_score ** 0.35
            return min(compressed * 15.0, 25.0)
