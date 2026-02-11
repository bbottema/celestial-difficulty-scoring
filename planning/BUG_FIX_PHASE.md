# Bug-Fix Phase: Aperture & Weather Issues

**Status:** READY TO START
**Priority:** 🔴 HIGH (blocks 6 tests)
**Created:** 2026-02-11
**Dependencies:** None

---

## Goal

Fix implementation bugs discovered during Phase 6 test suite overhaul. These are not feature gaps but broken existing functionality.

---

## Problem Statement

Phase 6 test overhaul revealed 6 failing tests exposing implementation bugs:

**Aperture Logic Issues (5 tests):**
1. Large aperture scoring **worse** than small aperture (inverted behavior)
2. Aperture having **zero effect** on bright objects when it should have minor effect
3. Aperture underperforming across the board

**Weather Threshold Issue (1 test):**
1. Overcast weather not severe enough (threshold too lenient)

---

## Failing Tests Analysis

### Aperture Bugs (5 tests)

#### Test: `test_aperture_helps_horsehead`
**Expected:** 400mm > 80mm for faint object (mag 10)
**Actual:** 400mm (0.049) < 80mm (0.057) ❌ **INVERTED**
**File:** `tests/scoring/test_observability_unit_tests.py:667`

#### Test: `test_aperture_minor_impact_on_jupiter`
**Expected:** 400mm > 80mm but ratio < 1.5 (minor improvement)
**Actual:** ratio = 1.5/1.5 = 1.0 ❌ **NO EFFECT**
**File:** `tests/scoring/test_observability_unit_tests.py:704`

#### Test: `test_aperture_extends_limiting_magnitude`
**Expected:** Larger aperture score > 0.5
**Actual:** 0.17 < 0.5 ❌ **UNDERPERFORMING**
**File:** `tests/scoring/test_limiting_magnitude_model.py:230`

#### Test: `test_aperture_makes_faint_objects_visible`
**Expected:** Aperture makes faint objects visible (score > 0.5)
**Actual:** 0.41 < 0.5 ❌ **UNDERPERFORMING**
**File:** `tests/scoring/test_limiting_magnitude_model.py:60`

#### Test: `test_large_aperture_helps_faint_galaxy_in_dark_skies`
**Expected:** 300mm > 150mm for M51 in Bortle 4
**Actual:** 300mm (0.506) < 150mm (0.532) ❌ **INVERTED**
**File:** `tests/scoring/test_benchmark_objects.py:195`

### Weather Bug (1 test)

#### Test: `test_overcast_kills_faint_objects`
**Expected:** Overcast score << clear score (ratio < 0.05)
**Actual:** Both scores identical (0.00251... = 0.00251...) ❌ **EQUAL**
**File:** `tests/scoring/test_advanced_scenarios.py:170`
**Note:** Weather is implemented but threshold too lenient

---

## Root Cause Investigation

### Likely Aperture Issues

1. **Equipment factor not using aperture correctly**
   - Check `equipment_factor.py` - aperture may be inverted or not applied
   - Check strategy files - equipment penalty may be overriding aperture benefit

2. **Limiting magnitude calculation bug**
   - Check `limiting_magnitude.py` - aperture gain may be inverted
   - Check if aperture is being used in visibility calculation

3. **Double-counting or cancellation**
   - Aperture benefit in one place may be canceled by penalty elsewhere
   - Site factor and equipment factor may be fighting each other

### Likely Weather Issue

- Weather penalty exists but threshold is too lenient
- Overcast (100% cloud cover) should nearly zero out scores
- Check `weather_factor.py` or weather penalty in strategies

---

## Implementation Plan

### Phase 1: Diagnosis (Investigation)

1. **Add debug logging to failing test**
   - Run one aperture test with detailed score breakdown
   - Identify which factor is causing inverted behavior

2. **Review aperture usage**
   ```bash
   # Find all aperture references
   grep -r "aperture" src/app/domain/services/
   ```

3. **Review equipment factor calculation**
   - File: `src/app/domain/services/factors/equipment_factor.py`
   - Verify aperture increases score, not decreases

4. **Review limiting magnitude model**
   - File: `src/app/domain/services/limiting_magnitude.py`
   - Verify larger aperture → higher limiting magnitude

### Phase 2: Fix Aperture Issues

**Target Files (likely):**
- `src/app/domain/services/factors/equipment_factor.py`
- `src/app/domain/services/limiting_magnitude.py`
- Strategy files if equipment penalty is wrong

**Fix Strategy:**
1. Identify where aperture effect is inverted
2. Fix the inversion (likely a sign error or inverted formula)
3. Verify fix doesn't break other tests
4. Run all 5 aperture tests to confirm

### Phase 3: Fix Weather Issue

**Target Files (likely):**
- `src/app/domain/services/factors/weather_factor.py`
- Strategy files if weather penalty is wrong

**Fix Strategy:**
1. Find weather penalty calculation
2. Make overcast (100% cloud cover) more severe
3. Test that clear weather still works correctly

### Phase 4: Validation

1. Run full test suite
2. Verify all 6 bugs are fixed
3. Verify no regressions in passing tests

---

## Success Criteria

- ✅ All 5 aperture tests pass
- ✅ Weather test passes
- ✅ No regressions in 104 currently passing tests
- ✅ Test suite at 113/113 passing (minus 3 Phase 2 moon tests)

---

## Files to Investigate

### High Priority
- `src/app/domain/services/factors/equipment_factor.py`
- `src/app/domain/services/limiting_magnitude.py`
- `src/app/domain/services/factors/weather_factor.py`

### Medium Priority
- `src/app/domain/services/strategies/*_strategy.py` (all strategies)
- `src/app/utils/scoring_constants.py`

### Low Priority
- Test files (only if test logic is wrong, not expected)

---

## Next Steps

1. Run diagnostic test with logging
2. Grep for aperture usage
3. Review equipment_factor.py
4. Review limiting_magnitude.py
5. Fix inverted aperture logic
6. Fix weather threshold
7. Validate full suite

---

**Start Here:** Investigate `equipment_factor.py` and `limiting_magnitude.py` for aperture inversion bug.
