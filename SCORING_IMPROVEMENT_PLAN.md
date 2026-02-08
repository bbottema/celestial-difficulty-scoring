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

### 6. **INCOMPLETE: Weather Not Wired to Scoring**

**Location:** `src/app/ui/main_window/observation_data/observation_data_component.py:365`

**Problem:** Weather dropdown exists in UI but selected value not passed to `ObservabilityCalculationService`.

**Current Code:**
```python
scored_celestial_objects = self.observability_calculation_service.score_celestial_objects(
    celestial_objects, telescope, eyepiece, site)
# Missing: weather parameter!
```

**Fix:**
- Add weather parameter to service methods
- Add weather to ScoringContext
- Add weather_factor to strategies (cloud cover → severe penalty)

**Priority:** 🔴 CRITICAL - Half-implemented feature confuses users

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

### Phase 1: Critical Fixes (Week 1)
**Goal:** Fix semantic bugs and complete half-implemented features

1. ✅ **Fix LargeFaintObjectScoringStrategy inversion** (Problem #1)
   - File: `strategies.py:209-213`
   - Invert magnitude score calculation
   - Add regression test

2. ✅ **Wire weather to scoring** (Problem #6)
   - Add weather parameter to `ObservabilityCalculationService`
   - Add weather to `ScoringContext`
   - Implement `_calculate_weather_factor()` in all strategies
   - Cloud cover → proportional penalty

3. ✅ **Test suite foundation**
   - Create `tests/scoring/test_observability_scenarios.py`
   - Implement sanity check tests (category 1)
   - Run full test suite and document baseline

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

### Phase 7: Advanced Features (Future)
**Goal:** Add surface brightness and other advanced factors

20. 🔮 **Surface brightness calculation**
    - Formula: `surface_brightness = magnitude + 2.5 * log10(size_arcmin²)`
    - Low surface brightness objects harder to see even if bright total magnitude
    - Add to LargeFaintObjectScoringStrategy

21. 🔮 **Atmospheric extinction**
    - More sophisticated altitude model
    - Include zenith extinction coefficient
    - Wavelength-dependent effects

22. 🔮 **Telescope-specific optimization**
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

*Last Updated: 2026-02-08*
*Author: Claude (Anthropic)*
*Project: Celestial Difficulty Scoring*
