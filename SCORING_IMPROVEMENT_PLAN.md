# Celestial Observability Scoring - Improvement Plan

## Current State (2026-02-09)

- ✅ Equipment-aware scoring with Strategy + Context pattern
- ✅ Three strategies: Solar System, Deep Sky, Large Faint Objects
- ✅ All magic numbers extracted to `scoring_constants.py` with full documentation
- ✅ Weather integration complete
- ✅ Multi-preset system (Friendly/Strict) implemented with UI selector
- ✅ Constants validated against astronomical research

**Goal:** Add moon proximity integration and continue improving the scoring system.

---

## Phase 3: Advanced Settings - Custom Preset Overrides 🟢 FUTURE

**Status:** NOT STARTED (Advanced feature, after basic preset selector)

**Goal:** Allow users to create custom presets by overriding individual constants.

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
    ├── Light Pollution Floors
    │   ├── Deep-sky minimum: [0.05] (default: 0.05)
    │   └── Large faint minimum: [0.03] (default: 0.03)
    └── Aperture Scaling
        ├── Large bonus: [1.40] (default: 1.40)
        └── ...
    [Reset to Preset Defaults]
    [Save as Custom Preset...]
```

**Tasks:**

1. **Create CustomPreset model**
   - Extends `ScoringPreset` with user overrides
   - Store as dict: `{"weather_factor_partly_cloudy": 0.70, ...}`
   - Merge with base preset on load

2. **Build advanced settings form**
   - Group constants by category (Weather, Altitude, Light Pollution, etc.)
   - Show current value + preset default value
   - Validation: ensure values are within reasonable ranges
   - Tooltips explaining what each constant does

3. **Custom preset management**
   - "Save as Custom Preset" button
   - User names their custom preset
   - Saved presets appear in dropdown alongside Friendly/Strict
   - Delete/rename custom presets

4. **Preset comparison view (optional)**
   - Side-by-side comparison of Friendly vs Strict
   - Highlight differences
   - Help users understand trade-offs

**Architecture:**
```python
@dataclass
class CustomPreset(ScoringPreset):
    base_preset: str  # "Friendly" or "Strict"
    overrides: dict[str, float]  # {"weather_factor_partly_cloudy": 0.70}

    def get_value(self, key: str) -> float:
        return self.overrides.get(key, getattr(base_preset, key))
```

**Validation Rules:**
- Weather factors: 0.0 - 1.0
- Altitude factors: 0.0 - 1.0
- Light pollution floors: 0.0 - 0.1
- Aperture factors: 0.5 - 2.0

**User Experience:**
- Start with preset selection (basic selector already implemented)
- Advanced users can expand and tweak
- Changes preview immediately in target list
- Can always "Reset to Defaults"

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

**Goal:** Make all scoring factors explicit and visible for debugging.

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

**Tasks:**
1. Separate magnitude_factor from size_factor in base score
2. Extend `CelestialObjectScore` to include `factors: dict`
3. Update all strategies to return factor breakdown
4. Add factor display to UI

---

## Phase 5: Limiting Magnitude Model 🟢 FUTURE

**Goal:** Replace arbitrary Bortle penalties with physics-based limiting magnitude model.

**Current:**
```python
factor = 1.0 - (bortle * PENALTY_PER_BORTLE)
return max(factor, MIN_FACTOR)
```

**Proposed:**
```python
limiting_magnitude = BORTLE_TO_LIMITING_MAGNITUDE[bortle]
if object_magnitude > limiting_magnitude:
    return 0.0  # Invisible
visibility_margin = limiting_magnitude - object_magnitude
factor = 1.0 - (1.0 / (1 + visibility_margin))
```

**Tasks:**
1. Create `src/app/utils/light_pollution_models.py`
2. Implement limiting magnitude formulas
3. Add visibility check to site factor calculations
4. Update tests

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

---

## Current Test Status

**As of 2026-02-09:**
- ✅ 78 passing (96 total run)
- ❌ 18 failing (calibration issues - unchanged from previous run)
- ⏭️ 13 skipped (11 moon, 2 combined adversity)

**Note:** Phase 8 constant adjustments did not change the failure count. The 18 failures are likely deeper calibration issues that need investigation.

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

*Last Updated: 2026-02-09*
*Next Priority: Phase 2 - Moon Proximity Integration*
