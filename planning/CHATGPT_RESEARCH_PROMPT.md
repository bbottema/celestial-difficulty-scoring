# ChatGPT Deep Research Prompt - Phase 8 API Investigation

Copy and paste this into ChatGPT-5.2 Deep Research:

---

I'm building a celestial object observability scoring system for amateur astronomy in Python. Currently using Excel exports from AstroPlanner, but need to integrate real astronomical catalog APIs.

## Research Mission

Comprehensively evaluate astronomical data APIs to determine:
1. Which APIs provide the data fields we need
2. Object classification depth/granularity available
3. Catalog breadth (how many objects)
4. Practical limitations (rate limits, offline capability, reliability)
5. Recommended architecture (primary source + fallbacks)

## Required Data Fields

**Must Have (Critical for Scoring):**
- Object name/identifier (Messier, NGC, IC, common names)
- RA/Dec coordinates (J2000, decimal degrees)
- Visual/integrated magnitude
- Angular size (arcminutes, ideally both major/minor axes)
- Object type/classification

**High Priority (Impacts Scoring Accuracy):**
- Surface brightness (mag/arcsec²) - **CRITICAL for faint objects**
- Object classification detail (see below)
- Multiple catalog cross-references

**Nice to Have:**
- Distance (light years or parsecs)
- Spectral type
- Double star: separation (arcseconds), position angle, secondary magnitude
- Redshift (for galaxies)

## Object Classification Requirements

**Current Problem:** AstroPlanner gives generic "DeepSky" - too vague!

**What We Need for Intelligent Scoring:**

Must distinguish between:
- **Galaxies:** spiral, elliptical, irregular, lenticular
- **Nebulae:** emission, reflection, dark, planetary
- **Clusters:** globular, open
- **Stars:** single, double/multiple, variable
- **Solar System:** planets, moon, sun, asteroids, comets

**Why This Matters:**
- Emission nebulae benefit from narrowband filters (H-alpha, OIII)
- Spiral galaxies need aperture for detail
- Planetary nebulae need high magnification
- Open clusters need wide field of view
- Dark nebulae need extreme dark skies

## APIs to Evaluate

### 1. SIMBAD Astronomical Database
- **URL:** http://simbad.u-strasbg.fr/simbad/
- **Python:** `astroquery.simbad`
- **Test:** Query M31, NGC 7000, M57, Albireo
- **Questions:**
  - What fields are returned?
  - How detailed is object classification?
  - Is surface brightness available?
  - What are actual rate limits (documented: 6/sec, 30/min)?
  - Can we query in batch?
  - How reliable is the service?

### 2. OpenNGC (Local Catalog)
- **URL:** https://github.com/mattiaverga/OpenNGC
- **Format:** CSV/JSON downloadable database
- **Questions:**
  - How many objects total?
  - What fields are included?
  - Is surface brightness included?
  - What object classifications are used?
  - How are cross-references handled (NGC vs IC vs Messier)?
  - Last update date? Update frequency?

### 3. VizieR Catalog Access
- **URL:** https://vizier.cds.unistra.fr/
- **Python:** `astroquery.vizier`
- **Focus:** Double star data (Washington Double Star Catalog)
- **Questions:**
  - Can we get separation, position angle, magnitudes for both stars?
  - How many double stars available?
  - What other specialized catalogs are useful?

### 4. Skyfield / PyEphem (Solar System)
- **Skyfield:** https://rhodesmill.org/skyfield/
- **PyEphem:** https://rhodesmill.org/pyephem/
- **Questions:**
  - Can we get real-time RA/Dec for planets?
  - Moon phase calculation accuracy?
  - Angular diameter for planets?
  - Sun position for solar observation planning?
  - Which is better maintained/recommended?

### 5. Other Services to Consider
- NASA/JPL Horizons (solar system ephemeris)
- STScI MAST (professional data, may be overkill)
- CDS Portal
- Any other astronomy APIs you discover

## Test Objects (Must Verify All Work)

**Deep Sky:**
1. M31 (Andromeda Galaxy) - bright, large spiral galaxy
2. M42 (Orion Nebula) - bright emission nebula
3. M13 (Hercules Cluster) - bright globular cluster
4. M57 (Ring Nebula) - planetary nebula
5. NGC 7000 (North America Nebula) - large, faint emission nebula
6. NGC 869/884 (Double Cluster) - open cluster pair
7. Barnard 33 (Horsehead Nebula) - dark nebula
8. M51 (Whirlpool Galaxy) - spiral galaxy with companion

**Double Stars:**
9. Albireo (Beta Cygni) - famous yellow/blue double
10. Mizar (Zeta UMa) - naked eye double in Big Dipper

**Solar System:**
11. Jupiter - current position, magnitude, angular size
12. Saturn - rings visible? current position
13. Moon - phase, position for tonight
14. Sun - position (for solar filter safety checks)

## Specific Research Tasks

### Task 1: Field Coverage Matrix
Create a comparison table:

| Field | SIMBAD | OpenNGC | VizieR | Skyfield | Notes |
|-------|--------|---------|--------|----------|-------|
| Name/ID | ? | ? | ? | ? | |
| RA/Dec | ? | ? | ? | ? | |
| Magnitude | ? | ? | ? | ? | |
| Size | ? | ? | ? | ? | Both axes? |
| Surface Brightness | ? | ? | ? | N/A | **CRITICAL** |
| Object Class | ? | ? | ? | N/A | How detailed? |
| Double Star Sep | ? | N/A | ? | N/A | |
| Cross-refs | ? | ? | ? | N/A | |
| Total Objects | ? | ? | ? | 9 | |
| Offline Capable | No | Yes | No | Yes | |
| Rate Limits | ? | No | ? | No | |

### Task 2: Surface Brightness Deep Dive

**This is CRITICAL - we must have this!**

Surface brightness (mag/arcsec²) determines if faint extended objects are visible.

1. Check if ANY API provides it directly
2. If not available, can we calculate it?
   - Formula: `SB ≈ magnitude + 2.5 * log10(π * (size/2)²)`
   - Test calculation vs known values (M31 SB ≈ 22.2 mag/arcsec²)
3. Validate calculation accuracy for test objects
4. Determine if calculated SB is "good enough" for scoring

### Task 3: Object Classification Mapping

**Test these specific objects and document exact classification strings returned:**

1. M31 - What classification? ("spiral galaxy" vs "galaxy" vs "SAB(s)bc"?)
2. M42 - "emission nebula" vs "nebula" vs "HII region"?
3. M57 - "planetary nebula" specific?
4. NGC 7000 - How is "emission nebula" classified?
5. Barnard 33 - "dark nebula" vs "nebula"?
6. M13 - "globular cluster" vs "cluster"?
7. NGC 869 - "open cluster" specific?

**Question:** Can we map their classification strings to our needs?

Example:
```
SIMBAD: "Em*" → We need: "emission_nebula"
SIMBAD: "Galaxy" → We need: "spiral_galaxy" or "elliptical_galaxy"
```

### Task 4: Practical Testing

**Real-world validation:**

1. **Batch Queries:** Can we query 100 objects at once? How long does it take?
2. **Rate Limits:** Test SIMBAD with rapid queries - what happens?
3. **Reliability:** Check service status pages, documented downtime
4. **Offline Fallback:** How much can we cache locally?
5. **Update Frequency:** How often do catalogs change? (solar system daily, deep sky rarely)

### Task 5: Cross-Reference Resolution

**Test these scenarios:**

1. User enters "M31" - can we resolve to NGC 224?
2. User enters "Andromeda" - can we find M31?
3. User enters "NGC 7000" - can we find "North America Nebula"?
4. Which API is best for name resolution?

## Architecture Recommendations Needed

Based on your findings, recommend:

### Primary Data Source
- Which API should be our main source and why?
- Pros/cons analysis

### Fallback Strategy
```
User queries "M31"
  ↓
1. Check local cache (SQLite) - instant
  ↓
2. Check embedded catalog (OpenNGC) - if offline
  ↓
3. Query online API (SIMBAD) - if internet available
  ↓
4. Cache result for future
```

Does this strategy make sense? Better alternatives?

### Caching Strategy
- What should we cache locally?
- How often to refresh cache?
- What's safe to cache forever (deep sky coords don't change much)?
- What must be real-time (solar system positions)?

### Solar System Handling
- Use Skyfield or PyEphem or JPL Horizons?
- Download ephemeris files or API calls?
- How to handle planets, moon, sun differently?

## Deliverables

Please provide:

1. **Field Coverage Matrix** (filled out with real test results)
2. **Object Classification Mapping Table** (what we get vs what we need)
3. **Surface Brightness Analysis** (available? calculable? accurate enough?)
4. **Recommended Architecture** (primary + fallbacks + caching)
5. **Code Examples** (sample queries that work)
6. **Gotchas/Warnings** (rate limits, reliability issues, missing data)
7. **Migration Path** (how to transition from AstroPlanner Excel to APIs)

## Success Criteria

Research is complete when we can answer:

✅ Can we get all required fields for our test objects?
✅ Is object classification detailed enough for intelligent scoring?
✅ Can we calculate/obtain surface brightness reliably?
✅ What's our offline fallback when internet is unavailable?
✅ What's the recommended architecture (primary + backups)?
✅ Are there any showstoppers (missing critical data, unreliable services)?

## Context: Why This Matters

**Current State:**
- Importing 150-200 objects from AstroPlanner Excel exports
- Generic "DeepSky" type means we can't apply smart scoring
- No surface brightness = visibility estimates are wrong
- Manual workflow = stale data

**Future State:**
- Automatic catalog lookup for any object
- Smart filter recommendations based on object type
- Accurate visibility predictions using surface brightness
- Real-time solar system positions
- Up-to-date data always

This research **unblocks 4 major features:**
- Phase 7: Object-type-aware scoring
- Phase 9: Filter effectiveness (needs object classification)
- Phase 10: Imaging mode (needs precise coordinates)
- Phase 11: Astrophotography planning (needs ephemeris)

**Take your time, be thorough, test everything. This is foundational work.**

---

## Additional Notes

- Focus on **free/open-source** solutions (this is an open-source project)
- **Offline capability** is important (some users observe at remote dark sites)
- **Reliability** matters (users plan observing sessions, can't have API failures)
- **Simplicity** for most common objects (M31, M42, etc. should "just work")
- **Completeness** for edge cases (obscure NGC objects, faint targets)

If you find better alternatives not listed above, absolutely include them!

Thank you! 🔭
