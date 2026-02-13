# Phase 9.1 Implementation Plan: Pre-Curated Object Lists

**Status:** In Progress
**Priority:** Critical (Replaces AstroPlanner Excel workflow)
**Duration:** 2-3 days
**Dependencies:** Phase 8 (Complete ✅)

---

## Decisions Made

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Caching** | In-memory dict cache NOW | Simple, effective; SQLite later in 9.2+ |
| **Failed Resolution** | Show in table with reason | Rare occurrence; visible but not intrusive |
| **Resolution Rate Test** | Yes, add quality gate | Critical for data quality assurance |
| **Plan Retention** | Keep until Phase 9 complete | Implementation reference value |
| **Seasonal Lists** | Defer to later | Messier+Caldwell covers 220+ objects; source online later |

## Canonical ID Format

**Important:** OpenNGC uses `NGC0224` format (zero-padded, no space).
- `"M31"` → `"NGC0224"` 
- `"NGC 224"` → `"NGC0224"`
- Solar System: name as-is (`"Jupiter"`, `"Moon"`)

---

## Implementation Progress

### ✅ Task 1: Create Data Models
**File:** `src/app/object_lists/models.py`

- [x] `ObjectListItem` - Single object entry
- [x] `ObjectListMetadata` - List metadata for UI
- [x] `ObjectList` - Complete list with items
- [x] `ResolutionFailure` - Failed resolution details
- [x] `ResolutionResult` - Resolution outcome with stats

### ✅ Task 2: Create ObjectListLoader Service
**File:** `src/app/object_lists/object_list_loader.py`

- [x] `get_available_lists()` - Scan directory
- [x] `load_list(list_id)` - Load JSON file
- [x] `resolve_objects()` - Resolve via CatalogService with caching
- [x] In-memory cache with `clear_cache()` and `get_cache_stats()`

### ✅ Task 3: Create Tests
**Files:** `tests/object_lists/`

- [x] `test_models.py` - Unit tests for dataclasses
- [x] `test_object_list_loader.py` - Service unit tests
- [x] `test_object_list_integration.py` - Quality gate tests (≥95% resolution)

### ✅ Task 4: Create Generation Script
**File:** `scripts/generate_object_lists.py`

- [x] Reads from `data/catalogs/NGC.csv` and `addendum.csv`
- [x] Generates `messier_110.json`, `caldwell_109.json`, `solar_system.json`

### ✅ Task 5: UI Integration
**File:** `src/app/ui/main_window/observation_data/observation_data_component.py`

- [x] Added ObjectListLoader to component
- [x] Created `_create_object_list_section()` with dropdown + Load & Score button
- [x] Created `_load_and_score_object_list()` with progress dialog
- [x] Updated `populate_table()` to show failures with reason

### ✅ Task 6: Generate JSON Files
**Directory:** `data/object_lists/`

**Ideal:** `python scripts/generate_object_lists.py`
**Actual:** Created manually (no terminal access)

- [x] `messier_110.json` - 110 objects with NGC canonical IDs
- [x] `caldwell_109.json` - 109 objects with NGC/IC canonical IDs  
- [x] `solar_system.json` - 9 objects (planets + Moon + Sun)

### 🔨 Task 7: Run Tests (USER ACTION REQUIRED)
**Ideal:** `python run_tests.py`

- [ ] Run `python run_tests.py` to verify all tests pass
- [ ] Verify integration tests pass (≥95% resolution rate)
- [ ] Fix any import or runtime errors

---

## File Structure (Final)

```
src/app/
├── object_lists/
│   ├── __init__.py
│   ├── models.py
│   └── object_list_loader.py
├── ui/main_window/observation_data/
│   └── observation_data_component.py (modified)

data/
├── object_lists/
│   ├── messier_110.json
│   ├── caldwell_109.json
│   ├── solar_system.json
│   ├── brightest_stars.json
│   ├── winter_highlights.json
│   ├── spring_highlights.json
│   ├── summer_highlights.json
│   ├── fall_highlights.json
│   └── binocular_targets.json

scripts/
├── generate_object_lists.py

tests/
├── object_lists/
│   ├── __init__.py
│   ├── test_models.py
│   ├── test_object_list_loader.py
│   └── test_object_list_integration.py
```

---

## Implementation Order

1. **Day 1 (Morning):** Task 1 + Task 4 - Data models and package structure
2. **Day 1 (Afternoon):** Task 2 - ObjectListLoader service (TDD)
3. **Day 2 (Morning):** Task 3 - Generate JSON files (Messier + Solar System first)
4. **Day 2 (Afternoon):** Task 5 - UI integration
5. **Day 3:** Task 6 - Integration tests + bug fixes + remaining JSON lists

---

## Success Criteria

- [ ] Users can select Messier catalog from dropdown
- [ ] "Load & Score" resolves and scores objects within 5 seconds
- [ ] At least 95% of objects in built-in lists resolve successfully
- [ ] Results display in existing scoring table
- [ ] Status bar shows resolution progress and any failures
- [ ] Zero setup required (lists ship with app)

---

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| OpenNGC IDs don't match JSON canonical_ids | Generate JSONs FROM OpenNGC using script |
| Slow resolution for 100+ objects | Add memory caching for resolved objects |
| UI hangs during resolution | Use QThread for background processing |
| JSON files have errors | Add validation in `load_list()` with clear error messages |

---

## Dependencies on Existing Code

- `CatalogService.get_object(canonical_id)` - For resolution
- `ObservabilityCalculationService` - For scoring
- `CelestialObject` model - Return type
- `@component` decorator - DI registration
- Existing results table widget - Display output

---

## Open Questions

1. **Object caching:** Should resolved objects be cached to SQLite for offline use, or memory-only for session?
   - **Recommendation:** Memory cache first, SQLite persistence in Phase 9.2

2. **Failed resolution handling:** Abort entire list or show partial results?
   - **Recommendation:** Show partial results with warning indicator

3. **List updates:** How to handle updates to shipped JSON lists?
   - **Recommendation:** Include version field, show "update available" in future phase
