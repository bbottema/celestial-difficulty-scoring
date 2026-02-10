# Phase 8: Astronomical API Integration

**Status:** NOT STARTED
**Priority:** 🔴 CRITICAL - Unblocks multiple future phases
**Dependencies:** None (can start immediately)

**Blocks:** Phase 6 (double stars), Phase 7 (object types), Phase 9-11 (filters/imaging)

---

## Goal

Replace AstroPlanner Excel exports with proper astronomical catalog APIs to provide rich, accurate, up-to-date object data.

---

## Problem Statement

**Current Data Source (AstroPlanner Excel):**
- ❌ Limited object types ("DeepSky" is too generic)
- ❌ No detailed classification (galaxy type, nebula type, cluster type)
- ❌ No surface brightness data (critical for visibility)
- ❌ No double star separation data
- ❌ Manual export/import workflow
- ❌ Data staleness (catalogs update, exports don't)
- ❌ No solar system ephemeris (positions change daily)

**Impact on other phases:**
- Phase 6 blocked (no double star data)
- Phase 7 blocked (no object classification)
- Phase 9 blocked (can't determine filter effectiveness without object type)
- Phase 10 blocked (can't calculate imaging windows without RA/Dec)

---

## Proposed API Integration Options

### Option 1: Simbad Astronomical Database
**URL:** http://simbad.u-strasbg.fr/simbad/

**Pros:**
- ✅ Comprehensive professional-grade database
- ✅ Free API access
- ✅ Object classification, coordinates, magnitudes, sizes, references
- ✅ Cross-references to other catalogs

**Cons:**
- ❌ Rate limits (6 requests/second, 30 requests/minute)
- ❌ Requires internet connection
- ❌ API downtime possible

**Example Query:**
```python
from astroquery.simbad import Simbad

# Query M31
result = Simbad.query_object("M31")
# Returns: RA, Dec, magnitude, object type, classifications, etc.
```

---

### Option 2: OpenNGC (Open New General Catalogue)
**URL:** https://github.com/mattiaverga/OpenNGC

**Pros:**
- ✅ Open source, can be embedded locally
- ✅ No API limits (local database)
- ✅ No internet required
- ✅ NGC/IC objects with detailed classifications
- ✅ Surface brightness data included

**Cons:**
- ❌ Deep-sky only (no solar system)
- ❌ Requires periodic manual updates
- ❌ Smaller catalog than Simbad (~13,000 objects)

**Example Usage:**
```python
import csv

# Load OpenNGC database (local CSV file)
with open('NGC.csv') as f:
    reader = csv.DictReader(f)
    for row in reader:
        if row['Name'] == 'NGC 7000':
            print(row['Type'])  # 'Nebula'
            print(row['Mag'])   # '4.0'
            print(row['SurfBr']) # Surface brightness
```

---

### Option 3: Hybrid Approach ⭐ RECOMMENDED

**Architecture:**
```
User requests object data
    ↓
1. Check local cache (fast)
    ↓
2. Check embedded catalogs (OpenNGC, Messier, Caldwell)
    ↓
3. Fallback to Simbad online API (slow but comprehensive)
    ↓
4. Cache result locally for future use
```

**Benefits:**
- ✅ Fast offline access for common objects
- ✅ Comprehensive coverage via Simbad fallback
- ✅ Graceful degradation (works without internet)
- ✅ Automatic cache updates

**Solar System Ephemeris:**
Use **Skyfield** or **PyEphem** for planetary positions:
```python
from skyfield.api import load

# Load ephemeris data (downloaded once, cached)
planets = load('de421.bsp')

# Calculate Jupiter position for date/time
earth = planets['earth']
jupiter = planets['jupiter barycenter']
astrometric = earth.at(time).observe(jupiter)
ra, dec, distance = astrometric.radec()
```

---

## Implementation Tasks

### 1. API Integration Layer

**Directory Structure:**
```
src/app/data/astronomical_catalogs/
├── catalog_service.py         # Unified interface
├── simbad_client.py           # Online API client
├── local_catalog.py           # Embedded OpenNGC/Messier
├── cache_manager.py           # Local cache (SQLite)
└── solar_system_ephemeris.py  # Planetary positions
```

---

### 2. Catalog Service (Unified Interface)

**File:** `src/app/data/astronomical_catalogs/catalog_service.py`

```python
from typing import Optional
from dataclasses import dataclass

@dataclass
class CatalogObject:
    """Rich object data from astronomical catalogs"""
    name: str
    aliases: list[str]  # ["M31", "NGC 224", "Andromeda"]
    ra: float           # decimal degrees (J2000)
    dec: float
    magnitude: float
    size_major: float   # arcminutes
    size_minor: Optional[float]
    object_type: str    # "DeepSky", "Planet", etc.
    object_classification: Optional[str]  # "spiral_galaxy", "planetary_nebula"
    surface_brightness: Optional[float]   # mag/arcsec²
    catalog_ids: dict[str, str]  # {"NGC": "224", "Messier": "31"}
    # Double star data
    separation: Optional[float]  # arcseconds
    position_angle: Optional[float]  # degrees
    magnitude_secondary: Optional[float]


class CatalogService:
    """
    Unified interface for querying astronomical catalogs.
    """

    def __init__(self):
        self.cache = CacheManager()
        self.local_catalog = LocalCatalog()
        self.simbad_client = SimbadClient()

    def get_object(self, name: str) -> Optional[CatalogObject]:
        """
        Query object data with fallback chain:
        1. Cache
        2. Local catalog (OpenNGC, Messier)
        3. Simbad API
        """
        # Check cache first
        cached = self.cache.get(name)
        if cached:
            return cached

        # Check local catalog
        local = self.local_catalog.query(name)
        if local:
            self.cache.set(name, local)
            return local

        # Fallback to Simbad (requires internet)
        try:
            simbad = self.simbad_client.query(name)
            if simbad:
                self.cache.set(name, simbad)
                return simbad
        except Exception as e:
            logger.warning(f"Simbad query failed for {name}: {e}")

        return None

    def enrich_object(self, celestial_object: CelestialObject) -> CelestialObject:
        """
        Enrich existing CelestialObject with catalog data.
        """
        catalog_data = self.get_object(celestial_object.name)

        if catalog_data:
            # Merge catalog data into object
            celestial_object.object_classification = catalog_data.object_classification
            celestial_object.surface_brightness = catalog_data.surface_brightness
            celestial_object.separation = catalog_data.separation
            # ... etc

        return celestial_object
```

---

### 3. Enhanced CelestialObject Model

**File:** `src/app/domain/model/celestial_object.py`

```python
@dataclass
class CelestialObject:
    name: str
    object_type: str                          # Keep for compatibility
    object_classification: Optional[str] = None  # NEW: "spiral_galaxy"
    magnitude: float
    surface_brightness: Optional[float] = None   # NEW: mag/arcsec²
    size: float
    size_minor_axis: Optional[float] = None      # NEW: for elongated objects
    altitude: float
    ra: Optional[float] = None                   # NEW: decimal degrees (J2000)
    dec: Optional[float] = None                  # NEW: decimal degrees
    catalog_ids: Optional[dict[str, str]] = None # NEW: {"NGC": "7000"}
    # Double star data
    separation: Optional[float] = None           # NEW: arcseconds
    position_angle: Optional[float] = None       # NEW: degrees
    magnitude_secondary: Optional[float] = None  # NEW: secondary magnitude
```

---

### 4. Data Migration Strategy

**Backward Compatibility:**
- Keep AstroPlanner import for existing users
- Add "Enrich from Catalog" button in UI
- New objects default to catalog lookup
- Cache enriched data to avoid repeated API calls

**Migration UI:**
```
┌─ Object Manager ─────────────────────────────┐
│                                               │
│ 📋 Objects: 150 imported from AstroPlanner   │
│                                               │
│ [Enrich All from Catalogs]                   │
│                                               │
│ ┌─────────────────────────────────────────┐  │
│ │ M31 - Andromeda  ✅ Enriched            │  │
│ │ M42 - Orion      ⏳ Enriching...        │  │
│ │ M51 - Whirlpool  ❌ Not found           │  │
│ └─────────────────────────────────────────┘  │
│                                               │
│ Progress: 45/150 (30%)                        │
└───────────────────────────────────────────────┘
```

---

### 5. Solar System Ephemeris

**File:** `src/app/data/astronomical_catalogs/solar_system_ephemeris.py`

```python
from skyfield.api import load
from datetime import datetime

class SolarSystemEphemeris:
    """
    Calculate real-time positions for planets, Sun, Moon.
    """

    def __init__(self):
        self.planets = load('de421.bsp')  # JPL ephemeris
        self.earth = self.planets['earth']

    def get_position(self, body_name: str, date: datetime, location) -> tuple[float, float]:
        """
        Get RA/Dec for solar system body at given date/location.
        """
        body = self.planets[body_name]
        time = load.timescale().from_datetime(date)

        astrometric = self.earth.at(time).observe(body)
        ra, dec, distance = astrometric.radec()

        return ra.degrees, dec.degrees

    def get_sun_position(self, date, location):
        return self.get_position('sun', date, location)

    def get_moon_position(self, date, location):
        return self.get_position('moon', date, location)

    def get_jupiter_position(self, date, location):
        return self.get_position('jupiter barycenter', date, location)
```

---

## Benefits Unlocked

Once Phase 8 is complete, the following phases can proceed:

| Phase | Benefit | Impact |
|-------|---------|--------|
| **Phase 6** | Double star separation data | Can score splitability |
| **Phase 7** | Object classification | 15-25% accuracy improvement |
| **Phase 9** | Object types for filter recommendations | Show "H-alpha for M42" |
| **Phase 10** | RA/Dec for imaging window calculations | Calculate integration time |
| **All** | Surface brightness data | More accurate visibility scoring |
| **All** | Real-time solar system positions | No manual updates needed |

---

## Testing

### Test 1: Catalog Service Fallback Chain
```python
def test_catalog_service_tries_cache_then_local_then_simbad():
    """Should try cache → local → Simbad in order"""
    service = CatalogService()

    # First call: miss cache, hit local
    m31 = service.get_object("M31")
    assert_that(m31.object_classification).is_equal_to("spiral_galaxy")

    # Second call: hit cache (no Simbad query)
    m31_cached = service.get_object("M31")
    assert_that(m31_cached).is_equal_to(m31)
```

### Test 2: Graceful Degradation Without Internet
```python
def test_works_offline_with_local_catalog():
    """Should work without internet using local catalogs"""
    service = CatalogService()

    # Disconnect internet (mock)
    service.simbad_client.enabled = False

    # Common objects should still work
    m42 = service.get_object("M42")
    assert_that(m42).is_not_none()

    # Obscure objects will return None (graceful failure)
    obscure = service.get_object("NGC 99999")
    assert_that(obscure).is_none()
```

### Test 3: Solar System Ephemeris Accuracy
```python
def test_jupiter_position_accurate():
    """Jupiter position should match JPL Horizons within 1 arcminute"""
    ephemeris = SolarSystemEphemeris()

    ra, dec = ephemeris.get_jupiter_position(
        date=datetime(2026, 2, 10, 21, 0, 0),
        location=(40.0, -80.0)
    )

    # Compare with known JPL Horizons data (±1')
    expected_ra = 124.5  # degrees
    expected_dec = 21.3  # degrees

    assert_that(ra).is_close_to(expected_ra, 1/60)  # 1 arcminute tolerance
    assert_that(dec).is_close_to(expected_dec, 1/60)
```

---

## Dependencies & Installation

```bash
# Simbad queries
pip install astroquery

# Solar system ephemeris
pip install skyfield

# OpenNGC (download CSV files)
git clone https://github.com/mattiaverga/OpenNGC.git
```

---

## Open Questions

1. **How often to update local catalogs?**
   - **Recommendation:** Check for updates monthly, notify user

2. **Should we cache failed queries?**
   - **Recommendation:** Yes, cache negative results for 24 hours to avoid repeated failed queries

3. **What to do with objects not found in any catalog?**
   - **Recommendation:** Allow manual entry, mark as "User Defined"

4. **How to handle catalog discrepancies?**
   - **Example:** Simbad says mag 8.0, OpenNGC says mag 8.5
   - **Recommendation:** Prefer Simbad (more recent), show data source in UI

---

## Future Enhancements

- **Phase 8.1: Catalog Update Notifications** - Alert user when new catalog versions available
- **Phase 8.2: Multi-Catalog Comparison** - Show data from multiple sources side-by-side
- **Phase 8.3: Community Corrections** - Allow users to report incorrect data

---

## References

- Simbad API: http://simbad.u-strasbg.fr/simbad/sim-help?Page=sim-url
- OpenNGC: https://github.com/mattiaverga/OpenNGC
- Skyfield: https://rhodesmill.org/skyfield/
- JPL Horizons: https://ssd.jpl.nasa.gov/horizons/

---

*Last Updated: 2026-02-10*
*Dependencies: None - can start immediately*
*Priority: CRITICAL - Unblocks phases 6, 7, 9, 10, 11*
*Estimated Effort: 2-3 weeks*
