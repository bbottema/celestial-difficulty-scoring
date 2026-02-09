"""
Scoring presets for different user preferences.

Provides switchable constant sets that tune the algorithm's behavior
for different observation planning styles:
- "Friendly Planner": Encourages exploration, fewer hard rejections
- "Strict Realism": Reduces false positives, conservative recommendations

Users can select their preferred preset in the settings tab.

All constant values are defined in scoring_constants.py with full documentation.
This module simply selects which constants to use for each preset.
"""

from dataclasses import dataclass
from app.utils.scoring_constants import (
    # Weather factors
    WEATHER_FACTOR_OVERCAST,
    WEATHER_FACTOR_OVERCAST_STRICT,
    WEATHER_FACTOR_MOSTLY_CLOUDY_FRIENDLY,
    WEATHER_FACTOR_MOSTLY_CLOUDY_STRICT,
    WEATHER_FACTOR_PARTLY_CLOUDY,
    WEATHER_FACTOR_PARTLY_CLOUDY_FRIENDLY,
    WEATHER_FACTOR_FEW_CLOUDS,

    # Altitude factors
    ALTITUDE_FACTOR_VERY_POOR_DEEPSKY_FRIENDLY,
    ALTITUDE_FACTOR_VERY_POOR_DEEPSKY_STRICT,

    # Light pollution floors
    LIGHT_POLLUTION_MIN_FACTOR_DEEPSKY_FRIENDLY,
    LIGHT_POLLUTION_MIN_FACTOR_DEEPSKY,
    LIGHT_POLLUTION_MIN_FACTOR_LARGE_FRIENDLY,
    LIGHT_POLLUTION_MIN_FACTOR_LARGE,
    LIGHT_POLLUTION_MIN_FACTOR_LARGE_STRICT,

    # Aperture factors
    APERTURE_FACTOR_LARGE_FRIENDLY,
    APERTURE_FACTOR_LARGE_STRICT,
    APERTURE_FACTOR_MEDIUM_FRIENDLY,
    APERTURE_FACTOR_MEDIUM_STRICT,
    APERTURE_FACTOR_TINY,
    APERTURE_FACTOR_TINY_STRICT,
)


@dataclass(frozen=True)
class ScoringPreset:
    """
    A collection of tunable scoring constants that define algorithm behavior.

    Frozen dataclass ensures presets cannot be accidentally modified at runtime.
    All values reference constants from scoring_constants.py.
    """

    name: str
    description: str

    # Weather factors
    weather_factor_few_clouds: float
    weather_factor_partly_cloudy: float
    weather_factor_mostly_cloudy: float
    weather_factor_overcast: float

    # Altitude factors (deep-sky)
    altitude_factor_very_poor_deepsky: float

    # Light pollution minimum floors
    light_pollution_min_factor_deepsky: float
    light_pollution_min_factor_large: float

    # Aperture factors (deep-sky emphasis)
    aperture_factor_large: float
    aperture_factor_medium: float
    aperture_factor_tiny: float


# ==============================================================================
# PRESET DEFINITIONS
# ==============================================================================

PRESET_FRIENDLY = ScoringPreset(
    name="Friendly Planner",
    description=(
        "Encourages trying challenging targets. Produces longer target lists "
        "with more 'maybe' results. Best for beginners exploring possibilities "
        "or observers willing to attempt difficult targets."
    ),

    # Weather - slightly more lenient
    weather_factor_few_clouds=WEATHER_FACTOR_FEW_CLOUDS,
    weather_factor_partly_cloudy=WEATHER_FACTOR_PARTLY_CLOUDY_FRIENDLY,
    weather_factor_mostly_cloudy=WEATHER_FACTOR_MOSTLY_CLOUDY_FRIENDLY,
    weather_factor_overcast=WEATHER_FACTOR_OVERCAST,

    # Altitude - less harsh at low altitude
    altitude_factor_very_poor_deepsky=ALTITUDE_FACTOR_VERY_POOR_DEEPSKY_FRIENDLY,

    # Light pollution - slightly higher floors
    light_pollution_min_factor_deepsky=LIGHT_POLLUTION_MIN_FACTOR_DEEPSKY_FRIENDLY,
    light_pollution_min_factor_large=LIGHT_POLLUTION_MIN_FACTOR_LARGE_FRIENDLY,

    # Aperture - moderate scaling
    aperture_factor_large=APERTURE_FACTOR_LARGE_FRIENDLY,
    aperture_factor_medium=APERTURE_FACTOR_MEDIUM_FRIENDLY,
    aperture_factor_tiny=APERTURE_FACTOR_TINY,
)

PRESET_STRICT = ScoringPreset(
    name="Strict Realism",
    description=(
        "Reduces false positives and wasted observation time. Produces shorter "
        "target lists with higher confidence. Best for experienced observers, "
        "time-limited dark-sky trips, or astrophotography planning."
    ),

    # Weather - more conservative
    weather_factor_few_clouds=WEATHER_FACTOR_FEW_CLOUDS,
    weather_factor_partly_cloudy=WEATHER_FACTOR_PARTLY_CLOUDY,
    weather_factor_mostly_cloudy=WEATHER_FACTOR_MOSTLY_CLOUDY_STRICT,
    weather_factor_overcast=WEATHER_FACTOR_OVERCAST_STRICT,

    # Altitude - harsher at low altitude
    altitude_factor_very_poor_deepsky=ALTITUDE_FACTOR_VERY_POOR_DEEPSKY_STRICT,

    # Light pollution - lower floors (honest about impossibility)
    light_pollution_min_factor_deepsky=LIGHT_POLLUTION_MIN_FACTOR_DEEPSKY,
    light_pollution_min_factor_large=LIGHT_POLLUTION_MIN_FACTOR_LARGE_STRICT,

    # Aperture - stronger scaling (aperture really matters)
    aperture_factor_large=APERTURE_FACTOR_LARGE_STRICT,
    aperture_factor_medium=APERTURE_FACTOR_MEDIUM_STRICT,
    aperture_factor_tiny=APERTURE_FACTOR_TINY_STRICT,
)

# Default preset for new users
DEFAULT_PRESET = PRESET_FRIENDLY

# All available presets (for UI dropdown)
AVAILABLE_PRESETS = [PRESET_FRIENDLY, PRESET_STRICT]


# ==============================================================================
# PRESET SELECTION
# ==============================================================================

# Global active preset (can be changed via settings)
_active_preset: ScoringPreset = DEFAULT_PRESET


def get_active_preset() -> ScoringPreset:
    """Get the currently active scoring preset."""
    return _active_preset


def set_active_preset(preset: ScoringPreset) -> None:
    """
    Set the active scoring preset.

    Args:
        preset: The preset to activate (must be one of AVAILABLE_PRESETS)

    Raises:
        ValueError: If preset is not in AVAILABLE_PRESETS
    """
    global _active_preset
    if preset not in AVAILABLE_PRESETS:
        raise ValueError(
            f"Invalid preset: {preset.name}. "
            f"Available presets: {[p.name for p in AVAILABLE_PRESETS]}"
        )
    _active_preset = preset


def set_active_preset_by_name(preset_name: str) -> None:
    """
    Set the active scoring preset by name.

    Args:
        preset_name: Name of the preset to activate

    Raises:
        ValueError: If preset_name doesn't match any available preset
    """
    for preset in AVAILABLE_PRESETS:
        if preset.name == preset_name:
            set_active_preset(preset)
            return

    raise ValueError(
        f"Unknown preset name: '{preset_name}'. "
        f"Available: {[p.name for p in AVAILABLE_PRESETS]}"
    )


def reset_to_default_preset() -> None:
    """Reset the active preset to default (Friendly Planner)."""
    global _active_preset
    _active_preset = DEFAULT_PRESET
