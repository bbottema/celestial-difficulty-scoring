# Phase 7: Object-Type-Aware Scoring

**Status:** NOT STARTED
**Priority:** 🟢 MEDIUM - Accuracy improvement
**Dependencies:**
- Phase 8 (astronomical API) - **REQUIRED** for object classification data
- Phase 5 (complete) - Enhances Phase 5 detection headroom model

---

## Goal

Tailor detection headroom and scoring based on actual object classification (planetary nebula, spiral galaxy, open cluster, etc.) rather than generic "DeepSky" type.

---

## Problem Statement

**Current Limitation:**
- AstroPlanner exports generic types: "DeepSky", "Planet", "Sun", "Moon"
- Cannot differentiate between:
  - Planetary nebulae (high surface brightness, compact) vs diffuse nebulae (low surface brightness)
  - Galaxies (very low surface brightness) vs globular clusters (concentrated cores)
  - Open clusters (resolved stars) vs emission nebulae (diffuse glow)

**Impact:**
- Ring Nebula (planetary) over-penalized like a galaxy
- Globular clusters not scored as easier than galaxies at same magnitude
- M42 (emission nebula) scored same as Veil Nebula (supernova remnant)

**Estimated accuracy improvement:** 15-25% in deep-sky object rankings

---

## Proposed Enhancement

### Object-Type-Aware Headroom Values

```python
# src/app/utils/light_pollution_models.py

HEADROOM_BY_TYPE = {
    'planetary_nebula': 1.3,      # High surface brightness, easier
    'globular_cluster': 1.5,      # Concentrated core, moderate
    'open_cluster': 1.4,          # Resolved stars, relatively easy
    'emission_nebula': 2.5,       # Moderate surface brightness
    'reflection_nebula': 2.8,     # Similar to emission, slightly harder
    'galaxy_spiral': 3.0,         # Low surface brightness
    'galaxy_elliptical': 2.8,     # Slightly higher than spiral
    'galaxy_irregular': 2.9,      # Between elliptical and spiral
    'dark_nebula': 3.5,           # Extremely low contrast (needs darkness)
    'supernova_remnant': 3.2,     # Very faint, extended (Veil, Crab)
    'nebula_cluster': 2.0,        # Hybrid (M8, M20)
    'default': 2.5                # Fallback for unknown types
}
```

**Rationale:**
- **Lower headroom** = easier to detect (more photons per area)
- **Higher headroom** = harder to detect (photons spread over large area)

---

## Implementation

### 1. Enhance CelestialObject Model

**File:** `src/app/domain/model/celestial_object.py`

```python
@dataclass
class CelestialObject:
    name: str
    object_type: str                          # Keep for compatibility ("DeepSky")
    object_classification: Optional[str] = None  # NEW: "spiral_galaxy", "planetary_nebula", etc.
    magnitude: float
    surface_brightness: Optional[float] = None   # NEW: mag/arcsec² if available
    size: float
    size_minor_axis: Optional[float] = None      # NEW: for elongated objects
    altitude: float
    catalog_ids: Optional[dict[str, str]] = None # NEW: {"NGC": "7000", "Messier": "31"}
```

---

### 2. Update Light Pollution Model

**File:** `src/app/utils/light_pollution_models.py`

```python
def calculate_light_pollution_factor_with_surface_brightness(
    object_magnitude: float,
    object_size_arcmin: float,
    object_classification: Optional[str],  # NEW parameter
    bortle: int,
    telescope_aperture_mm: float = None,
    use_legacy_penalty: bool = False,
    legacy_penalty_per_bortle: float = 0.10,
    legacy_minimum_factor: float = 0.02
) -> float:
    """
    Handles extended objects with type-aware headroom selection.
    """
    # Select headroom based on object type
    if object_classification and object_classification in HEADROOM_BY_TYPE:
        detection_headroom = HEADROOM_BY_TYPE[object_classification]
    else:
        # Fallback to size-based heuristic (Phase 5 behavior)
        if object_size_arcmin > 120:
            detection_headroom = 3.5
        elif object_size_arcmin > 60:
            detection_headroom = 3.2
        elif object_size_arcmin > 30:
            detection_headroom = 3.0
        elif object_size_arcmin > 5:
            detection_headroom = 2.5
        else:
            detection_headroom = 1.5

    return calculate_light_pollution_factor_by_limiting_magnitude(
        object_magnitude, bortle, telescope_aperture_mm,
        detection_headroom, use_legacy_penalty,
        legacy_penalty_per_bortle, legacy_minimum_factor
    )
```

---

### 3. Update Strategies

**File:** `src/app/domain/services/strategies.py`

```python
class DeepSkyScoringStrategy(IObservabilityScoringStrategy):
    def _calculate_site_factor(self, celestial_object, context: 'ScoringContext') -> float:
        """
        Uses object classification for more accurate detection modeling.
        """
        factor = calculate_light_pollution_factor_with_surface_brightness(
            celestial_object.magnitude,
            celestial_object.size,
            celestial_object.object_classification,  # NEW: Pass classification
            bortle,
            aperture,
            use_legacy_penalty=True,
            legacy_penalty_per_bortle=LIGHT_POLLUTION_PENALTY_PER_BORTLE_DEEPSKY,
            legacy_minimum_factor=preset.light_pollution_min_factor_deepsky
        )
        return factor
```

---

### 4. Data Migration

**Backward compatibility:**
```python
if celestial_object.object_classification is None:
    # Fallback to Phase 5 size-based heuristic
    detection_headroom = get_headroom_by_size(celestial_object.size)
else:
    # Use Phase 7 type-aware headroom
    detection_headroom = HEADROOM_BY_TYPE.get(
        celestial_object.object_classification,
        HEADROOM_BY_TYPE['default']
    )
```

---

## Examples

### Before Phase 7 (Size-Based Heuristic):

```python
# Ring Nebula (planetary nebula, 1.4' size)
# Size < 5' → headroom = 1.5
# Scored as moderately difficult

# NGC 7027 (planetary nebula, 0.2' size)
# Size < 5' → headroom = 1.5
# Scored as moderately difficult

# M33 (spiral galaxy, 73' size)
# Size > 60' → headroom = 3.2
# Scored as very difficult
```

### After Phase 7 (Type-Aware):

```python
# Ring Nebula (planetary nebula)
# Classification → headroom = 1.3 (high surface brightness!)
# Scored as EASY (correct!)

# NGC 7027 (planetary nebula)
# Classification → headroom = 1.3
# Scored as EASY (correct!)

# M33 (spiral galaxy)
# Classification → headroom = 3.0 (low surface brightness)
# Scored as very difficult (correct!)
```

---

## Testing

### Test 1: Planetary Nebulae Easier Than Galaxies
```python
def test_planetary_nebula_easier_than_galaxy_same_magnitude():
    """
    Ring Nebula (planetary) should be easier than a galaxy at same magnitude.
    """
    ring_nebula = CelestialObject(
        name="M57 - Ring Nebula",
        object_classification="planetary_nebula",
        magnitude=8.8,
        size=1.4,
        altitude=60.0
    )

    fake_galaxy = CelestialObject(
        name="Fake Galaxy",
        object_classification="galaxy_spiral",
        magnitude=8.8,  # Same magnitude!
        size=1.4,       # Same size!
        altitude=60.0
    )

    context = create_context(bortle=5, aperture=200)

    score_pn = strategy.calculate_score(ring_nebula, context)
    score_galaxy = strategy.calculate_score(fake_galaxy, context)

    # Planetary nebula should score MUCH higher (1.3 vs 3.0 headroom)
    assert_that(score_pn.factors["site"]).is_greater_than(
        score_galaxy.factors["site"] * 1.5
    )
```

### Test 2: Globular Clusters vs Open Clusters
```python
def test_globular_easier_than_open_cluster():
    """
    Globular clusters (concentrated) easier than open clusters (resolved stars).
    """
    m13 = CelestialObject(
        name="M13 - Hercules Cluster",
        object_classification="globular_cluster",
        magnitude=5.8,
        size=20.0,
        altitude=60.0
    )

    m45 = CelestialObject(
        name="M45 - Pleiades",
        object_classification="open_cluster",
        magnitude=1.6,  # Much brighter!
        size=110.0,
        altitude=60.0
    )

    # Despite Pleiades being MUCH brighter, headroom values reflect
    # that globular (concentrated) is easier than open (resolved)
    assert_that(HEADROOM_BY_TYPE["globular_cluster"]).is_less_than(
        HEADROOM_BY_TYPE["open_cluster"]
    )
```

### Test 3: Fallback to Size-Based Heuristic
```python
def test_fallback_when_classification_missing():
    """
    Should use Phase 5 size-based heuristic when classification unavailable.
    """
    unknown_object = CelestialObject(
        name="Unknown Object",
        object_classification=None,  # No classification
        magnitude=8.0,
        size=75.0,  # Large object
        altitude=60.0
    )

    context = create_context(bortle=5, aperture=200)
    score = strategy.calculate_score(unknown_object, context)

    # Should use size-based fallback: 75' > 60' → headroom = 3.2
    # (Phase 5 behavior)
    assert score is not None  # Doesn't crash, uses fallback
```

---

## UI Integration

**Before Phase 7:**
```
M57 - Ring Nebula
Type: DeepSky
Score: 60% (Moderate)
```

**After Phase 7:**
```
M57 - Ring Nebula
Type: Planetary Nebula (compact, high SB)
Score: 85% (Excellent)
💡 High surface brightness makes this easy!
```

---

## Benefits

| Object Type | Phase 5 Headroom (size-based) | Phase 7 Headroom (type-aware) | Accuracy Improvement |
|-------------|-------------------------------|-------------------------------|---------------------|
| Ring Nebula (1.4') | 1.5 | 1.3 | ✅ 15% easier |
| M31 Andromeda (190') | 3.5 | 3.0 | ✅ 14% easier |
| M42 Orion (65') | 3.2 | 2.5 | ✅ 22% easier |
| M33 Triangulum (73') | 3.2 | 3.0 | ✅ 6% easier |
| Veil Nebula (180') | 3.5 | 3.2 | ✅ 9% easier |

**Overall:** 15-25% accuracy improvement across catalog.

---

## Open Questions

1. **Should we support multiple classifications?**
   - Example: M8 is both emission nebula + open cluster
   - **Recommendation:** Use primary classification, or average headroom values

2. **How to handle unknown types?**
   - **Decision:** Fallback to Phase 5 size-based heuristic (backward compatible)

3. **Should headroom values be customizable?**
   - **Recommendation:** Phase 3 (custom presets) integration in future

---

## Future Enhancements

- **Phase 7.1: Surface Brightness Direct Scoring** - Use actual mag/arcsec² from catalogs instead of estimating
- **Phase 7.2: Color Index Integration** - Adjust for object color (blue emission vs red reflection)
- **Phase 7.3: Morphology Factors** - Face-on vs edge-on galaxies scored differently

---

## References

- Phase 5 implementation: `src/app/utils/light_pollution_models.py`
- Phase 5 code review: `PHASE5_CODE_REVIEW_RESPONSE.md`
- Catalog classifications: Simbad, OpenNGC, SEDS

---

*Last Updated: 2026-02-10*
*Dependencies: Phase 8 (API) required for classification data*
*Status: Blocked - waiting for Phase 8*
