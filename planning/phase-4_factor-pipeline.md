# Phase 4: Factor Pipeline Refactor

**Status:** NOT STARTED
**Priority:** 🟢 MEDIUM - Debugging & transparency feature
**Dependencies:**
- Phase 5 (complete) - Addresses Phase 5 code review items
- Phase 2 (moon proximity) - Includes moon_factor in pipeline

---

## Goal

Make all scoring factors explicit and visible for debugging, and address Phase 5 architectural improvements (aperture double-counting, solar system simplification).

---

## Problem Statement

**Current implementation:**
```python
base_score = (magnitude_score + size_score) / 2
return base_score * equipment_factor * site_factor * altitude_factor
```

**Issues:**
1. Individual factors not visible in output (hard to debug)
2. Magnitude and size combined into opaque base_score
3. Aperture counted in both equipment_factor (bonus) and site_factor (limiting magnitude)
4. Solar system objects use limiting magnitude model unnecessarily
5. No way to show users "why" object scored low/high

---

## Proposed Solution

```python
return (magnitude_factor *
        size_factor *
        equipment_factor *
        site_factor *
        altitude_factor *
        weather_factor *
        moon_factor)
```

**Benefits:**
- Each factor independently visible
- Easier debugging ("site_factor is 0.2, that's the problem!")
- Enables UI tooltips showing factor breakdown
- Can display physics_visibility vs environment_penalty separately

---

## Implementation Tasks

### 1. Separate magnitude_factor from size_factor

**Before:**
```python
magnitude_score = self._normalize_magnitude(10 ** (-0.4 * celestial_object.magnitude))
size_score = self._normalize_size(celestial_object.size)
base_score = (magnitude_score + size_score) / 2
```

**After:**
```python
magnitude_factor = self._normalize_magnitude(10 ** (-0.4 * celestial_object.magnitude))
size_factor = self._normalize_size(celestial_object.size)
# Both contribute independently (no averaging)
```

---

### 2. Extend CelestialObjectScore to Include Factors

**File:** `src/app/domain/model/celestial_object.py`

```python
@dataclass
class CelestialObjectScore:
    score: float
    normalized_score: float
    factors: dict[str, float]  # NEW: Factor breakdown

# Example usage:
score = CelestialObjectScore(
    score=0.45,
    normalized_score=4.5,
    factors={
        "magnitude": 0.8,
        "size": 0.9,
        "equipment": 1.2,
        "site": 0.5,   # ← The bottleneck!
        "altitude": 0.9,
        "weather": 1.0,
        "moon": 0.95
    }
)
```

---

### 3. Update All Strategies to Return Factor Breakdown

**File:** `src/app/domain/services/strategies.py`

```python
class DeepSkyScoringStrategy(IObservabilityScoringStrategy):
    def calculate_score(self, celestial_object, context: 'ScoringContext'):
        # Calculate all factors
        magnitude_factor = self._normalize_magnitude(...)
        size_factor = self._normalize_size(...)
        equipment_factor = self._calculate_equipment_factor(celestial_object, context)
        site_factor = self._calculate_site_factor(celestial_object, context)
        altitude_factor = self._calculate_altitude_factor(context.altitude)
        weather_factor = _calculate_weather_factor(context)
        moon_factor = self._calculate_moon_proximity_factor(celestial_object, context)

        # Calculate final score
        score = (magnitude_factor * size_factor * equipment_factor *
                site_factor * altitude_factor * weather_factor * moon_factor)

        # Return score WITH factor breakdown
        return CelestialObjectScore(
            score=score,
            normalized_score=score * 10,  # 0-10 scale
            factors={
                "magnitude": magnitude_factor,
                "size": size_factor,
                "equipment": equipment_factor,
                "site": site_factor,
                "altitude": altitude_factor,
                "weather": weather_factor,
                "moon": moon_factor
            }
        )
```

---

### 4. Add Factor Display to UI

**Visual representation:**

```
┌─ M51 - Whirlpool Galaxy ─────────────────────┐
│ Score: 35% (Marginal)                        │
│                                               │
│ Factor Breakdown:                             │
│ ├─ ✅ Magnitude: 90% (bright enough)         │
│ ├─ ✅ Size: 85% (appropriate)                │
│ ├─ ✅ Equipment: 120% (good aperture)        │
│ ├─ ⚠️ Site: 40% (light pollution!)          │
│ ├─ ✅ Altitude: 95% (high in sky)            │
│ ├─ ✅ Weather: 100% (clear)                  │
│ └─ ✅ Moon: 90% (acceptable distance)        │
│                                               │
│ 💡 Tip: Object limited by light pollution.   │
│    Try: Darker site or narrowband filter     │
└───────────────────────────────────────────────┘
```

**Color coding:**
- Green (✅): Factor > 0.7
- Yellow (⚠️): Factor 0.4-0.7
- Red (❌): Factor < 0.4

---

### 5. Address Phase 5 Code Review Items

#### 5a. Reduce Aperture Double-Counting

**Problem:** Aperture counted twice:
1. In `equipment_factor`: Large aperture gets 1.2-1.5x bonus
2. In `site_factor`: Aperture extends limiting magnitude

**Solution:** Reduce equipment_factor bonus

**File:** `src/app/domain/services/strategies.py` (DeepSkyScoringStrategy)

```python
# BEFORE (Phase 5):
def _calculate_equipment_factor(self, celestial_object, context: 'ScoringContext') -> float:
    aperture = context.get_aperture_mm()
    if aperture < 100:
        aperture_factor = 1.0
    elif aperture < 200:
        aperture_factor = 1.2  # 20% bonus
    else:
        aperture_factor = 1.5  # 50% bonus ← Too much!

# AFTER (Phase 4):
def _calculate_equipment_factor(self, celestial_object, context: 'ScoringContext') -> float:
    aperture = context.get_aperture_mm()
    if aperture < 100:
        aperture_factor = 1.0
    elif aperture < 200:
        aperture_factor = 1.05  # 5% bonus (magnification quality)
    else:
        aperture_factor = 1.1   # 10% bonus (magnification quality)

    # Aperture's main benefit is already in site_factor (limiting magnitude)
    # This bonus reflects better contrast/resolution, not brightness
```

**Rationale:** Aperture's visibility benefit is handled by limiting magnitude in `site_factor`. Equipment factor should focus on magnification/framing appropriateness.

#### 5b. Simplify Solar System Site Factor

**Problem:** Planets don't have limiting magnitude thresholds, but we're applying NELM model anyway.

**Solution:** Use simple linear penalty for planets

**File:** `src/app/domain/services/strategies.py` (SolarSystemScoringStrategy)

```python
# BEFORE (Phase 5):
def _calculate_site_factor(self, celestial_object, context: 'ScoringContext') -> float:
    """Planets barely affected by light pollution"""
    factor = calculate_light_pollution_factor_by_limiting_magnitude(
        celestial_object.magnitude,
        bortle,
        aperture,
        ...
    )  # Unnecessary complexity!
    return max(factor, 0.85)  # Floor at 85%

# AFTER (Phase 4):
def _calculate_site_factor(self, celestial_object, context: 'ScoringContext') -> float:
    """
    Planets are bright - light pollution barely affects them.
    Simple linear penalty for sky brightness (affects contrast).
    """
    bortle = context.get_bortle_number()

    # Linear penalty: Bortle 1 = 1.0, Bortle 9 = 0.85
    penalty_per_bortle = 0.02  # 2% penalty per Bortle class
    factor = 1.0 - ((bortle - 1) * penalty_per_bortle)

    return max(factor, 0.85)  # Floor at 85% (planets always visible)
```

**Rationale:** Planets are bright enough that visibility isn't the issue - contrast/detail quality is. Simple linear penalty is more appropriate.

#### 5c. Split Physics from Environment for UI

**Goal:** Show users separate "visibility" vs "conditions" scores.

**Example UI:**
```
M51 - Whirlpool Galaxy
├─ Physics Visibility: 85% ✅
│  └─ Object is detectable with your equipment
└─ Environment Penalty: 50% ⚠️
   └─ Light pollution reduces visibility
```

**Implementation:**
```python
@dataclass
class CelestialObjectScore:
    score: float
    normalized_score: float
    factors: dict[str, float]
    # NEW: Semantic groupings
    physics_visibility: float  # magnitude + equipment + site (NELM only)
    environment_penalty: float  # weather + moon + light pollution penalty
```

---

## Testing Strategy

### Test 1: Factor Breakdown Accuracy
```python
def test_factor_breakdown_multiplies_to_score():
    """All factors multiplied should equal final score"""
    result = strategy.calculate_score(m51, context)

    manual_product = 1.0
    for factor in result.factors.values():
        manual_product *= factor

    assert_that(manual_product).is_close_to(result.score, 0.01)
```

### Test 2: Aperture Double-Counting Fixed
```python
def test_aperture_bonus_reduced_in_equipment_factor():
    """Phase 4 should reduce equipment_factor aperture bonus"""
    context_200mm = create_context(aperture=200)
    context_80mm = create_context(aperture=80)

    score_200mm = strategy.calculate_score(m51, context_200mm)
    score_80mm = strategy.calculate_score(m51, context_80mm)

    equipment_ratio = (score_200mm.factors["equipment"] /
                      score_80mm.factors["equipment"])

    # Should be ~1.1x, not 1.5x (before Phase 4)
    assert_that(equipment_ratio).is_between(1.05, 1.15)
```

### Test 3: Solar System Simplification
```python
def test_jupiter_uses_simple_light_pollution_penalty():
    """Jupiter should use linear penalty, not NELM model"""
    strategy = SolarSystemScoringStrategy()

    jupiter_bortle3 = strategy.calculate_score(jupiter, context_bortle3)
    jupiter_bortle8 = strategy.calculate_score(jupiter, context_bortle8)

    # Site factor should differ by ~10% (2% per Bortle * 5 classes)
    site_ratio = jupiter_bortle3.factors["site"] / jupiter_bortle8.factors["site"]
    assert_that(site_ratio).is_close_to(1.10, 0.05)
```

---

## User Impact

### Before Phase 4:
```
M51 - Whirlpool Galaxy
Score: 35%

[User has no idea why it's low]
```

### After Phase 4:
```
M51 - Whirlpool Galaxy
Score: 35% (Marginal)

Bottleneck: Light pollution (40%)
├─ Physics visibility: 85% ✅
└─ Environment penalty: 50% ⚠️

💡 Recommendation: Visit darker site or use narrowband filter
```

---

## Phase 5 Integration

See `PHASE5_CODE_REVIEW_RESPONSE.md` for detailed rationale on:
- Aperture double-counting (Issue 2)
- Solar system NELM misuse (Issue 3)
- Separating physics from environment for UI clarity

---

## Future Enhancements

- **Factor weights customization**: Let users adjust importance of each factor
- **Factor trends**: Show how factors change over the night
- **Factor comparison**: Compare factors across multiple targets side-by-side

---

## References

- Phase 5 code review: `PHASE5_CODE_REVIEW_RESPONSE.md`
- Current strategies: `src/app/domain/services/strategies.py`
- Scoring constants: `src/app/utils/scoring_constants.py`

---

*Last Updated: 2026-02-10*
*Dependencies: Phase 5 complete, Phase 2 (moon) recommended*
*Status: Ready to implement*
