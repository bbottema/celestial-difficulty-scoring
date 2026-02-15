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
from app.domain.services.strategies.strategy_utils import calculate_weather_factor, calculate_moon_proximity_factor, get_size_arcmin
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
        # Use flux directly (not normalized) - it's on a sensible scale already
        flux = 10 ** (-0.4 * celestial_object.magnitude)
        # Moon flux: 10^(5.04) = 109,648
        # Jupiter flux: 10^(0.96) = 9.12
        # Saturn flux: 10^(-0.2) = 0.631

        # Size is in arcminutes (0.1-30 range)
        # Only add size contribution for objects >= 1 arcmin (extended objects)
        # For tiny objects (planets < 1'), size shouldn't outweigh brightness
        size_arcmin = get_size_arcmin(celestial_object)
        size_contribution = (size_arcmin / 10.0) * 0.20 if size_arcmin >= 1.0 else 0.0
        base_score = (flux / 100.0) * 0.80 + size_contribution

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
        size_arcmin = get_size_arcmin(celestial_object)
        
        if not context.has_equipment():
            # Naked-eye viewing depends on size
            # Large objects (Moon) are spectacular naked-eye
            # Planets are visible but lack detail without magnification
            if size_arcmin > 10.0:  # Moon-like (>10 arcmin)
                return 0.95  # Essentially perfect naked-eye
            elif size_arcmin > 1.0:  # Large extended objects (comets)
                return 0.80  # Good naked-eye
            elif celestial_object.magnitude < 0.0:  # Very bright planets (Venus, Jupiter)
                return 0.75  # Bright but tiny - visible but no detail
            else:  # Dimmer planets (Mars, Saturn, etc)
                return 0.50  # Visible but really need equipment

        magnification = context.get_magnification()

        # Magnification preferences based on angular size
        if size_arcmin > 10.0:  # Moon-like objects (huge)
            # Prefer LOW magnification (wide field, entire object visible)
            if magnification <= 50:
                return 1.2  # Optimal
            elif magnification <= 100:
                return 1.0  # Acceptable
            else:
                return 0.8  # Too much mag, loses field of view

        elif size_arcmin > 1.0:  # Large comets/extended objects
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
        """
        Normalize magnitude score for reflective objects.

        Uses Moon as reference (not Sun) because dividing by Sun's huge magnitude
        score (49 billion) crushes planets to zero.
        """
        return (score / MOON_MAGNITUDE_SCORE) * MAX_OBSERVABLE_SCORE

    @staticmethod
    def _normalize_size(score) -> float:
        """Normalize size score for reflective objects."""
        return (score / MAX_SOLAR_SIZE) * MAX_OBSERVABLE_SCORE

    def normalize_score(self, raw_score: float) -> float:
        """
        Normalize reflected light scores to 0-25 scale.

        Actual observed raw score ranges after all factors:
        - Moon: ~3-6 (mag -12.6, size 31')
        - Jupiter: ~0.08-0.15 (mag -2.4, size 0.8')
        - Mars: ~0.015-0.03 (mag -1.0, size 0.15')
        - Saturn: ~0.03-0.06 (mag 0.5, size 0.27')

        Strategy: Moon dominates (brightest natural object), planets scale up significantly.
        Using logarithmic-ish scaling to compress the huge magnitude range.
        """
        # Empirical mapping:
        # Moon (raw ~5): 5 * 3.5 = 17.5 ✓ (should be 15-20)
        # Jupiter (raw ~0.1): 0.1 * 120 = 12 ✓ (should be 10-15)
        # Mars (raw ~0.02): needs to beat Saturn
        # BUT: Simple multiplier doesn't work - need non-linear

        # Hybrid normalization: handles both very bright (Moon) and normal (planets)
        # For very bright objects (raw > 10): use logarithmic scaling to avoid capping
        # For normal objects (raw <= 10): use power scaling
        if raw_score <= 0:
            return 0.0
        elif raw_score > 10:
            # Logarithmic for Moon and other very bright objects
            # Moon (raw=865): 15 + log10(865) = 17.94
            import math
            return min(15 + math.log10(raw_score), 25.0)
        else:
            # Power scaling for planets
            # Jupiter (raw=0.07): 0.07^0.35 * 15 = 5.92
            compressed = raw_score ** 0.35
            return min(compressed * 15.0, 25.0)
