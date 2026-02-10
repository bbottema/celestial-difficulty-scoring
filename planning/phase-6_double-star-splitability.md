# Phase 6: Double Star Splitability

**Status:** NOT STARTED
**Priority:** 🟢 LOW - Niche but valuable feature
**Dependencies:**
- Phase 8 (astronomical API) - Required for separation data

---

## Goal

Score double stars based on whether telescope can split them using optical resolution limits (Dawes' limit, Rayleigh criterion).

---

## Problem Statement

Double stars are currently scored like single stars, ignoring the key challenge: **Can your telescope resolve the two components?**

- Albireo (wide separation): Easy to split with any telescope
- Epsilon Lyrae (tight separation): Requires large aperture and good seeing
- Current scoring doesn't differentiate between these

---

## Optical Resolution Limits

### Dawes' Limit
```
Resolution (arcseconds) = 116 / aperture_mm
```
- Empirical limit for resolving equal-magnitude stars
- Example: 100mm telescope → 1.16" resolution

### Rayleigh Criterion
```
Resolution (arcseconds) = 138 / aperture_mm
```
- Theoretical diffraction limit
- More conservative than Dawes' limit
- Example: 100mm telescope → 1.38" resolution

---

## Implementation

### 1. Add Separation Field to CelestialObject

**File:** `src/app/domain/model/celestial_object.py`

```python
@dataclass
class CelestialObject:
    name: str
    object_type: str
    magnitude: float
    size: float
    altitude: float
    separation: Optional[float] = None  # NEW: arcseconds (for double stars)
    magnitude_secondary: Optional[float] = None  # NEW: secondary component magnitude

    def is_double_star(self) -> bool:
        """Check if object is a double star"""
        return self.separation is not None
```

---

### 2. Implement Splitability Scoring

**File:** `src/app/domain/services/strategies.py` (new DoubleStarScoringStrategy)

```python
class DoubleStarScoringStrategy(IObservabilityScoringStrategy):
    """
    Scoring for double stars based on splitability.
    """

    def calculate_score(self, celestial_object, context: 'ScoringContext'):
        if not celestial_object.is_double_star():
            # Fallback to standard deep-sky scoring
            return DeepSkyScoringStrategy().calculate_score(celestial_object, context)

        # Calculate resolution capability
        aperture_mm = context.get_aperture_mm()
        dawes_limit = 116 / aperture_mm
        rayleigh_limit = 138 / aperture_mm

        separation = celestial_object.separation

        # Splitability factor
        if separation > dawes_limit * 2:
            splitability = 1.0  # Easily split
        elif separation > dawes_limit:
            splitability = 0.8  # Clearly split
        elif separation > rayleigh_limit:
            splitability = 0.5  # Barely split (challenging)
        else:
            splitability = 0.2  # Cannot split (single elongated star)

        # Magnitude difference penalty (unequal stars harder to split)
        if celestial_object.magnitude_secondary:
            mag_diff = abs(celestial_object.magnitude - celestial_object.magnitude_secondary)
            if mag_diff > 2.0:
                splitability *= 0.8  # 20% penalty for unequal brightness

        # Standard factors (altitude, weather, moon)
        altitude_factor = self._calculate_altitude_factor(context.altitude)
        weather_factor = _calculate_weather_factor(context)
        moon_factor = self._calculate_moon_proximity_factor(celestial_object, context)

        # Seeing factor (atmospheric turbulence affects resolution)
        seeing_factor = 1.0  # TODO: Integrate seeing conditions when available

        return (splitability * altitude_factor * weather_factor *
                moon_factor * seeing_factor)
```

---

### 3. Add Tests

```python
def test_albireo_easy_to_split():
    """Albireo (34.4" separation) should be easily split by any telescope"""
    albireo = CelestialObject(
        name="Albireo",
        object_type="DoubleStar",
        magnitude=3.1,
        size=34.4,  # separation in arcseconds
        separation=34.4,
        altitude=60.0
    )

    context_80mm = create_context(aperture=80)  # Dawes = 1.45"
    context_200mm = create_context(aperture=200)  # Dawes = 0.58"

    # Both should score high (easily split)
    score_80mm = strategy.calculate_score(albireo, context_80mm)
    score_200mm = strategy.calculate_score(albireo, context_200mm)

    assert_that(score_80mm.factors["splitability"]).is_greater_than(0.9)
    assert_that(score_200mm.factors["splitability"]).is_greater_than(0.9)


def test_epsilon_lyrae_requires_aperture():
    """Epsilon Lyrae (2.2" separation) requires larger aperture"""
    epsilon_lyrae = CelestialObject(
        name="Epsilon Lyrae",
        object_type="DoubleStar",
        magnitude=4.7,
        separation=2.2,
        altitude=60.0
    )

    context_80mm = create_context(aperture=80)   # Dawes = 1.45" (barely)
    context_200mm = create_context(aperture=200) # Dawes = 0.58" (easy)

    score_80mm = strategy.calculate_score(epsilon_lyrae, context_80mm)
    score_200mm = strategy.calculate_score(epsilon_lyrae, context_200mm)

    # 80mm should be marginal, 200mm should be good
    assert_that(score_80mm.factors["splitability"]).is_between(0.4, 0.6)
    assert_that(score_200mm.factors["splitability"]).is_greater_than(0.8)


def test_unequal_magnitude_penalty():
    """Unequal brightness makes splitting harder"""
    sirius_b = CelestialObject(
        name="Sirius B",
        object_type="DoubleStar",
        magnitude=-1.46,  # Sirius A
        magnitude_secondary=8.44,  # Sirius B (9.9 mag difference!)
        separation=10.0,
        altitude=60.0
    )

    context = create_context(aperture=200)  # Large aperture
    score = strategy.calculate_score(sirius_b, context)

    # Should be penalized despite large separation and large aperture
    assert_that(score.factors["splitability"]).is_less_than(0.7)
```

---

## UI Integration

```
┌─ Albireo (β Cygni) ──────────────────────────┐
│ Score: 95% (Excellent)                       │
│                                               │
│ Double Star Information:                      │
│ ├─ Separation: 34.4"                         │
│ ├─ Primary: mag 3.1 (golden)                 │
│ ├─ Secondary: mag 5.1 (blue)                 │
│ └─ Splitability: Easy ✅                     │
│                                               │
│ Your Equipment:                               │
│ ├─ 200mm aperture                            │
│ ├─ Dawes limit: 0.58"                        │
│ └─ Can split: 59x easier than limit          │
│                                               │
│ 💡 Beautiful color contrast - great target!  │
└───────────────────────────────────────────────┘
```

---

## Data Requirements

Double star data needed from Phase 8 (astronomical API):
- Separation (arcseconds)
- Position angle (degrees)
- Primary magnitude
- Secondary magnitude
- Color indices (optional, for visual interest)

**Catalog sources:**
- Washington Double Star Catalog (WDS)
- Simbad (includes WDS data)
- OpenNGC (some double star data)

---

## Future Enhancements

- **Seeing conditions integration**: Turbulence affects resolution
- **Multiple components**: Some systems have 3+ stars (Epsilon Lyrae double-double)
- **Orbital motion**: Show when separation changes over time
- **Color information**: Highlight colorful pairs (Albireo, Almach)

---

*Last Updated: 2026-02-10*
*Dependencies: Phase 8 (API integration) required*
*Status: Blocked - waiting for double star data*
