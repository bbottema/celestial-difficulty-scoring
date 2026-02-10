# Celestial Observability Scoring - Improvement Plan

## Current State (2026-02-09)

- ✅ Equipment-aware scoring with Strategy + Context pattern
- ✅ Three strategies: Solar System, Deep Sky, Large Faint Objects
- ✅ All magic numbers extracted to `scoring_constants.py` with full documentation
- ✅ Weather integration complete
- ✅ Multi-preset system (Friendly/Strict) implemented with UI selector
- ✅ Constants validated against astronomical research
- ✅ **Phase 5 Complete:** Physics-based limiting magnitude model with realism corrections

**Goal:** Add moon proximity integration and continue improving the scoring system.

---

## Phase 3: Advanced Settings - Custom Preset Overrides 🟡 MEDIUM PRIORITY

**Status:** NOT STARTED (Enhanced with Phase 5 parameters)

**Goal:** Allow users to create custom presets by overriding individual constants, including Phase 5 limiting magnitude model parameters.

**Vision:**
```
Settings Tab
├── Preset Selector: [Friendly Planner ▼]
└── Advanced Settings (expandable)
    ├── Weather Factors
    │   ├── Few Clouds: [0.85] (default: 0.85)
    │   ├── Partly Cloudy: [0.65] (default: 0.65)
    │   └── Mostly Cloudy: [0.30] (default: 0.30)
    ├── Altitude Factors
    │   └── Very Poor (<20°): [0.45] (default: 0.45)
    ├── Light Pollution Settings (NEW - Phase 5)
    │   ├── Aperture gain factor: [0.85] (0.75=conservative, 0.90=optimistic)
    │   ├── Detection headroom multiplier: [1.0] (0.9=easier, 1.1=harder)
    │   ├── Deep-sky minimum: [0.05] (default: 0.05)
    │   └── Large faint minimum: [0.03] (default: 0.03)
    └── Aperture Scaling
        ├── Large bonus: [1.40] (default: 1.40)
        └── ...
    [Reset to Preset Defaults]
    [Save as Custom Preset...]
```

**Enhanced ScoringPreset Model:**
```python
@dataclass
class ScoringPreset:
    name: str
    # Existing fields...
    weather_factor_overcast: float
    altitude_factor_very_poor_deepsky: float

    # NEW: Phase 5 limiting magnitude parameters
    aperture_gain_factor: float = 0.85
    detection_headroom_multiplier: float = 1.0
```

**Preset Values:**
```python
FRIENDLY_PRESET = ScoringPreset(
    name="Friendly Planner",
    aperture_gain_factor=0.90,           # More optimistic
    detection_headroom_multiplier=0.9,   # Lower detection threshold
    # ... other fields
)

STRICT_PRESET = ScoringPreset(
    name="Strict Planner",
    aperture_gain_factor=0.75,           # More conservative
    detection_headroom_multiplier=1.1,   # Higher detection threshold
    # ... other fields
)
```

**Tasks:**

1. **Enhance ScoringPreset model**
   - Add Phase 5 parameters: `aperture_gain_factor`, `detection_headroom_multiplier`
   - Update Friendly/Strict preset definitions

2. **Create CustomPreset model**
   - Extends `ScoringPreset` with user overrides
   - Store as dict: `{"aperture_gain_factor": 0.80, ...}`
   - Merge with base preset on load

3. **Build advanced settings form**
   - Group constants by category (Weather, Altitude, Light Pollution, etc.)
   - Add Phase 5 section with tooltips explaining physics parameters
   - Show current value + preset default value
   - Validation: ensure values are within reasonable ranges

4. **Custom preset management**
   - "Save as Custom Preset" button
   - User names their custom preset
   - Saved presets appear in dropdown alongside Friendly/Strict
   - Delete/rename custom presets

5. **Update light_pollution_models.py to read from active preset**
   - Currently uses function defaults
   - Should call `get_active_preset()` and use preset values

**Validation Rules:**
- Weather factors: 0.0 - 1.0
- Altitude factors: 0.0 - 1.0
- Light pollution floors: 0.0 - 0.1
- Aperture factors: 0.5 - 2.0
- **Aperture gain factor: 0.65 - 1.0** (NEW)
- **Detection headroom multiplier: 0.7 - 1.3** (NEW)

**User Experience:**
- Start with preset selection (basic selector already implemented)
- Advanced users can expand and tweak physics parameters
- Changes preview immediately in target list
- Can always "Reset to Defaults"
- Tooltips explain what each parameter means in plain language

**Phase 5 Integration:**
See `PHASE5_CODE_REVIEW_RESPONSE.md` Issue 5 for detailed design rationale.

---

## Phase 2: Moon Proximity Integration 🔴 NEXT UP

**Status:** NOT STARTED (11 tests waiting)

**Goal:** Factor moon conditions into scoring to avoid recommending targets near a bright moon.

**Tasks:**

1. **Create `MoonConditions` model**
   - File: `src/app/domain/model/moon_conditions.py`
   - Fields: `phase`, `illumination`, `altitude`, `ra`, `dec`
   - Helper: `calculate_separation(target_ra, target_dec) -> float`

2. **Implement moon proximity factor**
   - Add `_calculate_moon_proximity_factor()` to strategies
   - Formula: `penalty = (illumination / 100) * (60 / max(separation, 5))²`
   - Objects < 5° from bright moon → near zero score

3. **Integrate into scoring context**
   - Add `moon_conditions` parameter to `ScoringContext`
   - Pass through from `ObservabilityCalculationService`

4. **UI integration**
   - Add moon phase/altitude display to observation planning panel
   - Calculate moon position from date/time/location (use `ephem` or `skyfield`)

5. **Enable skipped tests**
   - 11 moon proximity tests in `test_advanced_scenarios.py`

---

## Phase 4: Factor Pipeline Refactor 🟢 FUTURE

**Goal:** Make all scoring factors explicit and visible for debugging + address Phase 5 architectural improvements.

**Current:**
```python
base_score = (magnitude_score + size_score) / 2
return base_score * equipment_factor * site_factor * altitude_factor
```

**Proposed:**
```python
return (magnitude_factor *
        size_factor *
        equipment_factor *
        site_factor *
        altitude_factor *
        weather_factor *
        moon_factor)
```

**Benefits:**
- Individual factors visible in output
- Easier debugging
- More modular
- Enables separate UI display of physics_visibility vs environment_penalty

**Tasks:**

1. **Separate magnitude_factor from size_factor in base score**
   - Make each factor contribute independently

2. **Extend `CelestialObjectScore` to include `factors: dict`**
   - Store breakdown: `{"magnitude": 0.8, "site": 0.6, "altitude": 0.9, ...}`
   - Enables UI tooltips showing why object scored low/high

3. **Update all strategies to return factor breakdown**
   - Modify strategy interface to return factors dict

4. **Add factor display to UI**
   - Show "Visibility: Marginal (limiting magnitude)" separate from "Bortle impact: High"

5. **Address Phase 5 Code Review Items:**
   - **Reduce aperture double-counting**: Decrease aperture bonus in `DeepSkyScoringStrategy.equipment_factor` from 1.5x → 1.1x
     - Aperture already handled in site_factor (limiting magnitude)
     - Equipment_factor should focus on magnification/framing appropriateness
   - **Simplify solar system site_factor**: Remove unnecessary NELM model
     - Planets don't have visibility thresholds, use simple linear penalty
     - Detail/quality already handled by altitude + magnification factors
   - **Split physics from environment**: Expose `physics_visibility` (0-1) and `environment_penalty` separately for UI

**Phase 5 Integration:**
See `PHASE5_CODE_REVIEW_RESPONSE.md` for detailed rationale on aperture refactor and solar system simplification.

---

## Phase 5: Limiting Magnitude Model ✅ COMPLETE

**Status:** COMPLETE (2026-02-09)

**Goal:** Replace arbitrary Bortle penalties with physics-based limiting magnitude model.

**What Was Implemented:**

1. **Physics-Based Visibility Model** (`light_pollution_models.py`)
   - Hard cutoffs: objects below limiting magnitude return 0.0
   - Exponential falloff near detection threshold: `1 - exp(-visibility_margin / headroom)`
   - Telescope limiting magnitude: `NELM + 5*log10(D/7) * aperture_gain_factor`
   - Hybrid mode: blends physics-based visibility with legacy penalties for compatibility

2. **Realism Corrections** (Critical improvements from code review)
   - **Aperture gain factor (0.85)**: Corrects theoretical formula for real-world conditions
     - Accounts for: optical losses, seeing, light pollution gradients, obstruction, observer skill
     - Mag 11 galaxy in Bortle 6 with 200mm: 0.5 → 0.17 (over-optimistic → marginal)
   - **Surface brightness penalties**: Graduated headroom scale by object size
     - >120': headroom 3.5, >60': 3.2, >30': 3.0, >5': 2.5, compact: 1.5
   - **Removed double-penalty**: LargeObjectStrategy no longer applies redundant size penalty
     - Andromeda (190') in Bortle 3 with 200mm: ~0.75 → 0.93 ⭐

3. **Test Coverage**
   - Added 19 new tests (115 total, 94 passing)
   - All Phase 5 tests passing (18/18)
   - Realism guard tests validate improvements (4/4)

**User Impact:**
- ✅ Fewer false positives in bright skies (Bortle 7-9)
- ✅ Equipment differences realistically reflected (200mm vs 80mm matters)
- ✅ Large faint objects appropriately rated (no more integrated-magnitude deception)
- ✅ Stable rankings (smooth exponential falloff)
- ✅ Foundation for "Excellent/Good/Marginal/Invisible" UI labels

**Known Limitations (Future Improvements):**
- Object type classification limited to "DeepSky", "Planet", "Sun", "Moon" from AstroPlanner exports
- No differentiation between planetary nebulae (high surface brightness) vs galaxies (low surface brightness)
- **See Phase 7 for object-type-aware improvements once proper astronomical APIs are integrated**

---

## Phase 6: Double Star Splitability 🟢 FUTURE

**Goal:** Score double stars based on whether telescope can split them.

**Missing:**
- `separation` field in `CelestialObject` (arcseconds)
- Dawes' limit: `116 / aperture_mm`
- Rayleigh criterion: `138 / aperture_mm`

**Tasks:**
1. Add `separation: Optional[float]` to `CelestialObject`
2. Add `is_double_star()` helper
3. Implement splitability scoring
4. Add tests
5. Update database schema

**Dependencies:** Requires proper astronomical API (see Phase 8)

---

## Phase 7: Object-Type-Aware Scoring 🟢 FUTURE

**Status:** BLOCKED - Waiting for proper astronomical API integration (Phase 8)

**Goal:** Tailor detection headroom and scoring based on actual object classification.

**Current Limitation:**
- Object types from AstroPlanner exports are generic: "DeepSky", "Planet", "Sun", "Moon"
- Cannot differentiate between:
  - Planetary nebulae (high surface brightness, compact) vs diffuse nebulae (low surface brightness)
  - Galaxies (very low surface brightness) vs globular clusters (concentrated cores)
  - Open clusters (resolved stars) vs emission nebulae (diffuse glow)

**Proposed Enhancement (once proper API available):**

```python
# Object-type-aware headroom selection
HEADROOM_BY_TYPE = {
    'planetary_nebula': 1.3,      # High surface brightness, easier
    'globular_cluster': 1.5,      # Concentrated core, moderate
    'open_cluster': 1.4,          # Resolved stars, relatively easy
    'emission_nebula': 2.5,       # Moderate surface brightness
    'galaxy_spiral': 3.0,         # Low surface brightness
    'galaxy_elliptical': 2.8,     # Slightly higher than spiral
    'dark_nebula': 3.5,           # Extremely low contrast
    'supernova_remnant': 3.2,     # Very faint, extended
}
```

**Benefits:**
- Ring Nebula (planetary) no longer over-penalized like a galaxy
- Globular clusters appropriately easier than galaxies at same magnitude
- M42 (emission nebula) scored differently than Veil Nebula (SNR)

**Implementation Plan:**
1. Integrate proper astronomical catalog (Simbad, OpenNGC, etc.) - **Phase 8 prerequisite**
2. Add `object_classification` field to `CelestialObject`
3. Update `calculate_light_pollution_factor_with_surface_brightness()` to accept classification
4. Map classifications to appropriate headroom values
5. Add tests comparing different types at same magnitude/size

**Estimated Impact:** 15-25% accuracy improvement in deep-sky object rankings

---

## Phase 8: Astronomical API Integration 🔴 HIGH PRIORITY

**Status:** NOT STARTED - **Critical dependency for future improvements**

**Goal:** Replace AstroPlanner Excel exports with proper astronomical catalog APIs.

**Current Data Source Limitations:**
- **AstroPlanner Excel exports**:
  - Limited object types ("DeepSky" is too generic)
  - No detailed classification (galaxy type, nebula type, cluster type)
  - No surface brightness data (critical for visibility)
  - Manual export/import workflow
  - Data staleness (catalogs update, exports don't)

**Proposed API Integration Options:**

### Option 1: Simbad Astronomical Database
- **Pros**: Comprehensive, professional-grade, free API
- **Cons**: Rate limits, requires internet
- **Data**: Object classification, coordinates, magnitudes, sizes, references

### Option 2: OpenNGC (Open New General Catalogue)
- **Pros**: Open source, can be embedded locally, no API limits
- **Cons**: Deep-sky only (no solar system), requires maintenance
- **Data**: NGC/IC objects with detailed classifications

### Option 3: Hybrid Approach (Recommended)
- **Local database**: OpenNGC + Messier + Caldwell catalogs (embedded)
- **Online fallback**: Simbad for objects not in local DB
- **Solar system**: JPL Horizons or Skyfield for planetary ephemeris

**Implementation Tasks:**

1. **API Integration Layer**
   ```python
   # src/app/data/astronomical_catalogs/
   ├── catalog_service.py         # Unified interface
   ├── simbad_client.py           # Online API client
   ├── local_catalog.py           # Embedded OpenNGC/Messier
   └── solar_system_ephemeris.py  # Planetary positions
   ```

2. **Enhanced CelestialObject Model**
   ```python
   @dataclass
   class CelestialObject:
       name: str
       object_type: str                    # Keep for compatibility
       object_classification: str          # NEW: "spiral_galaxy", "planetary_nebula", etc.
       magnitude: float
       surface_brightness: Optional[float] # NEW: mag/arcsec² if available
       size: float
       size_minor_axis: Optional[float]    # NEW: for elongated objects
       altitude: float
       catalog_ids: dict[str, str]         # NEW: {"NGC": "7000", "Messier": "31"}
   ```

3. **Data Migration Strategy**
   - Keep AstroPlanner import for backward compatibility
   - Add "Sync from Catalog" feature to enrich existing objects
   - New objects default to catalog lookup

4. **Benefits Unlocked:**
   - ✅ Phase 7: Object-type-aware scoring (immediate benefit)
   - ✅ Phase 6: Double star data (separation, magnitudes)
   - ✅ Surface brightness scoring (use actual mag/arcsec² instead of estimates)
   - ✅ Real-time solar system positions (no manual updates)
   - ✅ Automatic catalog updates (NGC revisions, new discoveries)

**Estimated Effort:** 2-3 weeks for full implementation
**Priority:** HIGH - Unblocks multiple future phases

---

## Phase 9-11: Filters, Imaging, and Astrophotography 🟢 FUTURE

**Status:** PLANNED (see EQUIPMENT_EXPANSION_PLAN.md)
**Priority:** MEDIUM-HIGH (after Phase 8)

**Overview:**
The application has database schema and UI for filters and imagers, but they are not integrated into scoring. Three major expansion phases planned:

- **Phase 9: Filter Integration** - Solar filters (safety), narrowband filters (H-alpha/OIII), broadband filters (LPR)
- **Phase 10: Astrophotography Scoring** - Different scoring strategy for imaging (integration time, pixel scale, stacking)
- **Phase 11: Advanced Imaging** - Multi-night planning, mosaics, lucky imaging

**Key Features:**
1. **Solar Safety** - Sun requires solar filter (score = 0.0 without filter)
2. **Narrowband Filters** - H-alpha/OIII boost nebula visibility by 2-3 Bortle classes in light pollution
3. **Imaging Mode** - Score for astrophotography: integration time, sensor size, moon phase
4. **Filter Recommendations** - Show "H-alpha recommended for M42" in UI
5. **Dual Scoring** - Compare visual observability vs imaging suitability

**Dependencies:**
- Phase 8: API integration needed for object classification (filter effectiveness varies by type)
- Phase 7: Object-type-aware scoring (emission nebulae benefit most from narrowband)

**Full details:** See `EQUIPMENT_EXPANSION_PLAN.md`

---

## Current Test Status

**As of 2026-02-09 (after Phase 5):**
- ✅ 94 passing (115 total run) - **+16 from Phase 5**
- ❌ 21 failing (3 affected by realism corrections, expected)
- ⏭️ 13 skipped (11 moon, 2 combined adversity)

**Phase 5 Test Additions:**
- 19 new tests for limiting magnitude model
- All Phase 5 tests passing (18/18)
- Realism guard tests validate improvements (4/4)
- Double-penalty fix test passing (1/1)

---

## Future Enhancement Ideas

- **Surface brightness calculation** for extended objects
- **Atmospheric seeing parameter** for planetary detail
- **Transparency/haze parameter** separate from cloud cover
- **Telescope-specific factors** (obstruction, optical quality)

---

## Testing Commands

```bash
# Run all tests
python run_tests.py

# Run specific category
python run_tests.py scoring

# With verbosity
python run_tests.py -v
```

---

---

## Phase 5 Follow-up: Monitoring & Calibration 📊 ONGOING

**Status:** MONITORING REQUIRED

**Goal:** Validate Phase 5 limiting magnitude model against real-world observing conditions.

**Tasks:**

1. **Real-World Calibration (Priority: HIGH)**
   - Test scoring against benchmark object set in known conditions
   - Adjust headroom values if systematic over/under-estimation detected
   - **Benchmark objects:**
     - Easy tier: M31, M42, M45 (should score >0.8 in Bortle 4)
     - Medium tier: M13, M51, M57 (should score 0.5-0.7 in Bortle 5)
     - Challenging tier: M33, NGC 7000 (should score 0.3-0.5 in Bortle 5)
     - Very challenging: Veil, California, IC 1396 (should score <0.3 in Bortle 6+)

2. **Monitor Key Metrics**
   - Score distribution across Bortle classes
   - Aperture sensitivity (200mm vs 80mm ratio should be ~2-3x)
   - Large object scores (Andromeda should stay >0.8 in Bortle 3-4)
   - Invisible count (what % of catalog becomes invisible in Bortle 6+)

3. **Red Flag Detection**
   - ⚠️ >80% of objects rated "good" in Bortle 6 → too optimistic
   - ⚠️ <5% of objects rated "good" in Bortle 4 → too pessimistic
   - ⚠️ Aperture difference >4x → double-counting issue
   - ⚠️ Classic showpieces <0.5 in dark skies → over-penalized

**Documentation:**
- See `PHASE5_CODE_REVIEW_RESPONSE.md` for detailed monitoring plan
- Report findings in GitHub issues or dedicated calibration log

---

## Priority Roadmap

**Immediate Next Steps:**
1. **Phase 2**: Moon Proximity Integration (11 tests waiting, unblocks night planning features)
2. **Phase 8**: Astronomical API Integration (HIGH PRIORITY - unblocks Phases 6 & 7)

**Medium Term:**
3. **Phase 7**: Object-Type-Aware Scoring (after Phase 8)
4. **Phase 4**: Factor Pipeline Refactor (debugging & UI transparency)

**Long Term:**
5. **Phase 3**: Custom Preset Overrides (power user feature)
6. **Phase 6**: Double Star Splitability (niche but valuable)

**Note:** Phase 8 (API Integration) should be prioritized before Phase 7, as it provides the data foundation needed for accurate object-type classification and unlocks multiple future improvements.

---

*Last Updated: 2026-02-09*
*Phase 5 Complete: Physics-based limiting magnitude model with realism corrections*
*Next Priority: Phase 2 (Moon Proximity) OR Phase 8 (API Integration - recommended)*
