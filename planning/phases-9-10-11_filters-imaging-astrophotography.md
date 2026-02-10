# Equipment Expansion Plan: Filters, Imaging, and Astrophotography

**Status:** NOT STARTED
**Created:** 2026-02-10
**Priority:** MEDIUM-HIGH (after Phase 8 API integration)

## Executive Summary

The application currently has **database schema and UI for filters and imagers**, but they are **not integrated into the scoring system**. This document plans the expansion to support:

1. **Optical filters** (narrowband, broadband, solar)
2. **Imaging equipment** (cameras, stacking)
3. **Astrophotography scoring** (different from visual observability)

---

## Current State

### ✅ Already Implemented (Database & UI)

**Filter Model** (entities.py:120-129):
- `name: str`
- `minimum_exit_pupil: int` (mm)
- `wavelengths: List[Wavelength]` (e.g., H-alpha, OIII, etc.)
- Associated with observation sites via many-to-many

**Imager Model** (entities.py:133-150):
- `name: str`
- Main sensor specs: `pixel_size_width/height`, `number_of_pixels_width/height`
- Guide sensor specs (optional): same fields for guide camera
- Associated with observation sites

**UI Components**:
- `manage_filters_tab.py` - Filter management UI
- `filter_repository.py` & `filter_service.py` - CRUD operations
- Equipment management UI includes filters and imagers

### ❌ Not Yet Implemented

- **Filters not used in scoring** - ScoringContext doesn't include filters
- **Imagers not used in scoring** - No imaging/stacking scoring mode
- **No solar observation safety checks** - Sun requires solar filters
- **No narrowband enhancements** - H-alpha/OIII filters boost nebula visibility
- **No astrophotography mode** - Different scoring logic for imaging vs visual

---

## Phase 9: Filter Integration 🟢 FUTURE

**Goal:** Integrate optical filters into visual observation scoring.

**Blocked by:** Phase 8 (API integration needed for object type classification)

### Use Cases

#### 1. Solar Filters (Safety-Critical)
**Problem:** Sun observation requires solar filters to prevent eye damage.

**Solution:**
```python
def _calculate_equipment_factor(self, celestial_object, context: 'ScoringContext') -> float:
    """Solar system scoring - Sun requires solar filter"""
    if celestial_object.name == "Sun":
        if not context.has_solar_filter():
            return 0.0  # INVISIBLE without solar filter (safety)
        # With solar filter, Sun is always excellent target
        return 1.5  # Bonus for having proper equipment
    # ... existing planet logic
```

**UX Implications:**
- Sun should show **"REQUIRES SOLAR FILTER"** warning in UI
- Score should be 0.0 without solar filter
- With solar filter, Sun becomes high-priority target
- Filter dropdown should highlight solar filters when Sun is selected

#### 2. Narrowband Filters (H-alpha, OIII, SII)
**Problem:** Emission nebulae are much easier to see with narrowband filters in light-polluted skies.

**Solution:**
```python
def _calculate_site_factor(self, celestial_object, context: 'ScoringContext') -> float:
    """Light pollution impact - narrowband filters help emission nebulae"""
    base_factor = calculate_light_pollution_factor_with_surface_brightness(...)

    # Narrowband filter bonus for emission nebulae
    if celestial_object.object_classification == "emission_nebula":
        if context.has_narrowband_filter():  # H-alpha, OIII, SII
            # Narrowband filters reduce light pollution impact
            light_pollution_reduction = 0.5  # Act like 2-3 Bortle classes darker
            enhanced_factor = calculate_with_reduced_bortle(...)
            return enhanced_factor

    return base_factor
```

**Filter Effectiveness by Object Type:**
| Filter Type | Best For | Light Pollution Improvement |
|------------|----------|---------------------------|
| H-alpha (656nm) | Emission nebulae (Orion, North America) | 2-3 Bortle classes |
| OIII (496/501nm) | Planetary nebulae (Ring, Dumbbell) | 2-3 Bortle classes |
| SII (672nm) | Supernova remnants (Veil) | 1-2 Bortle classes |
| UHC (broadband) | General nebulae | 1-2 Bortle classes |
| Light pollution | General deep sky | 0.5-1 Bortle class |

**UX Implications:**
- Show filter recommendations: "H-alpha filter recommended for M42"
- Display score with/without filter: "Score: 45% (70% with H-alpha)"
- Filter selector in equipment panel
- Color-code filters by type (H-alpha=red, OIII=blue-green)

#### 3. Broadband Filters (Light Pollution Reduction)
**Problem:** Broadband filters (UHC, LPR) provide modest improvements for all deep sky objects.

**Solution:**
```python
if context.has_broadband_filter():
    # Modest improvement for all deep sky objects
    base_factor *= 1.15  # 15% improvement
```

**UX Implications:**
- Show as equipment modifier in score breakdown
- "Light pollution reduced by broadband filter: +15%"

### Implementation Tasks

1. **Extend ScoringContext**
   ```python
   @dataclass
   class ScoringContext:
       telescope: Optional[Telescope]
       eyepiece: Optional[Eyepiece]
       observation_site: Optional[ObservationSite]
       filter: Optional[Filter] = None  # NEW
       altitude: float
       weather: Optional[dict] = None
   ```

2. **Add filter helper methods**
   ```python
   def has_solar_filter(self) -> bool:
       """Check if user has selected solar filter"""
       return self.filter and "solar" in self.filter.wavelengths

   def has_narrowband_filter(self) -> bool:
       """Check for H-alpha, OIII, SII"""
       return self.filter and any(w in self.filter.wavelengths
                                  for w in ["h_alpha", "oiii", "sii"])
   ```

3. **Update strategies**
   - `SolarSystemScoringStrategy`: Add solar filter check for Sun
   - `DeepSkyScoringStrategy`: Add narrowband filter bonuses
   - `LargeFaintObjectScoringStrategy`: Add narrowband filter bonuses

4. **Add safety validations**
   ```python
   def validate_sun_safety(context: ScoringContext) -> Optional[str]:
       """Return warning message if Sun observation is unsafe"""
       if celestial_object.name == "Sun":
           if not context.has_solar_filter():
               return "⚠️ DANGER: Solar filter required for Sun observation"
       return None
   ```

5. **Update UI**
   - Add filter selector to observation planning UI
   - Show filter recommendations for each object
   - Display score comparison with/without filters
   - Show safety warnings for Sun

6. **Tests**
   - Sun invisible without solar filter
   - Sun excellent with solar filter
   - M42 improves 50%+ with H-alpha in Bortle 6
   - Ring Nebula improves with OIII
   - Broadband filter provides modest improvement

**Dependencies:**
- Phase 8: API integration needed for `object_classification` field
- Phase 7: Object-type-aware scoring for filter effectiveness

---

## Phase 10: Astrophotography Scoring 🟢 FUTURE

**Goal:** Score objects for imaging suitability (different from visual observability).

**Blocked by:** Phase 9 (filter integration) and Phase 8 (API integration)

### Key Differences: Visual vs Imaging

| Factor | Visual Observation | Astrophotography |
|--------|-------------------|------------------|
| **Light pollution** | Major impact | Moderate (narrowband filters help) |
| **Aperture** | Critical for visibility | Less critical (integration time compensates) |
| **Object brightness** | Brighter = easier | Dimmer objects OK with long exposures |
| **Object size** | Bigger = harder (surface brightness) | Bigger = easier (more photons to collect) |
| **Altitude** | Low altitude = atmospheric distortion | Altitude matters less (can stack many frames) |
| **Moon phase** | Major impact | Critical (moonless nights essential) |
| **Tracking** | Not required | Essential (mount quality matters) |
| **Exposure time** | Not a factor | Primary factor (minutes to hours) |

### Imaging Scoring Strategy

```python
class AstrophotographyScoringStrategy(IObservabilityScoringStrategy):
    """
    Scoring for astrophotography imaging.
    Different factors than visual observability.
    """

    def calculate_score(self, celestial_object, context: 'ScoringContext'):
        # Base score from object properties
        magnitude_score = self._normalize_magnitude_for_imaging(celestial_object.magnitude)
        size_score = self._normalize_size_for_imaging(celestial_object.size)
        base_score = (magnitude_score + size_score) / 2

        # Equipment factor: sensor size, pixel scale, tracking
        equipment_factor = self._calculate_equipment_factor_imaging(context)

        # Site factor: light pollution, moon phase, altitude
        site_factor = self._calculate_site_factor_imaging(celestial_object, context)

        # Integration time factor: how long can you image?
        integration_factor = self._calculate_integration_time(context)

        # Filter factor: narrowband filters enable imaging in light pollution
        filter_factor = self._calculate_filter_factor(celestial_object, context)

        return base_score * equipment_factor * site_factor * integration_factor * filter_factor
```

### Imaging-Specific Factors

#### 1. Sensor & Pixel Scale
```python
def _calculate_equipment_factor_imaging(self, context: 'ScoringContext') -> float:
    """
    Imaging equipment: sensor size, pixel scale, tracking quality.
    """
    if not context.has_imager():
        return 0.3  # Can't do astrophotography without camera

    # Pixel scale: ideal is 1-2 arcsec/pixel (depends on object size)
    pixel_scale = calculate_pixel_scale(
        context.telescope.focal_length,
        context.imager.main_pixel_size_width
    )

    # Sensor size: larger sensors capture more of extended objects
    sensor_size = calculate_sensor_size(
        context.imager.main_pixel_size_width,
        context.imager.main_number_of_pixels_width,
        context.imager.main_pixel_size_height,
        context.imager.main_number_of_pixels_height
    )

    return combine_pixel_and_sensor_factors(pixel_scale, sensor_size, celestial_object.size)
```

#### 2. Integration Time
```python
def _calculate_integration_time(self, context: 'ScoringContext') -> float:
    """
    How much integration time is available?
    Depends on: object altitude over time, moon phase, season.
    """
    # Calculate how many hours object is above minimum altitude
    hours_above_horizon = calculate_imaging_window(
        celestial_object.ra,
        celestial_object.dec,
        context.observation_site.latitude,
        context.observation_site.longitude,
        context.date
    )

    # Moon phase penalty
    moon_phase = get_moon_phase(context.date)
    moon_penalty = 1.0 - (moon_phase / 100) * 0.7  # Full moon = 70% penalty

    return normalize_integration_time(hours_above_horizon) * moon_penalty
```

#### 3. Stacking & Post-Processing Potential
```python
def _calculate_stacking_potential(self, celestial_object, context: 'ScoringContext') -> float:
    """
    Some objects benefit more from stacking than others.
    """
    # Faint nebulae benefit greatly from stacking
    if celestial_object.object_classification in ["emission_nebula", "reflection_nebula"]:
        return 1.3  # 30% bonus for stacking potential

    # Bright targets don't need as much integration
    if celestial_object.magnitude < 5.0:
        return 0.9  # Slight penalty (easier to overexpose)

    return 1.0
```

### UX Design for Imaging Mode

#### Mode Selector
```
Observation Mode: [Visual ▼] [Imaging] [Both]
```

#### Imaging-Specific UI Elements
```
┌─ Astrophotography Planning ───────────────────────┐
│                                                    │
│ Equipment:                                         │
│   Camera: [ZWO ASI294MC Pro        ▼]             │
│   Filter: [Optolong L-eXtreme      ▼]             │
│   Mount:  [iOptron CEM70G          ▼]             │
│                                                    │
│ Target: M42 - Orion Nebula                        │
│   Imaging Window: 4.2 hours (8:30 PM - 12:42 AM)  │
│   Recommended Exposure: 180s x 84 frames           │
│   Total Integration: 4.2 hours                     │
│   Moon Phase: 23% (Good conditions)                │
│                                                    │
│ Score: 85% (Excellent imaging target)             │
│   ├─ Equipment: 90% (Good pixel scale)            │
│   ├─ Site: 70% (Bortle 6, narrowband helps)       │
│   ├─ Integration: 95% (Long imaging window)       │
│   └─ Filter: 120% (H-alpha boosts nebula signal)  │
│                                                    │
└────────────────────────────────────────────────────┘
```

### Implementation Tasks

1. **Extend database schema**
   ```python
   @dataclass
   class Mount(Base, EquipmentEntity):
       """New entity for tracking mounts"""
       __tablename__ = 'mounts'
       id: int | None
       name: str
       tracking_accuracy: float  # arcsec/min
       payload_capacity: float  # kg
   ```

2. **Create AstrophotographyScoringStrategy**
   - Implement imaging-specific scoring logic
   - Different weight for magnitude, size, altitude
   - Integration time calculations
   - Stacking potential factors

3. **Extend ScoringContext**
   ```python
   @dataclass
   class ScoringContext:
       # ... existing fields
       imager: Optional[Imager] = None  # NEW
       mount: Optional[Mount] = None    # NEW
       date: Optional[datetime] = None  # NEW for imaging window calculations
       observation_mode: str = "visual"  # "visual" | "imaging" | "both"
   ```

4. **Add imaging calculations**
   - Pixel scale calculator (already exists: `imager_calculator.py`)
   - Imaging window calculator (needs RA/Dec + date)
   - Stacking potential estimator
   - Moon phase impact

5. **Update UI**
   - Add "Imaging" mode toggle
   - Show imaging-specific metrics (integration time, pixel scale)
   - Display recommended exposure settings
   - Show moon phase and imaging window

6. **Tests**
   - Faint nebulae score higher for imaging than visual
   - Large objects benefit from big sensors
   - Moon phase severely impacts imaging scores
   - Narrowband filters boost imaging scores in light pollution

**Dependencies:**
- Phase 8: API integration for RA/Dec coordinates (imaging window calculations)
- Phase 9: Filter integration (narrowband crucial for imaging)

---

## Phase 11: Advanced Imaging Features 🔵 LOW PRIORITY

**Goal:** Advanced astrophotography scoring and recommendations.

### Features

#### 1. Multi-Night Planning
- Track which targets have been partially imaged
- Recommend continuing previous imaging sessions
- Calculate cumulative integration time across nights

#### 2. Mosaic Planning
- Score large objects (M31, M33, Veil) for mosaic imaging
- Calculate number of panels needed
- Estimate total imaging time for mosaic

#### 3. Lucky Imaging (Planetary)
- Different scoring for planetary imaging (video capture + stacking)
- Seeing conditions critical (atmospheric turbulence)
- High frame rate requirements

#### 4. Calibration Frame Reminders
- Remind user to capture darks, flats, bias frames
- Track when calibration library was last updated
- Different requirements for different filters

#### 5. Gear Recommendations
- "Upgrade aperture to improve visual observability"
- "Add narrowband filter to improve imaging in Bortle 6"
- "Increase sensor size to capture entire object"

---

## Summary: Implementation Roadmap

### Immediate Next Steps (After Phase 8)
1. **Phase 9: Filter Integration** (HIGH PRIORITY)
   - Solar filter safety checks for Sun
   - Narrowband filter bonuses for nebulae
   - UI filter selector and recommendations

### Medium-Term (After Phase 9)
2. **Phase 10: Astrophotography Scoring** (MEDIUM PRIORITY)
   - Imaging mode toggle
   - Integration time calculations
   - Different scoring strategy for imaging

### Long-Term (Optional)
3. **Phase 11: Advanced Imaging Features** (LOW PRIORITY)
   - Multi-night planning
   - Mosaic planning
   - Lucky imaging for planets

---

## Open Questions & Decisions Needed

1. **Should imaging and visual modes share the same UI?**
   - Option A: Toggle between modes (cleaner)
   - Option B: Side-by-side comparison (more info)
   - **Recommendation:** Toggle with "Compare Modes" button

2. **How to handle solar safety warnings?**
   - Option A: Block UI entirely without solar filter
   - Option B: Show warning but allow user to proceed
   - **Recommendation:** Show prominent warning, require checkbox confirmation

3. **Should we score camera quality?**
   - Factors: quantum efficiency, read noise, cooling
   - **Recommendation:** Phase 11 (nice-to-have, not critical)

4. **How to handle filter stacking?**
   - Some users stack multiple filters (e.g., UV/IR cut + H-alpha)
   - **Recommendation:** Phase 11 (advanced feature)

5. **Should we integrate with imaging software?**
   - Export targets to N.I.N.A., Sequence Generator Pro, etc.
   - **Recommendation:** Phase 12 (external integrations)

---

## References & Research

- **Filter Effectiveness**: [Cloudy Nights Filter Comparison](https://www.cloudynights.com/)
- **Pixel Scale Guidelines**: [Nyquist sampling theorem](https://en.wikipedia.org/wiki/Nyquist%E2%80%93Shannon_sampling_theorem) - 2-3x seeing FWHM
- **Integration Time**: [Exposure calculator by Deep Sky Watch](https://www.deepskywatch.com/)
- **Solar Safety**: [ISO 12312-2:2015 solar filters standard](https://en.wikipedia.org/wiki/Solar_viewer)
