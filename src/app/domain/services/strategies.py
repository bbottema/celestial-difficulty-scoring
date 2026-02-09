from abc import abstractmethod, ABC

from app.domain.model.scoring_context import ScoringContext
from app.utils.scoring_constants import *
from app.utils.scoring_presets import get_active_preset
from app.utils.light_pollution_models import (
    calculate_light_pollution_factor_by_limiting_magnitude,
    calculate_light_pollution_factor_with_surface_brightness
)


def _calculate_weather_factor(context: 'ScoringContext') -> float:
    """
    Weather impact on observability.
    Cloud cover reduces visibility proportionally.
    Uses active preset to determine factor values, allowing users to choose
    between 'Friendly' (more lenient) and 'Strict' (more conservative) scoring.
    Shared across all strategies since weather affects everything equally.
    """
    if not context.weather:
        return WEATHER_FACTOR_CLEAR  # No weather data = assume clear

    preset = get_active_preset()
    cloud_cover = context.weather.get('cloud_cover', 0)

    if cloud_cover >= WEATHER_CLOUD_COVER_OVERCAST:
        return preset.weather_factor_overcast
    elif cloud_cover >= WEATHER_CLOUD_COVER_MOSTLY_CLOUDY:
        return preset.weather_factor_mostly_cloudy
    elif cloud_cover >= WEATHER_CLOUD_COVER_PARTLY_CLOUDY:
        return preset.weather_factor_partly_cloudy
    elif cloud_cover >= WEATHER_CLOUD_COVER_FEW_CLOUDS:
        return preset.weather_factor_few_clouds
    else:
        return WEATHER_FACTOR_CLEAR


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
        site_factor = self._calculate_site_factor(celestial_object, context)

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
        weather_factor = _calculate_weather_factor(context)

        return base_score * equipment_factor * site_factor * altitude_factor * weather_factor

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
