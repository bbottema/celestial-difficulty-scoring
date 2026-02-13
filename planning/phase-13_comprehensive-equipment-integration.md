# Phase 13: Comprehensive Equipment Integration

**Status:** NOT STARTED
**Created:** 2026-02-11
**Priority:** 🔴 HIGH - Critical gap in equipment modeling
**Dependencies:** None (architectural foundation for other phases)
**Estimated Effort:** Large (3-4 weeks)

---

## Executive Summary

The application has **database models and UI for all equipment types** but only uses **telescope and eyepiece** in scoring. This creates a significant gap: users can configure filters, optical aids, and imagers in the UI, but they have **zero impact on observability scores**.

**Current Equipment Coverage:**
- ✅ **Telescope** - Fully integrated (aperture, focal length, type)
- ✅ **Eyepiece** - Partially integrated (only for magnification calculation)
- ❌ **Filters** - Database + UI only, **not used in scoring**
- ❌ **Optical Aids** - Database + UI only, **not used in scoring**
- ❌ **Imagers** - Database + UI only, **not used in scoring**

This phase provides the architectural foundation for equipment-aware scoring across all equipment types.

---

## Problem Statement

### Current Architecture Limitations

**1. ScoringContext Only Accepts Telescope + Eyepiece**

```python
@dataclass
class ScoringContext:
    telescope: Optional[Telescope]
    eyepiece: Optional[Eyepiece]
    observation_site: Optional[ObservationSite]
    # ❌ Missing: filters, optical_aids, imagers
```

**2. ObservabilityCalculationService Has Fixed Parameters**

```python
def score_celestial_object(self,
                          celestial_object: CelestialObject,
                          telescope: Optional[Telescope] = None,
                          eyepiece: Optional[Eyepiece] = None,
                          # ❌ No way to pass filters, optical aids, imagers
                          observation_site: Optional[ObservationSite] = None,
                          weather: Optional[dict] = None,
                          moon_conditions: Optional[MoonConditions] = None)
```

**3. Equipment Entities Exist But Are Orphaned**

```python
# These exist in entities.py but are NEVER passed to scoring:

class Filter(Base):
    wavelengths: List[Wavelength]  # H-alpha, OIII, etc.
    minimum_exit_pupil: int
    # ❌ Not used anywhere in scoring logic

class OpticalAid(Base):
    magnification: float  # 2x Barlow, 0.5x reducer, primary mirror mask (aperture stop/off-axis mask), etc.
    # ❌ Not used anywhere in scoring logic

class Imager(Base):
    pixel_size: int
    sensor_dimensions: int
    # ❌ Not used anywhere in scoring logic
```

### Real-World Impact

**User Experience Gap:**
1. User adds "2x Barlow" in equipment manager ✅
2. User creates observation plan with Barlow ✅
3. System calculates score... **ignoring the Barlow completely** ❌
4. User confused: "Why did I configure this equipment?"

**Physics Gap:**
- Barlows/reducers change magnification → affects field of view and object visibility
- Filters change contrast and light transmission → affects detection of faint objects
- Eyepiece AFOV affects true field of view → impacts large object viewing
- Imagers have different capabilities than eyepieces → need separate scoring mode

---

## Existing Equipment Models

### Database Entities (All Implemented)

**Filter** (`entities.py:120-129`):
```python
class Filter(Base, EquipmentEntity):
    name: str                              # "UHC Filter", "2\" OIII", etc.
    minimum_exit_pupil: int | None         # Minimum mm for effective use
    wavelengths: List[Wavelength]          # What wavelengths it passes/blocks
```

**Wavelength** (`wavelength_type.py:8-11`):
```python
@dataclass
class Wavelength:
    from_wavelength: int  # nm (e.g., 495 for OIII)
    to_wavelength: int    # nm (e.g., 505 for OIII)
```

**OpticalAid** (`entities.py:112-119`):
```python
class OpticalAid(Base, EquipmentEntity):
    name: str              # "2x Barlow", "0.63x Focal Reducer", etc.
    magnification: float   # 2.0, 0.63, 1.5, etc.
```

**Imager** (`entities.py:133-150`):
```python
class Imager(Base, EquipmentEntity):
    name: str
    # Main sensor
    main_pixel_size_width: int         # micrometers
    main_pixel_size_height: int
    main_number_of_pixels_width: int   # resolution
    main_number_of_pixels_height: int
    # Guide sensor (optional)
    guide_pixel_size_width: int | None
    guide_pixel_size_height: int | None
    guide_number_of_pixels_width: int | None
    guide_number_of_pixels_height: int | None
```

**Eyepiece** (`entities.py:70-77`):
```python
class Eyepiece(Base, EquipmentEntity):
    name: str
    focal_length: int                  # mm - ✅ USED in magnification calc
    barrel_size: float                 # inches - ❌ NOT USED
    apparent_field_of_view: int        # degrees - ❌ NOT USED
```

### Existing UI Components

All equipment types have full CRUD UI:
- ✅ `manage_telescopes_tab.py`
- ✅ `manage_eyepieces_tab.py`
- ✅ `manage_filters_tab.py`
- ✅ `manage_optical_aids_tab.py`
- ✅ `manage_imagers_tab.py`

### Existing Repositories & Services

All equipment types have full data layer:
- ✅ `telescope_repository.py` + `telescope_service.py`
- ✅ `eyepiece_repository.py` + `eyepiece_service.py`
- ✅ `filter_repository.py` + `filter_service.py`
- ✅ `optical_aid_repository.py` + `optical_aid_service.py`
- ✅ `imager_repository.py` + `imager_service.py`

---

## Architecture Assessment

### Gap Analysis

| Component | Telescope | Eyepiece | Filter | OpticalAid | Imager |
|-----------|-----------|----------|--------|------------|--------|
| **Database Model** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Repository** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Service** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **UI Management** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **ScoringContext** | ✅ | ✅ | ❌ | ❌ | ❌ |
| **Scoring Strategies** | ✅ | 🟡 Partial | ❌ | ❌ | ❌ |
| **API Parameters** | ✅ | ✅ | ❌ | ❌ | ❌ |

**Legend:**
- ✅ Fully integrated
- 🟡 Partially integrated (eyepiece only used for magnification, ignores AFOV/barrel)
- ❌ Not integrated in scoring

### Current Equipment Usage

**Telescope (Full Integration):**
- `aperture` → Limiting magnitude calculation
- `focal_length` → Magnification calculation (with eyepiece)
- `type` → Aperture efficiency factor (Phase 6.5)

**Eyepiece (Partial Integration):**
- `focal_length` → Magnification calculation ✅
- `apparent_field_of_view` → NOT USED ❌
- `barrel_size` → NOT USED ❌

**Magnification Calculation (Only Current Equipment Combo):**
```python
def get_magnification(self) -> float:
    # Only considers telescope + eyepiece
    # ❌ Ignores optical aids (Barlows, reducers)
    return self.telescope.focal_length / self.eyepiece.focal_length
```

---

## Proposed Architecture

### 1. Expand ScoringContext

**File:** `src/app/domain/model/scoring_context.py`

```python
from typing import Optional, List
from app.orm.model.entities import (
    Telescope, Eyepiece, Filter, OpticalAid, Imager, ObservationSite
)

@dataclass
class ScoringContext:
    """
    Context object containing all environmental and equipment factors
    needed to score celestial object observability.
    """
    # Core equipment
    telescope: Optional[Telescope]
    eyepiece: Optional[Eyepiece]
    observation_site: Optional[ObservationSite]

    # New: Extended equipment
    filters: List[Filter] = None                    # NEW
    optical_aids: List[OpticalAid] = None          # NEW
    imager: Optional[Imager] = None                # NEW

    # Environmental
    altitude: float  # Object's current altitude in degrees
    weather: Optional[dict] = None
    moon_conditions: Optional[MoonConditions] = None

    # New: Observation mode
    observation_mode: str = "visual"  # "visual" or "imaging"  # NEW

    def __post_init__(self):
        """Initialize empty lists for equipment collections"""
        if self.filters is None:
            self.filters = []
        if self.optical_aids is None:
            self.optical_aids = []

    # Existing methods
    def has_equipment(self) -> bool:
        """Check if minimum required equipment is present"""
        if self.observation_mode == "imaging":
            return self.telescope is not None and self.imager is not None
        else:  # visual
            return self.telescope is not None and self.eyepiece is not None

    def get_effective_magnification(self) -> float:
        """
        Calculate effective magnification including optical aids.

        NEW: Accounts for Barlows, focal reducers, etc.
        """
        if not self.has_equipment():
            return 0.0

        # Base magnification
        base_mag = self.telescope.focal_length / self.eyepiece.focal_length

        # Apply optical aids multiplicatively
        # Example: 2x Barlow → mag = base_mag * 2.0
        for aid in self.optical_aids:
            base_mag *= aid.magnification

        return base_mag

    def get_true_field_of_view(self) -> float:
        """
        Calculate true field of view in degrees.

        NEW: Uses eyepiece AFOV (previously ignored).

        Formula: TFOV = AFOV / magnification
        """
        if not self.has_equipment():
            return 0.0

        mag = self.get_effective_magnification()
        if mag == 0:
            return 0.0

        return self.eyepiece.apparent_field_of_view / mag

    def has_filter_type(self, wavelength_range: tuple) -> bool:
        """
        Check if context includes a filter covering given wavelength range.

        Args:
            wavelength_range: (from_nm, to_nm) tuple

        Example:
            has_filter_type((495, 505))  # Check for OIII (500nm)
        """
        target_from, target_to = wavelength_range

        for filter in self.filters:
            for wavelength in filter.wavelengths:
                # Check if filter wavelength range overlaps with target
                if (wavelength.from_wavelength <= target_to and
                    wavelength.to_wavelength >= target_from):
                    return True
        return False

    def has_solar_filter(self) -> bool:
        """Check if solar filter present (safety-critical for Sun)"""
        # Solar filters block ~99.999% of light (wavelength-independent)
        # We could add a filter.type field, or check wavelength coverage
        # For now, check for very narrow wavelength ranges (solar filters)
        for filter in self.filters:
            for wavelength in filter.wavelengths:
                # Solar filters have extremely narrow bandpass
                bandwidth = wavelength.to_wavelength - wavelength.from_wavelength
                if bandwidth < 1:  # < 1nm = solar filter
                    return True
        return False

    def has_narrowband_filter(self) -> bool:
        """Check if narrowband filter present (H-alpha, OIII, SII)"""
        # H-alpha: 656nm, OIII: 500nm, SII: 672nm
        narrowband_ranges = [
            (654, 658),  # H-alpha
            (495, 505),  # OIII
            (670, 674)   # SII
        ]

        for range in narrowband_ranges:
            if self.has_filter_type(range):
                return True
        return False

    def get_filter_transmission_factor(self) -> float:
        """
        Calculate combined light transmission loss from all filters.

        Most filters reduce light transmission:
        - UHC/LPR: 90-95% transmission
        - Narrowband: 85-90%
        - Color filters: 40-70%
        - ND/Solar: 0.001%

        Returns: 0.0-1.0 multiplier
        """
        transmission = 1.0

        for filter in self.filters:
            # TODO: Add transmission property to Filter model
            # For now, estimate based on wavelength coverage

            total_spectrum = 780 - 380  # Visible spectrum (nm)
            filter_bandwidth = sum(
                w.to_wavelength - w.from_wavelength
                for w in filter.wavelengths
            )

            # Narrower filters = more light blocked
            if filter_bandwidth < 50:  # Narrowband
                transmission *= 0.15  # Block 85% of light
            elif filter_bandwidth < 200:  # UHC/LPR
                transmission *= 0.30  # Block 70% of light
            else:  # Broadband
                transmission *= 0.90  # Block 10% of light

        return transmission

    def get_aperture_mm(self) -> int:
        """Get telescope aperture in millimeters"""
        return self.telescope.aperture if self.telescope else 0

    def get_bortle_number(self) -> int:
        """Extract Bortle scale number from observation site (1-9)"""
        # ... existing implementation
```

### 2. Update ObservabilityCalculationService

**File:** `src/app/domain/services/observability_calculation_service.py`

```python
from typing import Optional, List

class ObservabilityCalculationService:

    def score_celestial_object(self,
                               celestial_object: CelestialObject,
                               telescope: Optional[Telescope] = None,
                               eyepiece: Optional[Eyepiece] = None,
                               observation_site: Optional[ObservationSite] = None,
                               weather: Optional[dict] = None,
                               moon_conditions: Optional[MoonConditions] = None,
                               # NEW parameters:
                               filters: Optional[List[Filter]] = None,
                               optical_aids: Optional[List[OpticalAid]] = None,
                               imager: Optional[Imager] = None,
                               observation_mode: str = "visual") -> ScoredCelestialObject:

        context = ScoringContext(
            telescope=telescope,
            eyepiece=eyepiece,
            observation_site=observation_site,
            altitude=celestial_object.altitude,
            weather=weather,
            moon_conditions=moon_conditions,
            # NEW:
            filters=filters or [],
            optical_aids=optical_aids or [],
            imager=imager,
            observation_mode=observation_mode
        )

        # ... rest of scoring logic
```

**Breaking Change Mitigation:**
The new parameters are all `Optional` with defaults, so existing code continues to work.

### 3. Equipment-Aware Scoring Strategies

**A. Optical Aid Impact (Magnification)**

```python
# deep_sky_strategy.py

def _calculate_magnification_factor(self, celestial_object, context: 'ScoringContext') -> float:
    """
    MAGNIFICATION FACTOR: Is magnification appropriate for this object?

    NEW: Uses effective magnification (includes optical aids).
    """
    if not context.has_equipment():
        return self._no_equipment_penalty(celestial_object.magnitude)

    # NEW: get_effective_magnification() accounts for Barlows/reducers
    magnification = context.get_effective_magnification()

    # Large extended objects need LOW magnification
    if celestial_object.size > 60:  # Very large objects
        if magnification < 100:
            return 1.0  # Perfect
        elif magnification < 200:
            return 0.85  # Acceptable
        else:
            return 0.5  # Too much mag, can't fit in FOV

    # ... rest of logic
```

**B. Filter Impact (Contrast Enhancement)**

```python
# deep_sky_strategy.py

def _calculate_sky_darkness_factor(self, celestial_object, context: 'ScoringContext') -> float:
    """
    SKY DARKNESS FACTOR: Light pollution penalties.

    NEW: Narrowband filters can reduce light pollution impact.
    """
    bortle = context.get_bortle_number()

    # NEW: Check for narrowband filters
    if context.has_narrowband_filter():
        # Narrowband filters effectively reduce light pollution by 2-3 Bortle classes
        # for emission nebulae (they block most LP but pass nebula wavelengths)
        if celestial_object.object_type == "emission_nebula":
            bortle = max(1, bortle - 2)  # Simulate darker skies

    # Apply Bortle penalty
    penalty_per_bortle = 0.10
    base_factor = 1.0 - (penalty_per_bortle * (bortle - 1))

    # NEW: Account for filter transmission loss
    # Filters block some light from the object too
    transmission = context.get_filter_transmission_factor()

    return base_factor * transmission
```

**C. Solar Filter Safety Check**

```python
# sun_strategy.py

def calculate_score(self, celestial_object, context: 'ScoringContext') -> float:
    """
    Sun scoring - REQUIRES solar filter for safety.

    NEW: Returns 0.0 if no solar filter present.
    """
    # SAFETY CHECK: Sun requires solar filter
    if not context.has_solar_filter():
        return 0.0  # Invisible (and dangerous) without filter

    # With solar filter, Sun is always excellent target
    # (weather permitting)
    altitude_factor = self._calculate_altitude_factor(celestial_object)
    weather_factor = calculate_weather_factor(context)

    return 100.0 * altitude_factor * weather_factor
```

**D. True Field of View Matching**

```python
# deep_sky_strategy.py (or large_faint_object_strategy.py)

def _calculate_field_of_view_factor(self, celestial_object, context: 'ScoringContext') -> float:
    """
    NEW FACTOR: Does object fit in the field of view?

    Uses eyepiece AFOV and optical aids to calculate TFOV.
    Objects larger than TFOV should be penalized.
    """
    if not context.has_equipment():
        return 1.0  # No penalty for naked eye

    tfov = context.get_true_field_of_view()  # degrees
    object_size = celestial_object.size / 60.0  # arcmin to degrees

    # Object should fit comfortably in FOV
    if object_size < tfov * 0.5:
        return 1.0  # Plenty of room
    elif object_size < tfov * 0.8:
        return 0.95  # Fits but tight
    elif object_size < tfov:
        return 0.85  # Barely fits
    else:
        # Object larger than FOV - significant penalty
        overhang = object_size / tfov
        return 0.5 / overhang  # Worse as object gets larger
```

### 4. Imaging Mode Support (Future)

```python
# imaging_strategy.py (NEW FILE)

class ImagingStrategy(IObservabilityScoringStrategy):
    """
    Scoring strategy for astrophotography/imaging.

    Different from visual observing:
    - Uses imager sensor specs instead of eyepiece
    - Considers pixel scale, sampling, SNR
    - Integration time matters (not instant like visual)
    - Less affected by moon (can image during full moon with filters)
    """

    def calculate_score(self, celestial_object, context: 'ScoringContext') -> float:
        if context.observation_mode != "imaging":
            raise ValueError("ImagingStrategy requires observation_mode='imaging'")

        # Imaging-specific factors
        pixel_scale_factor = self._calculate_pixel_scale_match(celestial_object, context)
        signal_noise_factor = self._calculate_snr(celestial_object, context)
        integration_time_factor = self._calculate_required_integration(celestial_object, context)

        return pixel_scale_factor * signal_noise_factor * integration_time_factor
```

---

## Implementation Roadmap

### Phase 13.1: Foundation (Week 1)
**Goal:** Extend architecture to support all equipment types

1. ✅ Expand `ScoringContext` to include filters, optical_aids, imager
2. ✅ Add `observation_mode` field ("visual" vs "imaging")
3. ✅ Add equipment helper methods:
   - `get_effective_magnification()` - includes optical aids
   - `get_true_field_of_view()` - uses eyepiece AFOV
   - `has_filter_type()`, `has_solar_filter()`, etc.
4. ✅ Update `ObservabilityCalculationService` API with new parameters
5. ✅ Maintain backward compatibility (all new params optional)

**Tests:**
- Context correctly combines optical aids in magnification
- Filter detection methods work correctly
- Backward compatibility: old code still works

### Phase 13.2: Optical Aids (Week 2)
**Goal:** Integrate Barlows, focal reducers, etc.

1. ✅ Update `_calculate_magnification_factor()` to use `get_effective_magnification()`
2. ✅ Add `_calculate_field_of_view_factor()` using `get_true_field_of_view()`
3. ✅ Test scenarios:
   - 2x Barlow doubles magnification
   - 0.63x reducer widens field
   - Combinations (reducer + eyepiece swap)

**Tests:**
- Barlow increases magnification for planetary viewing
- Reducer improves large object scores
- FOV factor penalizes oversized objects

### Phase 13.3: Filters - Safety (Week 3)
**Goal:** Critical safety feature for solar observation

1. ✅ Add solar filter check in `sun_strategy.py`
2. ✅ Return score = 0.0 if Sun without solar filter
3. ✅ UI warning: "REQUIRES SOLAR FILTER" badge
4. ✅ Filter dropdown highlights solar filters when Sun selected

**Tests:**
- Sun scores 0.0 without solar filter
- Sun scores high with solar filter
- Other objects unaffected

### Phase 13.4: Filters - Narrowband (Week 3-4)
**Goal:** Model narrowband filter benefits for emission nebulae

1. ✅ Implement `has_narrowband_filter()` detection
2. ✅ Update `_calculate_sky_darkness_factor()`:
   - Reduce effective Bortle by 2 for emission nebulae with narrowband
   - Apply filter transmission loss
3. ✅ Test with Orion Nebula, North America Nebula in Bortle 7

**Tests:**
- UHC filter improves nebula scores in light pollution
- Narrowband filter makes Bortle 7 behave like Bortle 5
- Filter transmission loss partially offsets benefit

### Phase 13.5: Eyepiece Enhancements (Week 4)
**Goal:** Use eyepiece AFOV for field of view calculations

1. ✅ Implement `get_true_field_of_view()`
2. ✅ Add `_calculate_field_of_view_factor()` to strategies
3. ✅ Test with wide-field eyepieces (82° AFOV) vs narrow (50° AFOV)

**Tests:**
- Wide AFOV improves large object scores
- Narrow AFOV penalizes objects that don't fit

### Phase 13.6: Imaging Mode (Future - Phase 14+)
**Goal:** Support astrophotography scoring

1. Add `ImagingStrategy` for camera-based observation
2. Calculate pixel scale, sampling, SNR
3. UI mode toggle: "Visual Observing" vs "Astrophotography"

---

## Database Schema Changes

**None required!** All equipment models already exist.

**Optional Enhancement:**
Add `transmission: float` field to `Filter` model for more accurate light loss modeling.

```python
# entities.py - Optional enhancement

class Filter(Base, EquipmentEntity):
    # ... existing fields
    transmission: float | None = cast(float, Column(Float, nullable=True))  # NEW
    # 0.0-1.0 (1.0 = 100% transmission, 0.15 = 15% transmission)
```

---

## Testing Strategy

### Unit Tests

```python
class TestEquipmentIntegration(unittest.TestCase):
    def test_barlow_doubles_magnification(self):
        """2x Barlow should double magnification"""
        context = ScoringContext(
            telescope=Telescope(..., focal_length=1200),
            eyepiece=Eyepiece(..., focal_length=25),
            optical_aids=[OpticalAid(name="2x Barlow", magnification=2.0)]
        )

        # Without Barlow: 1200/25 = 48x
        # With 2x Barlow: 48 * 2 = 96x
        assert_that(context.get_effective_magnification()).is_equal_to(96.0)

    def test_narrowband_filter_helps_emission_nebula(self):
        """OIII filter should improve nebula score in light pollution"""
        orion = CelestialObject("M42", "emission_nebula", 4.0, 65.0, 45.0)

        # Bortle 7 (suburban), no filter
        context_no_filter = ScoringContext(..., bortle=7, filters=[])
        score_no_filter = service.score(orion, context_no_filter)

        # Bortle 7, with OIII filter
        oiii = Filter(name="OIII", wavelengths=[Wavelength(495, 505)])
        context_with_filter = ScoringContext(..., bortle=7, filters=[oiii])
        score_with_filter = service.score(orion, context_with_filter)

        # Filter should improve score by acting like Bortle 5
        assert_that(score_with_filter).is_greater_than(score_no_filter * 1.5)

    def test_sun_requires_solar_filter(self):
        """Sun should score 0.0 without solar filter"""
        sun = CelestialObject("Sun", "Sun", -26.7, 31.0, 45.0)

        context_no_filter = ScoringContext(...)
        score_no_filter = service.score(sun, context_no_filter)

        assert_that(score_no_filter).is_equal_to(0.0)

    def test_true_field_of_view_calculation(self):
        """TFOV should use eyepiece AFOV"""
        context = ScoringContext(
            telescope=Telescope(..., focal_length=1200),
            eyepiece=Eyepiece(..., focal_length=25, afov=82),  # Wide-field
            optical_aids=[]
        )

        # Mag = 1200/25 = 48x
        # TFOV = 82° / 48 = 1.71°
        assert_that(context.get_true_field_of_view()).is_close_to(1.71, 0.01)
```

### Integration Tests

```python
class TestRealisticScenarios(unittest.TestCase):
    def test_planetary_observation_with_barlow(self):
        """Jupiter with 2x Barlow should score better than without"""
        jupiter = TestFixtures.jupiter()

        # High mag good for planets
        context_with_barlow = ScoringContext(
            telescope=medium_scope,
            eyepiece=short_eyepiece,  # 10mm
            optical_aids=[Barlow2x]
        )

        context_without_barlow = ScoringContext(
            telescope=medium_scope,
            eyepiece=short_eyepiece
        )

        with_barlow = service.score(jupiter, context_with_barlow)
        without_barlow = service.score(jupiter, context_without_barlow)

        # Barlow brings mag from 120x to 240x, better for Jupiter
        assert_that(with_barlow).is_greater_than(without_barlow)

    def test_emission_nebula_suburban_with_uhc(self):
        """Orion Nebula in Bortle 6 should be much better with UHC filter"""
        orion = TestFixtures.orion_nebula()

        suburban_no_filter = service.score(orion, suburban_context_no_filter)
        suburban_with_uhc = service.score(orion, suburban_context_uhc_filter)

        # UHC should act like ~2 Bortle classes darker
        assert_that(suburban_with_uhc).is_greater_than(suburban_no_filter * 1.8)
```

---

## UI/UX Considerations

### Equipment Selection UI

**Current:**
- User selects telescope + eyepiece for observation plan

**Proposed:**
```
┌─ Equipment Configuration ─────────────────────┐
│                                                │
│ Telescope: [8" Dobsonian ▼]                  │
│ Eyepiece:  [25mm Plossl  ▼]                  │
│                                                │
│ Optical Aids: (optional)                       │
│   [✓] 2x Barlow                               │
│   [ ] 0.63x Focal Reducer                     │
│                                                │
│ Filters: (optional)                            │
│   [✓] UHC Filter                              │
│   [ ] OIII Filter                             │
│   [ ] Solar Filter   ⚠️ Required for Sun      │
│                                                │
│ Calculated:                                    │
│   Magnification: 96x (48x base × 2x Barlow)   │
│   True FOV: 0.52° (good for planets)          │
│                                                │
└────────────────────────────────────────────────┘
```

### Score Display Enhancements

**Current:**
```
M42 - Orion Nebula
Score: 65%
```

**Proposed:**
```
M42 - Orion Nebula
Score: 78%  (+13% with UHC filter)

Equipment Impact:
  ✓ UHC Filter: +20% (contrast boost in Bortle 6)
  ⚠ Magnification: -5% (96x slightly high for 65' object)
  ✓ Field of View: Good (object fits comfortably)
```

---

## Dependencies & Blockers

**Blocked By:**
- None! This is foundational work.

**Blocks:**
- Phase 9: Filter Integration (now has architecture)
- Phase 10: Imaging Support (now has imager in context)
- Phase 11: Astrophotography Scoring (now has observation_mode)

**Synergies:**
- Phase 4 (Factor Pipeline): Equipment factors would be visible
- Phase 8 (API Integration): Object classification enables filter matching

---

## Success Metrics

1. **Equipment Coverage:**
   - ✅ 5/5 equipment types integrated in scoring (was 2/5)

2. **User Experience:**
   - ✅ Equipment configured in UI actually affects scores
   - ✅ Solar filter warning prevents dangerous observations
   - ✅ Filter recommendations shown for light-polluted sites

3. **Physics Accuracy:**
   - ✅ Barlow/reducer magnification correctly calculated
   - ✅ Narrowband filters model ~2 Bortle class improvement
   - ✅ TFOV calculated using eyepiece AFOV

4. **Backward Compatibility:**
   - ✅ Existing code continues to work (new params optional)
   - ✅ Old test suite passes unchanged

---

## Future Enhancements (Post-Phase 13)

1. **Filter Database Expansion:**
   - Add `transmission` field to Filter model
   - Add `filter_type` enum (UHC, OIII, H-alpha, Solar, Color, etc.)
   - Preload common filters with accurate specs

2. **Smart Filter Recommendations:**
   - "OIII filter recommended for this emission nebula in Bortle 6"
   - "UHC filter would improve score by 25%"
   - Auto-highlight best filter for selected object

3. **Equipment Optimizer:**
   - "Try 0.63x reducer for better field of view"
   - "2x Barlow would improve planetary detail"
   - Equipment combination suggestions

4. **Imaging Mode Full Implementation:**
   - Pixel scale calculator
   - SNR estimator
   - Integration time recommendations
   - Stacking strategy suggestions

---

## References

- AstroPlanner: Optical aids concept (Barlows, reducers, etc.)
- Sky & Telescope: Filter effectiveness guides
- CloudyNights: UHC/OIII filter reviews and light pollution reduction
- Telescopius: Field of view calculations

---

*Last Updated: 2026-02-11*
*Status: Ready for implementation*
*Priority: HIGH - Foundation for equipment-aware scoring*
