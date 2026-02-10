from app.domain.model.scoring_context import ScoringContext
from app.utils.scoring_constants import *
from app.utils.scoring_presets import get_active_preset


def calculate_weather_factor(context: 'ScoringContext') -> float:
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


def calculate_moon_proximity_factor(celestial_object, context: 'ScoringContext') -> float:
    """
    Moon proximity penalty - bright moon near target washes out faint objects.
    Solar system objects (planets, sun) are bright enough to ignore moon interference.

    Formula: penalty = (illumination / 100) * (60 / max(separation, 5))²

    Examples:
    - 100% illumination, 5° separation → factor ≈ 0.03 (nearly invisible)
    - 100% illumination, 30° separation → factor = 0.75 (still impacted)
    - 100% illumination, 60° separation → factor = 1.0 (no penalty)
    - 50% illumination, any distance → 50% of above penalties
    - Moon below horizon → factor = 1.0 (no penalty)
    """
    if not context.moon_conditions or not context.moon_conditions.is_above_horizon():
        return 1.0  # No moon = no penalty

    # Solar system objects unaffected by moon (bright enough)
    if celestial_object.object_type in ["Planet", "Sun", "Moon"]:
        return 1.0

    moon = context.moon_conditions
    separation = moon.calculate_separation(celestial_object.ra, celestial_object.dec)

    # Beyond 60° separation, moon has negligible impact
    if separation >= 60.0:
        return 1.0

    # Minimum separation of 1.0 degree to avoid extreme penalties
    # Objects closer than 1° are essentially occluded
    separation = max(separation, 1.0)

    # Angular distance penalty (inverse square falloff from 60°)
    # At 5°: (60/5)² = 144 → capped to 1.0 → nearly invisible with full moon
    # At 15°: (60/15)² = 16 → capped to 1.0 → very strong penalty
    # At 30°: (60/30)² = 4 → capped to 1.0 → still strong penalty
    # At 60°: handled above (no penalty)
    distance_penalty = min((60.0 / separation) ** 2, 1.0)

    # Illumination factor (linear with moon brightness)
    illumination_factor = moon.illumination / 100.0

    # Combined penalty
    penalty = illumination_factor * distance_penalty

    return max(1.0 - penalty, 0.0)  # Ensure non-negative
