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
WEATHER_CLOUD_COVER_OVERCAST = 90  # percent
"""
90%+ cloud cover = overcast conditions.
Based on meteorological standards: overcast is 7/8 oktas (87.5%+).
Set to 90% because weather APIs often report 90-99% rather than exactly 100%.
Reference: https://en.wikipedia.org/wiki/Okta
"""

WEATHER_CLOUD_COVER_MOSTLY_CLOUDY = 75  # percent
"""
75%+ cloud cover = mostly cloudy (5/8 to 6/8 oktas).
Significant obstruction, but occasional gaps allow brief observations.
"""

WEATHER_CLOUD_COVER_PARTLY_CLOUDY = 50  # percent
"""
50% cloud cover = partly cloudy (4/8 oktas).
Moderate obstruction - represents "scattered" clouds in aviation terminology.
"""

WEATHER_CLOUD_COVER_FEW_CLOUDS = 25  # percent
"""
25% cloud cover = few clouds (2/8 oktas).
Minor obstruction - most of sky accessible.
"""

# Weather impact factors (multipliers)
# Note: These are base/default values. Presets may override some of these.

WEATHER_FACTOR_OVERCAST = 0.05
"""
Overcast conditions (90%+ cloud cover).
Only brightest objects (Sun/Moon) barely visible through brief gaps.
95% reduction in observability.
Interpretation: "time-occlusion" - target visible ~5% of session duration.
"""

WEATHER_FACTOR_OVERCAST_STRICT = 0.02
"""
Strict preset: even less optimistic for overcast.
98% reduction - nearly impossible conditions.
"""

WEATHER_FACTOR_MOSTLY_CLOUDY = 0.25
"""
Mostly cloudy conditions (75%+ cloud cover).
75% reduction in observability.
Observers report catching targets in gaps, but unreliable.
Deep-sky targets typically not worth attempting.
"""

WEATHER_FACTOR_MOSTLY_CLOUDY_FRIENDLY = 0.30
"""
Friendly preset: slightly more lenient for mostly cloudy.
Encourages attempting targets during gaps.
"""

WEATHER_FACTOR_MOSTLY_CLOUDY_STRICT = 0.20
"""
Strict preset: more conservative for mostly cloudy.
Reduces false greens on unreliable nights.
"""

WEATHER_FACTOR_PARTLY_CLOUDY = 0.60
"""
Partly cloudy conditions (50% cloud cover) - base value.
40% reduction in observability.
Based on observer experience: "mostly cloudy, I caught gaps" scenarios.
Represents time target is accessible during session.
Value tuned to avoid false greens for faint targets.
"""

WEATHER_FACTOR_PARTLY_CLOUDY_FRIENDLY = 0.65
"""
Friendly preset: more optimistic for partly cloudy.
Encourages observing in variable conditions.
"""

WEATHER_FACTOR_FEW_CLOUDS = 0.85
"""
Few clouds (25% cloud cover).
15% reduction in observability.
Should still yield many green-rated results for good targets.
Matches "gap probability" interpretation from observer reports.
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

ALTITUDE_FACTOR_NEAR_ZENITH = 1.0
"""
No penalty at zenith (>80°).
Zenith has minimal airmass and is optimal for atmospheric transparency.
Previous penalty had no atmospheric physics basis - zenith is best observing altitude.
Any ergonomic issues (neck strain, mount clearance) are equipment-specific, not observability.
"""

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

ALTITUDE_FACTOR_VERY_POOR_DEEPSKY = 0.40
"""
60% reduction for DSOs at <20° altitude - base value.
At low altitude, airmass becomes severe:
  - 20°: airmass ≈ 2.9
  - 10°: airmass ≈ 5.8
Effects beyond dimming:
  - Contrast destruction for low surface brightness objects (galaxies, nebulae)
  - Light domes concentrate near horizon in polluted sites
  - Atmospheric dispersion smears colors
  - Seeing turbulence increases
Value set conservatively for planning app: prefer "don't waste your night" over false greens.
Reference: Kasten & Young airmass model
"""

ALTITUDE_FACTOR_VERY_POOR_DEEPSKY_FRIENDLY = 0.45
"""
Friendly preset: less harsh penalty for low altitude DSOs.
55% reduction - encourages attempting low-altitude targets.
Some experienced observers can pull detail from objects at 15-20° in good conditions.
"""

ALTITUDE_FACTOR_VERY_POOR_DEEPSKY_STRICT = 0.35
"""
Strict preset: harsher penalty for low altitude DSOs.
65% reduction - more realistic for typical observing conditions.
Contrast loss and light dome effects make most DSOs difficult below 20°.
"""

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
MAGNIFICATION_PLANETARY_OPTIMAL_MIN = 120
"""
Minimum magnification for planetary detail.
Based on exit pupil approach: 0.5-1.0mm exit pupil optimal for planets.
  - 80mm scope: optimal ~120-140× (exit pupil 0.57-0.67mm)
  - 150mm scope: optimal ~150-250× (exit pupil 0.6-1.0mm)
  - 200mm scope: optimal ~200-300× (exit pupil 0.67-1.0mm)
Previous value (150×) was too aggressive for small scopes (70-100mm).
Reference: Exit pupil = aperture_mm / magnification
"""

MAGNIFICATION_PLANETARY_OPTIMAL_MAX = 250
"""
Maximum useful magnification for planets before atmospheric seeing degrades image.
Based on practical seeing limits and exit pupil approach.
Common rule: ~50× per inch aperture, or 2× per mm (~0.5mm exit pupil).
  - 100mm scope: ~200× max
  - 200mm scope: ~400× theoretical, but 250× more practical in average seeing
Previous value (300×) caps out early for large scopes on steady nights, but 250× is more
conservative and fits broader user base across typical seeing conditions.
"""

MAGNIFICATION_PLANETARY_TOO_LOW = 60
"""
Below 60×, planets appear as small disks without significant detail.
At 60×, Jupiter (~45" diameter) appears as 0.75mm disk at typical eyepiece.
Cloud bands and Great Red Spot become visible around 80-100×.
Moons visible, but planetary detail requires higher power.
"""

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
APERTURE_FACTOR_LARGE = 1.5
"""
50% bonus for large aperture (200mm+) on deep-sky objects - base value.
Light gathering power scales as D²:
  - 200mm vs 100mm: (200/100)² = 4× light = ~1.5 magnitudes deeper
  - 200mm vs 70mm: (200/70)² = 8× light = ~2.3 magnitudes deeper
For solar system objects, use lower factors (seeing dominates over aperture).
Increased from 1.3 to emphasize aperture importance for faint DSOs.
Reference: Limiting magnitude ≈ 5 × log₁₀(D) where D in mm
"""

APERTURE_FACTOR_LARGE_FRIENDLY = 1.40
"""
Friendly preset: moderate aperture bonus.
40% bonus - aperture helps but doesn't dominate scoring.
"""

APERTURE_FACTOR_LARGE_STRICT = 1.55
"""
Strict preset: stronger aperture bonus.
55% bonus - emphasizes that large aperture really matters for faint DSOs.
"""

APERTURE_FACTOR_MEDIUM = 1.2
"""
20% bonus for medium aperture (100-199mm) - base value.
Standard amateur range - good balance of portability and light gathering.
Increased from 1.1 to better reflect light gathering advantage.
"""

APERTURE_FACTOR_MEDIUM_FRIENDLY = 1.15
"""
Friendly preset: moderate medium aperture bonus.
15% bonus.
"""

APERTURE_FACTOR_MEDIUM_STRICT = 1.25
"""
Strict preset: stronger medium aperture bonus.
25% bonus.
"""

APERTURE_FACTOR_SMALL = 1.0
"""No bonus for small aperture (70-99mm) - baseline."""

APERTURE_FACTOR_TINY = 0.75
"""
25% penalty for very small aperture (<70mm) - base value.
Finder scope range - limited light gathering for faint objects.
Still useful for bright targets (Moon, planets, bright stars, Pleiades).
Increased penalty from 0.8 to reflect genuine difficulty with faint DSOs.
"""

APERTURE_FACTOR_TINY_STRICT = 0.70
"""
Strict preset: harsher penalty for tiny apertures.
30% penalty - realistic about limitations.
"""

# ==============================================================================
# LIGHT POLLUTION CONSTANTS
# ==============================================================================

LIGHT_POLLUTION_DEFAULT_BORTLE = 5
"""Default Bortle scale value when site data is unavailable (suburban baseline)."""

LIGHT_POLLUTION_PENALTY_PER_BORTLE_SOLAR = 0.01
"""
Minimal light pollution impact on bright solar system objects.
1% reduction per Bortle level (max 9% in Bortle 9).
Planets remain visible even in heavily light-polluted skies (Bortle 8-9).
"""

LIGHT_POLLUTION_PENALTY_PER_BORTLE_DEEPSKY = 0.10
"""
Significant light pollution impact on deep-sky objects.
10% reduction per Bortle level (can approach zero in cities).
Linear penalty is simplified model; reality shows steeper drop in bright skies,
but combined with minimum floors provides reasonable planning estimates.
"""

LIGHT_POLLUTION_PENALTY_PER_BORTLE_LARGE = 0.12
"""
Severe light pollution impact on large faint objects (low surface brightness).
12% reduction per Bortle level.
Large extended objects (nebulae, galaxy halos) suffer more than compact objects
because their surface brightness is distributed over larger area.
"""

LIGHT_POLLUTION_MIN_FACTOR_DEEPSKY = 0.02
"""
Deep-sky objects become nearly impossible in worst light pollution (Bortle 9) - base value.
Lowered from 0.1 to 0.02 to honestly reflect difficulty in inner-city observing.
Planning apps should err toward "don't waste your night" rather than false hope.
Only brightest DSOs (M42, M31 core, M45) have any chance in Bortle 8-9.
"""

LIGHT_POLLUTION_MIN_FACTOR_DEEPSKY_FRIENDLY = 0.05
"""
Friendly preset: slightly higher floor for deep-sky in cities.
5% minimum - allows some "challenging but possible" ratings for brightest DSOs.
"""

LIGHT_POLLUTION_MIN_FACTOR_LARGE = 0.02
"""
Large faint objects become nearly impossible in cities - base value.
Lowered from 0.05 to 0.02 for realism.
Low surface brightness objects (galaxy halos, faint nebulae, supernova remnants)
genuinely invisible in Bortle 8-9 regardless of aperture.
Example: Veil Nebula, California Nebula, outer regions of Andromeda.
"""

LIGHT_POLLUTION_MIN_FACTOR_LARGE_FRIENDLY = 0.03
"""
Friendly preset: slightly higher floor for large faint objects.
3% minimum - acknowledges some may attempt anyway.
"""

LIGHT_POLLUTION_MIN_FACTOR_LARGE_STRICT = 0.00
"""
Strict preset: zero floor for large faint objects in bright cities.
Honestly impossible - don't waste your time.
"""

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
Bortle scale to naked-eye limiting magnitude (NELM) mapping.
Based on empirical observations and published astronomy references.
Limiting magnitude = faintest star visible to dark-adapted naked eye (zenith).

This mapping is used for reference and potential future visibility calculations.
Current scoring uses linear penalty model (LIGHT_POLLUTION_PENALTY_PER_BORTLE)
rather than direct limiting magnitude cutoffs.

Future enhancement could use: visibility_factor = 1.0 - (object_mag - limiting_mag) / headroom
where headroom represents how far below limiting magnitude object needs to be for detection.

Reference: https://en.wikipedia.org/wiki/Bortle_scale
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

SIRIUS_DEEPSKY_MAGNITUDE_SCORE = 6.081350012787176e-05
"""
Pre-calculated magnitude score for Sirius with deep-sky offset.
Formula: 10 ** (-0.4 * (SIRIUS_APPARENT_MAGNITUDE + MAGNITUDE_OFFSET_DEEPSKY))
      = 10 ** (-0.4 * (-1.46 + 12))
      = 10 ** (-0.4 * 10.54)
      = 10 ** -4.216
      ≈ 6.081 × 10^-5
Used to normalize deep-sky object brightness to 0-25 scale.
"""

MAX_OBSERVABLE_SCORE = 25
"""
Maximum score value for base observability calculations.
Final scores are normalized to 0-10 range after applying all factors.
"""

OPTIMAL_ALTITUDE = 90  # degrees
"""Optimal observing altitude (zenith) - looking straight up."""
