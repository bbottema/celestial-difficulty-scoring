# Phase 8 Research Plan: API Data Discovery

**Goal:** Determine the best astronomical data APIs and validate they provide the fields we need for scoring.

---

## Critical Questions to Answer

### 1. Field Coverage Validation

**Must Have:**
- Name/Identifier (Messier, NGC, IC, common names)
- RA/Dec (J2000 coordinates)
- Magnitude (visual/integrated)
- Angular size (arcminutes)
- Object type/classification

**Nice to Have:**
- Surface brightness (mag/arcsec²)
- Secondary size (minor axis for elliptical objects)
- Double star separation + position angle
- Spectral type
- Distance
- Multiple catalog cross-references

**Test Objects:**
We need to verify these are available:
- M31 (Andromeda Galaxy) - spiral galaxy, large extended
- M42 (Orion Nebula) - emission nebula
- M13 (Hercules Cluster) - globular cluster
- NGC 7000 (North America Nebula) - large emission nebula
- Albireo (Beta Cygni) - famous double star
- Ring Nebula (M57) - planetary nebula
- Horsehead Nebula (Barnard 33) - dark nebula
- Jupiter, Saturn, Mars - planets (ephemeris)

### 2. Object Type Classification Depth

**Current (AstroPlanner):**
```
object_type = "DeepSky"  # Too generic!
```

**Needed for Phase 7 (Object-Type-Aware Scoring):**
```
object_classification = "emission_nebula"     # Needs narrowband filters
object_classification = "spiral_galaxy"       # Benefits from aperture
object_classification = "globular_cluster"    # Needs high magnification
object_classification = "planetary_nebula"    # Small, high surface brightness
object_classification = "open_cluster"        # Needs wide field
object_classification = "dark_nebula"         # Needs extreme dark skies
object_classification = "reflection_nebula"   # Different from emission
```

**Question:** Can we get this level of detail from APIs?

### 3. Catalog Breadth/Coverage

**AstroPlanner has access to:**
- Messier (110 objects)
- Caldwell (109 objects)
- NGC (~7,840 objects)
- IC (~5,386 objects)
- Herschel 400
- SAC (Saguaro Astronomy Club) lists
- Double star catalogs

**Question:** Can free APIs match this breadth?

---

## Research Tasks

### Task 1: Test Simbad Coverage (Online API)

**Action Items:**
1. Test query for sample objects (M31, NGC 7000, Albireo, etc.)
2. Check what fields are returned
3. Verify object classification granularity
4. Test rate limits in practice
5. Check if surface brightness is available

**Tools:**
- `astroquery.simbad` Python library
- Web interface: http://simbad.u-strasbg.fr/simbad/

**Expected Output:** CSV/JSON of returned fields for test objects

---

### Task 2: Evaluate OpenNGC (Local Catalog)

**Action Items:**
1. Download OpenNGC database: https://github.com/mattiaverga/OpenNGC
2. Count total objects
3. List available fields
4. Check object type classifications
5. Verify surface brightness availability
6. Check for cross-references to other catalogs

**Expected Output:** Field list + object count + sample data

---

### Task 3: Test Skyfield/PyEphem for Solar System

**Action Items:**
1. Install Skyfield or PyEphem
2. Calculate Jupiter position for tonight
3. Verify we can get: RA, Dec, magnitude, angular diameter
4. Check Moon phase calculation
5. Test Sun position for solar filter safety checks

**Expected Output:** Sample ephemeris data for Jupiter/Moon/Sun

---

### Task 4: Check VizieR for Double Stars

**Action Items:**
1. Query VizieR for Albireo (famous double star)
2. Check if we get separation, position angle, magnitudes
3. Verify coverage of Washington Double Star Catalog (WDS)
4. Test query limits

**Tools:**
- `astroquery.vizier` Python library
- Web: https://vizier.cds.unistra.fr/

**Expected Output:** Double star fields available

---

### Task 5: Surface Brightness Investigation

**Critical for faint object visibility!**

**Action Items:**
1. Check if Simbad provides surface brightness
2. Check OpenNGC for surface brightness field
3. If not available: Can we calculate it from size + magnitude?
   - Formula: `SB = mag + 2.5 * log10(size²)` (approximate)
4. Test calculation accuracy vs known values

**Expected Output:** Surface brightness availability or calculation method

---

## Research Deliverables

### Document 1: API Comparison Matrix

```markdown
| Field               | Simbad | OpenNGC | VizieR | Skyfield |
|---------------------|--------|---------|--------|----------|
| Name/ID             | ✅     | ✅      | ✅     | ✅       |
| RA/Dec              | ✅     | ✅      | ✅     | ✅       |
| Magnitude           | ✅     | ✅      | ✅     | ✅       |
| Size                | ✅     | ✅      | ✅     | ✅       |
| Surface Brightness  | ?      | ?       | ?      | N/A      |
| Classification      | ?      | ?       | N/A    | N/A      |
| Double Star Sep     | ?      | N/A     | ✅     | N/A      |
| Object Count        | ~11M   | ~13K    | Varies | 9        |
| Offline?            | ❌     | ✅      | ❌     | ✅       |
| Rate Limits         | Yes    | No      | Yes    | No       |
```

### Document 2: Object Classification Mapping

Map what classification strings we get vs what we need:

```markdown
**Simbad Returns:**
- "Galaxy"
- "EmissionNeb"
- "PlanetaryNeb"
- etc.

**We Need:**
- "spiral_galaxy", "elliptical_galaxy", "irregular_galaxy"
- "emission_nebula", "reflection_nebula", "dark_nebula"
- "planetary_nebula"
- "globular_cluster", "open_cluster"
- "double_star", "variable_star"
```

### Document 3: Recommended Architecture

Based on findings, recommend:
1. Primary data source (Simbad vs OpenNGC vs hybrid)
2. Fallback strategy
3. Caching approach
4. Fields we can get vs fields we must calculate/estimate
5. Migration path from AstroPlanner data

---

## Research Tools/Methods

### Option A: I Can Research (Limited)

**My Capabilities:**
- ✅ Can use WebSearch for recent information
- ✅ Can use WebFetch to read API documentation
- ✅ Can write test scripts to probe APIs
- ⚠️ Limited to one-shot queries (can't iterate deeply)

**Limitations:**
- ❌ Can't install/test Python packages interactively
- ❌ Can't make iterative API calls to refine queries
- ❌ Can't browse interactive catalogs

### Option B: ChatGPT Deep Research (Recommended)

**Your Suggestion:**
Use ChatGPT-5.2 deep research to:
1. Comprehensively test multiple APIs
2. Compare field coverage across services
3. Test rate limits and query patterns
4. Validate object classification schemes
5. Research best practices from astronomy community

**Prompt for ChatGPT-5.2:**
```
I'm building an observability scoring system for amateur astronomy. I need to
integrate astronomical catalog APIs to replace Excel imports.

Research and compare:
1. Simbad API - field coverage, classification depth, rate limits
2. OpenNGC - local catalog breadth, field availability
3. VizieR - double star data availability
4. Skyfield/PyEphem - solar system ephemeris capabilities

For each, test these objects: M31, M42, M57, NGC 7000, Albireo, Jupiter

Required fields: RA/Dec, magnitude, size, object classification
Nice to have: surface brightness, double star separation

Deliverable: Comparison table + recommended architecture
```

### Option C: Hybrid Approach

**Split Work:**
1. **You + ChatGPT Deep Research:**
   - Comprehensive API testing
   - Field coverage validation
   - Object classification mapping
   - Rate limit testing

2. **Me (Claude):**
   - Design caching architecture
   - Plan data migration from AstroPlanner
   - Design CelestialObject model enhancements
   - Write integration code once we know what APIs provide

---

## Next Steps

**Your Decision:**

1. **I can start basic research now:**
   - Use WebFetch to read Simbad/OpenNGC docs
   - Use WebSearch for recent API comparison articles
   - Draft architecture based on documented capabilities

2. **You handle deep research with ChatGPT-5.2:**
   - Comprehensive API testing
   - Field validation with real queries
   - Performance/limit testing
   - Provide findings back to me

3. **Hybrid:**
   - I start with documentation review
   - You validate with ChatGPT deep research
   - We merge findings

**What would you prefer?**
