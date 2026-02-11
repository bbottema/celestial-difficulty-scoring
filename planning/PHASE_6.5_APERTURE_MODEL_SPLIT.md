# Phase 6.5: Aperture Model Split

**Status:** 🔴 IN PROGRESS
**Priority:** CRITICAL (Bug-fix phase)
**Created:** 2026-02-11
**Dependencies:** Phase 5 (complete), Phase 6 (complete)

---

## Goal

Split the single `aperture_gain_factor` fudge factor (0.85) into physically meaningful components to:
1. Fix 6 failing aperture tests
2. Prepare architecture for Phase 7 (object-type-aware scoring)
3. Improve physics accuracy without requiring API data

---

## Problem Statement

**Current Issue:** Aperture handled in TWO places causing conflicts:

1. **Equipment Factor** (`deep_sky_strategy.py`): Returns multipliers like 1.5x for large aperture
2. **Site Factor** (`light_pollution_models.py`): Uses `aperture_gain_factor` (0.85) to extend limiting magnitude

**The Conflict:**
```python
# Horsehead Nebula (mag 10) with 80mm in Bortle 3:
equipment_factor = 0.3  # Small aperture penalty
site_factor = 0.0       # Below limiting magnitude → ZERO!
final_score = base * 0.3 * 0.0 = 0  # Equipment factor irrelevant!

# With 400mm:
equipment_factor = 1.575  # Large aperture bonus
site_factor = 0.15       # Above limiting magnitude
final_score = base * 1.575 * 0.15 = meaningful score

# BUT: Tests expect 2x difference, actual is infinite (0 vs non-zero)
```

**Root Cause:** Single `aperture_gain_factor` (0.85) masks 5 different physical phenomena:

| Phenomenon | Affects | Depends On | Current | Should Be |
|-----------|---------|------------|---------|-----------|
| Optical losses | All objects equally | Telescope type | 0.85 (universal) | 0.80-0.95 (type-specific) |
| Central obstruction | All objects equally | Telescope type | 0.85 (universal) | Built into optical efficiency |
| Atmospheric seeing | Extended objects more | Altitude, weather | 0.85 (universal) | 0.80-1.0 (condition-dependent) |
| Observer experience | Faint objects more | User skill | 0.85 (universal) | 0.85-0.95 (user setting) |
| Surface brightness | Extended objects only | Object size | Partially handled | Already separate |

---

## Solution: Split Into Components

### Architecture

Replace single `aperture_gain_factor` with:

```python
aperture_gain_factor = (
    optical_efficiency(telescope_type) *      # 0.85-0.95
    seeing_factor(altitude, weather) *        # 0.80-1.0
    observer_experience(user_skill)           # 0.85-0.95
)

# Example calculations:
# Refractor, 60° alt, intermediate: 0.95 * 0.90 * 0.90 = 0.77
# SCT, 20° alt, beginner: 0.82 * 0.80 * 0.85 = 0.56
# Dobsonian, 80° alt, expert: 0.88 * 1.0 * 0.95 = 0.84
```

---

## Implementation Plan

### Step 1: Create New Module

**File:** `src/app/utils/aperture_models.py`

```python
"""
Aperture gain factor components - splits Phase 5's single fudge factor.

Replaces aperture_gain_factor (0.85) with physically meaningful components:
- Optical efficiency (telescope-type dependent)
- Seeing impact (atmospheric conditions)
- Observer experience (user skill level)
"""

from app.domain.model.telescope_type import TelescopeType


def calculate_optical_efficiency(telescope_type: TelescopeType) -> float:
    """
    Optical losses from coatings, obstruction, corrector plates.

    Based on:
    - Mirror/lens coatings: 2-5% loss per surface
    - Central obstruction: SCT/Newt lose 10-15% effective area
    - Corrector plates: SCT/Mak lose 5-10% transmission
    """
    efficiency = {
        TelescopeType.REFRACTOR: 0.95,           # 2 glass surfaces, no obstruction
        TelescopeType.ACHROMATIC_REFRACTOR: 0.93,  # Slight chromatic aberration
        TelescopeType.APOCHROMATIC_REFRACTOR: 0.95,
        TelescopeType.REFLECTOR: 0.88,           # 2 mirror coatings + spider
        TelescopeType.DOBSONIAN: 0.88,           # Same as reflector
        TelescopeType.SCT: 0.82,                 # Corrector + large obstruction (30-40%)
        TelescopeType.MAKSUTOV: 0.85,            # Thicker corrector, smaller obstruction
        TelescopeType.CASSEGRAIN: 0.85,
    }
    return efficiency.get(telescope_type, 0.85)  # Default: generic telescope


def calculate_seeing_factor(altitude: float, weather: dict = None) -> float:
    """
    Atmospheric seeing impact on limiting magnitude.

    More important for extended objects (handled separately in strategies).
    This affects ALL objects but is more significant at low altitudes.

    Args:
        altitude: Object altitude in degrees
        weather: Weather conditions (future: explicit seeing parameter)

    Returns:
        Factor 0.80-1.0 representing atmospheric transparency
    """
    # Low altitude = more atmosphere to penetrate
    if altitude < 20:
        return 0.80  # Significant atmospheric extinction
    elif altitude < 40:
        return 0.90  # Moderate extinction
    elif altitude < 60:
        return 0.95  # Minimal extinction
    else:
        return 1.0   # Negligible extinction at high altitudes


def calculate_observer_factor(skill_level: str = 'intermediate') -> float:
    """
    Observer experience impact on detection of faint objects.

    Experienced observers:
    - Know averted vision techniques
    - Better dark adaptation habits
    - Can recognize subtle contrast
    - More patient with faint targets

    Args:
        skill_level: 'beginner', 'intermediate', or 'expert'

    Returns:
        Factor 0.85-0.95 representing observer capability
    """
    factors = {
        'beginner': 0.85,      # Learning curve, less dark adaptation
        'intermediate': 0.90,  # Competent, knows techniques
        'expert': 0.95,        # Experienced, maximizes visibility
    }
    return factors.get(skill_level, 0.90)


def calculate_aperture_gain_factor(
    telescope_type: TelescopeType,
    altitude: float,
    weather: dict = None,
    observer_skill: str = 'intermediate'
) -> float:
    """
    Calculate realistic aperture gain factor by splitting components.

    Replaces Phase 5's single 0.85 fudge factor with physics-based components.
    Each component models a specific real-world effect.

    Args:
        telescope_type: Type of telescope (affects optical efficiency)
        altitude: Object altitude in degrees (affects seeing)
        weather: Weather conditions (optional, for future seeing refinement)
        observer_skill: User's observing experience level

    Returns:
        Combined factor typically 0.60-0.90

    Examples:
        >>> # Ideal conditions
        >>> calculate_aperture_gain_factor(
        ...     TelescopeType.REFRACTOR, 80, None, 'expert'
        ... )
        0.90  # 0.95 * 1.0 * 0.95

        >>> # Challenging conditions
        >>> calculate_aperture_gain_factor(
        ...     TelescopeType.SCT, 15, None, 'beginner'
        ... )
        0.56  # 0.82 * 0.80 * 0.85
    """
    optical = calculate_optical_efficiency(telescope_type)
    seeing = calculate_seeing_factor(altitude, weather)
    observer = calculate_observer_factor(observer_skill)

    return optical * seeing * observer
```

### Step 2: Integrate Into Limiting Magnitude Model

**File:** `src/app/utils/light_pollution_models.py`

```python
# Add import
from app.utils.aperture_models import calculate_aperture_gain_factor

# Modify function signature
def calculate_light_pollution_factor_by_limiting_magnitude(
    object_magnitude: float,
    bortle: int,
    telescope_aperture_mm: float = None,
    telescope_type: TelescopeType = None,  # NEW
    altitude: float = 45.0,                 # NEW
    observer_skill: str = 'intermediate',   # NEW
    detection_headroom: float = 1.5,
    use_legacy_penalty: bool = False,
    legacy_penalty_per_bortle: float = 0.10,
    legacy_minimum_factor: float = 0.02
) -> float:
    """
    Calculate light pollution factor based on limiting magnitude model.

    Now uses split aperture gain factor (Phase 6.5) instead of single constant.
    """
    import math

    nelm = BORTLE_TO_LIMITING_MAGNITUDE.get(bortle, 5.6)

    if telescope_aperture_mm:
        # Calculate dynamic aperture gain factor
        if telescope_type and altitude is not None:
            # Use split model (Phase 6.5)
            gain_factor = calculate_aperture_gain_factor(
                telescope_type, altitude, None, observer_skill
            )
        else:
            # Fallback to Phase 5 default
            gain_factor = 0.85

        aperture_gain = 5 * math.log10(telescope_aperture_mm / 7) * gain_factor
        limiting_magnitude = nelm + aperture_gain
    else:
        limiting_magnitude = nelm

    # Rest of function unchanged...
```

### Step 3: Update Strategy Calls

**File:** `src/app/domain/services/strategies/deep_sky_strategy.py`

```python
# Update site_factor calculation
def _calculate_site_factor(self, celestial_object, context: 'ScoringContext') -> float:
    """
    Light pollution is CRITICAL for faint deep-sky objects.
    Uses hybrid model with Phase 6.5 split aperture gain.
    """
    if not context.observation_site:
        return 0.7

    bortle = context.get_bortle_number()
    aperture = context.get_aperture_mm() if context.has_equipment() else None
    telescope_type = context.telescope.type if context.has_equipment() else None
    preset = get_active_preset()

    # Determine penalty based on object brightness
    if celestial_object.magnitude <= 6:
        penalty_per_bortle = 0.06
    elif celestial_object.magnitude <= 9:
        penalty_per_bortle = LIGHT_POLLUTION_PENALTY_PER_BORTLE_DEEPSKY
    else:
        penalty_per_bortle = 0.13

    # Use hybrid model with split aperture gain (Phase 6.5)
    factor = calculate_light_pollution_factor_with_surface_brightness(
        celestial_object.magnitude,
        celestial_object.size,
        bortle,
        aperture,
        telescope_type=telescope_type,              # NEW
        altitude=celestial_object.altitude,         # NEW
        observer_skill='intermediate',              # NEW (future: user setting)
        use_legacy_penalty=True,
        legacy_penalty_per_bortle=penalty_per_bortle,
        legacy_minimum_factor=preset.light_pollution_min_factor_deepsky
    )

    return factor
```

---

## Success Criteria

✅ All 6 aperture tests pass:
- `test_aperture_helps_horsehead`
- `test_aperture_minor_impact_on_jupiter`
- `test_aperture_extends_limiting_magnitude`
- `test_aperture_makes_faint_objects_visible`
- `test_large_aperture_helps_faint_galaxy_in_dark_skies`
- `test_sirius_visible_naked_eye` (no regression)

✅ No regressions in 104 currently passing tests

✅ Architecture ready for Phase 7 object-type refinement

---

## Future Enhancements (Phase 7)

Phase 6.5 prepares the architecture. Phase 7 will add:

```python
# Phase 7: Object-type-specific refinements
def calculate_seeing_factor(altitude: float, object_classification: str = None):
    """
    Phase 7 enhancement: Different objects affected differently by seeing.

    - Point sources (stars): minimal seeing impact
    - Compact objects (planetary nebulae): moderate impact
    - Extended objects (galaxies): major impact
    """
    base_factor = _calculate_base_seeing_factor(altitude)

    if object_classification:
        modifiers = {
            'star': 1.0,                    # Minimal seeing effect
            'planetary_nebula': 0.95,       # Slight effect
            'globular_cluster': 0.92,       # Moderate effect
            'galaxy_spiral': 0.85,          # Major effect (low surface brightness)
            'emission_nebula': 0.88,        # Moderate-major effect
        }
        modifier = modifiers.get(object_classification, 0.90)
        return base_factor * modifier

    return base_factor
```

---

## Testing Strategy

1. **Unit tests** for new functions in `aperture_models.py`
2. **Integration tests** verify limiting magnitude calc uses split model
3. **Regression tests** ensure existing 104 tests still pass
4. **Aperture bug tests** verify all 6 failures now pass

---

## Documentation Updates

- ✅ This file (Phase 6.5 spec)
- ✅ Updated `SCORING_IMPROVEMENT_PLAN.md`
- ⬜ Code comments in new `aperture_models.py`
- ⬜ Docstrings in modified `light_pollution_models.py`

---

**Next Steps:** Implement `aperture_models.py` and integrate with limiting magnitude model.
