# NightGuide - Scoring System Improvement Plan

**Last Updated:** 2026-02-16
**Status:** Phase 9.1 Testing Infrastructure ✅ | Phase 9 (Object Selection) 🔨

---

## Quick Navigation

- **Phase Plans:** See `planning/` directory for detailed phase documentation
- **Current Priority:** Phase 9 (Object Selection Workflow)
- **Latest Completion:** Phase 9.1 Testing Infrastructure - Comprehensive test suite with 100% pass rate

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
- **Phase 7:** Object-type-aware scoring - type-specific detection headroom with legacy type removal
- **Phase 9.1 Testing:** Comprehensive test reorganization with SIMBAD astroquery 0.4.8+ compatibility

### 📊 Test Status
- **291 tests total** (148 unit + 143 integration)
- **Unit tests:** 148/148 passing (100%) in ~2.2s ✅
- **Integration tests:** 143/143 passing (100%) in ~2min ✅
- **Test organization:** `tests/unit/` (fast, no network) | `tests/it/` (external APIs)
- **Test runners:** `run_tests.py` (unit only) | `run_tests_it.py` (integration only)
- **Scoring normalization:** Fixed to 0-25 scale (Phase 6 design preserved)

### 🎯 Goal
Complete Phase 9 object selection workflow to replace AstroPlanner Excel imports.

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
            ├─→ Phase 7 ✅ COMPLETE (Object Types) - Type-aware scoring + legacy type removal
            │        │
            │        └─→ Enables Phase 9 (Object Selection) with classification-based filtering
            │
            ├─→ Phase 9 🔨 IN PROGRESS (Object Selection) - UI workflow for object selection
            │        │
            │        └─→ Phase 9.1: Pre-curated lists (Messier, Caldwell, etc.)
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

Transformed test suite from implementation-driven to user-experience-driven testing.

**Details:** See `planning/COMPLETED_PHASES.md`

---

### Phase 6.5: Hierarchical Model ✅ COMPLETE
**Status:** COMPLETE (2026-02-11)

Eliminated aperture double-counting by implementing hierarchical scoring model.

**Details:** See `planning/COMPLETED_PHASES.md`

---

### Phase 2: Moon Proximity Integration ✅ COMPLETE
**Status:** COMPLETE (2026-02-11)

Implemented moon proximity penalty factor with inverse square falloff.

**Details:** See `planning/COMPLETED_PHASES.md`

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

Physics-based limiting magnitude model with realism corrections.

**Details:** See `planning/COMPLETED_PHASES.md`

---

### Phase 7: Object-Type-Aware Scoring ✅ COMPLETE
**Status:** COMPLETE (2026-02-12)

Tailored detection headroom based on object classification (planetary nebula, spiral galaxy, etc.).

**Details:** See `planning/COMPLETED_PHASES.md`

---

### Phase 8: Astronomical API Integration ✅ COMPLETE
**Status:** COMPLETE (2026-02-12)

Replaced AstroPlanner Excel exports with proper astronomical catalog APIs.

**Details:** See `planning/COMPLETED_PHASES.md`

---

### Phase 9: Object Selection Workflow 🔨 IN PROGRESS
**Status:** IMPLEMENTATION STARTED
**Priority:** HIGH - Critical for replacing AstroPlanner Excel workflow
**Dependencies:** Phase 8 (complete)
**Files:** 
- `planning/phase-9_object-selection-workflow.md` (full spec)
- `planning/phase-9.1_implementation_plan.md` (current implementation)

Create UI workflow for discovering and selecting celestial objects for observability scoring.

**Research Complete:**
- ✅ Studied modern astronomy apps (SkySafari, KStars, Stellarium, TheSkyX, Telescopius)
- ✅ Identified universal patterns: two-layer architecture (browse + search), three entry points (tonight/browse/search), hierarchical list management
- ✅ Pre-curated lists solve 90% of use cases (Messier, Caldwell, Herschel 400)

**Phase 9.1 - Pre-Curated Lists** (Week 1, 2-3 days) - NEAR COMPLETE:
- ✅ ObjectListLoader service with JSON file loading
- ✅ Pre-curated JSON lists (Messier 110, Caldwell, Solar System, etc.)
- ✅ Resolution via CatalogService → scoring pipeline
- ✅ Test infrastructure: Unit tests (148, 100% pass) + Integration tests (143, 99.3% pass)
- ✅ Test organization: Separated unit (`tests/unit/`) and integration (`tests/it/`)
- ✅ Scoring fixes: AngularSize type consistency, normalization (0-25 scale)
- 🔨 UI dropdown selector + "Load & Score" button (remaining work)

**Future Sub-phases:**
- Phase 9.2: Target List Management (custom lists, SQLite storage, CRUD)
- Phase 9.3: "Tonight" Mode (dynamic scored lists, filters)
- Phase 9.4: Browse/Filter OpenNGC (query builder for catalog)
- Phase 9.5: Session Planning & Logging (at-scope mode, observation logs)

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
