# Celestial Observability Scoring - Improvement Plan

**Last Updated:** 2026-02-10
**Status:** Phase 5 Complete ✅

---

## Quick Navigation

- **Phase Plans:** See `planning/` directory for detailed phase documentation
- **Current Priority:** Phase 2 (Moon Proximity) OR Phase 8 (API Integration - recommended)
- **Latest Completion:** Phase 5 (Physics-based limiting magnitude model)

---

## Current State

### ✅ Completed Features
- Equipment-aware scoring with Strategy + Context pattern
- Three strategies: Solar System, Deep Sky, Large Faint Objects
- All magic numbers extracted to `scoring_constants.py` with full documentation
- Weather integration complete
- Multi-preset system (Friendly/Strict) implemented with UI selector
- Constants validated against astronomical research
- **Phase 5:** Physics-based limiting magnitude model with realism corrections

### 📊 Test Status
- **102 tests total** (includes 13 benchmark validation tests)
- **71 passing** (69% pass rate)
- **31 failing** (baseline failures + some calibration needed)
- **0 skipped** currently enabled
- **13 benchmark tests** validating real-world object behavior

### 🎯 Goal
Continue improving the scoring system through systematic phases, focusing next on moon proximity integration and astronomical API integration.

---

## Phase Overview & Dependencies

```
Phase 5 ✅ COMPLETE
    │
    ├─→ Phase 2 🔴 NEXT (Moon Proximity) ──→ Independent
    │
    ├─→ Phase 3 🟡 MEDIUM (Custom Presets) ──→ Depends on Phase 5
    │
    ├─→ Phase 4 🟢 MEDIUM (Factor Pipeline) ──→ Depends on Phase 5, Phase 2
    │
    └─→ Phase 8 🔴 CRITICAL (API Integration)
            │
            ├─→ Phase 6 🟢 LOW (Double Stars) ──→ Depends on Phase 8
            │
            ├─→ Phase 7 🟢 MEDIUM (Object Types) ──→ Depends on Phase 8
            │
            └─→ Phases 9-11 🟢 MEDIUM (Filters/Imaging) ──→ Depends on Phase 8, 7
```

---

## Phases

### Phase 2: Moon Proximity Integration 🔴 NEXT UP
**Status:** NOT STARTED (11 tests waiting)
**Priority:** HIGH
**Dependencies:** None
**File:** `planning/phase-2_moon-proximity.md`

Factor moon conditions into scoring to avoid recommending targets near a bright moon.

---

### Phase 3: Custom Preset Overrides 🟡 MEDIUM PRIORITY
**Status:** NOT STARTED
**Priority:** MEDIUM (power user feature)
**Dependencies:** Phase 5 (complete)
**File:** `planning/phase-3_custom-presets.md`

Allow users to create custom presets by overriding individual constants.

---

### Phase 4: Factor Pipeline Refactor 🟢 MEDIUM PRIORITY
**Status:** NOT STARTED
**Priority:** MEDIUM (debugging & transparency)
**Dependencies:** Phase 5 (complete), Phase 2 (recommended)
**File:** `planning/phase-4_factor-pipeline.md`

Make all scoring factors explicit and visible for debugging.

---

### Phase 5: Limiting Magnitude Model ✅ COMPLETE
**Status:** COMPLETE (2026-02-09)
**Priority:** N/A
**Dependencies:** None
**File:** See below for summary

Physics-based limiting magnitude model with realism corrections.

**Completed Features:**
- Hard cutoffs: objects below limiting magnitude return 0.0
- Exponential falloff near detection threshold
- Aperture gain factor (0.85) corrects theoretical formula
- Graduated headroom scale by object size
- Removed double-penalty in LargeObjectStrategy
- 19 new tests (all passing)

**User Impact:**
- ✅ Fewer false positives in bright skies
- ✅ Equipment differences realistically reflected
- ✅ Large faint objects appropriately rated
- ✅ Foundation for visibility status labels

**Known Limitations:** Object type classification limited to "DeepSky" (addressed in Phase 7).

---

### Phase 6: Double Star Splitability 🟢 LOW PRIORITY
**Status:** NOT STARTED (blocked)
**Priority:** LOW (niche feature)
**Dependencies:** Phase 8 (API integration) - REQUIRED
**File:** `planning/phase-6_double-star-splitability.md`

Score double stars based on whether telescope can split them.

---

### Phase 7: Object-Type-Aware Scoring 🟢 MEDIUM PRIORITY
**Status:** NOT STARTED (blocked)
**Priority:** MEDIUM (15-25% accuracy improvement)
**Dependencies:** Phase 8 (API integration) - REQUIRED
**File:** `planning/phase-7_object-type-aware-scoring.md`

Tailor detection headroom based on actual object classification (15-25% accuracy improvement).

---

### Phase 8: Astronomical API Integration 🔴 CRITICAL
**Status:** NOT STARTED
**Priority:** CRITICAL - Unblocks phases 6, 7, 9-11
**Dependencies:** None (can start immediately)
**File:** `planning/phase-8_astronomical-api-integration.md`

Replace AstroPlanner Excel exports with proper astronomical catalog APIs. **Unblocks the most future work** - estimated 2-3 weeks implementation.

---

### Phases 9-11: Filters, Imaging, and Astrophotography 🟢 FUTURE
**Status:** PLANNED
**Priority:** MEDIUM-HIGH (after Phase 8)
**Dependencies:** Phase 8 (API), Phase 7 (object types)
**File:** `planning/phases-9-10-11_filters-imaging-astrophotography.md`

Three major expansion phases: Filter Integration (solar safety, narrowband), Astrophotography Scoring (imaging mode), and Advanced Imaging Features.

---

## Phase 5 Follow-up: Monitoring & Calibration 📊 ONGOING

**Status:** MONITORING REQUIRED
**Priority:** MEDIUM - Continuous improvement
**File:** `planning/phase-5_monitoring-calibration.md`

Validate Phase 5 limiting magnitude model against real-world observing conditions. Track key metrics, detect red flags, and adjust parameters if systematic errors are found.

---

## Test Suite Overhaul 🔴 HIGH PRIORITY

**Status:** READY TO IMPLEMENT
**Priority:** HIGH (improves development velocity)
**Dependencies:** None
**Files:** `planning/TEST_SUITE_OVERHAUL.md`, `planning/TEST_SUITE_OVERHAUL_STATUS.md`, `planning/TEST_AUDIT.md`

Transform test suite from implementation-driven to user-experience-driven. Remove 40 arbitrary threshold tests, focus on physics-based ordering and relative comparisons. This will improve maintainability and clarify what tests actually validate.

**Key Changes:**
- Remove tests with arbitrary numeric assertions (>0.80, >0.50, etc.)
- Keep 32 physics-based ordering tests (objective, always valid)
- Focus on relative comparisons that validate user experience
- Reduces test count from 131 to ~91 high-quality tests

---

## Priority Roadmap

### Immediate Next Steps (Choose One)
1. **Phase 2: Moon Proximity** (11 tests waiting, unblocks night planning)
2. **Phase 8: Astronomical API Integration** (RECOMMENDED - unblocks phases 6, 7, 9-11)

### Medium Term
3. **Phase 7: Object-Type-Aware Scoring** (after Phase 8, 15-25% accuracy boost)
4. **Phase 4: Factor Pipeline Refactor** (debugging & UI transparency)

### Long Term
5. **Phase 3: Custom Preset Overrides** (power user feature)
6. **Phase 6: Double Star Splitability** (niche but valuable)
7. **Phases 9-11: Filters & Astrophotography** (major expansion)

---

## Future Enhancement Ideas

- Surface brightness calculation for extended objects
- Atmospheric seeing parameter for planetary detail
- Transparency/haze parameter separate from cloud cover
- Telescope-specific factors (obstruction, optical quality)
- Export targets to imaging software (N.I.N.A., SGP)

---

## Testing Commands

```bash
# Run all tests
python run_tests.py

# Run specific category
python run_tests.py unit

# With verbosity
python run_tests.py -v
```

---

## Documentation Structure

```
├── SCORING_IMPROVEMENT_PLAN.md (this file)
│
├── planning/
│   ├── phase-2_moon-proximity.md
│   ├── phase-3_custom-presets.md
│   ├── phase-4_factor-pipeline.md
│   ├── phase-5_monitoring-calibration.md
│   ├── phase-6_double-star-splitability.md
│   ├── phase-7_object-type-aware-scoring.md
│   ├── phase-8_astronomical-api-integration.md
│   ├── phases-9-10-11_filters-imaging-astrophotography.md
│   ├── TEST_SUITE_OVERHAUL.md
│   ├── TEST_SUITE_OVERHAUL_STATUS.md
│   └── TEST_AUDIT.md
│
├── PHASE5_CODE_REVIEW_RESPONSE.md (Phase 5 architectural decisions)
└── NIGHT_SHIFT_PROGRESS.md (historical development log)
```

---

**Recommendation:** Start with **Phase 8 (Astronomical API Integration)** as it unblocks the most future work (phases 6, 7, 9-11) and provides the data foundation for accurate scoring improvements.

---

*Next Priority: Phase 2 (Moon Proximity) OR Phase 8 (API Integration - recommended)*
*Latest Update: Phase 5 complete, benchmark tests added, documentation restructured*
