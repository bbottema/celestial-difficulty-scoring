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

    # Objects within 1° of moon are essentially occluded
    if separation < 1.0:
        return 0.0

    # Minimum separation of 5.0 degrees to avoid complete obliteration
    # Objects closer than 5° are extremely difficult to observe near bright moon
    separation = max(separation, 5.0)

    # Angular distance penalty (inverse square falloff)
    # Use ratio (60° / separation)² but with smooth scaling
    # At separation = 5°:  (60/5)²  = 144 → strong penalty
    # At separation = 10°: (60/10)² = 36  → severe penalty
    # At separation = 20°: (60/20)² = 9   → moderate penalty
    # At separation = 30°: (60/30)² = 4   → mild penalty
    # At separation = 60°: handled above (no penalty)

    # Scale factor to convert inverse square to reasonable penalty range
    # We want 5° to give ~97% penalty, 10° to give ~90% penalty, 30° to give ~50% penalty
    raw_penalty = (60.0 / separation) ** 2

    # Normalize: at sep=5°, raw=144 → we want penalty≈0.97
    # At sep=30°, raw=4 → we want penalty≈0.5
    # Using formula: penalty = 1 - (1 / (1 + raw/C))
    # Where C controls the scaling. C=3 gives reasonable results:
    # sep=5°: 1-(1/(1+144/3)) = 1-(1/49) ≈ 0.98
    # sep=10°: 1-(1/(1+36/3)) = 1-(1/13) ≈ 0.92
    # sep=30°: 1-(1/(1+4/3)) = 1-(1/2.33) ≈ 0.57
    C = 3.0
    distance_penalty = 1.0 - (1.0 / (1.0 + raw_penalty / C))

    # Illumination factor (linear with moon brightness)
    illumination_factor = moon.illumination / 100.0

    # Combined penalty
    penalty = illumination_factor * distance_penalty

    return max(1.0 - penalty, 0.0)  # Ensure non-negative
