"""
Scoring constants for celestial observability calculations.

All magic numbers extracted into named constants with documentation
explaining their derivation and meaning.

Following Clean Code principles (Uncle Bob would approve!)
"""

# ==============================================================================
# WEATHER THRESHOLDS AND FACTORS
# ==============================================================================

# Cloud cover thresholds (percentage)
WEATHER_CLOUD_COVER_OVERCAST = 100  # percent
"""100% cloud cover = overcast conditions. Based on meteorological standards."""

WEATHER_CLOUD_COVER_MOSTLY_CLOUDY = 75  # percent
"""75%+ cloud cover = mostly cloudy. Significant obstruction."""

WEATHER_CLOUD_COVER_PARTLY_CLOUDY = 50  # percent
"""50% cloud cover = partly cloudy. Moderate obstruction."""

WEATHER_CLOUD_COVER_FEW_CLOUDS = 25  # percent
"""25% cloud cover = few clouds. Minor obstruction."""

# Weather impact factors (multipliers)
WEATHER_FACTOR_OVERCAST = 0.05
"""
Overcast conditions (100% cloud cover).
Only brightest objects (Sun/Moon) barely visible.
95% reduction in observability.
"""

WEATHER_FACTOR_MOSTLY_CLOUDY = 0.25
"""
Mostly cloudy conditions (75%+ cloud cover).
75% reduction in observability.
"""

WEATHER_FACTOR_PARTLY_CLOUDY = 0.50
"""
Partly cloudy conditions (50% cloud cover).
50% reduction in observability - proportional to coverage.
"""

WEATHER_FACTOR_FEW_CLOUDS = 0.75
"""
Few clouds (25% cloud cover).
25% reduction in observability.
"""

WEATHER_FACTOR_CLEAR = 1.0
"""
Clear skies (< 25% cloud cover).
No weather penalty.
"""

# ==============================================================================
# ALTITUDE THRESHOLDS AND FACTORS
# ==============================================================================

# Altitude thresholds (degrees above horizon)
ALTITUDE_BELOW_HORIZON = 0  # degrees
"""Objects below horizon are impossible to observe."""

ALTITUDE_OPTIMAL_MIN_SOLAR = 30  # degrees
"""
Optimal minimum altitude for solar system objects (planets, moon).
Below 30°, airmass increases significantly:
  - At 30°: airmass ≈ 2.0 (double atmosphere)
  - At 20°: airmass ≈ 2.9 (triple atmosphere)
"""

ALTITUDE_ZENITH_MAX = 80  # degrees
"""Near zenith (80-90°) can have slight distortion due to overhead viewing angle."""

ALTITUDE_GOOD_MIN_SOLAR = 20  # degrees
"""Acceptable viewing altitude for planets."""

ALTITUDE_POOR_MIN_SOLAR = 10  # degrees
"""Poor viewing altitude - significant atmospheric effects."""

ALTITUDE_OPTIMAL_MIN_DEEPSKY = 60  # degrees
"""Optimal altitude for deep-sky objects - minimal atmospheric extinction."""

ALTITUDE_GOOD_MIN_DEEPSKY = 40  # degrees

ALTITUDE_FAIR_MIN_DEEPSKY = 30  # degrees

ALTITUDE_POOR_MIN_DEEPSKY = 20  # degrees

ALTITUDE_OPTIMAL_MIN_LARGE = 50  # degrees
"""Optimal altitude for large faint objects."""

ALTITUDE_GOOD_MIN_LARGE = 35  # degrees

ALTITUDE_FAIR_MIN_LARGE = 25  # degrees

# Altitude impact factors
ALTITUDE_FACTOR_BELOW_HORIZON = 0.0
"""Objects below horizon cannot be observed."""

ALTITUDE_FACTOR_OPTIMAL = 1.0
"""No atmospheric penalty at optimal altitude."""

ALTITUDE_FACTOR_NEAR_ZENITH = 0.95
"""Slight penalty near zenith (>80°) due to overhead viewing angle."""

ALTITUDE_FACTOR_GOOD_SOLAR = 0.85
"""15% atmospheric reduction for planets at 20-30° altitude."""

ALTITUDE_FACTOR_POOR_SOLAR = 0.65
"""35% atmospheric reduction for planets at 10-20° altitude."""

ALTITUDE_FACTOR_VERY_POOR_SOLAR = 0.4
"""60% atmospheric reduction for planets at <10° altitude."""

ALTITUDE_FACTOR_GOOD_DEEPSKY = 0.95
"""5% reduction for DSOs at 40-60° altitude."""

ALTITUDE_FACTOR_FAIR_DEEPSKY = 0.85
"""15% reduction for DSOs at 30-40° altitude."""

ALTITUDE_FACTOR_POOR_DEEPSKY = 0.70
"""30% reduction for DSOs at 20-30° altitude."""

ALTITUDE_FACTOR_VERY_POOR_DEEPSKY = 0.5
"""50% reduction for DSOs at <20° altitude."""

ALTITUDE_FACTOR_GOOD_LARGE = 0.90
"""10% reduction for large objects at 35-50° altitude."""

ALTITUDE_FACTOR_FAIR_LARGE = 0.75
"""25% reduction for large objects at 25-35° altitude."""

ALTITUDE_FACTOR_POOR_LARGE = 0.5
"""50% reduction for large objects at <25° altitude."""

# ==============================================================================
# MAGNIFICATION THRESHOLDS AND FACTORS
# ==============================================================================

# Magnification ranges for different object types
MAGNIFICATION_PLANETARY_OPTIMAL_MIN = 150
"""
Minimum magnification for planetary detail.
Below this, cloud bands and surface features become hard to resolve.
"""

MAGNIFICATION_PLANETARY_OPTIMAL_MAX = 300
"""
Maximum useful magnification for planets before atmospheric seeing degrades image.
General rule: 50x per inch of aperture (e.g., 200mm = 8" → 400x max, but 300x practical)
"""

MAGNIFICATION_PLANETARY_TOO_LOW = 50
"""Below 50x, planets appear as small disks without detail."""

MAGNIFICATION_LARGE_OBJECT_MAX = 50
"""
Large objects (>30 arcmin) need low magnification for wide field of view.
Above 50x, object doesn't fit in eyepiece field of view.
"""

MAGNIFICATION_LARGE_OBJECT_OPTIMAL_MAX = 30
"""Optimal maximum for very large objects (>100 arcmin)."""

# Magnification impact factors
MAGNIFICATION_FACTOR_OPTIMAL = 1.2
"""20% bonus for ideal magnification range."""

MAGNIFICATION_FACTOR_ACCEPTABLE = 1.0
"""No bonus or penalty for acceptable magnification."""

MAGNIFICATION_FACTOR_TOO_LOW = 0.7
"""30% penalty for insufficient magnification (too little detail)."""

MAGNIFICATION_FACTOR_TOO_HIGH = 0.6
"""40% penalty for excessive magnification (FOV too narrow or seeing-limited)."""

# ==============================================================================
# APERTURE THRESHOLDS AND FACTORS
# ==============================================================================

# Aperture categories (millimeters)
APERTURE_LARGE = 200  # mm (8 inches)
"""Large amateur telescope - 200mm+. Professional/serious amateur range."""

APERTURE_MEDIUM = 100  # mm (4 inches)
"""Medium amateur telescope - 100-199mm. Standard hobbyist range."""

APERTURE_SMALL = 70  # mm (2.75 inches)
"""Small telescope - 70-99mm. Beginner range."""

APERTURE_TINY = 50  # mm (2 inches)
"""Finder scope / very small telescope range."""

# Aperture impact factors
APERTURE_FACTOR_LARGE = 1.3
"""
30% bonus for large aperture (200mm+).
Light gathering power: (200/100)² = 4x more light than 100mm.
"""

APERTURE_FACTOR_MEDIUM = 1.1
"""10% bonus for medium aperture (100-199mm)."""

APERTURE_FACTOR_SMALL = 1.0
"""No bonus for small aperture (70-99mm) - baseline."""

APERTURE_FACTOR_TINY = 0.8
"""20% penalty for very small aperture (<70mm)."""

# ==============================================================================
# LIGHT POLLUTION CONSTANTS
# ==============================================================================

LIGHT_POLLUTION_DEFAULT_BORTLE = 5
"""Default Bortle scale value when site data is unavailable (suburban baseline)."""

LIGHT_POLLUTION_PENALTY_PER_BORTLE_SOLAR = 0.01
"""
Minimal light pollution impact on bright solar system objects.
1% reduction per Bortle level (max 9% in Bortle 9).
"""

LIGHT_POLLUTION_PENALTY_PER_BORTLE_DEEPSKY = 0.10
"""
Significant light pollution impact on deep-sky objects.
10% reduction per Bortle level (can approach zero in cities).
"""

LIGHT_POLLUTION_PENALTY_PER_BORTLE_LARGE = 0.12
"""
Severe light pollution impact on large faint objects (low surface brightness).
12% reduction per Bortle level.
"""

LIGHT_POLLUTION_MIN_FACTOR_DEEPSKY = 0.1
"""Deep-sky objects never go below 10% even in worst light pollution."""

LIGHT_POLLUTION_MIN_FACTOR_LARGE = 0.05
"""Large faint objects can become nearly impossible in cities (5% minimum)."""

# Bortle scale to limiting magnitude mapping
BORTLE_TO_LIMITING_MAGNITUDE = {
    1: 7.6,  # Excellent dark-sky site
    2: 7.1,  # Typical truly dark site
    3: 6.6,  # Rural sky
    4: 6.1,  # Rural/suburban transition
    5: 5.6,  # Suburban sky
    6: 5.1,  # Bright suburban sky
    7: 4.6,  # Suburban/urban transition
    8: 4.1,  # City sky
    9: 3.6,  # Inner-city sky
}
"""
Bortle scale to naked-eye limiting magnitude mapping.
Based on empirical observations and published astronomy references.
Limiting magnitude = faintest star visible to adapted eye.
"""

# ==============================================================================
# EQUIPMENT PENALTY CONSTANTS (NO EQUIPMENT)
# ==============================================================================

EQUIPMENT_PENALTY_SOLAR_SYSTEM = 0.5
"""
50% penalty for observing solar system objects without telescope.
Planets visible to naked eye but details impossible to see.
"""

EQUIPMENT_PENALTY_DEEPSKY = 0.3
"""
70% penalty for observing deep-sky objects without telescope.
Only brightest DSOs (M31, M42, Pleiades) visible naked eye.
"""

EQUIPMENT_PENALTY_LARGE_FAINT = 0.1
"""
90% penalty for observing large faint objects without telescope.
Low surface brightness makes naked-eye observation nearly impossible.
"""

# ==============================================================================
# SCORE NORMALIZATION CONSTANTS
# ==============================================================================

# Weight factors for combining magnitude and size
WEIGHT_MAGNITUDE_LARGE_OBJECTS = 0.4
"""40% weight on magnitude for large objects - size matters more."""

WEIGHT_SIZE_LARGE_OBJECTS = 0.6
"""60% weight on size for large objects - extent dominates."""

WEIGHT_MAGNITUDE_COMPACT_OBJECTS = 0.5
"""50% weight on magnitude for compact objects - balanced."""

WEIGHT_SIZE_COMPACT_OBJECTS = 0.5
"""50% weight on size for compact objects - balanced."""

NORMALIZATION_DIVISOR = 10
"""
Scale factor for large faint objects to bring scores into 0-1 range.
Compensates for different baseline magnitudes used in strategies.
"""

# ==============================================================================
# MAGNITUDE BASELINES
# ==============================================================================

FAINT_OBJECT_MAGNITUDE_BASELINE = 12
"""
Baseline magnitude for faint object scoring.
Objects brighter than mag 12 score higher, fainter score lower.
"""

MAGNITUDE_OFFSET_DEEPSKY = 12
"""
Magnitude offset added to deep-sky objects to bring them into scoreable range.
Deep-sky objects are typically mag 5-15, offset brings them closer to 0.
"""

# ==============================================================================
# SIZE THRESHOLDS
# ==============================================================================

LARGE_OBJECT_SIZE_THRESHOLD = 30  # arcminutes
"""
Threshold for classifying objects as "large".
Objects > 30 arcmin use LargeFaintObjectScoringStrategy.
Examples: Andromeda (190'), Pleiades (110'), Veil Nebula (180')
"""

MAX_DEEPSKY_SIZE_COMPACT = 200  # arcminutes
"""
Maximum expected size for compact deep-sky objects (for normalization in DeepSkyScoringStrategy).
Most deep-sky objects (galaxies, nebulae, clusters) fall within this range.
Examples: M42 Orion Nebula (~65'), M13 Hercules Cluster (~20'), M51 Whirlpool (~11')
"""

MAX_DEEPSKY_SIZE_LARGE = 300  # arcminutes
"""
Maximum expected size for large extended deep-sky objects (for normalization in LargeFaintObjectScoringStrategy).
Used for very large objects like supernova remnants and large nebula complexes.
Examples: Veil Nebula complex (~180'), North America Nebula (~120')
"""

MAX_SOLAR_SIZE = 31  # arcminutes
"""
Maximum angular size for solar system objects (Sun and Moon).
Both Sun and Moon have angular diameter of approximately 31 arcminutes (0.5 degrees).
Used for normalization in SolarSystemScoringStrategy.
"""

# ==============================================================================
# REFERENCE OBJECTS AND BASELINE VALUES
# ==============================================================================

SUN_APPARENT_MAGNITUDE = -26.74
"""Apparent magnitude of the Sun - brightest object visible from Earth."""

SUN_ANGULAR_SIZE = 31.00  # arcminutes
"""Angular size of the Sun at mean Earth-Sun distance."""

SUN_ALTITUDE_FOR_BASELINE = 90.00  # degrees
"""Reference altitude (zenith) for baseline calculations."""

SIRIUS_APPARENT_MAGNITUDE = -1.46
"""Apparent magnitude of Sirius - brightest star in night sky."""

SIRIUS_ANGULAR_SIZE = 0.0001  # arcminutes
"""Angular size of Sirius - point source for practical purposes."""

# Pre-calculated normalization values for performance
SUN_MAGNITUDE_SCORE = 49659232145.03358
"""
Pre-calculated magnitude score for the Sun.
Formula: 10 ** (-0.4 * SUN_APPARENT_MAGNITUDE)
Used to normalize solar system object brightness to 0-25 scale.
"""

SIRIUS_DEEPSKY_MAGNITUDE_SCORE = 0.015275660582380723
"""
Pre-calculated magnitude score for Sirius with deep-sky offset.
Formula: 10 ** (-0.4 * (SIRIUS_APPARENT_MAGNITUDE + MAGNITUDE_OFFSET_DEEPSKY))
Used to normalize deep-sky object brightness to 0-25 scale.
"""

MAX_OBSERVABLE_SCORE = 25
"""
Maximum score value for base observability calculations.
Final scores are normalized to 0-10 range after applying all factors.
"""

OPTIMAL_ALTITUDE = 90  # degrees
"""Optimal observing altitude (zenith) - looking straight up."""
