# Completed Phases - Summary

## Phase 6: Test Suite Overhaul ✅
**Completed:** 2026-02-11

**Change:** Removed 40 arbitrary threshold tests, kept physics-based ordering tests.
**Philosophy:** Focus on relative comparisons (brighter > dimmer) vs magic numbers (>0.80).
**Result:** 131 tests → 113 tests, clearer failures.

Phase 6 represents a fundamental shift in testing philosophy: from implementation-driven testing with arbitrary thresholds to user-experience-driven testing focused on relative comparisons and physics-based ordering.

---

## Phase 6.5: Hierarchical Scoring Model ✅
**Completed:** 2026-02-11

**Problem:** Aperture benefits double-counted in both equipment_factor and site_factor.
**Solution:** Hierarchical separation - aperture only in detection_factor (limiting magnitude).
**Architecture:**
- Detection factor (aperture-dependent) - Can we detect it?
- Magnification factor (aperture-independent) - Is mag appropriate?
- Sky darkness factor (aperture-independent) - Light pollution penalties

**Result:** 92% → 93% pass rate, fixed 3 aperture tests.

---

## Phase 2: Moon Proximity ✅
**Completed:** 2026-02-11

**Implementation:** Moon proximity penalty using inverse square falloff with smooth scaling (C=3.0).
**Formula:**
- < 1° separation: factor = 0.0 (occluded)
- 5° separation: ~98% penalty
- 10° separation: ~92% penalty
- 30° separation: ~57% penalty
- ≥ 60° separation: no penalty

**Result:** 93% → 96% pass rate, fixed 3 moon tests.

---

## Test Status
- **Total:** 113 tests
- **Passing:** 108 (96%)
- **Failing:** 5 (2 limiting magnitude, 2 benchmark aperture, 1 weather)
