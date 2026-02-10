"""
Scoring strategy for solar-illuminated objects (Moon, Planets, Comets, Asteroids).

These objects reflect sunlight and share common characteristics:
- Brightness dominates (magnitude-based scoring)
- Angular size determines optimal magnification needs
- Essentially unaffected by light pollution (they're bright!)
- Aperture helps with fainter objects (comets, asteroids)

This unified approach eliminates special cases for Moon vs Planets
by treating them through their physical properties.
"""

from app.domain.model.scoring_context import ScoringContext
from app.domain.services.strategies.strategy_utils import calculate_weather_factor, calculate_moon_proximity_factor
from app.utils.scoring_constants import *
from app.domain.services.strategies.base_strategy import IObservabilityScoringStrategy


class ReflectedLightStrategy(IObservabilityScoringStrategy):
    """
    Scoring strategy for objects that reflect sunlight (Moon, Planets, Comets).

    Key principle: Brightness (magnitude) dominates, angular size determines
    optimal viewing strategy (magnification needs).
    """

    def calculate_score(self, celestial_object, context: 'ScoringContext'):
        # Base score from brightness and size
        # Brightness dominates (makes object visible), size adds detail
        magnitude_score = self._normalize_magnitude(10 ** (-0.4 * celestial_object.magnitude))
        size_score = self._normalize_size(celestial_object.size)
        base_score = magnitude_score * 0.80 + size_score * 0.20  # Brightness-dominant weighting

        # Equipment factor: magnification needs depend on angular size
        equipment_factor = self._calculate_equipment_factor(celestial_object, context)

        # Site factor: bright reflective objects are essentially unaffected by light pollution
        site_factor = self._calculate_site_factor(celestial_object, context)

        # Altitude factor: atmosphere matters
        altitude_factor = self._calculate_altitude_factor(context.altitude)

        # Weather factor: clouds affect all objects
        weather_factor = calculate_weather_factor(context)

        # Moon proximity factor: doesn't affect solar system objects (they're too bright)
        moon_factor = calculate_moon_proximity_factor(celestial_object, context)

        return base_score * equipment_factor * site_factor * altitude_factor * weather_factor * moon_factor

    def _calculate_equipment_factor(self, celestial_object, context: 'ScoringContext') -> float:
        """
        Equipment factor based on angular size and magnification.

        Large objects (Moon): prefer low magnification, great naked-eye
        Tiny objects (Planets): need high magnification to see detail
        Medium objects (Large comets): medium magnification
        """
        if not context.has_equipment():
            # Naked-eye viewing depends on size
            # Large objects (Moon) are spectacular naked-eye
            # Planets are visible but lack detail without magnification
            if celestial_object.size > 10.0:  # Moon-like (>10 arcmin)
                return 0.95  # Essentially perfect naked-eye
            elif celestial_object.size > 1.0:  # Large extended objects (comets)
                return 0.80  # Good naked-eye
            elif celestial_object.magnitude < 0.0:  # Very bright planets (Venus, Jupiter)
                return 0.75  # Bright but tiny - visible but no detail
            else:  # Dimmer planets (Mars, Saturn, etc)
                return 0.50  # Visible but really need equipment

        magnification = context.get_magnification()

        # Magnification preferences based on angular size
        if celestial_object.size > 10.0:  # Moon-like objects (huge)
            # Prefer LOW magnification (wide field, entire object visible)
            if magnification <= 50:
                return 1.2  # Optimal
            elif magnification <= 100:
                return 1.0  # Acceptable
            else:
                return 0.8  # Too much mag, loses field of view

        elif celestial_object.size > 1.0:  # Large comets/extended objects
            # Prefer LOW to MEDIUM magnification
            if magnification <= 80:
                return 1.2  # Optimal
            elif magnification <= 150:
                return 1.0  # Acceptable
            else:
                return 0.9  # Bit high

        else:  # Planets (tiny - size < 1 arcmin, typically < 1 arcsec!)
            # Prefer HIGH magnification to see detail
            if MAGNIFICATION_PLANETARY_OPTIMAL_MIN <= magnification <= MAGNIFICATION_PLANETARY_OPTIMAL_MAX:
                return MAGNIFICATION_FACTOR_OPTIMAL
            elif 100 <= magnification < MAGNIFICATION_PLANETARY_OPTIMAL_MIN or \
                 MAGNIFICATION_PLANETARY_OPTIMAL_MAX < magnification <= 400:
                return MAGNIFICATION_FACTOR_ACCEPTABLE
            elif MAGNIFICATION_PLANETARY_TOO_LOW <= magnification < 100:
                return 0.8  # Too low - can't see detail
            else:
                return MAGNIFICATION_FACTOR_TOO_HIGH

    def _calculate_site_factor(self, celestial_object, context: 'ScoringContext') -> float:
        """
        Light pollution impact on bright reflective objects.

        These objects are so bright that light pollution barely affects them.
        Moon is essentially unaffected. Planets have minimal impact.
        """
        if not context.observation_site:
            return 0.95  # Small penalty for unknown site

        # All reflective objects are bright enough to be minimally affected
        # No need for special Moon case - it's handled by its magnitude (-12)
        # vs planets (typically -4 to +1)

        # Use minimal penalty - these objects cut through light pollution
        bortle = context.get_bortle_number()
        penalty_per_bortle = 0.005  # 0.5% per Bortle level (very minimal)
        factor = 1.0 - (bortle * penalty_per_bortle)

        return max(factor, 0.95)  # Never drop below 95%

    def _calculate_altitude_factor(self, altitude: float) -> float:
        """Altitude factor - same as solar system strategy."""
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

    @staticmethod
    def _normalize_magnitude(score) -> float:
        """Normalize magnitude score for reflective objects."""
        return (score / SUN_MAGNITUDE_SCORE) * MAX_OBSERVABLE_SCORE

    @staticmethod
    def _normalize_size(score) -> float:
        """Normalize size score for reflective objects."""
        return (score / MAX_SOLAR_SIZE) * MAX_OBSERVABLE_SCORE
