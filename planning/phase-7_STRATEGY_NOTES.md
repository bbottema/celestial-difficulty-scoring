# Phase 7 Strategy Architecture Notes

**Date:** 2026-02-10
**Context:** Post-strategy refactor (ReflectedLightStrategy/SunStrategy split)

---

## Strategy Mapping After Refactor

As of the Phase 5 calibration refactor, we now have a cleaner strategy architecture:

### Current Strategies (Post-Refactor)
1. **SunStrategy** - Dedicated Sun handling (safety-first)
2. **ReflectedLightStrategy** - Moon, Planets (physics-based: magnitude + angular size)
3. **DeepSkyScoringStrategy** - Compact deep-sky objects (stars, small galaxies, nebulae)
4. **LargeFaintObjectScoringStrategy** - Extended deep-sky (M31, M42, etc.)

### Impact on Phase 7 Object Type Integration

When Phase 7 adds detailed object types from APIs, the strategy selector will need updating:

```python
# observability_calculation_service.py::_determine_scoring_strategy()

def _determine_scoring_strategy(celestial_object):
    if celestial_object.object_type == 'Sun':
        return SunStrategy()

    elif celestial_object.object_type in ['Planet', 'Moon']:
        return ReflectedLightStrategy()

    # NEW: Phase 7 detailed types
    elif celestial_object.object_type in ['Comet', 'Asteroid']:
        # Comets/asteroids are reflective objects, use same strategy
        return ReflectedLightStrategy()

    # Deep-sky types (Phase 7)
    elif celestial_object.object_type in [
        'planetary_nebula', 'globular_cluster', 'open_cluster',
        'emission_nebula', 'reflection_nebula', 'dark_nebula',
        'supernova_remnant', 'nebula_cluster', 'HII_region'
    ]:
        # Size-based routing for deep-sky
        if celestial_object.size > LARGE_OBJECT_SIZE_THRESHOLD:
            return LargeFaintObjectScoringStrategy()
        else:
            return DeepSkyScoringStrategy()

    elif celestial_object.object_type in [
        'galaxy_spiral', 'galaxy_elliptical', 'galaxy_irregular',
        'galaxy_dwarf', 'galaxy_lenticular'
    ]:
        # Most galaxies are large and faint
        if celestial_object.size > LARGE_OBJECT_SIZE_THRESHOLD:
            return LargeFaintObjectScoringStrategy()
        else:
            return DeepSkyScoringStrategy()

    elif celestial_object.object_type == 'star':
        # Stars are point sources - use deep-sky strategy
        return DeepSkyScoringStrategy()

    else:
        # Fallback for unknown types
        return DeepSkyScoringStrategy()
```

### Object Type → Strategy Mapping Table

| Object Type | Strategy | Notes |
|-------------|----------|-------|
| Sun | SunStrategy | Safety-first, filter required |
| Moon | ReflectedLightStrategy | Large (30'), bright (-12) |
| Planet (Venus, Jupiter, Mars, Saturn, etc.) | ReflectedLightStrategy | Tiny (<1'), bright (-4 to +1) |
| Comet (bright) | ReflectedLightStrategy | Variable size, magnitude-dependent |
| Asteroid | ReflectedLightStrategy | Tiny, faint - same physics as planets |
| Planetary Nebula | DeepSky or LargeFaint | Based on size threshold |
| Globular Cluster | DeepSky or LargeFaint | Based on size threshold |
| Open Cluster | DeepSky | Typically compact |
| Emission Nebula | LargeFaint (usually) | Typically extended |
| Galaxy (all types) | LargeFaint (usually) | Typically extended |
| Supernova Remnant | LargeFaint | Very extended |
| Star | DeepSky | Point source |

### Key Design Decision: ReflectedLightStrategy Versatility

The **ReflectedLightStrategy** was designed to be versatile based on physics:
- **Large + Bright** (Moon) → Low magnification preferred, minimal light pollution impact
- **Tiny + Bright** (Planets) → High magnification preferred, minimal light pollution impact
- **Large + Faint** (Bright Comets) → Low-medium magnification, aperture helps
- **Tiny + Faint** (Asteroids) → High magnification needed, aperture critical

This means **comets and asteroids automatically work** without code changes - they're just parameterized differently (size + magnitude).

### Phase 7 Implementation Notes

When implementing Phase 7:

1. **Update strategy selector** (observability_calculation_service.py)
   - Add detailed object type mappings as shown above
   - Consider creating a mapping dict/enum for maintainability

2. **Keep strategies unchanged**
   - Strategies remain generic (size/magnitude-based)
   - Type-specific logic goes in detection_headroom selection

3. **Update detection headroom selection** (light_pollution_models.py)
   - Replace generic size-based headroom with type-specific values
   - Use `HEADROOM_BY_TYPE` dict from phase-7 planning doc

4. **Testing considerations**
   - Update test fixtures to use new detailed types
   - Test that comets/asteroids route to ReflectedLightStrategy
   - Verify deep-sky subtypes route correctly

### Migration Path

**Phase 7 should NOT require strategy refactoring** - the current strategies are designed to be generic. Phase 7 work is mostly:
1. Update strategy selector routing (10 lines of code)
2. Update headroom selection logic (20 lines of code)
3. Update tests to use new types (testing overhead)

The heavy lifting was done in this refactor (separating Sun, eliminating Moon special cases, physics-based approach).

---

## Benefits of Current Architecture

✅ **Physics-based** - No special cases for individual objects
✅ **Extensible** - Comets/asteroids work automatically
✅ **Clean separation** - Sun is special (safety), everything else follows patterns
✅ **Future-proof** - API object types map cleanly to strategies
✅ **Maintainable** - No per-object conditionals, parameter-driven behavior
