# Phase 9: Object Selection Workflow

**Status:** Planning
**Priority:** High (Critical for replacing AstroPlanner Excel workflow)
**Dependencies:** Phase 8 (API integration) complete

## Problem Statement

Users need a way to select groups of celestial objects to score for observability. Previously, users would search/filter objects in AstroPlanner, export to Excel, and import into this tool. With Phase 8 API integration complete, we need a new workflow that:

1. Lets users discover and select objects without external tools
2. Works offline where possible (leveraging local OpenNGC catalog)
3. Supports common observing scenarios (tonight's best, working through catalogs, etc.)
4. Scales from casual "show me the planets" to serious "score 1000 galaxies for imaging"

## Research Findings

Research into modern astronomy software (SkySafari, KStars, Stellarium, TheSkyX, Telescopius, AstroPlanner) revealed universal patterns:

### Two-Layer Architecture
- **Browsable selector** (local catalog) generates working sets
- **Lookup/enrichment** (online APIs) handles ad-hoc queries
- Maps perfectly to our OpenNGC (local) + SIMBAD/Horizons (online) setup

### Three Entry Points
1. **"Tonight"** - Dynamic, scored, location/time-dependent lists
2. **"Browse"** - Catalog filtering by type, magnitude, constellation, etc.
3. **"Search/Import"** - Name lookup, batch add, file import

### Hierarchical List Management
- **Target Lists** (long-term): "Messier", "Winter imaging targets"
- **Sessions** (dated plans): "Feb 15 observing at Dark Site"
- Flow: Browse → List → Session → Observe → Log

### Pre-Curated Lists Solve 90% of Use Cases
- Named catalogs: Messier (110), Caldwell (109), Herschel 400
- Astronomical League observing programs
- Seasonal highlights
- Equipment-specific lists

See: `planning/UX workflow research result.md` for detailed research findings.

---

## Phase 9.1: Pre-Curated Object Lists

**Goal:** Replace AstroPlanner Excel import with built-in object lists
**Timeline:** Week 1 (2-3 days)
**Priority:** Critical - Unblocks all other phases

### Features

#### 9.1.1: Object List Data Structure
Create JSON format for object lists:
```json
{
  "list_id": "messier_110",
  "name": "Messier Catalog",
  "description": "The classic 110 deep-sky objects",
  "category": "named_catalog",
  "version": "1.0",
  "created_date": "2026-02-12",
  "objects": [
    {
      "name": "M1",
      "canonical_id": "NGC1952",
      "type": "nebula",
      "ra": 83.633,
      "dec": 22.014,
      "magnitude": 8.4
    },
    ...
  ]
}
```

Storage location: `data/object_lists/*.json`

#### 9.1.2: Built-In Lists to Ship
- `messier_110.json` - Classic 110 deep-sky showpieces
- `caldwell_109.json` - Supplement to Messier
- `brightest_stars.json` - Navigation stars (~50 objects)
- `winter_highlights.json` - Seasonal best (30-40 objects)
- `spring_highlights.json`
- `summer_highlights.json`
- `fall_highlights.json`
- `solar_system.json` - Planets + Moon (8 planets + Moon = 9 objects)
- `binocular_targets.json` - Large, bright objects (~50 objects)
- `challenge_objects.json` - Faint NGC/IC for large scopes (~30 objects)

Total: ~500-600 pre-curated objects across all lists

#### 9.1.3: ObjectListLoader Service
```python
class ObjectListLoader:
    """Load and manage pre-curated object lists"""

    def load_list(self, list_id: str) -> ObjectList:
        """Load list from JSON file"""

    def get_available_lists(self) -> list[ObjectListMetadata]:
        """Get all available lists with metadata"""

    def resolve_objects(self, object_list: ObjectList,
                       catalog_service: CatalogService) -> list[CelestialObject]:
        """Resolve object names to full CelestialObject instances"""
```

Resolution strategy:
1. Try object's `canonical_id` first via `CatalogService.get_object()`
2. Fall back to `name` field if canonical ID lookup fails
3. Cache resolved objects in memory for session
4. Return list of successfully resolved objects + list of failures

#### 9.1.4: UI Integration
Location: Main scoring tab ("Plan Tonight's Session")

**Changes:**
1. Add section above current import controls:
   - Label: "Select Object List"
   - Dropdown: Shows all available lists with object counts
     - "Messier Catalog (110 objects)"
     - "Winter Highlights (35 objects)"
     - etc.
   - Button: "Load & Score"

2. On "Load & Score":
   - Load selected list via `ObjectListLoader`
   - Resolve objects via `CatalogService`
   - Run through existing scoring pipeline
   - Display in existing results table

3. Status feedback:
   - Show progress: "Loading Messier Catalog... 45/110 objects resolved"
   - Show errors: "3 objects could not be resolved"

### Success Criteria
- [ ] Users can select and score Messier catalog without external tools
- [ ] Lists load and resolve within 5 seconds
- [ ] At least 95% of objects in built-in lists resolve successfully
- [ ] Zero-setup experience (lists ship with app)

### Testing
- Unit tests for `ObjectListLoader`
- Integration test: Load Messier → resolve → score → verify results
- Manual test: Score each built-in list and verify no crashes

---

## Phase 9.2: Target List Management

**Goal:** Let users create and manage custom object lists (like SkySafari Observing Lists)
**Timeline:** Week 2 (3-4 days)
**Priority:** High - Enables power users

### Features

#### 9.2.1: Data Model
New SQLite tables:
```sql
CREATE TABLE target_lists (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    category TEXT,  -- 'custom', 'imported', 'generated'
    created_at TIMESTAMP,
    modified_at TIMESTAMP
);

CREATE TABLE target_list_items (
    id INTEGER PRIMARY KEY,
    list_id INTEGER REFERENCES target_lists(id) ON DELETE CASCADE,
    object_name TEXT NOT NULL,
    canonical_id TEXT,
    object_type TEXT,
    ra REAL,
    dec REAL,
    magnitude REAL,
    observed BOOLEAN DEFAULT 0,
    observed_date TIMESTAMP,
    notes TEXT,
    sort_order INTEGER
);

CREATE INDEX idx_list_items_list_id ON target_list_items(list_id);
```

#### 9.2.2: TargetListService
```python
@dataclass
class TargetList:
    id: int
    name: str
    description: str
    category: str
    created_at: datetime
    modified_at: datetime
    objects: list[TargetListItem]

@dataclass
class TargetListItem:
    id: int
    list_id: int
    object_name: str
    canonical_id: str
    object_type: str
    ra: float
    dec: float
    magnitude: float
    observed: bool
    observed_date: Optional[datetime]
    notes: str
    sort_order: int

class TargetListService:
    # CRUD operations
    def create_list(self, name: str, description: str) -> TargetList
    def get_list(self, list_id: int) -> TargetList
    def get_all_lists(self) -> list[TargetList]
    def update_list(self, list_id: int, name: str, description: str)
    def delete_list(self, list_id: int)

    # Item operations
    def add_object(self, list_id: int, object_name: str) -> TargetListItem
    def remove_object(self, list_id: int, item_id: int)
    def mark_observed(self, item_id: int, observed: bool, date: datetime, notes: str)
    def reorder_objects(self, list_id: int, item_ids_in_order: list[int])

    # Bulk operations
    def merge_lists(self, target_list_id: int, source_list_id: int)
    def copy_list(self, list_id: int, new_name: str) -> TargetList
    def filter_unobserved(self, list_id: int) -> list[TargetListItem]
```

#### 9.2.3: UI - "My Lists" Tab
Location: New subtab in Data tab

**Layout:**
- Left panel: List of user's target lists (table)
  - Columns: Name, Object Count, Observed Count, Last Modified
  - Actions: New, Edit, Delete, Copy
- Right panel: Objects in selected list (table)
  - Columns: Name, Type, Magnitude, Observed (checkbox), Notes
  - Actions: Add Object, Remove, Mark Observed, Reorder
  - Search box: Filter objects by name

**Add Object Dialog:**
- Input: Object name
- Button: Lookup (uses CatalogService)
- Shows: Preview of object data (RA, Dec, Type, Magnitude)
- Button: Add to List

#### 9.2.4: Import/Export
```python
class TargetListImportExport:
    def export_csv(self, list_id: int, filepath: Path)
    def import_csv(self, filepath: Path, list_name: str) -> TargetList
    def export_skylist(self, list_id: int, filepath: Path)  # Future
    def import_skylist(self, filepath: Path) -> TargetList  # Future
```

**CSV Format:**
```csv
Name,Type,RA,Dec,Magnitude,Notes
M31,Galaxy,10.68,41.27,3.4,"Andromeda Galaxy"
NGC7000,Nebula,312.25,44.52,4.0,"North America Nebula"
```

Import process:
1. Parse CSV
2. For each row, attempt to resolve name via CatalogService
3. Create list with resolved objects
4. Show report: "45/50 objects imported successfully, 5 failed"

### Success Criteria
- [ ] Users can create custom lists and add/remove objects
- [ ] Lists persist across app restarts
- [ ] Import/export CSV works correctly
- [ ] Observed status tracking works

### Testing
- Unit tests for TargetListService CRUD operations
- Integration test: Create list → add objects → export → import → verify
- UI test: Create list, add objects, mark observed, verify persistence

---

## Phase 9.3: "Tonight" Mode

**Goal:** Dynamic "best targets for tonight" using scoring engine
**Timeline:** Week 3 (3-4 days)
**Priority:** High - Major differentiator feature

### Features

#### 9.3.1: Tonight Mode Service
```python
class TonightModeService:
    def generate_tonight_list(
        self,
        site: ObservationSite,
        observation_time: datetime,
        equipment_profile: EquipmentProfile,
        filters: TonightFilters
    ) -> list[ScoredCelestialObject]:
        """Generate scored list of best targets for tonight"""

@dataclass
class TonightFilters:
    min_score: float = 0.0
    min_altitude_deg: float = 20.0
    moon_avoidance_enabled: bool = True
    moon_separation_deg: float = 30.0
    object_types: list[str] = None  # None = all types
    magnitude_max: float = 15.0
```

**Algorithm:**
1. Load "seed list" (default: Messier + Caldwell + brightest 200 NGC = ~420 objects)
2. For each object:
   - Resolve via CatalogService (use cached if available)
   - Calculate score using existing scoring engine
   - Check altitude at observation time
   - Check Moon separation if enabled
3. Filter by thresholds
4. Sort by score descending (or optionally by transit time)
5. Return top N objects (default 50)

#### 9.3.2: UI - "Tonight's Best" Tab
Location: New main tab (same level as "Plan Tonight's Session")

**Layout:**

**Control Panel (top):**
- Site selector (dropdown from existing sites)
- Date/time picker (defaults to tonight at sunset)
- Equipment profile selector (dropdown)
- Filters:
  - Min score: Slider (0-100)
  - Min altitude: Slider (0-90°)
  - Moon avoidance: Checkbox + separation spinner (10-90°)
  - Object types: Multi-select (Galaxy, Nebula, Cluster, etc.)
- Button: "Generate List"

**Results Panel:**
- Table showing scored objects:
  - Columns: Name, Type, Magnitude, Score, Altitude, Azimuth, Transit Time, Time to Set
  - Current best target: Highlighted row
  - Sort: By score (default), transit time, or RA
- Actions:
  - "Next Target" button (highlights next highest score)
  - "Mark Observed" button
  - "Add to List" button (adds to selected target list)
  - "Export Tonight's Plan" (CSV/PDF)

**Status Bar:**
- Shows: "50 targets found | Next transit: M42 in 1h 23m | Moon: 45% illuminated, 32° from target"

#### 9.3.3: Seed List Configuration
Allow users to configure which objects feed into "Tonight" mode:

**Default seed list:**
- Messier (110)
- Caldwell (109)
- Brightest 200 NGC (magnitude < 10)
- Total: ~420 objects

**Future: User-configurable:**
- Settings dialog: "Tonight Mode Seed List"
- Checkboxes for which pre-curated lists to include
- Custom magnitude/size thresholds for NGC objects

#### 9.3.4: "Next Target" Logic
Smart algorithm for suggesting next target:
1. Filter to objects above horizon
2. Consider:
   - Current altitude (prefer 30-60° for best seeing)
   - Time to transit (prefer rising objects)
   - Time to set (avoid objects setting within 1 hour)
   - Moon separation (if enabled)
   - Observed status (prefer unobserved)
3. Return highest-scoring object meeting criteria

### Success Criteria
- [ ] "Generate List" completes in < 10 seconds
- [ ] Results match user's equipment and site
- [ ] "Next Target" provides sensible suggestions
- [ ] Users can go from app launch → observing in < 60 seconds

### Testing
- Unit tests for TonightModeService filtering logic
- Integration test: Generate list for test site/equipment → verify scores
- Performance test: Ensure 420 objects score in < 10 seconds
- Manual test: Run on real observing night, verify suggestions match reality

---

## Phase 9.4: Browse/Filter OpenNGC

**Goal:** Query builder for generating custom lists from local OpenNGC catalog
**Timeline:** Week 4 (4-5 days)
**Priority:** Medium - Power user feature

### Features

#### 9.4.1: OpenNGC Filter Service
```python
@dataclass
class CatalogFilters:
    object_types: list[str] = None  # ['galaxy', 'nebula', 'cluster']
    magnitude_min: float = 0.0
    magnitude_max: float = 20.0
    size_min_arcmin: float = 0.0
    size_max_arcmin: float = 180.0
    surface_brightness_min: float = 0.0
    surface_brightness_max: float = 30.0
    constellations: list[str] = None
    ra_range: tuple[float, float] = None  # (0, 360)
    dec_range: tuple[float, float] = None  # (-90, 90)

class OpenNGCFilterService:
    def __init__(self, openngc_provider: OpenNGCProvider):
        self.provider = openngc_provider
        self.df = openngc_provider.df

    def apply_filters(self, filters: CatalogFilters) -> pd.DataFrame:
        """Filter OpenNGC DataFrame by criteria"""

    def count_matches(self, filters: CatalogFilters) -> int:
        """Quick count without full filtering"""

    def get_distinct_constellations(self) -> list[str]:
        """Get list of all constellations in catalog"""
```

#### 9.4.2: UI - "Browse Catalog" Tab
Location: New subtab in Data tab

**Layout:**

**Left Panel - Filters (collapsible sections):**

*Basic Filters:*
- Object Type: Checkboxes (Galaxy, Nebula-Emission, Nebula-Planetary, Nebula-Reflection, Cluster-Open, Cluster-Globular)
- Magnitude: Range slider (0-20)
- Size: Range slider (1-180 arcminutes)

*Advanced Filters (collapsed by default):*
- Surface Brightness: Range slider (10-28 mag/arcsec²)
- Constellation: Multi-select dropdown
- RA Range: Two spinners (0-24h)
- Dec Range: Two spinners (-90 to +90°)

*Quick Presets:*
- "Bright galaxies" (G, mag < 11)
- "Large nebulae" (nebula, size > 30')
- "Binocular targets" (mag < 8, size > 20')
- "Imaging targets" (nebula, size 10-60')

**Right Panel - Results:**
- Preview count: "347 objects match filters" (updates as filters change)
- Results table (paginated, 50 per page):
  - Columns: ID, Name, Type, Magnitude, Size, Constellation, RA, Dec
  - Select: Checkboxes for each row
  - Sort: Clickable column headers
- Actions (bottom):
  - "Score Selected" (runs scoring on checked objects)
  - "Save as Target List" (creates new list from checked objects)
  - "Export CSV"

#### 9.4.3: Advanced Filters (Phase 9.4.5)
Future enhancements:
- FOV match: "Objects that fit [equipment profile] field of view"
- Declination limits: "Objects visible from [site] latitude"
- Observable tonight: Checkbox (filters to objects above horizon tonight)
- Moon avoidance: "Objects > 30° from Moon tonight"

### Success Criteria
- [ ] Filters apply in < 1 second (in-memory DataFrame filtering)
- [ ] Preview count updates in real-time as filters change
- [ ] Users can generate custom lists (e.g., "All galaxies 10-12 mag in Virgo")
- [ ] Results can be saved as target list

### Testing
- Unit tests for filter logic (verify correct DataFrame queries)
- Performance test: Ensure filtering 14k objects is < 1 second
- Integration test: Apply filters → save as list → verify list contents
- Manual test: Create several custom lists using different filter combinations

---

## Phase 9.5: Session Planning & Logging

**Goal:** Dated observing sessions with at-scope mode and observation logging
**Timeline:** Weeks 5-6 (5-6 days)
**Priority:** Medium - Completes the workflow loop

### Features

#### 9.5.1: Data Model
```sql
CREATE TABLE observing_sessions (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    session_date DATE NOT NULL,
    site_id INTEGER REFERENCES observation_sites(id),
    equipment_profile_id INTEGER,
    seeing INTEGER,  -- 1-5 scale
    transparency INTEGER,  -- 1-5 scale
    moon_phase REAL,  -- 0-1
    moon_altitude REAL,
    notes TEXT,
    created_at TIMESTAMP,
    started_at TIMESTAMP,
    ended_at TIMESTAMP
);

CREATE TABLE session_targets (
    id INTEGER PRIMARY KEY,
    session_id INTEGER REFERENCES observing_sessions(id) ON DELETE CASCADE,
    object_name TEXT NOT NULL,
    canonical_id TEXT,
    planned_order INTEGER,
    observed BOOLEAN DEFAULT 0,
    observed_time TIMESTAMP,
    seeing_rating INTEGER,  -- 1-5 scale
    eyepiece_used TEXT,
    filter_used TEXT,
    notes TEXT,
    sketch_path TEXT,
    photo_path TEXT
);

CREATE INDEX idx_session_targets_session_id ON session_targets(session_id);
```

#### 9.5.2: ObservingSessionService
```python
@dataclass
class ObservingSession:
    id: int
    name: str
    session_date: date
    site_id: int
    equipment_profile_id: Optional[int]
    seeing: Optional[int]
    transparency: Optional[int]
    moon_phase: Optional[float]
    moon_altitude: Optional[float]
    notes: str
    started_at: Optional[datetime]
    ended_at: Optional[datetime]
    targets: list[SessionTarget]

@dataclass
class SessionTarget:
    id: int
    session_id: int
    object_name: str
    canonical_id: str
    planned_order: int
    observed: bool
    observed_time: Optional[datetime]
    seeing_rating: Optional[int]
    eyepiece_used: Optional[str]
    filter_used: Optional[str]
    notes: str

class ObservingSessionService:
    def create_session(self, name: str, date: date, site_id: int) -> ObservingSession
    def get_session(self, session_id: int) -> ObservingSession
    def get_all_sessions(self) -> list[ObservingSession]
    def start_session(self, session_id: int)
    def end_session(self, session_id: int)

    def add_target(self, session_id: int, object_name: str, order: int)
    def mark_observed(self, target_id: int, observed_time: datetime,
                     seeing: int, notes: str)
    def get_next_target(self, session_id: int) -> Optional[SessionTarget]
```

#### 9.5.3: UI - "Sessions" Tab
Location: New main tab (same level as "Plan Tonight's Session")

**Session List View:**
- Table: All sessions
  - Columns: Name, Date, Site, Targets (planned/observed), Duration
  - Actions: New, Edit, Delete, Start Session
- Button: "New Session"

**New Session Dialog:**
- Name: Text input
- Date: Date picker
- Site: Dropdown (from existing sites)
- Equipment: Dropdown (optional)
- Current conditions:
  - Seeing: 1-5 stars
  - Transparency: 1-5 stars
  - Moon phase: Auto-calculated from date
- Button: "Create & Add Targets"

**Session Detail View (when session selected):**
- Header: Session name, date, site, conditions
- Targets table:
  - Columns: Order, Name, Type, Magnitude, Observed (checkbox), Time, Notes
  - Actions: Add Target, Remove, Reorder, Mark Observed
- Button: "Start At-Scope Mode"

**Add Targets to Session:**
- Options:
  1. From Tonight's Best (import current Tonight list)
  2. From Target List (select existing list)
  3. Manual add (search by name)
- Automatically sets planned order

#### 9.5.4: At-Scope Mode UI
Full-screen mode optimized for field use (night-vision friendly):

**Layout:**
- Dark red theme (preserves night vision)
- Extra-large fonts
- Minimal controls

**Current Target Card (center, large):**
- Name (huge font)
- Type, magnitude, size
- Current: Altitude, Azimuth
- Time to transit / Time to set
- Finder chart (optional, future)

**Quick Actions (large buttons):**
- "Mark Observed" → opens quick logging dialog
- "Skip to Next"
- "Previous"
- "Exit At-Scope Mode"

**Status Bar (top):**
- Session name, time, objects observed count
- Current conditions (seeing, transparency)

**Quick Logging Dialog:**
- Seeing: 1-5 stars (large buttons)
- Eyepiece used: Dropdown (from equipment profile)
- Filter used: Dropdown
- Notes: Text area
- Buttons: "Log & Next", "Log", "Cancel"

#### 9.5.5: Session Export
```python
class SessionExporter:
    def export_markdown(self, session_id: int, filepath: Path)
    def export_pdf(self, session_id: int, filepath: Path)  # Future
```

**Markdown Format:**
```markdown
# Observing Session: Winter Deep Sky
**Date:** 2026-02-15
**Site:** Dark Site Ridge (Lat: 42.5, Lon: -71.2)
**Equipment:** 10" Dobsonian + 14mm eyepiece

## Conditions
- Seeing: 4/5
- Transparency: 5/5
- Moon: 23% illuminated, 15° altitude

## Objects Observed (8/12 planned)

### M42 - Orion Nebula
- **Time:** 21:45
- **Seeing:** 5/5
- **Eyepiece:** 14mm
- **Notes:** Incredible detail in trapezium. Green cast visible.

### M31 - Andromeda Galaxy
- **Time:** 22:15
- **Seeing:** 4/5
- **Filter:** UHC
- **Notes:** Dust lanes visible. M32 and M110 easy.

...
```

### Success Criteria
- [ ] Users can create sessions and add targets
- [ ] At-scope mode provides clear, night-vision-friendly interface
- [ ] Logging workflow is fast (< 10 seconds per object)
- [ ] Export generates readable markdown reports

### Testing
- Unit tests for session CRUD operations
- Integration test: Create session → add targets → mark observed → export → verify
- UI test: Full at-scope mode workflow
- Field test: Use at telescope on real observing night

---

## Technical Architecture

### Storage Strategy
- **Pre-curated lists:** JSON files in `data/object_lists/` (shipped with app)
- **User target lists:** SQLite tables (`target_lists`, `target_list_items`)
- **Sessions:** SQLite tables (`observing_sessions`, `session_targets`)
- **Resolved objects cache:** In-memory during session, optionally persist to SQLite

### Caching Strategy
```python
class ObjectCache:
    """In-memory cache for resolved CelestialObjects"""
    def __init__(self):
        self._cache: dict[str, CelestialObject] = {}
        self._cache_time: dict[str, datetime] = {}

    def get(self, canonical_id: str, max_age_hours: int = 24) -> Optional[CelestialObject]:
        """Get cached object if not stale"""

    def put(self, canonical_id: str, obj: CelestialObject):
        """Cache object"""
```

Strategy:
- Cache resolved objects for session duration
- Persist SIMBAD lookups to avoid re-querying (24 hour TTL)
- OpenNGC objects don't need caching (always local)

### Import/Export Formats

**Priority Order:**
1. **CSV** - Universal, easy to implement, works with Excel/Google Sheets
2. **JSON** - Native format, preserves all metadata
3. **SkySafari .skylist** (Phase 9.6+) - Opens entire ecosystem of shared lists
4. **Stellarium JSON** (Phase 9.7+) - For advanced users

### Service Layer Architecture
```
UI Layer
    ↓
Service Layer:
    - ObjectListLoader (Phase 9.1)
    - TargetListService (Phase 9.2)
    - TonightModeService (Phase 9.3)
    - OpenNGCFilterService (Phase 9.4)
    - ObservingSessionService (Phase 9.5)
    ↓
Data Layer:
    - CatalogService (Phase 8)
    - ObservabilityCalculationService (existing)
    - SQLite repositories
```

---

## Implementation Order

### Immediate (Week 1)
✅ **Phase 9.1: Pre-Curated Lists**
- Highest value/effort ratio
- Unblocks users immediately
- Replaces AstroPlanner Excel workflow

### Near-term (Weeks 2-3)
**Phase 9.2: Target List Management**
- Enables power users
- Required for Phase 9.3

**Phase 9.3: Tonight Mode**
- Major differentiator feature
- Leverages scoring engine
- High user value

### Medium-term (Weeks 4-6)
**Phase 9.4: Browse/Filter**
- Power user feature
- Nice-to-have, not critical

**Phase 9.5: Session Planning**
- Completes workflow
- Professional-level feature

### Future Phases
**Phase 9.6: SkySafari Integration**
- Import/export .skylist format
- Opens ecosystem of shared lists

**Phase 9.7: Advanced Features**
- Smart recommendations based on observing history
- Equipment-based auto-suggestions
- Weather integration
- Social features (share lists, see popular targets)

---

## Success Metrics

### Phase 9.1
- Users can score pre-curated lists without external tools
- Zero setup required
- 95%+ object resolution success rate

### Phase 9.2
- Users create and manage custom lists
- Import/export works correctly
- Lists persist across sessions

### Phase 9.3
- "Tonight" mode generates useful suggestions in < 10 seconds
- "Next Target" logic makes sense to users
- Users prefer this over manual selection

### Phase 9.4
- Advanced users can generate custom lists from filters
- Filter performance < 1 second
- Query builder is intuitive

### Phase 9.5
- Observing sessions are logged successfully
- At-scope mode is usable in the field
- Export reports are readable and complete

---

## Risk Mitigation

### Risk: Pre-curated lists have errors
**Mitigation:**
- Source data from well-known catalogs (Messier, Caldwell)
- Validate object names resolve via CatalogService
- Include version numbers in list metadata for updates

### Risk: Scoring 500+ objects is too slow
**Mitigation:**
- Profile scoring engine performance
- Implement object caching
- Show progress bar with cancel option
- Consider background threading for large lists

### Risk: Users want lists we don't have
**Mitigation:**
- Phase 9.2 provides custom list creation
- Phase 9.4 provides query builder
- Import/export allows users to share lists

### Risk: UI becomes cluttered with too many tabs
**Mitigation:**
- Use nested tabs where appropriate
- Keep main workflow (Tonight/Browse/Sessions) at top level
- Move advanced features (My Lists, Browse Catalog) to subtabs

---

## References

- Research document: `planning/UX workflow research result.md`
- Phase 8 (API integration): `planning/phase-8_api-integration.md`
- Scoring engine: `src/app/domain/services/observability_calculation_service.py`
- Catalog service: `src/app/catalog/catalog_service.py`
