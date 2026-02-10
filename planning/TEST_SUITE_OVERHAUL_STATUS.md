# Phase 6: Test Suite Overhaul - Implementation Status

**Status:** READY TO IMPLEMENT
**Priority:** HIGHEST
**Decision Date:** 2026-02-10

---

## Executive Summary

Phase 6 represents a fundamental shift in testing philosophy: from implementation-driven testing with arbitrary thresholds to user-experience-driven testing focused on relative comparisons and physics-based ordering.

### Key Decision: Remove Arbitrary Threshold Tests

**Rationale:**
- 40 tests (33% of suite) assert arbitrary numeric values (>0.80, >0.50, etc.)
- No physical or empirical basis for these thresholds
- Created circular logic: tuning constants to pass tests that were themselves arbitrary
- Made maintenance difficult and obscured real issues

**Approach Going Forward:**
- Keep 32 physics-based ordering tests (objective, always valid)
- Remove 40 arbitrary threshold tests (dead weight)
- Focus on relative comparisons that validate UX

---

## Current State Analysis

### Test Suite Breakdown (131 tests total)

**Tier 1: Physics Ordering (32 tests - 26%)** ✅ KEEP
- Objective comparisons based on physical laws
- Examples: brighter > dimmer, larger aperture > smaller, higher altitude > lower
- **Action:** Keep and fix any failures

**Tier 3: Equipment/Mixed (46 tests - 38%)** ⚠️ REVIEW
- Mix of equipment comparisons and some threshold checks
- Need manual review to recategorize
- **Action:** Review in implementation phase

**Tier 4: Edge Case/Sanity (3 tests - 2%)** ✅ KEEP
- Simple invariants: positive scores, sun always highest, below horizon = 0
- **Action:** Keep as-is

**Tier 5: Arbitrary Threshold (40 tests - 33%)** ❌ REMOVE
- Tests with magic numbers lacking justification
- Examples: `assert_that(ratio).is_greater_than(0.80)`
- **Action:** Delete entirely

### Tests to Remove (40 tests)

```
test_andromeda_hurt_by_suburbs
test_aperture_extends_limiting_magnitude
test_aperture_makes_faint_objects_visible
test_barely_past_moon_still_very_hard
test_bright_object_always_visible
test_bright_object_survives_adversity
test_california_nebula_requires_excellent_conditions
test_compact_galaxies_benefit_from_concentration
test_exponential_falloff_near_threshold
test_faint_object_devastated_by_moon
test_faint_object_near_moon_in_clouds
test_horsehead_devastated_by_city_light
test_horsehead_needs_equipment
test_jupiter_okay_without_equipment
test_jupiter_resilient_to_light_pollution
test_jupiter_resilient_to_moon
test_large_object_not_overly_crushed
test_m13_visible_in_bortle_6_with_medium_scope
test_m27_good_in_bortle_4_with_large_scope
test_m31_visible_in_bortle_5_with_small_scope
test_m33_challenging_in_bortle_5
test_m42_excellent_in_bortle_3_with_medium_scope
test_m51_invisible_in_bortle_7
test_moon_excellent_without_equipment
test_moon_unaffected_by_light_pollution
test_north_america_nebula_invisible_in_bortle_5
test_object_near_full_moon_severe_penalty
test_object_very_close_to_full_moon
test_orion_nebula_moderately_affected
test_overcast_devastates_jupiter
test_overcast_devastates_moon
test_partial_clouds_proportional_penalty
test_ring_nebula_hurt_by_city_light
test_ring_nebula_needs_equipment
test_saturn_resilient_to_light_pollution
test_sirius_visible_naked_eye
test_veil_nebula_needs_dark_skies
test_200mm_scope_bortle6_mag11_galaxy_documents_optimism
test_25_percent_clouds
test_aperture_does_not_overcome_terrible_light_pollution
```

---

## User Decisions (2026-02-10)

### Question 1: Approach
**Decision:** ✅ Approved - Focus on relative comparisons, not absolute thresholds

### Question 2: Qualitative Tier Ranges
**Decision:** ❌ Not needed
**Reasoning:** Would create another normalization layer that reduces object distinction for users

### Question 3: Handling Threshold Tests
**Decision:** ✅ Option A - Delete entirely
**Reasoning:** "Let's not drag around dead weight"

### Question 4: Next Steps
**Decision:** Complete documentation only, no code changes this session
**Reasoning:** Continuing work tonight from different location, need clean git state

---

## Implementation Plan

### Phase 1: Cleanup (Next Session)
1. **Remove 40 threshold tests**
   - Delete from test files
   - Update test count documentation
   - Expected result: 91 tests remaining

2. **Review 46 mixed tests**
   - Manually categorize each
   - Convert pure ordering tests to Tier 1
   - Remove or refactor remaining thresholds

3. **Fix physics ordering failures**
   - Currently 16 tests failing
   - All should be fixable with current model
   - Focus on real bugs, not threshold tuning

### Phase 2: Enhancement (Future)
1. **Add user workflow tests**
   - "Generate top 10 observable targets"
   - "Compare equipment setups"
   - "Filter by difficulty/type"

2. **Add integration tests**
   - End-to-end scoring scenarios
   - API response validation
   - Performance benchmarks

3. **Update documentation**
   - Testing philosophy guide
   - How to write good tests
   - Contribution guidelines

---

## Expected Outcomes

### After Phase 1 Cleanup
- **~91 tests** (down from 131)
- **Higher quality:** All tests have clear purpose
- **Easier maintenance:** No arbitrary threshold chasing
- **Clearer failures:** Test failures indicate real UX issues

### Long-term Benefits
- **Faster development:** No tuning constants to pass arbitrary tests
- **Better confidence:** Tests validate actual user experience
- **Easier onboarding:** New contributors understand test purpose
- **Flexible calibration:** Can adjust scoring without breaking tests

---

## Technical Notes

### Current Session Progress (Pre-Phase 6)
- Started with 29 failing tests
- Fixed 13 tests through:
  - Unified base scoring formula (flux-based)
  - Hybrid normalization (logarithmic + power scaling)
  - Size threshold (1 arcmin minimum)
  - Magnitude-dependent equipment penalty
  - Zero-score threshold fix
- Ended with 16 failing tests
- **45% reduction in failures**

### Code Changes Made This Session
1. `src/app/domain/services/strategies/reflected_light_strategy.py`
   - Unified flux formula: `(flux/100) * 0.80 + (size/10) * 0.20`
   - Hybrid normalization
   - Size threshold: only apply if >= 1 arcmin

2. `src/app/domain/services/strategies/deep_sky_strategy.py`
   - Unified flux formula (same as above)
   - Magnitude-dependent equipment penalty (0.95 for mag < 1)
   - Hybrid normalization

3. `src/app/domain/services/strategies/sun_strategy.py`
   - Unified flux formula
   - Hybrid normalization

4. `src/app/utils/scoring_constants.py`
   - Added `MOON_MAGNITUDE_SCORE` constant

### Key Architectural Decisions
1. **All strategies use same base formula** (except LargeFaintObject)
2. **LargeFaintObject keeps its formula** (tried unification, broke 9 tests)
3. **Size matters only for objects >= 1 arcmin** (prevents tiny planets outscoring stars)
4. **Equipment penalty is magnitude-dependent** (bright stars visible naked-eye)

---

## Files Created/Modified

### Documentation (This Session)
- `planning/PHASE_6_TEST_SUITE_OVERHAUL.md` - Complete plan
- `planning/TEST_AUDIT.md` - Automated test categorization (121 tests analyzed)
- `planning/PHASE_6_IMPLEMENTATION_STATUS.md` - This file
- `planning/PHASE_7_STRATEGY_NOTES.md` - Created earlier for API expansion

### Code (This Session)
- All strategy files modified with unified formulas
- All changes committed: Ready for git push

---

## Ready for Git Commit

**Status:** ✅ Ready to push

**Branch:** master

**Commit Message Suggestion:**
```
Phase 6 preparation: Test suite overhaul planning and strategy unification

- Design Phase 6: UX-driven testing approach (remove 40 arbitrary threshold tests)
- Complete test audit: categorize all 131 tests by tier
- Unified scoring formulas across Sun/Moon/Planet/DeepSky strategies
- Fix 13 tests (29 → 16 failures, 45% reduction)
- Key fixes: hybrid normalization, size threshold, magnitude-dependent equipment penalty

Phase 6 implementation deferred to next session per user request.
Ready to continue tonight from different location.

🤖 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>
```

---

## Next Session Checklist

When you resume tonight:

1. ✅ Review Phase 6 documentation
2. ⬜ Remove 40 threshold tests (listed above)
3. ⬜ Review and recategorize 46 mixed tests
4. ⬜ Fix remaining 16 physics ordering test failures
5. ⬜ Update TESTING_GUIDE.md with new philosophy
6. ⬜ Mark Phase 6 as complete

---

**End of Phase 6 Planning - Ready for Implementation**
