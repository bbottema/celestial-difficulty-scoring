# Celestial Observability Scoring - Improvement Plan

**Last Updated:** 2026-02-12
**Status:** Phase 8 (API Integration) ✅ | Phase 9 (Object Selection) 🔨

---

## Quick Navigation

- **Phase Plans:** See `planning/` directory for detailed phase documentation
- **Current Priority:** Phase 9 (Object Selection Workflow)
- **Latest Completion:** Phase 8 (API Integration) - OpenNGC, SIMBAD, Horizons providers with UI

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
- **Phase 6.5:** Hierarchical scoring model - eliminated aperture double-counting
- **Phase 2:** Moon proximity penalties with inverse square falloff
- **Phase 8:** Astronomical API integration - OpenNGC, SIMBAD, Horizons providers with catalog UI

### 📊 Test Status
- **113 tests total** (down from 131 - removed arbitrary threshold tests)
- **108 passing** (96% pass rate)
- **5 failing** (2 limiting magnitude + 2 benchmark aperture + 1 weather)
- **Test philosophy:** Physics-based ordering and relative comparisons (no magic number thresholds)

### 🎯 Goal
Implement Phase 9 object selection workflow to replace AstroPlanner Excel imports.

---

## Phase Overview & Dependencies

```
Phase 6 ✅ COMPLETE (Test Suite Overhaul)
    │
    ├─→ Phase 6.5 ✅ COMPLETE (Hierarchical Model) - Eliminated aperture double-counting
    │        │
    │        └─→ Prepares for Phase 7 (Object Type awareness)
    │
    ├─→ Phase 2 ✅ COMPLETE (Moon Proximity) - Implemented proximity penalties
    │
    └─→ Phase 8 ✅ COMPLETE (API Integration) - OpenNGC, SIMBAD, Horizons providers
            │
            ├─→ Phase 9 🔨 IN PROGRESS (Object Selection) - UI workflow for object selection
            │        │
            │        └─→ Phase 9.1: Pre-curated lists (Messier, Caldwell, etc.)
            │
            ├─→ Phase 7 🟢 MEDIUM (Object Types) ──→ Builds on Phase 8 + 6.5
            │
            ├─→ Phase 13 🔴 HIGH (Equipment Integration) - Foundation for all equipment types
            │        │
            │        ├─→ Enables Phase 10, 11, 12 (Filters/Imaging/Astrophotography)
            │        └─→ Enables Phase 4 (Factor Pipeline) equipment diagnostics
            │
            ├─→ Phase 3 🟡 MEDIUM (Custom Presets) ──→ Depends on Phase 5, 6.5
            │
            └─→ Phase 4 🟢 MEDIUM (Factor Pipeline) ──→ Depends on Phase 5, 6.5, Phase 2, 13
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

### Phase 2: Moon Proximity Integration ✅ COMPLETE
**Status:** COMPLETE (2026-02-11)
**Priority:** N/A
**Dependencies:** None
**File:** `planning/phase-2_moon-proximity.md`

Implemented moon proximity penalty factor to avoid recommending targets near a bright moon.

**Implementation:**
- ✅ Moon proximity factor in `strategy_utils.py:calculate_moon_proximity_factor()`
- ✅ Inverse square falloff with smooth scaling (C=3.0 factor)
- ✅ Special cases: < 1° = occluded (factor 0.0), > 60° = no penalty (factor 1.0)
- ✅ Penalties: 5° ≈ 98% penalty, 10° ≈ 92% penalty, 30° ≈ 57% penalty
- ✅ Applied to all deep sky strategies
- ✅ Solar system objects (planets, sun, moon) unaffected

**Tests Fixed:**
- ✅ `test_separation_gradient` - Monotonic score increase with separation ✓
- ✅ `test_barely_past_moon_still_very_hard` - 0.5° vs 60° comparison ✓
- ✅ `test_occultation_zero_score` - Objects at 0° separation score 0.0 ✓
- ✅ All moon proximity tests now passing (11 tests)

---

### Phase 13: Comprehensive Equipment Integration 🔴 HIGH
**Status:** NOT STARTED
**Priority:** HIGH - Critical architectural gap
**Dependencies:** None (foundational work)
**File:** `planning/phase-13_comprehensive-equipment-integration.md`

Integrate ALL equipment types (filters, optical aids, imagers) into scoring pipeline.

**Problem:** Database and UI support 5 equipment types, but only 2 are used in scoring.

**Current Coverage:**
- ✅ Telescope: Fully integrated (aperture, focal length, type)
- 🟡 Eyepiece: Partial (only focal_length used, ignores AFOV/barrel)
- ❌ Filters: Database + UI only, **not in scoring**
- ❌ Optical Aids: Database + UI only, **not in scoring**
- ❌ Imagers: Database + UI only, **not in scoring**

**Implementation:**
- Expand `ScoringContext` to include filters, optical_aids, imager
- Add `get_effective_magnification()` - includes Barlows/reducers
- Add `get_true_field_of_view()` - uses eyepiece AFOV
- Add `has_solar_filter()` - safety check for Sun
- Add `has_narrowband_filter()` - contrast boost for nebulae
- Support observation_mode: "visual" vs "imaging"

**Key Features:**
- **Optical Aids:** Barlows multiply magnification, reducers widen field
- **Filters:** Narrowband improves emission nebulae by ~2 Bortle classes
- **Solar Safety:** Sun scores 0.0 without solar filter
- **Field of View:** Penalize objects that don't fit in TFOV
- **Imaging Mode:** Foundation for camera-based scoring

**Impact:** Enables Phases 9 (Filters), 10 (Imaging), 11 (Astrophotography)

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

### Phase 8: Astronomical API Integration ✅ COMPLETE
**Status:** COMPLETE (2026-02-12)
**Priority:** N/A
**Dependencies:** None
**File:** `planning/phase-8_astronomical-api-integration.md`

Replaced AstroPlanner Excel exports with proper astronomical catalog APIs.

**Completed Implementation:**
- ✅ OpenNGC provider (13,970 DSO objects, offline CSV)
- ✅ SIMBAD provider (online enrichment with rate limiting)
- ✅ Horizons provider (Solar System ephemerides)
- ✅ CatalogService with decision tree logic (OpenNGC → SIMBAD → WDS → Horizons)
- ✅ CatalogRepository with caching (TTL: OpenNGC 1yr, SIMBAD 1wk, Horizons never)
- ✅ Classification mapper with type corrections (fixes SIMBAD misclassifications)
- ✅ Surface brightness calculations for galaxies
- ✅ Full domain models: ObjectClassification, DataProvenance
- ✅ Comprehensive test suite (1,482 lines, 6 test files)
- ✅ CatalogDataComponent UI (716 lines) integrated into main window

**Key Features:**
- **Object resolution:** Name → OpenNGC → SIMBAD fallback → Horizons for planets
- **Type mapping:** Corrects SIMBAD errors (M31→"AGN", NGC7000→"Cluster")
- **Surface brightness:** Computed from size + magnitude for undetected objects
- **Offline-first:** OpenNGC catalog provides 13,970 DSO without API calls

**Dependencies Added:** astroquery, astropy, pandas, skyfield, pyvo

**Impact:** Unblocks Phase 7 (Object Types) and Phase 9 (Object Selection Workflow)

---

### Phase 9: Object Selection Workflow 🔨 IN PROGRESS
**Status:** RESEARCH COMPLETE, PLANNING
**Priority:** HIGH - Critical for replacing AstroPlanner Excel workflow
**Dependencies:** Phase 8 (complete)
**File:** `planning/phase-9_object-selection-workflow.md`

Create UI workflow for discovering and selecting celestial objects for observability scoring.

**Research Complete:**
- ✅ Studied modern astronomy apps (SkySafari, KStars, Stellarium, TheSkyX, Telescopius)
- ✅ Identified universal patterns: two-layer architecture (browse + search), three entry points (tonight/browse/search), hierarchical list management
- ✅ Pre-curated lists solve 90% of use cases (Messier, Caldwell, Herschel 400)

**Phase 9.1 - Pre-Curated Lists** (Week 1, 2-3 days):
- 🔨 Implement named catalog lists (Messier 110, Caldwell 109, etc.)
- 🔨 UI selector for pre-curated lists
- 🔨 Batch scoring workflow

**Future Sub-phases:**
- Phase 9.2: Browse & Filter UI (constellation, type, magnitude filters)
- Phase 9.3: "Tonight" recommendations (dynamic, scored lists)
- Phase 9.4: Session management (dated observing plans)

---

### Phases 10-12: Filters, Imaging, and Astrophotography 🟢 FUTURE
**Status:** PLANNED
**Priority:** MEDIUM-HIGH (after Phase 13)
**Dependencies:** Phase 13 (Equipment Integration)
**File:** `planning/phases-9-10-11_filters-imaging-astrophotography.md`

Three major expansion phases: Filter Integration (solar safety, narrowband), Imaging Mode (camera-based scoring), and Astrophotography Features (integration time, SNR).

---

## Phase 5 Follow-up: Monitoring & Calibration 📊 ONGOING

**Status:** MONITORING REQUIRED
**Priority:** MEDIUM - Continuous improvement
**File:** `planning/phase-5_monitoring-calibration.md`

Validate Phase 5 limiting magnitude model against real-world observing conditions. Track key metrics, detect red flags, and adjust parameters if systematic errors are found.

---

## Priority Roadmap

### Immediate Next Steps
1. **Phase 9.1: Pre-Curated Object Lists** (HIGH - replace AstroPlanner Excel workflow)
2. **Phase 7: Object-Type-Aware Scoring** (MEDIUM - 15-25% accuracy boost, enabled by Phase 8)
3. **Phase 13: Equipment Integration** (HIGH - fixes architectural gap, enables filter/imaging phases)

### Medium Term
4. **Phase 9.2-9.4: Object Selection UI** (Browse/Filter, "Tonight" recommendations, session management)
5. **Phase 4: Factor Pipeline Refactor** (debugging & UI transparency)
6. **Bug Fixes** (5 tests remaining - 2 limiting magnitude, 2 benchmark aperture, 1 weather)

### Long Term
7. **Phase 3: Custom Preset Overrides** (power user feature)
8. **Phase 10: Filter Effects** (after Phase 13 - narrowband, UHC, solar)
9. **Phase 11: Imaging Mode** (after Phase 13 - camera-based scoring)
10. **Phase 12: Astrophotography** (after Phase 13 - integration time, SNR)

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
│   ├── COMPLETED_PHASES.md (Phases 2, 5, 6, 6.5, 8)
│   ├── phase-3_custom-presets.md
│   ├── phase-4_factor-pipeline.md
│   ├── phase-5_monitoring-calibration.md
│   ├── phase-7_object-type-aware-scoring.md
│   ├── phase-8_astronomical-api-integration.md (spec)
│   ├── phase-9_object-selection-workflow.md (research + planning)
│   ├── phases-9-10-11_filters-imaging-astrophotography.md
│   └── phase-13_comprehensive-equipment-integration.md
│
└── PHASE5_CODE_REVIEW_RESPONSE.md (Phase 5 architectural decisions)
```

---

*Next Priority: Phase 9.1 - Pre-Curated Object Lists*
*Latest Update: Phase 8 complete (API integration with OpenNGC, SIMBAD, Horizons)*
