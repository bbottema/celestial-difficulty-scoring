from abc import abstractmethod, ABC
from typing import TYPE_CHECKING

from app.utils.constants import *

if TYPE_CHECKING:
    from app.domain.model.scoring_context import ScoringContext


def _calculate_weather_factor(context: 'ScoringContext') -> float:
    """
    Weather impact on observability.
    Cloud cover reduces visibility proportionally.
    Shared across all strategies since weather affects everything equally.
    """
    if not context.weather:
        return 1.0  # No weather data = assume clear

    cloud_cover = context.weather.get('cloud_cover', 0)

    # Cloud cover is 0-100 percentage
    # 0% = clear (factor 1.0)
    # 100% = overcast (factor 0.05, nearly impossible)
    if cloud_cover >= 100:
        return 0.05  # Overcast - nearly impossible
    elif cloud_cover >= 75:
        return 0.25  # Mostly cloudy - very difficult
    elif cloud_cover >= 50:
        return 0.50  # Partly cloudy - moderate impact
    elif cloud_cover >= 25:
        return 0.75  # Few clouds - minor impact
    else:
        return 1.0  # Clear skies


class IObservabilityScoringStrategy(ABC):
    @abstractmethod
    def calculate_score(self, celestial_object, context: 'ScoringContext') -> float:
        pass


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
        site_factor = self._calculate_site_factor(context)

        # Altitude factor: atmosphere matters more for planets
        altitude_factor = self._calculate_altitude_factor(context.altitude)

        # Weather factor: clouds affect all objects
        weather_factor = _calculate_weather_factor(context)

        return base_score * equipment_factor * site_factor * altitude_factor * weather_factor

    def _calculate_equipment_factor(self, celestial_object, context: 'ScoringContext') -> float:
        """
        For planets: higher magnification = better (see more detail)
        Target: 150-300x for planets
        """
        if not context.has_equipment():
            return 0.5  # Significant penalty without equipment

        magnification = context.get_magnification()

        # Optimal magnification range for planets: 150-300x
        if 150 <= magnification <= 300:
            return 1.2  # Bonus for ideal magnification
        elif 100 <= magnification < 150 or 300 < magnification <= 400:
            return 1.0  # Acceptable magnification
        elif 50 <= magnification < 100:
            return 0.8  # Low magnification - less detail
        else:
            return 0.6  # Too low or too high

    def _calculate_site_factor(self, context: 'ScoringContext') -> float:
        """Light pollution barely affects bright solar system objects"""
        if not context.observation_site:
            return 0.9  # Small penalty for unknown site

        bortle = context.get_bortle_number()
        # Minimal penalty even in cities - planets are very bright
        return 1.0 - (bortle * 0.01)  # Max 9% penalty in Bortle 9

    def _calculate_altitude_factor(self, altitude: float) -> float:
        """
        Atmospheric distortion affects planets significantly
        Optimal: 30-80 degrees
        """
        if altitude >= 80:
            return 0.95  # Near zenith - some distortion
        elif altitude >= 30:
            return 1.0  # Optimal viewing
        elif altitude >= 20:
            return 0.85  # More atmosphere
        elif altitude >= 10:
            return 0.65  # Significant atmosphere
        else:
            return 0.4  # Too low - heavy atmosphere

    # normalize to 0-10 scale
    @staticmethod
    def _normalize_magnitude(score) -> float:
        return (score / sun_solar_magnitude_score) * max_observable_score

    @staticmethod
    def _normalize_size(score) -> float:
        return (score / max_solar_size) * max_observable_score


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
        weather_factor = _calculate_weather_factor(context)

        return base_score * equipment_factor * site_factor * altitude_factor * weather_factor

    def _calculate_equipment_factor(self, celestial_object, context: 'ScoringContext') -> float:
        """
        For deep-sky: aperture is critical (light gathering power)
        More aperture = see fainter objects
        """
        if not context.has_equipment():
            return 0.3  # Major penalty - faint objects need equipment

        aperture = context.get_aperture_mm()

        # Aperture impact depends on object brightness
        # Faint objects benefit much more from large aperture
        if celestial_object.magnitude <= 6:  # Bright deep-sky
            # Even small scopes work
            if aperture >= 100:
                return 1.1
            elif aperture >= 70:
                return 1.0
            else:
                return 0.8
        elif celestial_object.magnitude <= 9:  # Medium faint
            # Need decent aperture
            if aperture >= 200:
                return 1.3
            elif aperture >= 150:
                return 1.1
            elif aperture >= 100:
                return 0.9
            else:
                return 0.6
        else:  # Very faint (>9 mag)
            # Really need large aperture
            if aperture >= 250:
                return 1.4
            elif aperture >= 200:
                return 1.2
            elif aperture >= 150:
                return 0.9
            elif aperture >= 100:
                return 0.6
            else:
                return 0.3  # Very difficult with small scope

    def _calculate_site_factor(self, celestial_object, context: 'ScoringContext') -> float:
        """Light pollution is CRITICAL for faint deep-sky objects"""
        if not context.observation_site:
            return 0.7  # Moderate penalty for unknown site

        bortle = context.get_bortle_number()

        # Fainter objects suffer much more from light pollution
        if celestial_object.magnitude <= 6:  # Bright deep-sky
            # Less affected by light pollution
            penalty_per_bortle = 0.06
        elif celestial_object.magnitude <= 9:  # Medium faint
            penalty_per_bortle = 0.10
        else:  # Very faint
            penalty_per_bortle = 0.13

        factor = 1.0 - (bortle * penalty_per_bortle)
        return max(factor, 0.1)  # Never go below 0.1

    def _calculate_altitude_factor(self, altitude: float) -> float:
        """Higher altitude = less atmosphere to penetrate"""
        if altitude >= 60:
            return 1.0  # Optimal
        elif altitude >= 40:
            return 0.95
        elif altitude >= 30:
            return 0.85
        elif altitude >= 20:
            return 0.70
        else:
            return 0.5  # Low altitude - difficult

    @staticmethod
    def _normalize_magnitude(score) -> float:
        return (score / sirius_deepsky_magnitude_score) * max_observable_score

    @staticmethod
    def _normalize_size(score) -> float:
        return (score / max_deepsky_size) * max_observable_score


class LargeFaintObjectScoringStrategy(IObservabilityScoringStrategy):
    """
    Scoring strategy for large, faint extended objects (e.g., M31, IC 1396).
    These need wide field of view (low magnification) and dark skies.
    """

    def calculate_score(self, celestial_object, context: 'ScoringContext'):
        # Adjust the magnitude score to increase with brightness (lower magnitude = higher score)
        magnitude_score = max(0, (faint_object_magnitude_baseline - celestial_object.magnitude))

        # Adjust the size score to increase with size
        size_score = min(celestial_object.size / max_deepsky_size, 1)  # Cap the size score at 1

        # Combine scores
        base_score = (0.4 * magnitude_score) + (0.6 * size_score)
        base_score = min(base_score, max_observable_score) / 10

        # Equipment factor: need wide field of view (low magnification)
        equipment_factor = self._calculate_equipment_factor(celestial_object, context)

        # Site factor: dark skies are critical for faint nebulosity
        site_factor = self._calculate_site_factor(context)

        # Altitude factor: higher is better
        altitude_factor = self._calculate_altitude_factor(context.altitude)

        # Weather factor: clouds affect all objects
        weather_factor = _calculate_weather_factor(context)

        return base_score * equipment_factor * site_factor * altitude_factor * weather_factor

    def _calculate_equipment_factor(self, celestial_object, context: 'ScoringContext') -> float:
        """
        Large objects need LOW magnification for wide field of view.
        Need to fit the entire object in the eyepiece.
        """
        if not context.has_equipment():
            return 0.4  # Significant penalty

        magnification = context.get_magnification()

        # For large objects (>60 arcmin), we want low magnification
        # Optimal: 30-80x for wide field
        if 30 <= magnification <= 80:
            return 1.3  # Bonus for wide field
        elif 20 <= magnification < 30 or 80 < magnification <= 120:
            return 1.0  # Acceptable
        elif magnification < 20:
            return 0.9  # Too wide - dimmer image
        else:
            return 0.6  # Too much magnification - can't see whole object

    def _calculate_site_factor(self, context: 'ScoringContext') -> float:
        """Dark skies are critical for faint extended nebulosity"""
        if not context.observation_site:
            return 0.6  # Significant penalty

        bortle = context.get_bortle_number()

        # These objects are very affected by light pollution
        # Even worse than standard deep-sky because of low surface brightness
        penalty_per_bortle = 0.12
        factor = 1.0 - (bortle * penalty_per_bortle)
        return max(factor, 0.05)  # Can become nearly impossible in cities

    def _calculate_altitude_factor(self, altitude: float) -> float:
        """Higher altitude = better for faint objects"""
        if altitude >= 50:
            return 1.0
        elif altitude >= 35:
            return 0.90
        elif altitude >= 25:
            return 0.75
        else:
            return 0.5
