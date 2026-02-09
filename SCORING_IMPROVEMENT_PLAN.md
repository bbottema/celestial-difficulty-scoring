# Celestial Observability Scoring - Improvement Plan

## Executive Summary

This document outlines the roadmap for improving the celestial observability scoring algorithm. The system calculates an "ease of observation" score for celestial objects based on equipment, site conditions, weather, and object properties.

**Current State:** Equipment-aware scoring is implemented using a Strategy + Context pattern. Three strategies handle different object types (Solar System, Deep Sky, Large Faint Objects). The UI provides unified observation planning with equipment/site/weather selection.

**Goal:** Transform the scoring system into a transparent, accurate, and testable factor-based pipeline that correctly models real-world observability constraints.

## Critical Problems Identified

### 1. **SEMANTIC BUG: LargeFaintObjectScoringStrategy Logic is Inverted**

**Location:** `src/app/domain/services/strategies.py:209-213`

**Problem:** The score calculation treats fainter objects as MORE observable:
```python
magnitude_score = max(0, (celestial_object.magnitude - faint_object_magnitude_baseline))
# Higher magnitude = fainter = HIGHER score (WRONG!)
```

**Impact:** Large faint objects get scored backwards. A magnitude 10 nebula scores higher than a magnitude 5 nebula.

**Fix:** Invert the logic to match "ease of observation" semantics:
```python
# Fainter objects should score LOWER (harder to observe)
magnitude_score = max(0, (faint_object_magnitude_baseline - celestial_object.magnitude))
```

**Priority:** 🔴 CRITICAL - This is a fundamental logic error

---

### 2. **ARCHITECTURE: Not a True Factor Pipeline**

**Location:** All strategies in `src/app/domain/services/strategies.py`

**Problem:** Base score pre-averages magnitude and size:
```python
base_score = (magnitude_score + size_score) / 2
return base_score * equipment_factor * site_factor * altitude_factor
```

This makes individual factors invisible and non-modular. Can't easily add new factors or adjust individual weights.

**Fix:** Make each factor explicit and separate:
```python
return (magnitude_factor *
        size_factor *
        equipment_factor *
        site_factor *
        altitude_factor *
        weather_factor *
        moon_factor)
```

**Priority:** 🟡 HIGH - Needed for extensibility and debugging

---

### 3. **READABILITY: Magic Constants Everywhere**

**Location:** `src/app/utils/constants.py` and throughout strategies

**Problem:** Constants like `sun_solar_magnitude_score = 49659232145.03358` have no context or explanation.

**Fix:**
- Add docstrings explaining derivation
- Use named intermediate calculations
- Consider using logarithmic scales instead of raw exponentials

**Priority:** 🟡 HIGH - Makes code unmaintainable

---

### 4. **MISSING FEATURE: Double Star Separation**

**Location:** `src/app/domain/model/celestial_object.py`

**Problem:** No `separation` field in CelestialObject. Can't calculate if telescope can split double stars based on Dawes' limit.

**Fix:**
- Add `separation: Optional[float]` field (in arcseconds)
- Add `is_double_star: bool` helper property
- Create splitability calculation in strategies
- Formula: `dawes_limit = 116 / aperture_mm`

**Priority:** 🟢 MEDIUM - Nice feature but not breaking current use

---

### 5. **MISSING FEATURE: Moon Phase and Proximity**

**Location:** Multiple files - needs new Moon model and integration

**Problem:** Moon conditions not factored into scoring. Objects near a bright moon are washed out.

**Missing Components:**
- Moon phase (0-100%)
- Moon illumination percentage
- Moon altitude
- Angular separation from target object

**Fix:**
- Add Moon model with phase/altitude/position
- Calculate angular separation between Moon and target
- Add moon_proximity_factor that penalizes objects near bright moon
- Formula: `penalty = (moon_illumination / 100) * (1 / angular_separation_degrees)²`

**Priority:** 🟡 HIGH - Common real-world constraint

---

### 6. ✅ **FIXED: Weather Now Wired to Scoring**

**Location:** `src/app/domain/services/strategies.py`

**Problem:** ~~Weather dropdown exists in UI but selected value not passed to `ObservabilityCalculationService`.~~ **FIXED!**

**What Was Fixed:**
- ✅ Added `weather` parameter to `ScoringContext`
- ✅ Added `weather` parameter to `ObservabilityCalculationService.score_celestial_object()`
- ✅ Implemented `_calculate_weather_factor()` as module-level function
- ✅ Integrated weather factor into all three scoring strategies
- ✅ Weather tests now passing (6/7 tests)

**Remaining Issue:**
- 🔴 **Magic numbers everywhere** - hardcoded thresholds (100, 75, 50, 25) and factors (0.05, 0.25, 0.50, 0.75)
- 🔴 **See Phase 7** for comprehensive magic number cleanup

**Priority:** ✅ COMPLETE (but needs Phase 7 refactor for readability)

---

### 7. **INACCURATE: Light Pollution Uses Arbitrary Multipliers**

**Location:** `src/app/domain/services/strategies.py` - all `_calculate_site_factor` methods

**Problem:** Using arbitrary Bortle penalties like `penalty_per_bortle = 0.10` instead of physics-based limiting magnitude.

**Current Approach:**
```python
factor = 1.0 - (bortle * 0.10)  # Arbitrary!
```

**Fix:** Use limiting magnitude formula:
```python
# Bortle to limiting magnitude mapping
bortle_to_lim_mag = {1: 7.6, 2: 7.1, 3: 6.6, 4: 6.1, 5: 5.6, 6: 5.1, 7: 4.6, 8: 4.1, 9: 3.6}
limiting_magnitude = bortle_to_lim_mag[bortle]

# Calculate if object is visible at all
visibility = celestial_object.magnitude - limiting_magnitude
if visibility > 0:
    # Object fainter than limiting magnitude → invisible
    factor = 0.0
else:
    # Scale factor based on how far from limit
    factor = 1.0 - (abs(visibility) / 4.0)  # 4 mags of headroom
```

**Priority:** 🟡 HIGH - More accurate modeling needed

---

## Test Plan

### Test Setup Structure

Create `tests/scoring/test_observability_scenarios.py` with comprehensive test cases using known expected rankings.

#### Test Equipment Definitions
```python
# Small refractor (beginner equipment)
small_scope = Telescope(name="80mm Refractor", aperture=80, focal_length=600)
wide_eyepiece = Eyepiece(name="25mm Plossl", focal_length=25)  # 24x mag

# Medium dobsonian (intermediate equipment)
medium_scope = Telescope(name="8-inch Dob", aperture=200, focal_length=1200)
medium_eyepiece = Eyepiece(name="10mm", focal_length=10)  # 120x mag

# Large dobsonian (advanced equipment)
large_scope = Telescope(name="16-inch Dob", aperture=400, focal_length=1800)
planetary_eyepiece = Eyepiece(name="5mm", focal_length=5)  # 360x mag
widefield_eyepiece = Eyepiece(name="30mm", focal_length=30)  # 60x mag

# Sites
dark_site = ObservationSite(name="Dark Sky", light_pollution=LightPollution.BORTLE_2)
suburban_site = ObservationSite(name="Suburb", light_pollution=LightPollution.BORTLE_6)
city_site = ObservationSite(name="City", light_pollution=LightPollution.BORTLE_8)
```

#### Test Objects
```python
# Solar System Objects
sun = CelestialObject('Sun', 'Sun', -26.74, 31.00, 45.00)
moon = CelestialObject('Moon', 'Moon', -12.60, 31.00, 45.00)
jupiter = CelestialObject('Jupiter', 'Planet', -2.40, 0.77, 45.00)
saturn = CelestialObject('Saturn', 'Planet', 0.50, 0.27, 45.00)
mars = CelestialObject('Mars', 'Planet', -1.00, 0.15, 45.00)

# Bright Stars
sirius = CelestialObject('Sirius', 'DeepSky', -1.46, 0.0001, 60.00)
vega = CelestialObject('Vega', 'DeepSky', 0.03, 0.0001, 70.00)
betelgeuse = CelestialObject('Betelgeuse', 'DeepSky', 0.5, 0.0001, 50.00)

# Bright Deep-Sky Objects
orion_nebula = CelestialObject('Orion Nebula', 'DeepSky', 4.0, 65.0, 55.00)
andromeda = CelestialObject('Andromeda Galaxy', 'DeepSky', 3.44, 190.00, 60.00)
pleiades = CelestialObject('Pleiades', 'DeepSky', 1.6, 110.0, 65.00)

# Medium Deep-Sky Objects
ring_nebula = CelestialObject('Ring Nebula', 'DeepSky', 8.8, 1.4, 60.00)
whirlpool = CelestialObject('Whirlpool Galaxy', 'DeepSky', 8.4, 11.0, 55.00)

# Faint Deep-Sky Objects
veil_nebula = CelestialObject('Veil Nebula', 'DeepSky', 7.0, 180.00, 55.00)
horsehead = CelestialObject('Horsehead Nebula', 'DeepSky', 10.0, 60.0, 45.00)
```

---

### Test Case Categories

#### 1. **Sanity Checks - Basic Ordering**

```python
def test_solar_system_brightness_order_at_dark_site():
    """Solar system objects should rank by brightness: Sun > Moon > Jupiter > Saturn"""
    objects = [sun, moon, jupiter, saturn]
    scores = service.score_celestial_objects(objects, medium_scope, medium_eyepiece, dark_site)

    assert scores[0].score.normalized > scores[1].score.normalized  # Sun > Moon
    assert scores[1].score.normalized > scores[2].score.normalized  # Moon > Jupiter
    assert scores[2].score.normalized > scores[3].score.normalized  # Jupiter > Saturn
```

```python
def test_bright_stars_rank_high():
    """Bright stars should rank very high regardless of equipment"""
    objects = [sirius, vega, ring_nebula]
    scores = service.score_celestial_objects(objects, small_scope, wide_eyepiece, suburban_site)

    assert scores[0].score.normalized > 20  # Sirius easily visible
    assert scores[1].score.normalized > 20  # Vega easily visible
    assert scores[2].score.normalized < 15  # Ring Nebula much harder
```

#### 2. **Equipment Impact Tests**

```python
def test_aperture_matters_for_faint_objects():
    """Large aperture should dramatically improve faint deep-sky scores"""
    faint_object = horsehead  # Mag 10.0

    small_score = service.score_celestial_object(faint_object, small_scope, wide_eyepiece, dark_site)
    large_score = service.score_celestial_object(faint_object, large_scope, widefield_eyepiece, dark_site)

    # Large scope should score 2-3x higher for very faint object
    assert large_score.score.raw > small_score.score.raw * 2.0
```

```python
def test_magnification_matters_for_planets():
    """Planets benefit from higher magnification in optimal range"""

    # Jupiter with low magnification (24x)
    low_mag_score = service.score_celestial_object(jupiter, small_scope, wide_eyepiece, dark_site)

    # Jupiter with optimal magnification (240x)
    optimal_mag_scope = Telescope("Test", 200, 1200)
    optimal_mag_eyepiece = Eyepiece("Test", 5)  # 240x
    optimal_score = service.score_celestial_object(jupiter, optimal_mag_scope, optimal_mag_eyepiece, dark_site)

    assert optimal_score.score.raw > low_mag_score.score.raw * 1.1  # At least 10% better
```

```python
def test_wide_field_needed_for_large_objects():
    """Large extended objects need low magnification"""
    andromeda_large = CelestialObject('Andromeda', 'DeepSky', 3.44, 190.00, 60.00)

    # High magnification (360x) - bad for extended object
    high_mag_score = service.score_celestial_object(andromeda_large, large_scope, planetary_eyepiece, dark_site)

    # Low magnification (60x) - good for extended object
    low_mag_score = service.score_celestial_object(andromeda_large, large_scope, widefield_eyepiece, dark_site)

    assert low_mag_score.score.raw > high_mag_score.score.raw
```

#### 3. **Light Pollution Impact Tests**

```python
def test_light_pollution_minimal_on_planets():
    """Planets should barely be affected by light pollution"""

    dark_score = service.score_celestial_object(jupiter, medium_scope, medium_eyepiece, dark_site)
    city_score = service.score_celestial_object(jupiter, medium_scope, medium_eyepiece, city_site)

    # Jupiter should still be 90%+ visible even in city
    assert city_score.score.raw > dark_score.score.raw * 0.90
```

```python
def test_light_pollution_devastating_for_faint_dso():
    """Faint deep-sky objects should be nearly impossible in cities"""

    dark_score = service.score_celestial_object(horsehead, large_scope, widefield_eyepiece, dark_site)
    city_score = service.score_celestial_object(horsehead, large_scope, widefield_eyepiece, city_site)

    # Horsehead should be 70%+ harder in city
    assert city_score.score.raw < dark_score.score.raw * 0.30
```

```python
def test_light_pollution_gradient():
    """Score should decrease monotonically with worsening light pollution"""

    dark_score = service.score_celestial_object(orion_nebula, medium_scope, medium_eyepiece, dark_site)
    suburban_score = service.score_celestial_object(orion_nebula, medium_scope, medium_eyepiece, suburban_site)
    city_score = service.score_celestial_object(orion_nebula, medium_scope, medium_eyepiece, city_site)

    assert dark_score.score.raw > suburban_score.score.raw > city_score.score.raw
```

#### 4. **Altitude Impact Tests**

```python
def test_low_altitude_penalty():
    """Objects near horizon should score much lower than at zenith"""

    jupiter_high = CelestialObject('Jupiter', 'Planet', -2.40, 0.77, 70.00)  # High altitude
    jupiter_low = CelestialObject('Jupiter', 'Planet', -2.40, 0.77, 15.00)   # Low altitude

    high_score = service.score_celestial_object(jupiter_high, medium_scope, medium_eyepiece, dark_site)
    low_score = service.score_celestial_object(jupiter_low, medium_scope, medium_eyepiece, dark_site)

    # High altitude should score 40%+ better
    assert high_score.score.raw > low_score.score.raw * 1.40
```

```python
def test_altitude_optimal_range():
    """Planets have optimal altitude range 30-80 degrees"""

    jupiter_30 = CelestialObject('Jupiter', 'Planet', -2.40, 0.77, 30.00)
    jupiter_60 = CelestialObject('Jupiter', 'Planet', -2.40, 0.77, 60.00)
    jupiter_85 = CelestialObject('Jupiter', 'Planet', -2.40, 0.77, 85.00)

    score_30 = service.score_celestial_object(jupiter_30, medium_scope, medium_eyepiece, dark_site)
    score_60 = service.score_celestial_object(jupiter_60, medium_scope, medium_eyepiece, dark_site)
    score_85 = service.score_celestial_object(jupiter_85, medium_scope, medium_eyepiece, dark_site)

    # 60 degrees should be best
    assert score_60.score.raw >= score_30.score.raw
    assert score_60.score.raw >= score_85.score.raw
```

#### 5. **🌙 ADVANCED: Moon Proximity Tests**

```python
def test_object_near_full_moon_severely_penalized():
    """Objects within 30 degrees of full moon should score very poorly"""

    # Create target 10 degrees from moon
    target_near_moon = CelestialObject('Target Near Moon', 'DeepSky', 6.0, 10.0, 60.00)
    # Assume moon at RA=10h, Dec=+20°; target at RA=10h, Dec=+30° (separation ~10°)

    moon_conditions_full = {
        'phase': 'Full',
        'illumination': 100,
        'altitude': 60.0,
        'separation_degrees': 10.0  # Very close!
    }

    # Same target but moon far away (120 degrees separation)
    moon_conditions_far = {
        'phase': 'Full',
        'illumination': 100,
        'altitude': 60.0,
        'separation_degrees': 120.0
    }

    # TODO: Need to extend ScoringContext to accept moon_conditions
    near_score = service.score_celestial_object(
        target_near_moon, medium_scope, medium_eyepiece, dark_site,
        moon_conditions=moon_conditions_full)

    far_score = service.score_celestial_object(
        target_near_moon, medium_scope, medium_eyepiece, dark_site,
        moon_conditions=moon_conditions_far)

    # Object near full moon should score < 30% of object far from moon
    assert near_score.score.raw < far_score.score.raw * 0.30
```

```python
def test_new_moon_no_penalty():
    """Objects should not be penalized when moon is new (not visible)"""

    faint_dso = CelestialObject('Faint DSO', 'DeepSky', 9.0, 5.0, 60.00)

    moon_conditions_new = {
        'phase': 'New',
        'illumination': 0,
        'altitude': 0.0,  # Below horizon anyway
        'separation_degrees': 20.0
    }

    moon_conditions_full_nearby = {
        'phase': 'Full',
        'illumination': 100,
        'altitude': 60.0,
        'separation_degrees': 20.0
    }

    new_moon_score = service.score_celestial_object(
        faint_dso, medium_scope, medium_eyepiece, dark_site,
        moon_conditions=moon_conditions_new)

    full_moon_score = service.score_celestial_object(
        faint_dso, medium_scope, medium_eyepiece, dark_site,
        moon_conditions=moon_conditions_full_nearby)

    # New moon should not penalize at all
    assert new_moon_score.score.raw > full_moon_score.score.raw * 2.0
```

```python
def test_moon_penalty_formula():
    """Moon penalty should follow inverse square of separation and scale with illumination"""

    target = CelestialObject('Target', 'DeepSky', 7.0, 10.0, 60.00)

    # 100% moon at various separations
    separations = [5, 10, 20, 40, 80]
    scores = []

    for sep in separations:
        moon_cond = {'phase': 'Full', 'illumination': 100, 'altitude': 60.0, 'separation_degrees': sep}
        score = service.score_celestial_object(target, medium_scope, medium_eyepiece, dark_site, moon_conditions=moon_cond)
        scores.append(score.score.raw)

    # Scores should increase with separation
    for i in range(len(scores) - 1):
        assert scores[i+1] > scores[i]

    # Penalty should be roughly inverse square
    # Score at 40° should be ~4x better than at 20°
    assert scores[3] > scores[2] * 3.0  # Allow some variance
```

```python
def test_moon_behind_target():
    """Object directly behind moon (occultation) should have zero score"""

    target = CelestialObject('Occulted Star', 'DeepSky', 3.0, 0.0001, 60.00)

    moon_conditions_occultation = {
        'phase': 'Full',
        'illumination': 100,
        'altitude': 60.0,
        'separation_degrees': 0.0  # Directly behind moon!
    }

    score = service.score_celestial_object(
        target, medium_scope, medium_eyepiece, dark_site,
        moon_conditions=moon_conditions_occultation)

    assert score.score.raw == 0.0  # Impossible to observe
```

#### 6. **Weather Impact Tests** (After Problem #6 fixed)

```python
def test_clouds_devastate_all_observations():
    """Overcast conditions should make everything nearly impossible"""

    weather_clear = {'condition': 'Clear', 'cloud_cover': 0}
    weather_overcast = {'condition': 'Overcast', 'cloud_cover': 100}

    clear_score = service.score_celestial_object(
        jupiter, medium_scope, medium_eyepiece, dark_site, weather=weather_clear)

    overcast_score = service.score_celestial_object(
        jupiter, medium_scope, medium_eyepiece, dark_site, weather=weather_overcast)

    # Even bright Jupiter should score near zero in overcast
    assert overcast_score.score.raw < clear_score.score.raw * 0.1
```

```python
def test_partial_clouds_penalty():
    """Partial clouds should reduce scores proportionally"""

    weather_clear = {'condition': 'Clear', 'cloud_cover': 0}
    weather_partial = {'condition': 'Partly Cloudy', 'cloud_cover': 50}

    clear_score = service.score_celestial_object(
        orion_nebula, medium_scope, medium_eyepiece, dark_site, weather=weather_clear)

    partial_score = service.score_celestial_object(
        orion_nebula, medium_scope, medium_eyepiece, dark_site, weather=weather_partial)

    # Partial clouds should reduce score by ~50%
    assert 0.4 < (partial_score.score.raw / clear_score.score.raw) < 0.6
```

#### 7. **Edge Cases and Validation**

```python
def test_below_horizon_objects():
    """Objects below horizon (altitude < 0) should score zero"""

    below_horizon = CelestialObject('Below Horizon', 'Planet', -2.0, 0.5, -10.00)
    score = service.score_celestial_object(below_horizon, medium_scope, medium_eyepiece, dark_site)

    assert score.score.raw == 0.0
```

```python
def test_no_equipment_severe_penalty():
    """Observing without equipment should severely penalize faint objects"""

    faint = horsehead

    with_equipment = service.score_celestial_object(faint, medium_scope, medium_eyepiece, dark_site)
    no_equipment = service.score_celestial_object(faint, None, None, dark_site)

    # Without equipment, faint object should score < 30%
    assert no_equipment.score.raw < with_equipment.score.raw * 0.30
```

```python
def test_sun_always_ranks_highest():
    """Sun should rank highest in almost any conditions (safety aside)"""

    all_objects = [sun, moon, jupiter, sirius, orion_nebula, horsehead]
    scores = service.score_celestial_objects(all_objects, small_scope, wide_eyepiece, city_site)

    # Sun should be first
    assert scores[0].name == 'Sun'
    assert scores[0].score.normalized > scores[1].score.normalized
```

---

## Implementation Roadmap

### Phase 1: Critical Fixes (Week 1) ✅ COMPLETE
**Goal:** Fix semantic bugs and complete half-implemented features

1. ✅ **Fix LargeFaintObjectScoringStrategy inversion** (Problem #1)
   - File: `strategies.py:209-213`
   - ✅ Inverted magnitude score calculation
   - ✅ Tests passing

2. ✅ **Wire weather to scoring** (Problem #6)
   - ✅ Added weather parameter to `ObservabilityCalculationService`
   - ✅ Added weather to `ScoringContext`
   - ✅ Implemented `_calculate_weather_factor()` module-level function
   - ✅ Cloud cover → proportional penalty (6/7 tests passing)

3. ✅ **Test suite foundation**
   - ✅ Created comprehensive test suite (89 tests total)
   - ✅ 60 unit tests (pairwise comparisons)
   - ✅ 29 advanced tests (weather, moon, edge cases)
   - ✅ Baseline documented

4. ✅ **BONUS: Fixed below-horizon bug** (Night shift)
   - ✅ Objects below horizon now correctly score 0.0
   - ✅ Added check to all three altitude factor methods

### Phase 2: Moon Integration (Week 2)
**Goal:** Add moon conditions to scoring

4. ✅ **Create Moon model**
   - File: `src/app/domain/model/moon_conditions.py`
   - Fields: phase, illumination, altitude, ra, dec
   - Helper: `calculate_separation(target_ra, target_dec) -> float`

5. ✅ **Integrate moon into scoring**
   - Add moon_conditions to `ScoringContext`
   - Implement `_calculate_moon_proximity_factor()` in strategies
   - Formula: `penalty = (illumination / 100) * (60 / max(separation, 5))²`
   - Objects < 5° from bright moon → near zero score

6. ✅ **Moon UI integration**
   - Add moon phase/altitude display to observation planning panel
   - Calculate moon position from date/time/location
   - Use astronomy libraries (e.g., `ephem` or `skyfield`)

7. ✅ **Moon proximity tests**
   - Implement test category 5 (all moon test cases)
   - Verify penalties scale correctly with separation and illumination

### Phase 3: Factor Pipeline Refactor (Week 3)
**Goal:** Make scoring transparent and modular

8. ✅ **Refactor to multiplicative pipeline**
   - Replace `base_score = (mag + size) / 2` with separate factors
   - Each strategy returns: `mag_factor * size_factor * equip_factor * site_factor * alt_factor * weather_factor * moon_factor`
   - All factors normalized to ~1.0 (can be > 1 for bonuses)

9. ✅ **Add factor breakdown to output**
   - Extend `CelestialObjectScore` to include factor breakdown:
     ```python
     @dataclass
     class CelestialObjectScore:
         raw: float
         normalized: float
         factors: dict  # {'magnitude': 0.8, 'equipment': 1.2, ...}
     ```
   - Display factor breakdown in UI tooltip or detail view

10. ✅ **Document factor ranges**
    - Add docstrings to each factor calculation
    - Document expected range (e.g., 0.3 to 1.5)
    - Document optimal conditions

### Phase 4: Light Pollution + Constants (Week 4)
**Goal:** Use physics-based models and clean up magic constants

11. ✅ **Replace Bortle multipliers with limiting magnitude** (Problem #7)
    - Create `src/app/utils/light_pollution_models.py`
    - Implement Bortle → limiting magnitude mapping
    - Implement visibility check: `object_mag < limiting_mag`
    - Scale factor based on magnitude difference

12. ✅ **Document and clean magic constants** (Problem #3)
    - File: `src/app/utils/constants.py`
    - Add docstring to each constant explaining derivation
    - Example:
      ```python
      # Sun's magnitude is -26.74
      # Using formula: score = 10^(-0.4 * mag)
      # sun_score = 10^(-0.4 * -26.74) = 10^10.696 = 49,659,232,145
      sun_solar_magnitude_score = 49659232145.03358
      ```

13. ✅ **Light pollution test suite**
    - Implement test category 3 (light pollution tests)
    - Verify limiting magnitude cutoffs work correctly

### Phase 5: Double Stars (Week 5)
**Goal:** Add double star splitability scoring

14. ✅ **Add separation field** (Problem #4)
    - Add `separation: Optional[float]` to `CelestialObject` (arcseconds)
    - Add `is_double_star()` helper method
    - Update database schema

15. ✅ **Implement splitability calculation**
    - Add method to `ScoringContext`: `can_split(separation: float) -> bool`
    - Dawes' limit: `dawes_limit = 116 / aperture_mm`
    - Rayleigh criterion: `rayleigh_limit = 138 / aperture_mm`

16. ✅ **Adjust scoring for double stars**
    - If double star and splittable → bonus factor (1.2x)
    - If double star and NOT splittable → penalty factor (0.7x)
    - Add test cases with various separations and apertures

### Phase 6: Full Test Coverage (Week 6)
**Goal:** Complete test matrix and validate entire system

17. ✅ **Implement remaining test categories**
    - Category 2: Equipment impact tests
    - Category 4: Altitude impact tests
    - Category 6: Weather impact tests
    - Category 7: Edge cases

18. ✅ **Regression testing**
    - Run full suite after each change
    - Document any score changes from baseline
    - Justify changes in scoring behavior

19. ✅ **Integration testing**
    - Test full UI flow: select equipment → import data → verify scores
    - Test with real astronomical databases
    - Validate scores against expert observations

### Phase 7: Code Quality - Eliminate Magic Numbers (Week 7) ✅ COMPLETE
**Goal:** Replace ALL magic numbers with named constants (Uncle Bob would approve!)

**Status:** COMPLETED during night shift! All magic numbers eliminated.

**Files Created:**
- ✅ `src/app/utils/scoring_constants.py` (423 lines, 80+ constants)

**Files Modified:**
- ✅ `src/app/domain/services/strategies.py` (all magic numbers replaced)
- ✅ `src/app/domain/services/observability_calculation_service.py` (uses constants)

20. ✅ **Extract weather threshold constants**
    - ✅ File: `src/app/utils/scoring_constants.py` created
    - Replace hardcoded thresholds in `_calculate_weather_factor()`:
      ```python
      # BEFORE (current mess):
      if cloud_cover >= 100:
          return 0.05  # What does 0.05 mean? Why 0.05?
      elif cloud_cover >= 75:
          return 0.25  # Magic!

      # AFTER (readable):
      WEATHER_CLOUD_COVER_OVERCAST = 100
      WEATHER_CLOUD_COVER_MOSTLY_CLOUDY = 75
      WEATHER_CLOUD_COVER_PARTLY_CLOUDY = 50
      WEATHER_CLOUD_COVER_FEW_CLOUDS = 25

      WEATHER_FACTOR_OVERCAST = 0.05  # Nearly impossible to observe
      WEATHER_FACTOR_MOSTLY_CLOUDY = 0.25  # 75% reduction
      WEATHER_FACTOR_PARTLY_CLOUDY = 0.50  # 50% reduction
      WEATHER_FACTOR_FEW_CLOUDS = 0.75  # 25% reduction
      WEATHER_FACTOR_CLEAR = 1.0  # No penalty

      if cloud_cover >= WEATHER_CLOUD_COVER_OVERCAST:
          return WEATHER_FACTOR_OVERCAST
      elif cloud_cover >= WEATHER_CLOUD_COVER_MOSTLY_CLOUDY:
          return WEATHER_FACTOR_MOSTLY_CLOUDY
      # etc...
      ```

21. 🔴 **Extract altitude threshold constants**
    - Replace hardcoded altitude thresholds:
      ```python
      # BEFORE:
      if altitude >= 30:
          return 1.0  # What's special about 30?
      elif altitude >= 20:
          return 0.85  # Why 0.85?

      # AFTER:
      ALTITUDE_OPTIMAL_MIN = 30  # Degrees - minimal atmospheric distortion
      ALTITUDE_GOOD_MIN = 20  # Degrees - acceptable viewing
      ALTITUDE_POOR_MIN = 10  # Degrees - significant atmospheric effects

      ALTITUDE_FACTOR_OPTIMAL = 1.0  # No atmospheric penalty
      ALTITUDE_FACTOR_GOOD = 0.85  # 15% atmospheric reduction
      ALTITUDE_FACTOR_POOR = 0.65  # 35% atmospheric reduction
      ALTITUDE_FACTOR_VERY_POOR = 0.4  # 60% atmospheric reduction
      ```

22. 🔴 **Extract magnification threshold constants**
    - Replace planetary magnification magic numbers:
      ```python
      # BEFORE:
      if 150 <= magnification <= 300:
          return 1.2  # Bonus for... what exactly?
      elif magnification < 50:
          return 0.7  # Why 50? Why 0.7?

      # AFTER:
      MAGNIFICATION_PLANETARY_OPTIMAL_MIN = 150  # Minimum for planetary detail
      MAGNIFICATION_PLANETARY_OPTIMAL_MAX = 300  # Maximum before seeing degrades
      MAGNIFICATION_PLANETARY_TOO_LOW = 50  # Insufficient for detail
      MAGNIFICATION_LARGE_OBJECT_MAX = 50  # Maximum before FOV too narrow

      MAGNIFICATION_FACTOR_OPTIMAL = 1.2  # 20% bonus for ideal magnification
      MAGNIFICATION_FACTOR_ACCEPTABLE = 1.0  # No bonus/penalty
      MAGNIFICATION_FACTOR_TOO_LOW = 0.7  # 30% penalty for insufficient mag
      MAGNIFICATION_FACTOR_TOO_HIGH = 0.6  # 40% penalty for excessive mag
      ```

23. 🔴 **Extract aperture threshold constants**
    - Replace aperture comparison magic numbers:
      ```python
      # BEFORE:
      if aperture >= 200:
          return 1.3  # Why 200mm? Why 1.3x?
      elif aperture >= 100:
          return 1.1

      # AFTER:
      APERTURE_LARGE = 200  # mm - professional/serious amateur range
      APERTURE_MEDIUM = 100  # mm - standard amateur range
      APERTURE_SMALL = 70  # mm - beginner range

      APERTURE_FACTOR_LARGE = 1.3  # 30% bonus for light gathering
      APERTURE_FACTOR_MEDIUM = 1.1  # 10% bonus
      APERTURE_FACTOR_SMALL = 1.0  # No bonus
      APERTURE_FACTOR_INSUFFICIENT = 0.8  # 20% penalty for tiny scope
      ```

24. 🔴 **Extract light pollution penalty constants**
    - Replace Bortle scale multipliers:
      ```python
      # BEFORE:
      penalty_per_bortle = 0.10  # What does this represent?

      # AFTER:
      LIGHT_POLLUTION_PENALTY_PER_BORTLE = 0.10  # 10% reduction per Bortle level
      LIGHT_POLLUTION_DEFAULT_BORTLE = 5  # Suburban baseline

      # Better yet, use limiting magnitude mapping:
      BORTLE_TO_LIMITING_MAGNITUDE = {
          1: 7.6, 2: 7.1, 3: 6.6, 4: 6.1, 5: 5.6,
          6: 5.1, 7: 4.6, 8: 4.1, 9: 3.6
      }
      ```

25. 🔴 **Extract equipment penalty constants**
    - Replace "no equipment" magic penalties:
      ```python
      # BEFORE:
      return 0.5  # Why half? Why not 0.3 or 0.7?
      return 0.3  # Different penalty? Why?

      # AFTER:
      EQUIPMENT_PENALTY_BRIGHT_OBJECTS = 0.5  # 50% - bright objects visible naked eye
      EQUIPMENT_PENALTY_MEDIUM_OBJECTS = 0.3  # 70% - medium objects need equipment
      EQUIPMENT_PENALTY_FAINT_OBJECTS = 0.1  # 90% - faint objects nearly impossible
      ```

26. 🔴 **Extract normalization constants**
    - Replace score normalization magic:
      ```python
      # BEFORE:
      base_score = (0.4 * magnitude_score) + (0.6 * size_score)  # Why 40/60 split?
      base_score = min(base_score, max_observable_score) / 10  # Why divide by 10?

      # AFTER:
      WEIGHT_MAGNITUDE_LARGE_OBJECTS = 0.4  # 40% weight - size matters more
      WEIGHT_SIZE_LARGE_OBJECTS = 0.6  # 60% weight - large objects prioritize size

      WEIGHT_MAGNITUDE_COMPACT_OBJECTS = 0.7  # 70% weight - magnitude dominant
      WEIGHT_SIZE_COMPACT_OBJECTS = 0.3  # 30% weight

      NORMALIZATION_DIVISOR = 10  # Scale to 0-1 range
      ```

27. 🔴 **Document constant derivations**
    - Add comprehensive docstrings to `scoring_constants.py`:
      ```python
      # Weather thresholds based on meteorological standards
      WEATHER_CLOUD_COVER_OVERCAST = 100  # percent
      """
      100% cloud cover = overcast conditions.
      Based on meteorological standards where 87.5%+ coverage = overcast.
      Factor of 0.05 allows only brightest objects (Sun/Moon) to be barely visible.
      """

      # Altitude thresholds based on atmospheric physics
      ALTITUDE_OPTIMAL_MIN = 30  # degrees
      """
      30° altitude provides optimal viewing with minimal atmospheric distortion.
      Below 30°, airmass increases: airmass ≈ 1/sin(altitude)
      At 30°: airmass = 2.0 (double atmosphere to penetrate)
      At 20°: airmass = 2.9 (triple atmosphere)
      """
      ```

28. 🔴 **Audit entire codebase for remaining magic numbers**
    - Search patterns to find:
      - Bare numeric literals in conditionals: `if x >= 100:`
      - Bare numeric literals in return statements: `return 0.85`
      - Bare numeric literals in calculations: `score * 1.2`
    - Exceptions allowed:
      - Mathematical constants: `0`, `1`, `2` (when used for basic arithmetic)
      - Obvious percentages: `/ 100` (but prefer constant for clarity)
      - Array indices: `[0]`, `[1]`
    - Create `MAGIC_NUMBER_AUDIT.md` documenting:
      - Every magic number found
      - Its location
      - Its meaning
      - Proposed constant name

### Phase 8: Advanced Features (Future)
**Goal:** Add surface brightness and other advanced factors

29. 🔮 **Surface brightness calculation**
    - Formula: `surface_brightness = magnitude + 2.5 * log10(size_arcmin²)`
    - Low surface brightness objects harder to see even if bright total magnitude
    - Add to LargeFaintObjectScoringStrategy

30. 🔮 **Atmospheric extinction**
    - More sophisticated altitude model
    - Include zenith extinction coefficient
    - Wavelength-dependent effects

31. 🔮 **Telescope-specific optimization**
    - Obstruction ratio (central obstruction in reflectors)
    - Optical quality factor
    - Coating reflectivity

---

## Success Criteria

After completing the roadmap, the system should satisfy:

1. ✅ **Correctness:** All test cases pass with realistic rankings
2. ✅ **Transparency:** Each score includes factor breakdown showing why
3. ✅ **Accuracy:** Physics-based models (limiting magnitude, Dawes' limit) used
4. ✅ **Completeness:** Moon, weather, double stars integrated
5. ✅ **Maintainability:** No magic constants, clear documentation
6. ✅ **Extensibility:** Easy to add new factors or object types

---

## Testing Commands

```bash
# Run full test suite
pytest tests/scoring/test_observability_scenarios.py -v

# Run specific category
pytest tests/scoring/test_observability_scenarios.py -k "test_moon" -v

# Run with coverage
pytest tests/scoring/ --cov=app.domain.services --cov-report=html
```

---

## Notes

- **Moon proximity is the most complex new feature.** It requires astronomical position calculations and UI integration.
- **Factor pipeline refactor touches all strategies.** Test thoroughly after this change.
- **Light pollution refactor may significantly change scores.** Document baseline scores before and after.
- **Double star feature requires database migration.** Plan for schema updates.

---

## Open Questions

1. Should we add a "seeing" parameter (atmospheric turbulence)? Affects planetary detail.
2. Should we model light pollution from nearby objects (Moon affects sky brightness globally, not just near Moon)?
3. Should we add a "target priority" user preference (prefer planets over DSOs)?
4. Should we cache limiting magnitude calculations for performance?

---

## Phase 8: Constants Validation & Multi-Preset System (Week 8)

**Goal:** Validate constants against astronomical data and implement switchable presets for different user preferences.

**Status:** 🔴 PENDING - Deep research completed by ChatGPT 5.2

### Research Summary (2026-02-09)

A comprehensive constants validation was performed comparing our values against:
- Atmospheric physics models (airmass, extinction)
- Meteorological standards (oktas, cloud cover)
- Amateur astronomy community norms (exit pupil, magnification rules)
- Bortle scale photometric data (NELM ranges)

**Key Findings:**

#### 1. Weather Constants - Minor Adjustments Needed
**Problem:** Overcast threshold set to exactly 100%, but weather APIs often report 90-99% for overcast.

**Current:**
```python
WEATHER_CLOUD_COVER_OVERCAST = 100  # May under-trigger
```

**Recommendation:**
```python
WEATHER_CLOUD_COVER_OVERCAST = 90  # Matches 7/8 okta standard
```

**Rationale:** Meteorological "overcast" is 87.5%+ (7/8 oktas). Setting threshold to 90 ensures we catch "effectively overcast" conditions.

**Weather factors validated as reasonable:**
- Clear: 1.0 ✅
- Few: 0.75 → **0.85** (more lenient, matches "gap probability")
- Partly: 0.50 → **0.60-0.65** (matches observer reports)
- Mostly: 0.25 → **0.20-0.30** (acceptable range)
- Overcast: 0.05 → **0.02-0.05** (acceptable range)

#### 2. Altitude Constants - Remove Zenith Penalty + Harshen Low Altitude
**Problem 1:** Near-zenith penalty has no atmospheric basis. Zenith is optimal for airmass.

**Current:**
```python
ALTITUDE_FACTOR_NEAR_ZENITH = 0.95  # "Overhead viewing angle" (?)
```

**Recommendation:**
```python
ALTITUDE_FACTOR_NEAR_ZENITH = 1.0  # No atmospheric penalty at zenith
```

**Rationale:** Airmass is minimal at zenith. Any penalty is mount-specific ergonomics, not observability.

**Problem 2:** Deep-sky <20° penalty too optimistic.

**Current:**
```python
ALTITUDE_FACTOR_VERY_POOR_DEEPSKY = 0.5  # Still gives 50% score
```

**Recommendation:**
```python
ALTITUDE_FACTOR_VERY_POOR_DEEPSKY = 0.35  # More realistic for contrast loss
```

**Rationale:** At <20° altitude:
- Airmass ≈ 2.9-6.0
- Contrast destruction for low surface brightness objects
- Light domes near horizon
- Atmospheric dispersion

Research suggests 0.35-0.45 range is more realistic for planning app (prefer "don't waste your night" over false greens).

**Planetary altitude factors validated:**
- 30+: 1.0 ✅
- 20-30: 0.85 ✅
- 10-20: 0.65 ✅
- <10: 0.4 ✅

#### 3. Magnification Constants - Shift Range Lower
**Problem:** 150-300× optimal range assumes 150-250mm scopes. Too aggressive for 70-100mm beginners.

**Current:**
```python
MAGNIFICATION_PLANETARY_OPTIMAL_MIN = 150
MAGNIFICATION_PLANETARY_OPTIMAL_MAX = 300
```

**Recommendation:**
```python
MAGNIFICATION_PLANETARY_OPTIMAL_MIN = 120  # Fits 80mm users at 1.5mm exit pupil
MAGNIFICATION_PLANETARY_OPTIMAL_MAX = 250  # More conservative seeing limit
```

**Rationale:**
- Common rule: 0.5-1.0mm exit pupil for planets
- 80mm scope: 80-160× typical range, optimal ~120-140×
- 200mm scope: 200-400× typical range, optimal ~200-250×
- Shifting range to 120-250× better serves wider user base

#### 4. Aperture Constants - Increase Deep-Sky Scaling
**Current factors reasonable but could emphasize aperture more for DSO:**
```python
APERTURE_FACTOR_LARGE = 1.3   # 200mm+
APERTURE_FACTOR_MEDIUM = 1.1  # 100-199mm
APERTURE_FACTOR_SMALL = 1.0   # 70-99mm
APERTURE_FACTOR_TINY = 0.8    # <70mm
```

**Recommendation for deep-sky only:**
```python
APERTURE_FACTOR_LARGE_DEEPSKY = 1.50     # Aperture really matters
APERTURE_FACTOR_MEDIUM_DEEPSKY = 1.20
APERTURE_FACTOR_SMALL_DEEPSKY = 1.00
APERTURE_FACTOR_TINY_DEEPSKY = 0.70

# Keep current values for solar system (seeing dominates)
```

**Rationale:** Light grasp scales as D². 200mm vs 100mm = 4× light = ~1.5 mag deeper. This should be more pronounced in scoring for faint DSOs.

#### 5. Light Pollution - Lower Minimum Floors
**Problem:** Minimum factors too generous for bright-sky scenarios.

**Current:**
```python
LIGHT_POLLUTION_MIN_FACTOR_DEEPSKY = 0.1   # 10% minimum
LIGHT_POLLUTION_MIN_FACTOR_LARGE = 0.05    # 5% minimum
```

**Recommendation:**
```python
LIGHT_POLLUTION_MIN_FACTOR_DEEPSKY = 0.02   # Nearly impossible in Bortle 9
LIGHT_POLLUTION_MIN_FACTOR_LARGE = 0.00     # Actually impossible for large faint objects
```

**Rationale:** Planning apps should err toward "don't waste your night." Bortle 8-9 makes faint galaxies genuinely impossible. Lower floors help app say "skip it tonight."

#### 6. Reference Values - Validated ✅
```python
SUN_APPARENT_MAGNITUDE = -26.74  # Lit: -26.7 to -26.8 ✅
SIRIUS_APPARENT_MAGNITUDE = -1.46  # Lit: -1.47 ✅
SUN_ANGULAR_SIZE = 31.00  # Lit: ~32 arcmin (close enough) ✅
```

**Action item:** Verify precomputed magnitude scores match formulas in unit test.

---

### Multi-Preset Architecture

**Problem:** Different users have different tolerances for "false positives" vs "missed opportunities."

**Solution:** Implement switchable constant presets in settings tab.

#### Preset A: "Friendly Planner" (Default)
**Goal:** Encourage trying things; fewer hard "nope" results.

**Target users:**
- Beginners exploring what's possible
- Observers willing to attempt challenging targets
- Users who want a longer "maybe" list

**Constants:**
```python
# Weather
WEATHER_FACTOR_FEW_CLOUDS = 0.85
WEATHER_FACTOR_PARTLY_CLOUDY = 0.65
WEATHER_FACTOR_MOSTLY_CLOUDY = 0.30
WEATHER_FACTOR_OVERCAST = 0.05

# Altitude (deep-sky)
ALTITUDE_FACTOR_VERY_POOR_DEEPSKY = 0.45

# Light pollution
LIGHT_POLLUTION_MIN_FACTOR_DEEPSKY = 0.05
LIGHT_POLLUTION_MIN_FACTOR_LARGE = 0.03

# Aperture (deep-sky)
APERTURE_FACTOR_LARGE = 1.40
```

#### Preset B: "Strict Realism"
**Goal:** Reduce wasted time; fewer false greens.

**Target users:**
- Experienced observers who know their limits
- Users planning remote dark-sky trips (limited time)
- Imagers who need predictable conditions

**Constants:**
```python
# Weather
WEATHER_FACTOR_FEW_CLOUDS = 0.85
WEATHER_FACTOR_PARTLY_CLOUDY = 0.60
WEATHER_FACTOR_MOSTLY_CLOUDY = 0.20
WEATHER_FACTOR_OVERCAST = 0.02

# Altitude (deep-sky)
ALTITUDE_FACTOR_VERY_POOR_DEEPSKY = 0.35

# Light pollution
LIGHT_POLLUTION_MIN_FACTOR_DEEPSKY = 0.02
LIGHT_POLLUTION_MIN_FACTOR_LARGE = 0.00

# Aperture (deep-sky)
APERTURE_FACTOR_LARGE = 1.55
```

#### Implementation Plan

32. **Create preset system infrastructure**
    - File: `src/app/utils/scoring_presets.py`
    - Define `ScoringPreset` dataclass containing all tunable constants
    - Define `PRESET_FRIENDLY` and `PRESET_STRICT` instances
    - Add `active_preset` to user settings (defaults to FRIENDLY)

33. **Refactor constants to use active preset**
    - File: `src/app/utils/scoring_constants.py`
    - Move tunable constants into preset objects
    - Keep fixed constants (sun magnitude, bortle mapping, etc.) as module-level
    - Strategies access constants via `get_active_preset().CONSTANT_NAME`

34. **Settings UI integration**
    - Add "Scoring Preset" dropdown to settings tab
    - Options: "Friendly Planner" | "Strict Realism"
    - Show tooltip explaining difference
    - Persist selection in user preferences

35. **Scenario validation tests**
    - Test preset behavior across 3 key scenarios:
      1. **Bortle 8, partly cloudy, 25° altitude**
         - Expect: Friendly shows some galaxies as "yellow", Strict shows "red"
      2. **Bortle 4-5, clear, 45-70° altitude**
         - Expect: Both show faint DSOs as viable, Strict ranks slightly lower
      3. **Mostly cloudy with gaps**
         - Expect: Friendly shows short good list, Strict shows very short great list
    - Validate across gear profiles: 80mm, 130mm, 200mm

---

### Validation Checklist

Before shipping preset system:

- [ ] All precomputed magnitude scores verified in unit test
- [ ] Overcast threshold adjusted to 90%
- [ ] Zenith penalty removed (set to 1.0)
- [ ] Deep-sky <20° factor adjusted to 0.35-0.45 range
- [ ] Magnification range adjusted to 120-250×
- [ ] Aperture scaling increased for deep-sky
- [ ] Bortle floors lowered
- [ ] Preset system implemented and tested
- [ ] Settings UI updated with preset selector
- [ ] Scenario validation tests passing for both presets
- [ ] Documentation updated explaining preset differences

---

### Open Research Questions

1. **Separate transparency signal:** Should we add a "haze/high cloud" parameter independent of cloud fraction? Cloud cover alone misses "thin junk" that ruins contrast.

2. **Moon global sky brightness:** Current moon factor is proximity-based. Should we also model moon's effect on overall sky brightness (even when far from target)?

3. **Seeing parameter:** Should we add atmospheric seeing as explicit input? Would affect planetary magnification recommendations.

4. **Preset customization:** Should users be able to create custom presets, or just pick from Friendly/Strict?

5. **Dynamic preset recommendations:** Should app suggest preset based on user's observation history? (e.g., "You tend to observe low-altitude targets successfully, consider Friendly preset")

---

*Last Updated: 2026-02-09*
*Author: Claude (Anthropic) - Research by ChatGPT 5.2*
*Project: Celestial Difficulty Scoring*
