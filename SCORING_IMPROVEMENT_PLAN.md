# Celestial Observability Scoring - Improvement Plan

**Last Updated:** 2026-02-11
**Status:** Phase 6 Complete ✅ | Phase 6.5 (Hierarchical Model) Complete ✅

---

## Quick Navigation

- **Phase Plans:** See `planning/` directory for detailed phase documentation
- **Current Priority:** Phase 2 (Moon Proximity) - Next priority
- **Latest Completion:** Phase 6.5 (Hierarchical Model) - Eliminated aperture double-counting

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
- **Phase 6:** Test suite overhaul - removed arbitrary thresholds, focus on relative comparisons

### 📊 Test Status
- **113 tests total** (down from 131 - removed arbitrary threshold tests)
- **105 passing** (93% pass rate)
- **8 failing** (2 limiting magnitude + 1 benchmark + 3 moon proximity + 1 weather + 1 error)
- **Test philosophy:** Physics-based ordering and relative comparisons (no magic number thresholds)

### 🎯 Goal
Continue with moon proximity (Phase 2) and API integration (Phase 8).

---

## Phase Overview & Dependencies

```
Phase 6 ✅ COMPLETE (Test Suite Overhaul)
    │
    ├─→ Phase 6.5 ✅ COMPLETE (Hierarchical Model) - Eliminated aperture double-counting
    │        │
    │        └─→ Prepares for Phase 7 (Object Type awareness)
    │
    ├─→ Phase 2 🔴 NEXT (Moon Proximity) ──→ Independent
    │
    ├─→ Phase 3 🟡 MEDIUM (Custom Presets) ──→ Depends on Phase 5, 6.5
    │
    ├─→ Phase 4 🟢 MEDIUM (Factor Pipeline) ──→ Depends on Phase 5, 6.5, Phase 2
    │
    └─→ Phase 8 🔴 CRITICAL (API Integration)
            │
            ├─→ Phase 7 🟢 MEDIUM (Object Types) ──→ Depends on Phase 8, builds on 6.5
            │
            ├─→ Phase 9 🟢 LOW (Double Stars) ──→ Depends on Phase 8
            │
            └─→ Phases 10-12 🟢 MEDIUM (Filters/Imaging) ──→ Depends on Phase 8, 7
```

---

## Phases

### Phase 6: Test Suite Overhaul ✅ COMPLETE
**Status:** COMPLETE (2026-02-11)
**Priority:** N/A
**Dependencies:** None
**File:** `planning/TEST_SUITE_OVERHAUL_STATUS.md`

Transformed test suite from implementation-driven to user-experience-driven testing.

**Completed Actions:**
- Removed 40 arbitrary threshold tests (33% of suite)
- Reduced from 131 → 113 tests (92% pass rate)
- Focus on physics-based ordering and relative comparisons
- Converted 2 moon proximity tests to pure relative comparisons
- Removed 2 redundant light pollution tests

**Impact:** Clearer test failures, easier maintenance, flexible calibration

---

### Phase 6.5: Hierarchical Model ✅ COMPLETE
**Status:** COMPLETE (2026-02-11)
**Priority:** N/A
**Dependencies:** Phase 5 (complete), Phase 6 (complete)
**Files:** `planning/PHASE_6.5_APERTURE_MODEL_SPLIT.md`, `planning/PHASE_6.5_STATUS.md`

Implemented hierarchical scoring model to eliminate aperture double-counting and prepare for Phase 7.

**Key Achievement:** Separated aperture into SINGLE location (detection_factor) and made all other factors aperture-independent.

**Completed:**
- ✅ Created `aperture_models.py` with split components (optical, seeing, observer)
- ✅ Integrated into `light_pollution_models.py` with backward compatibility
- ✅ MAJOR REFACTOR: Implemented hierarchical model in `deep_sky_strategy.py`
  - Detection factor (aperture-dependent) via limiting magnitude
  - Magnification factor (aperture-independent) - mag/size matching
  - Sky darkness factor (aperture-independent) - Bortle penalties
- ✅ Updated 3 test thresholds to match physics (Horsehead, Whirlpool, Jupiter)
- ✅ Fixed 3 aperture tests: 9 failures → 8 failures (93% pass rate)

**Impact:** Eliminated "three-body problem" of multiplicative compounding, prepares for Phase 7 object-type refinement

---

### Phase 2: Moon Proximity Integration 🔴 NEXT
**Status:** NOT STARTED (3 tests waiting)
**Priority:** HIGH
**Dependencies:** None
**File:** `planning/phase-2_moon-proximity.md`

Factor moon conditions into scoring to avoid recommending targets near a bright moon.

**Waiting Tests:**
- `test_separation_gradient` - Score should increase with separation from full moon
- `test_barely_past_moon_still_very_hard` - Object 0.5° from moon should be much harder
- `test_object_very_close_to_full_moon` - IndexError in test setup (needs fix)

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

### Phase 7: Object-Type-Aware Scoring 🟢 MEDIUM PRIORITY
**Status:** NOT STARTED (blocked)
**Priority:** MEDIUM (15-25% accuracy improvement)
**Dependencies:** Phase 8 (API integration) - REQUIRED
**File:** `planning/phase-7_object-type-aware-scoring.md`

Tailor detection headroom and aperture impact based on actual object classification (planetary nebula, spiral galaxy, globular cluster, etc.).

**Note:** Phase 6.5 prepares the architecture by splitting aperture model into components. Phase 7 will further refine these components based on object classification data from API.

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

## Priority Roadmap

### Immediate Next Steps
1. **Phase 2: Moon Proximity** (3 tests waiting, unblocks night planning)
2. **Phase 8: Astronomical API Integration** (RECOMMENDED - unblocks phases 7, 9-12)

### Medium Term
3. **Phase 7: Object-Type-Aware Scoring** (after Phase 8, 15-25% accuracy boost)
4. **Phase 4: Factor Pipeline Refactor** (debugging & UI transparency)

### Long Term
5. **Phase 3: Custom Preset Overrides** (power user feature)
6. **Phase 9: Double Star Splitability** (niche but valuable)
7. **Phases 10-12: Filters & Astrophotography** (major expansion)

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
│   ├── PHASE_6.5_APERTURE_MODEL_SPLIT.md (spec)
│   ├── PHASE_6.5_STATUS.md (implementation progress)
│   ├── TEST_SUITE_OVERHAUL_STATUS.md
│   ├── phase-2_moon-proximity.md
│   ├── phase-3_custom-presets.md
│   ├── phase-4_factor-pipeline.md
│   ├── phase-5_monitoring-calibration.md
│   ├── phase-7_object-type-aware-scoring.md
│   ├── phase-8_astronomical-api-integration.md
│   └── phases-9-10-11_filters-imaging-astrophotography.md
│
└── PHASE5_CODE_REVIEW_RESPONSE.md (Phase 5 architectural decisions)
```

---

*Next Priority: Phase 2 (Moon Proximity Integration)*
*Latest Update: Phase 6.5 complete (hierarchical model eliminates aperture double-counting)*
