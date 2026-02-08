# Test Suite Results - Initial Run

**Date:** 2026-02-08
**Total Tests:** 89 (60 unit + 29 advanced)
**Status:** 44 passed, 20 failed, 5 errors, 20 skipped

## Summary

This initial test run establishes a baseline for the scoring system. As expected, many tests fail because features are not yet implemented. This is **intentional** - we developed the test suite first to guide implementation.

## Results Breakdown

### ✅ Passing Tests (44/89 = 49%)

These tests validate currently working features:

**Basic Magnitude Ordering:**
- Sun > Moon hierarchy working
- Jupiter > Saturn ordering correct
- Most deep-sky magnitude comparisons correct

**Altitude Penalties:**
- Higher altitude scores better than lower
- Altitude gradient working correctly

**Equipment Impact:**
- Large objects prefer low magnification ✓
- Planets prefer high magnification ✓
- Light pollution gradient working ✓

**Moon Dominance:**
- Moon beats most other objects correctly

### ❌ Failing Tests (20/89 = 22%)

These failures indicate known issues:

**Magnitude Comparison Issues:**
1. `test_brighter_always_better` - FAIL
   - Issue: LargeFaintObject strategy has inverted logic (brighter → lower score)
   - Fix: Problem #1 in SCORING_IMPROVEMENT_PLAN.md

2. `test_pleiades_beats_andromeda` - FAIL
   - Related to size vs magnitude weighting

3. `test_orion_nebula_beats_veil_nebula` - FAIL
   - Large objects with different magnitudes not ordering correctly

4. `test_ic_1396_beats_horsehead` - FAIL
   - Faint object ordering broken (inverted logic bug)

**Stars vs Planets:**
5. `test_sirius_beats_saturn` - FAIL
6. `test_vega_beats_saturn` - FAIL
   - Stars not properly competing with planets

**Light Pollution:**
7. `test_andromeda_hurt_by_suburbs` - FAIL
   - Light pollution penalties not strong enough
8. `test_orion_nebula_moderately_affected` - FAIL
   - Light pollution impact not calibrated correctly
9. `test_moon_unaffected_by_light_pollution` - FAIL
   - Moon being penalized by light pollution (shouldn't be)

**Naked Eye Visibility:**
10. `test_jupiter_okay_without_equipment` - FAIL
11. `test_moon_excellent_without_equipment` - FAIL
12. `test_sirius_visible_naked_eye` - FAIL
    - No equipment penalty too harsh for bright objects

**Altitude:**
13. `test_below_horizon_is_zero` - FAIL
    - Objects below horizon not scoring zero

**Other:**
14. `test_mars_beats_saturn` - FAIL
15. `test_moon_beats_horsehead` - FAIL

### ⚠️ Errors (5/89 = 6%)

These tests encountered exceptions:

1. `test_aperture_helps_horsehead` - ERROR
2. `test_aperture_helps_ring_nebula` - ERROR
3. `test_aperture_helps_whirlpool` - ERROR
4. `test_aperture_minor_impact_on_jupiter` - ERROR
5. `test_aperture_minor_impact_on_moon` - ERROR

**Likely cause:** Equipment entities not properly initialized or missing required fields.

### ⏭️ Skipped Tests (20/89 = 22%)

These tests are skipped because features are not yet implemented:

**Weather Features (7 tests):**
- `test_clear_weather_no_penalty` - Weather parameter not implemented
- `test_overcast_devastates_jupiter` - Weather parameter not implemented
- `test_overcast_devastates_moon` - Weather parameter not implemented
- `test_overcast_kills_faint_objects` - Weather parameter not implemented
- `test_partial_clouds_proportional_penalty` - Weather parameter not implemented
- `test_25_percent_clouds` - Weather parameter not implemented
- `test_weather_gradient_jupiter` - Weather parameter not implemented

**Moon Proximity Features (11 tests):**
- `test_object_near_full_moon_severe_penalty` - Moon conditions not implemented
- `test_object_very_close_to_full_moon` - Moon conditions not implemented
- `test_new_moon_no_penalty` - Moon conditions not implemented
- `test_quarter_moon_moderate_penalty` - Moon conditions not implemented
- `test_crescent_moon_minor_penalty` - Moon conditions not implemented
- `test_separation_gradient` - Moon conditions not implemented
- `test_double_separation_significant_improvement` - Moon conditions not implemented
- `test_occultation_zero_score` - Moon conditions not implemented
- `test_barely_past_moon_still_very_hard` - Moon conditions not implemented
- `test_jupiter_resilient_to_moon` - Moon conditions not implemented
- `test_faint_object_devastated_by_moon` - Moon conditions not implemented

**Combined Factors (2 tests):**
- `test_faint_object_near_moon_in_clouds` - Combined parameters not implemented
- `test_bright_object_survives_adversity` - Combined parameters not implemented

## Test Coverage by Feature

| Feature | Tests | Pass | Fail | Error | Skip | Coverage |
|---------|-------|------|------|-------|------|----------|
| Basic Magnitude | 12 | 7 | 5 | 0 | 0 | 58% |
| Altitude Impact | 4 | 3 | 1 | 0 | 0 | 75% |
| Equipment (Aperture) | 5 | 0 | 0 | 5 | 0 | 0% |
| Equipment (Magnification) | 5 | 5 | 0 | 0 | 0 | 100% |
| Light Pollution | 9 | 6 | 3 | 0 | 0 | 67% |
| No Equipment | 5 | 2 | 3 | 0 | 0 | 40% |
| Object Type Comparisons | 15 | 13 | 2 | 0 | 0 | 87% |
| Weather | 7 | 0 | 0 | 0 | 7 | N/A |
| Moon Proximity | 11 | 0 | 0 | 0 | 11 | N/A |
| Combined Factors | 2 | 0 | 0 | 0 | 2 | N/A |
| Edge Cases | 8 | 8 | 0 | 0 | 0 | 100% |
| Sanity Checks | 3 | 2 | 1 | 0 | 0 | 67% |

## Priority Fixes

Based on failure patterns, prioritize these fixes:

### 🔴 Critical (Fix First)
1. **LargeFaintObject inverted logic** - Affects 5+ tests
   - File: `strategies.py:209-213`
   - Fix: Invert magnitude score calculation

2. **Below horizon not zero** - Safety issue
   - Objects below horizon should be impossible to observe

3. **Equipment entity errors** - Blocking 5 tests
   - Check Telescope/Eyepiece initialization

### 🟡 High Priority
4. **Light pollution calibration** - Affects multiple test categories
   - Moon should be unaffected
   - DSOs need stronger penalties

5. **No equipment penalties** - Naked eye visibility wrong
   - Bright objects should remain visible

6. **Stars vs Planets ordering** - Magnitude comparison issues

### 🟢 Medium Priority
7. **Weather parameter** - Add to service (20 skipped tests)
8. **Moon conditions** - Add Moon model (11 skipped tests)

## Next Steps

1. **Fix critical bugs** (items 1-3 above)
2. **Re-run test suite** - Track improvement
3. **Implement weather** - Unblock 7 tests
4. **Implement moon proximity** - Unblock 11 tests
5. **Refactor to factor pipeline** - Make debugging easier

## How to Use This Report

1. **Pick a failing test** from the list above
2. **Read the test code** to understand expected behavior
3. **Debug the strategy** that handles that object type
4. **Fix the issue** and re-run tests
5. **Track progress** by watching pass rate increase

## Running Tests

```bash
# Run all tests
python run_tests.py

# Run only unit tests
python run_tests.py unit

# Run only advanced tests
python run_tests.py advanced

# Run specific test class
python -m unittest tests.scoring.test_observability_unit_tests.TestSolarSystemBrightnessOrdering -v

# With PYTHONPATH
PYTHONPATH=src python run_tests.py
```

---

**Goal:** 100% pass rate (excluding legitimately skipped tests)
**Current:** 49% pass rate (excluding skipped)
**Next Milestone:** 75% pass rate after fixing critical bugs
