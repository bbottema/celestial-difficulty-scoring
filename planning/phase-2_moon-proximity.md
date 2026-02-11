# Phase 2: Moon Proximity Integration

**Status:** ✅ COMPLETE (2026-02-11)
**Priority:** N/A
**Dependencies:** None

---

## Goal

Factor moon conditions into scoring to avoid recommending targets near a bright moon.

---

## Problem Statement

Currently, the scoring system does not consider the moon's position or phase. This leads to:
- Recommending faint deep-sky objects near a bright moon (invisible due to scattered light)
- No differentiation between new moon nights (excellent) vs full moon nights (poor for DSO)
- Users waste time planning sessions without moon awareness

---

## Implementation Tasks

### 1. Create `MoonConditions` Model

**File:** `src/app/domain/model/moon_conditions.py`

```python
from dataclasses import dataclass
import math

@dataclass
class MoonConditions:
    """
    Represents current moon state and position.
    """
    phase: float              # 0-1 (0=new, 0.5=full, 1=new)
    illumination: float       # 0-100 percentage
    altitude: float           # degrees above horizon (-90 to +90)
    ra: float                 # right ascension (decimal degrees)
    dec: float                # declination (decimal degrees)

    def calculate_separation(self, target_ra: float, target_dec: float) -> float:
        """
        Calculate angular separation between moon and target in degrees.
        Uses spherical law of cosines.
        """
        ra1, dec1 = math.radians(self.ra), math.radians(self.dec)
        ra2, dec2 = math.radians(target_ra), math.radians(target_dec)

        cos_separation = (math.sin(dec1) * math.sin(dec2) +
                         math.cos(dec1) * math.cos(dec2) *
                         math.cos(ra1 - ra2))

        return math.degrees(math.acos(cos_separation))

    def is_above_horizon(self) -> bool:
        """Check if moon is currently visible"""
        return self.altitude > 0
```

---

### 2. Implement Moon Proximity Factor

Add to each scoring strategy:

```python
def _calculate_moon_proximity_factor(self, celestial_object, context: 'ScoringContext') -> float:
    """
    Moon proximity penalty - bright moon near target washes out faint objects.

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

    # Minimum separation to avoid division by zero
    separation = max(separation, 5.0)

    # Angular distance penalty (inverse square)
    distance_penalty = (60.0 / separation) ** 2
    distance_penalty = min(distance_penalty, 1.0)  # Cap at 1.0

    # Illumination penalty (linear)
    illumination_penalty = moon.illumination / 100.0

    # Combined penalty
    penalty = illumination_penalty * distance_penalty

    return 1.0 - penalty  # Convert penalty to factor
```

**Add to strategy `calculate_score()` methods:**
```python
# Add moon_factor to scoring chain
moon_factor = self._calculate_moon_proximity_factor(celestial_object, context)

return (base_score * equipment_factor * site_factor *
        altitude_factor * weather_factor * moon_factor)
```

---

### 3. Integrate into Scoring Context

**File:** `src/app/domain/model/scoring_context.py`

```python
from app.domain.model.moon_conditions import MoonConditions

@dataclass
class ScoringContext:
    telescope: Optional[Telescope]
    eyepiece: Optional[Eyepiece]
    observation_site: Optional[ObservationSite]
    altitude: float
    weather: Optional[dict] = None
    moon_conditions: Optional[MoonConditions] = None  # NEW
```

**File:** `src/app/domain/services/observability_calculation_service.py`

Update to calculate and pass moon conditions:
```python
def calculate_observability_scores(...):
    # Calculate moon conditions from date/time/location
    moon_conditions = calculate_moon_conditions(date, location)

    context = ScoringContext(
        telescope=telescope,
        eyepiece=eyepiece,
        observation_site=site,
        altitude=altitude,
        weather=weather,
        moon_conditions=moon_conditions  # NEW
    )

    # ... rest of scoring logic
```

---

### 4. Moon Position Calculator

**File:** `src/app/utils/moon_calculator.py`

Use `ephem` or `skyfield` library:

```python
import ephem
from datetime import datetime
from app.domain.model.moon_conditions import MoonConditions

def calculate_moon_conditions(
    date: datetime,
    latitude: float,
    longitude: float
) -> MoonConditions:
    """
    Calculate moon position and phase for given date/location.
    """
    observer = ephem.Observer()
    observer.lat = str(latitude)
    observer.lon = str(longitude)
    observer.date = date

    moon = ephem.Moon(observer)

    return MoonConditions(
        phase=moon.moon_phase,
        illumination=moon.moon_phase * 100,
        altitude=math.degrees(moon.alt),
        ra=math.degrees(moon.ra),
        dec=math.degrees(moon.dec)
    )
```

**Add dependency:**
```bash
pip install ephem
# OR
pip install skyfield
```

---

### 5. UI Integration

**Add to observation planning panel:**

```
┌─ Observation Conditions ──────────────────────┐
│                                                │
│ Date: 2026-02-15  Time: 21:00                 │
│ Location: Dark Sky Site (Bortle 3)            │
│                                                │
│ 🌙 Moon: 23% illuminated (Waxing Crescent)    │
│    Altitude: 15° (sets at 22:30)              │
│                                                │
│ ☁️ Weather: Clear skies                        │
│                                                │
└────────────────────────────────────────────────┘

┌─ Target Scores ───────────────────────────────┐
│ M42 - Orion Nebula        Score: 85%          │
│   Moon impact: -5% (35° away)                 │
│                                                │
│ M31 - Andromeda           Score: 40%          │
│   Moon impact: -45% (8° away) ⚠️              │
│   Warning: Too close to moon!                 │
└────────────────────────────────────────────────┘
```

**Visual indicators:**
- 🌑 New moon (0-10% illumination)
- 🌒 Waxing crescent (10-40%)
- 🌓 First quarter (40-60%)
- 🌔 Waxing gibbous (60-90%)
- 🌕 Full moon (90-100%)
- 🌖 Waning gibbous (60-90%)
- 🌗 Last quarter (40-60%)
- 🌘 Waning crescent (10-40%)

---

### 6. Enable Skipped Tests

**File:** `tests/scoring/test_advanced_scenarios.py`

Remove `@unittest.skip` decorator from 11 moon proximity tests:

```python
# BEFORE:
@unittest.skip("Moon proximity not yet implemented")
def test_full_moon_near_target(self):
    ...

# AFTER:
def test_full_moon_near_target(self):
    """Full moon within 10° should devastate score"""
    ...
```

---

## Test Cases

### Test 1: Full Moon Near Target
```python
def test_full_moon_near_target(self):
    """Full moon within 10° should devastate score (>80% penalty)"""
    object_without_moon = score_object(m42, moon=None)
    object_with_nearby_moon = score_object(m42, moon=MoonConditions(
        illumination=100, altitude=45, ra=m42.ra + 5, dec=m42.dec
    ))

    penalty = 1 - (object_with_nearby_moon / object_without_moon)
    assert_that(penalty).is_greater_than(0.8)
```

### Test 2: Full Moon Far From Target
```python
def test_full_moon_far_from_target(self):
    """Full moon >60° away should have minimal impact (<10% penalty)"""
    object_with_distant_moon = score_object(m42, moon=MoonConditions(
        illumination=100, altitude=45, ra=m42.ra + 70, dec=m42.dec
    ))

    penalty = 1 - (object_with_distant_moon / object_without_moon)
    assert_that(penalty).is_less_than(0.1)
```

### Test 3: New Moon
```python
def test_new_moon_no_penalty(self):
    """New moon should have no impact on scoring"""
    object_with_new_moon = score_object(m42, moon=MoonConditions(
        illumination=0, altitude=45, ra=m42.ra, dec=m42.dec
    ))

    assert_that(object_with_new_moon).is_equal_to(object_without_moon)
```

### Test 4: Half Moon Moderate Distance
```python
def test_half_moon_moderate_distance(self):
    """50% moon at 30° should cause ~25% penalty"""
    object_with_half_moon = score_object(m42, moon=MoonConditions(
        illumination=50, altitude=45, ra=m42.ra + 30, dec=m42.dec
    ))

    penalty = 1 - (object_with_half_moon / object_without_moon)
    assert_that(penalty).is_between(0.20, 0.30)
```

### Test 5: Moon Below Horizon
```python
def test_moon_below_horizon(self):
    """Moon below horizon should have no impact"""
    object_with_set_moon = score_object(m42, moon=MoonConditions(
        illumination=100, altitude=-10, ra=m42.ra, dec=m42.dec
    ))

    assert_that(object_with_set_moon).is_equal_to(object_without_moon)
```

### Test 6: Planets Unaffected
```python
def test_jupiter_unaffected_by_moon(self):
    """Bright planets should be unaffected by moon proximity"""
    jupiter_no_moon = score_object(jupiter, moon=None)
    jupiter_with_moon = score_object(jupiter, moon=MoonConditions(
        illumination=100, altitude=45, ra=jupiter.ra + 5, dec=jupiter.dec
    ))

    assert_that(jupiter_with_moon).is_equal_to(jupiter_no_moon)
```

---

## Expected Test Results

**Before Phase 2:** 11 tests skipped
**After Phase 2:** 11 tests passing

---

## User Impact

### Before Phase 2:
- User plans M31 observation
- Doesn't realize moon is 10° away and 90% full
- Drives to dark site, sees nothing
- Frustration and wasted time

### After Phase 2:
- User plans M31 observation
- System shows: "Score: 30% (Moon penalty: -60%)"
- Warning: "Moon too close! Wait 3 days for better conditions"
- User reschedules, has successful observation

---

## Open Questions

1. **Should moon penalty affect solar system objects?**
   - **Decision:** No, planets/Sun are bright enough to ignore moon
   - Moon observing the Moon should always score 100%

2. **What's the minimum safe separation?**
   - **Recommendation:** 30° for faint objects, 60° ideal
   - Will be validated with real-world calibration

3. **Should we show moon rise/set times?**
   - **Recommendation:** Yes, Phase 2.1 enhancement
   - "Moon sets at 22:30, excellent viewing after midnight"

4. **How to handle eclipses?**
   - **Recommendation:** Phase 2.2 enhancement (special case)
   - Lunar eclipse = excellent moon observing opportunity

---

## Future Enhancements (Phase 2.1, 2.2)

- **Phase 2.1: Moon Rise/Set Times** - Show when moon sets for late-night planning
- **Phase 2.2: Eclipse Detection** - Special scoring for lunar/solar eclipses
- **Phase 2.3: Moon Observing Mode** - Score moon features (craters, maria) based on phase/lighting

---

## References

- [Moon Phase Formula](https://en.wikipedia.org/wiki/Lunar_phase)
- [Angular Separation Calculator](https://en.wikipedia.org/wiki/Angular_distance)
- [PyEphem Documentation](https://rhodesmill.org/pyephem/)
- [Skyfield Documentation](https://rhodesmill.org/skyfield/)

---

*Last Updated: 2026-02-10*
*Status: Ready to implement*
