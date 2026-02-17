# Phase 9.2 Implementation Plan: Target List Management

**Status:** In Progress
**Priority:** High (Enables power users to create custom lists)
**Duration:** 3-4 days
**Dependencies:** Phase 9.1 (Complete ✅)

---

## Overview

Phase 9.2 enables users to create and manage custom target lists that persist to SQLite. This replaces the need for external tools to manage observing lists.

**Key Features:**
- Create/edit/delete custom target lists
- Add/remove objects from lists
- Mark objects as observed with notes
- Import/export CSV
- Persist across app restarts

---

## Data Model

### New SQLite Tables

```sql
CREATE TABLE target_lists (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    category TEXT DEFAULT 'custom',  -- 'custom', 'imported', 'generated'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE target_list_items (
    id INTEGER PRIMARY KEY,
    list_id INTEGER NOT NULL REFERENCES target_lists(id) ON DELETE CASCADE,
    object_name TEXT NOT NULL,
    canonical_id TEXT,
    object_type TEXT,
    ra REAL,
    dec REAL,
    magnitude REAL,
    observed BOOLEAN DEFAULT 0,
    observed_date TIMESTAMP,
    notes TEXT,
    sort_order INTEGER DEFAULT 0,
    UNIQUE(list_id, canonical_id)
);

CREATE INDEX idx_target_list_items_list_id ON target_list_items(list_id);
```

---

## Implementation Tasks

### ✅ Task 1: Create Entity Models
**File:** `src/app/orm/model/entities.py`

- [x] Add `TargetList` entity class
- [x] Add `TargetListItem` entity class
- [x] Set up relationship between them

### ✅ Task 2: Create Repository
**File:** `src/app/orm/repositories/target_list_repository.py`

- [x] `TargetListRepository` with CRUD operations
- [x] Bulk operations for items (add many, reorder)

### ✅ Task 3: Create Service
**File:** `src/app/orm/services/target_list_service.py`

- [x] `TargetListService` with business logic
- [x] Object resolution on add
- [x] Mark observed functionality
- [x] Event bus integration

### ✅ Task 4: Create Import/Export
**File:** `src/app/target_lists/import_export.py`

- [x] `export_csv(list_id, filepath)`
- [x] `import_csv(filepath, list_name) -> TargetList`

### ✅ Task 5: Create UI Component
**File:** `src/app/ui/main_window/target_lists/target_list_component.py`

- [x] Left panel: List of target lists
- [x] Right panel: Objects in selected list
- [x] CRUD dialogs
- [x] Import/Export buttons

### ✅ Task 6: Integrate into Main Window
**File:** `src/app/ui/main_window/main_window.py`

- [x] Add "My Target Lists" tab

### ✅ Task 7: Create Tests
**Files:** `tests/unit/target_lists/`

- [x] Unit tests for repository
- [x] Unit tests for service
- [x] Unit tests for import/export

### 🔨 Task 8: Run Tests and Verify (USER ACTION REQUIRED)

- [ ] Run `python run_tests.py` to verify tests pass
- [ ] Run the app and test UI functionality
- [ ] Verify database persistence works

---

## File Structure

```
src/app/
├── orm/
│   ├── model/
│   │   └── entities.py (modified - add TargetList, TargetListItem)
│   ├── repositories/
│   │   └── target_list_repository.py (new)
│   └── services/
│       └── target_list_service.py (new)
├── target_lists/
│   └── import_export.py (new)
└── ui/
    └── main_window/
        └── target_lists/
            ├── __init__.py
            └── target_list_component.py (new)

tests/
└── unit/
    └── target_lists/
        ├── __init__.py
        ├── test_target_list_repository.py
        └── test_target_list_service.py
```

---

## Success Criteria

- [ ] Users can create custom lists and add/remove objects
- [ ] Lists persist across app restarts
- [ ] Import/export CSV works correctly
- [ ] Observed status tracking works
- [ ] UI is intuitive and responsive

---

## Implementation Order

1. **Day 1:** Tasks 1-3 (Data model, repository, service)
2. **Day 2:** Task 4-5 (Import/export, UI component)
3. **Day 3:** Task 6-7 (Integration, tests, polish)
