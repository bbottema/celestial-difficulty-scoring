# Astronomical Data APIs for an Amateur Observability Scoring System

## Scope and approach

Your scoring system needs a stable “object facts” layer (name/IDs, J2000 RA/Dec, integrated magnitude, angular size, and a type that’s more specific than “DeepSky”), plus an “ephemeris” layer for Solar System objects and per-night planning. Your current AstroPlanner → Excel pipeline supplies some of this, but you’re missing two big ingredients: (a) a type taxonomy that’s usable for instrument-aware scoring and (b) surface brightness or a reliable substitute.

This report evaluates the services you listed, adds a few that materially improve name resolution and offline resiliency, and verifies behavior on your test objects using published outputs and documentation.

Key constraints that shape the recommended design:

* **SIMBAD explicitly excludes Solar System bodies** (planets, satellites, comets, asteroids). citeturn12search8  
* **SIMBAD object types are multi-valued and literature-driven**; the “main” type can be surprising (for example, M 31 is shown as “Active Galaxy Nucleus”). citeturn14view0turn12search6  
* **OpenNGC is offline-friendly and has a DSO-oriented type code system** (e.g., `EmN`, `RfN`, `DrkN`, `OCl`, `GCl`, `PN`, `G`) with galaxy Hubble types and a galaxy surface-brightness field (B-band, within the 25 mag isophote). citeturn24view0turn23search2  
* **For double stars, the Washington Double Star Catalog (WDS) in VizieR is purpose-built** and supplies separation and position angle (plus magnitudes), at a scale far beyond what you would want to scrape from general-purpose object pages. citeturn0search8turn0search11  
* **For Solar System accuracy and “right now” values (RA/Dec, magnitude, angular size, illumination), JPL Horizons via astroquery is the most complete single interface**, and it exposes exactly the observing-planning fields you listed. citeturn28view0turn28view1  
* **For offline Solar System computation**, Skyfield is the modern library recommended over PyEphem by the PyEphem author, and it uses local ephemeris files (e.g., `de421.bsp`) in examples. citeturn27view1turn27view0  

## Field coverage matrix

The table below answers “can I get this field?” and (just as important) “is it a natural fit for this service?”

**Legend:** ✅ native field is available; ⚠️ possible but indirect / inconsistent / per-object; 🧮 compute; ❌ not provided / not in scope.

| Field | SIMBAD | OpenNGC (local CSV or VO mirror) | VizieR (WDS focus) | Skyfield | JPL Horizons (astroquery) | Notes |
|---|---|---|---|---|---|---|
| Name / identifier (Messier, NGC, IC, common) | ✅ (many identifiers) citeturn14view0 | ✅ (`name`, `messier_nr`, `comname`, `other_id`) citeturn22search3turn24view0 | ⚠️ depends on catalog; WDS uses WDS IDs & discoverer designations citeturn0search11 | ❌ | ✅ target names in output (`targetname`) citeturn28view0 | SIMBAD excels at cross-identifications; OpenNGC is strong for “DSO-style naming.” citeturn14view0turn24view0 |
| RA/Dec (J2000, decimal degrees) | ✅ (API supports RA(d)/Dec(d)) citeturn8view0turn12search2 | ✅ (`raj2000`, `dej2000` in degrees) citeturn22search3turn24view0 | ✅ (WDS includes J2000 coordinates) citeturn0search11 | ✅ (computed; output is time-dependent for moving bodies) citeturn27view0 | ✅ (`RA`, `DEC`, `RA_app`, `DEC_app`) citeturn28view0 | For DSOs, J2000 is stable; for Solar System, coordinates are time-dependent. citeturn28view0turn27view0 |
| Visual / integrated magnitude | ⚠️ (`flux(V)` exists; availability varies by object) citeturn8view0turn14view0 | ✅ (`mag_v`) citeturn22search3turn24view0 | ⚠️ WDS includes component magnitudes, not integrated DSO magnitude citeturn0search11 | ❌ (not a core Skyfield feature) | ✅ (`V` column in ephemerides) citeturn28view0 | SIMBAD magnitudes are heterogeneous, pulled from many sources. citeturn11search0 |
| Angular size (major/minor axes) | ⚠️ `dim_majaxis`/`dim_minaxis` exist when measured citeturn8view0turn14view0 | ✅ (`maj_ax_deg`, `min_ax_deg` + `pos_ang`) citeturn22search3turn24view0 | ❌ (WDS is stellar pairs) | 🧮 (can compute angular diameter from distance + physical radii if you supply them) | ✅ (`ang_width` present in ephemerides columns list) citeturn28view0 | DSO sizes can be wavelength-dependent; OpenNGC documents multiple provenance paths. citeturn23search2turn14view0 |
| **Surface brightness (mag/arcsec²)** | ❌ (no dedicated DSO SB field in the exposed VOTable field list) citeturn8view0turn12search2 | ⚠️ ✅ **for galaxies only** (`surf_br_B`, mean SB within 25 mag isophote in B-band) citeturn24view0turn23search2 | ❌ (WDS) | ❌ | ✅ (`surfbright` appears among ephemerides columns) citeturn28view0 | For DSOs, you’ll typically compute an “average SB” from magnitude + apparent area; galaxy-only SB from OpenNGC is a strong anchor but not universal. citeturn24view0turn23search2 |
| Object class / type | ✅ (hierarchical; multi-type) citeturn12search3turn13view0 | ✅ (compact type codes designed for DSOs) citeturn24view0 | ✅ for doubles (catalog-specific classification) citeturn0search11 | N/A | N/A | SIMBAD main type can be non-observing-centric (e.g., M31 shown as AGN). citeturn14view0 |
| Classification depth for galaxies (spiral/elliptical etc.) | ⚠️ morphology exists (`mt`, Hubble class string), mostly for galaxies citeturn14view0turn8view0 | ✅ `hubble_type` for galaxies citeturn24view0turn23search2 | ❌ | N/A | N/A | M31 morphology example: `SA(s)b`. citeturn14view0 |
| Cross-references (multi-catalog) | ✅ identifiers list is extensive citeturn14view0turn13view0 | ✅ `other_id`, `comname`, Messier cross-ref, duplicates fields citeturn24view0turn22search3 | ⚠️ per-catalog | ❌ | ⚠️ Solar System naming is different (IDs, designations) citeturn27view2 | OpenNGC includes explicit duplicate markers (`Dup`, `NonEx`) in its type system. citeturn24view0 |
| Double star separation / PA / component mags | ❌ (not the core output for SIMBAD object pages) | ❌ | ✅ (WDS provides pair measures at scale) citeturn0search11turn0search8 | ❌ | ❌ | Use WDS for Albireo/Mizar; SIMBAD confirms they are multiple systems but doesn’t replace WDS. citeturn18search6turn19view0 |
| Distance (pc/ly) | ⚠️ some objects have distance measurements tables (varies) citeturn13view0turn16search0 | ❌ in the core OpenNGC fields list citeturn24view0 | ⚠️ per-catalog | ❌ | ⚠️ distances are not typical ephemeris output (except via geometry you compute) | If you need distances, treat them as optional enrichment from SIMBAD measurement tables. citeturn8view0turn13view0 |
| Spectral type | ✅ (`sp` / spectral-type measurements exist) citeturn8view0turn12search2 | ❌ | ✅ for stars in some catalogs | ❌ | ❌ | SIMBAD is a strong star metadata source when you need SpT. citeturn8view0 |
| Redshift (galaxies) | ✅ (redshift/radial velocity fields exist) citeturn8view0turn14view0 | ✅ (`z`, `rv`) citeturn24view0turn23search2 | ⚠️ per-catalog | ❌ | ❌ | M51 example shows redshift output in SIMBAD. citeturn18search1 |
| Offline capable | ⚠️ cacheable results; service itself is online | ✅ | ⚠️ depends (you can mirror catalogs, but that’s separate work) | ✅ | ❌ (service) / ⚠️ you can cache results per night | OpenNGC + Skyfield are the cleanest “remote dark site” story. citeturn23search2turn27view0 |
| Rate limits / practical throttles | ✅ documented guidance: ≤6 queries/sec; higher can trigger temporary blacklist citeturn5search4turn2search0 | ✅ none (local) | ✅ varies by service; VizieR is designed for catalog access but rate limits depend on endpoint | ✅ none (local compute) | ✅ network/service dependent; output can be large unless you restrict quantities citeturn28view1 | Use batching and caching to avoid “one object = one HTTP call” patterns. citeturn5search2turn5search4 |

## Object classification depth and mapping for your test objects

The two biggest practical findings from the test objects:

* SIMBAD types are **multi-valued**, and the “headline” type is not always what an observer expects (M31 → “Active Galaxy Nucleus”; NGC 7000 → “Cluster of Stars”). citeturn14view0turn13view0  
* SIMBAD also provides “Other object types” that often contain the observing-relevant class you want (e.g., NGC 7000 includes `HII` among its other types). citeturn13view0  

image_group{"layout":"carousel","aspect_ratio":"16:9","query":["M31 Andromeda Galaxy widefield image","M42 Orion Nebula image","M57 Ring Nebula close-up image","Barnard 33 Horsehead Nebula image"],"num_per_query":1}

### Verified SIMBAD classification strings on the test set

Below are the exact “Basic data” type strings and the “Other object types” codes shown on SIMBAD pages for your specific targets.

**Deep sky**

* **M31**  
  * Basic data: **“Active Galaxy Nucleus”** citeturn14view0  
  * Other object types include: `G`, `AGN`, `QSO`, `IR`, `Rad`, … citeturn14view0  
  * Morphological type: `SA(s)b` citeturn14view0  
  Mapping implication: for scoring you likely want `galaxy.spiral` inferred from morphology, and treat AGN as an attribute, not the primary observing class. citeturn14view0  

* **M42**  
  * Basic data: **“HII Region”** citeturn29view1  
  * Other object types include: `HII`, `Rad`, `X`, `OpC`, `Cl*`, `Cl?` citeturn29view1  
  Mapping implication: `nebula.emission` (H II) with optional “contains cluster” hints (Trapezium region effect). citeturn29view1  

* **M13**  
  * Basic data: **“Globular Cluster”** citeturn29view0  
  * Other object types include: `GlC`, `Cl*`, `G` citeturn29view0  
  Mapping implication: clean `cluster.globular`. citeturn29view0  

* **M57**  
  * Basic data: **“Planetary Nebula”** citeturn29view2  
  * Other object types include: `PN`, plus stellar-related types (central star / white dwarf) citeturn29view2  
  Mapping implication: clean `nebula.planetary`, with optional “central star magnitude” as a separate field (OpenNGC explicitly models PN central star mags). citeturn23search2turn24view0  

* **NGC 7000**  
  * Basic data: **“Cluster of Stars”** citeturn13view0  
  * Other object types include: `HII` and `Rad` in addition to `Cl*` citeturn13view0  
  Mapping implication: you cannot trust *only* the SIMBAD main type; your mapper needs to inspect the full type set and prefer nebular classes (`HII`) over generic cluster classes when both exist. citeturn13view0  

* **NGC 869 / NGC 884**  
  * NGC 869 basic data: **“Open Cluster”** citeturn20view0  
  * NGC 884 basic data: **“Open Cluster”** citeturn17search2  
  Mapping implication: clean `cluster.open` for both. citeturn20view0turn17search2  

* **Barnard 33**  
  * Basic data: **“Dark Cloud (nebula)”** citeturn29view3  
  * Other object types include: `DNe` (dark nebula), plus cloud-related codes citeturn29view3  
  Mapping implication: `nebula.dark`. citeturn29view3  

* **M51 / NGC 5194**  
  * Basic data: **“Seyfert 2 Galaxy”** citeturn18search1turn18search4  
  * Morphological type shown: `SA` citeturn18search1  
  Mapping implication: `galaxy.spiral` is supported (SA → unbarred spiral family), but the subtype detail (b/c etc.) may be missing or uneven across objects. citeturn18search1  

**Double stars**

* **Albireo** basic data: **“Double or Multiple Star”** citeturn18search6  
* **Mizar** basic data: **“Double or Multiple Star”** citeturn19view0  

For scoring (split difficulty), you still need WDS separation and PA; SIMBAD is mainly useful here for name resolution and cross-IDs that include WDS identifiers. citeturn18search6turn19view0  

### OpenNGC’s object type system maps cleanly to your needs

OpenNGC’s published type codes directly encode many of your required distinctions: `G`, `OCl`, `GCl`, `PN`, `HII`, `DrkN`, `EmN`, `RfN`, `SNR`, plus “housekeeping” codes (`Dup`, `NonEx`, `Other`). citeturn24view0  

For galaxies, OpenNGC exposes a galaxy `hubble_type` field intended to carry morphological Hubble types. citeturn24view0turn22search3  

This means you can build a deterministic mapping layer like:

* `obj_type == 'G'` + `hubble_type` starts with `E` → `galaxy.elliptical`  
* `obj_type == 'G'` + `hubble_type` contains `S0` → `galaxy.lenticular`  
* `obj_type == 'G'` + `hubble_type` contains `SA`/`SB`/`SAB` → `galaxy.spiral` (optionally bar classification)  
* `obj_type == 'EmN'` or `HII` → `nebula.emission`  
* `obj_type == 'RfN'` → `nebula.reflection`  
* `obj_type == 'DrkN'` → `nebula.dark`  
* `obj_type == 'PN'` → `nebula.planetary`  
* `obj_type == 'OCl'` → `cluster.open`  
* `obj_type == 'GCl'` → `cluster.globular` citeturn24view0  

## Surface brightness strategy for scoring

### What you can obtain directly

* **OpenNGC provides `surf_br_B`** described as “Mean surface brightness within the 25 mag isophote (B-band); only given for galaxies.” citeturn24view0turn22search3  
  OpenNGC also documents that galaxy surface brightness (and morphology) comes from HyperLEDA when available. citeturn23search2  
  Practical implication: this is a high-quality SB signal for galaxies, but it does **not** solve nebulae/clusters SB. citeturn24view0turn23search2  

* **JPL Horizons ephemerides include `surfbright`** (surface brightness) among many available columns for Solar System bodies. citeturn28view0  
  Practical implication: this is useful for bright extended Solar System targets (e.g., Moon surface brightness varies with phase), but it does not cover DSOs. citeturn28view0  

* **SIMBAD’s exposed VOTable field list includes fluxes and dimensions, but not a DSO surface-brightness field.** citeturn8view0turn12search2  

### Computing an “average surface brightness” from magnitude and size

For DSOs, the most workable approach is to compute an **average** surface brightness from integrated magnitude and apparent area whenever you have both. Use an ellipse when you have major/minor axes:

\[
SB \approx m + 2.5 \log_{10}(A_{\text{arcsec}^2})
\]
where  
\[
A_{\text{arcsec}^2} = \pi \cdot \left(\frac{a}{2}\cdot 60\right)\cdot \left(\frac{b}{2}\cdot 60\right)
\]
and \(a,b\) are major/minor diameters in arcminutes.

This is “mean SB” over the ellipse. It is not equivalent to isophotal SB (like OpenNGC’s `surf_br_B`) and will differ for objects with bright cores and faint halos, strong gradients, or poorly defined “edges.” citeturn24view0turn23search2  

### Worked example using your test object M31

SIMBAD lists for M31:

* V magnitude: **3.44** citeturn14view0  
* Angular size: **199.53 × 70.79 arcmin** citeturn14view0  

Plugging these into the ellipse formula yields an average SB of ~**22.44 mag/arcsec²** (computed value). citeturn14view0  

Why this is “good enough” for scoring:

* The result lands in the expected faint-extended-object regime, and it appropriately penalizes very large objects with modest integrated magnitude (exactly your scoring need). citeturn14view0  
* Your score should treat this as an **uncertainty-bearing feature** (error bars), because input magnitudes/sizes are catalog- and wavelength-dependent. OpenNGC explicitly notes that galaxy axes can come from 2MASS IR measures when LEDA data is missing, which changes “visual” surface brightness meaning. citeturn23search2turn14view0  

Recommended SB rule set:

1. **If OpenNGC `surf_br_B` exists (galaxies): use it as SB_primary** and keep your computed SB as a fallback/comparison value. citeturn24view0turn23search2  
2. **Else compute SB from (`mag_v`, `maj_ax`, `min_ax`)** when those exist (OpenNGC often has these for many DSOs). citeturn24view0turn22search3  
3. **Else compute from SIMBAD `flux(V)` + dimensions** when present. citeturn8view0turn12search2  
4. **Else mark SB as unknown** and fall back to object-type heuristics (e.g., open clusters generally tolerate brighter skies than dark nebulae). citeturn24view0  

## Practical limits, batching, and reliability considerations

### SIMBAD query mechanics and throttling

* The astroquery SIMBAD interface supports `query_object` and `query_objects` (a list of object names), which directly addresses your “100 objects at once” requirement without doing one HTTP request per object. citeturn5search2turn15search12  
* SIMBAD’s published guidance (surfaced in astroquery docs) is **no more than ~6 queries per second**, and exceeding this may temporarily blacklist an IP. citeturn5search4turn2search0  
* SIMBAD describes itself as **dynamic and updated every working day**, reinforcing that online lookups can change (and that caching should store a “fetched_at” timestamp). citeturn11search0  

### OpenNGC update cadence and distribution options

* OpenNGC is licensed **CC-BY-SA-4.0** and intended to be “license friendly” compared to older NGC compilations. citeturn23search2turn23search1  
* The GAVO-published VO mirror of OpenNGC shows a concrete “Data updated” timestamp and a news log (e.g., updated to upstream commit on 2023‑12‑13). citeturn22search13turn24view0  
* Base catalog breadth: NGC has **7,840** objects and the Index Catalogues add **5,386**, which sets the floor at **13,226** NGC/IC entries. citeturn23search0  
* OpenNGC also ships an **addendum** of non-NGC/IC objects (including Messier objects without NGC/IC designations like M40/M45). citeturn23search2  

### VizieR and WDS practicality

* The WDS catalog in VizieR is very large (example snapshot: **157,263 rows** with a VizieR “last updated” date shown as 2025‑11‑20). citeturn0search11  
* WDS includes the fields you asked for (pair positional measures; component magnitudes), and is the right layer for “double star scoring.” citeturn0search11turn0search8  

### Solar System: Skyfield vs PyEphem vs Horizons

* PyEphem’s own documentation recommends **preferring Skyfield for new projects**, and calls out PyEphem’s unit handling as a source of confusion. citeturn27view1  
* Skyfield includes almanac routines for moon phases, risings/settings, twilight, etc., and examples load a local ephemeris file `de421.bsp`. citeturn27view0  
* Horizons via astroquery is explicitly designed to provide ephemerides, and the ephemerides output includes many planning fields including **RA/DEC, AZ/EL, V magnitude, illumination, angular width, surface brightness**, etc.; it also warns that querying most quantities “might take a while” and supports a `quantities` filter to limit output. citeturn28view0turn28view1  

## Recommended architecture, caching, and migration path

### Primary + fallback data flow

A version of your proposed strategy is sound; the main improvements are:

* Put **name resolution** up front (so every downstream step uses a canonical key).  
* Treat **OpenNGC as the primary DSO facts source** for NGC/IC/Messier-style DSOs because it is offline-capable and already encodes DSO-centric object types. citeturn24view0turn23search2  
* Use **SIMBAD for enrichment** (extra identifiers, morphology, star metadata) and for objects outside OpenNGC’s domain. citeturn11search0turn8view0  
* Use **WDS (VizieR) for double stars**. citeturn0search11turn0search8  
* Use **Horizons for online Solar System truth**, and **Skyfield for offline computation**. citeturn28view0turn27view0turn27view1  

Suggested decision tree:

*User input* → **Name resolution layer**  
→ if Solar System target → Horizons (online) / Skyfield (offline)  
→ else if looks like NGC/IC/M/“Caldwell-style” DSO → OpenNGC local  
→ else → SIMBAD  
→ if object is a double/multiple star and you want split difficulty → WDS lookup by resolved identifier or by coordinate match.

SIMBAD’s URL documentation explicitly highlights the CDS **Sesame name resolver** as a service, which is a good front-door name-to-position resolver before you decide which catalog to use. citeturn6view0  

### Caching strategy

**Cache “facts” aggressively; compute “events” per session.**

Good candidates to cache “forever” (refresh on catalog release):

* DSO fixed coordinates (J2000), sizes, type codes, cross-IDs from OpenNGC. citeturn24view0turn23search2  
* SIMBAD-resolved identifier sets for objects you’ve already used (to avoid repeat name resolution calls). M31’s page shows dozens of identifiers, illustrating the benefit of caching a cleaned identifier set. citeturn14view0  

Cache with a time-to-live:

* SIMBAD measurements that may update (e.g., redshift compilation, parallax, literature-driven attributes). SIMBAD updates every working day. citeturn11search0turn8view0  
* WDS records: separation/PA can change over time for many systems, so store “fetched_at” and refresh periodically (e.g., monthly). citeturn0search11  

Do not cache as “truth”:

* Solar System RA/Dec, angular size, magnitude for “tonight.” Compute each session (Skyfield offline) or fetch (Horizons online). citeturn27view0turn28view0  

### Cross-reference resolution: verified scenarios

These are verified directly from SIMBAD’s identifier lists (good evidence that SIMBAD is strong for “what other names does this have?”).

* “M31” resolves to “NGC 224”: NGC 224 appears in M31’s identifiers list. citeturn14view0  
* “Andromeda” resolves to M31: M31 identifiers include “NAME Andromeda” and “NAME Andromeda Galaxy.” citeturn14view0  
* “NGC 7000” resolves to “North America Nebula”: NGC 7000 identifiers include “NAME North America Nebula.” citeturn13view0  
* SIMBAD’s user guide shows the “NAME …” convention (e.g., `NAME ALTAIR`) and flexible parsing of identifiers like `m31`. citeturn12search4  

### Migration path from AstroPlanner Excel exports

A low-risk transition plan keeps your current workflow working while progressively replacing columns with API-backed values.

1. **Define your internal canonical schema** (SQLite is fine): `canonical_id`, `ra_deg`, `dec_deg`, `obj_class`, `subclass`, `mag_v`, `maj_arcmin`, `min_arcmin`, `sb_est`, `sb_source`, `ids[]`, `sources[]`, `fetched_at`, `precision_flags`.  
2. **Import AstroPlanner rows as “observing list items,” not as authoritative facts**, storing the original text name and any AstroPlanner-provided magnitude/size.  
3. For each imported row, run **name resolution** (Sesame/SIMBAD) and store:
   * canonical SIMBAD identifier (or OpenNGC `name` when you have it),
   * coordinate,  
   * a normalized set of cross-IDs (Messier/NGC/IC/common). citeturn14view0turn13view0turn12search4  
4. Fill facts in priority order:
   * OpenNGC local lookup when the object matches NGC/IC/Messier (preferred offline backbone). citeturn24view0turn23search2  
   * SIMBAD enrichment for morphology, extra IDs, star spectral types, and to reconcile ambiguous cases like NGC 7000’s “main type vs other types.” citeturn13view0turn8view0  
   * WDS lookup when the object is a double star for separation/PA/mags. citeturn0search11turn18search6turn19view0  
5. Compute `sb_est` and mark provenance:
   * `sb_source='openngc_surf_br_B'` for galaxies when present. citeturn24view0  
   * `sb_source='computed_mag_size'` otherwise.  
6. Keep a “diff view” during development: compare (AstroPlanner mag/size/type) vs (OpenNGC/SIMBAD) and log conflicts; SIMBAD notes that by construction it is inhomogeneous because it compiles literature values. citeturn11search0  

## Code examples that match the proposed architecture

### Install dependencies

```bash
pip install astroquery astropy pyvo pandas skyfield
```

### OpenNGC local backbone (CSV → DataFrame → normalized units)

OpenNGC’s CSV is semicolon-delimited in common usage examples. citeturn23search9  

```python
import pandas as pd
from pathlib import Path

def load_openngc_csv(path: Path) -> pd.DataFrame:
    # Typical OpenNGC column order is documented externally; keep a stable internal schema.
    # The VO mirror defines field meanings (raj2000/dej2000 in degrees, maj/min axes in degrees).
    df = pd.read_csv(path, sep=';', dtype=str).fillna('')

    # Normalize numeric fields where present
    for col in ['raj2000', 'dej2000', 'maj_ax_deg', 'min_ax_deg', 'mag_v', 'mag_b']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # Convert axes: degrees -> arcmin
    if 'maj_ax_deg' in df.columns:
        df['maj_arcmin'] = df['maj_ax_deg'] * 60.0
    if 'min_ax_deg' in df.columns:
        df['min_arcmin'] = df['min_ax_deg'] * 60.0

    return df

# usage:
# openngc = load_openngc_csv(Path("OpenNGC.csv"))
# row = openngc.loc[openngc["messier_nr"] == 31].iloc[0]
```

Field semantics (including `surf_br_B` galaxy-only SB and `hubble_type`) are explicitly documented in the OpenNGC VO table metadata. citeturn24view0turn22search3  

### SIMBAD enrichment (astroquery)

SIMBAD’s astroquery interface supports adding VOTable fields and querying lists. citeturn5search2turn5search4  

```python
from astroquery.simbad import Simbad

def simbad_enrich(names: list[str]):
    simbad = Simbad()
    simbad.ROW_LIMIT = len(names)

    # Commonly useful for your scoring:
    # - otype: main type
    # - dim: major/minor axis when available
    # - morphtype: galaxy morphology when available
    # - flux(V): V magnitude
    simbad.add_votable_fields("otype", "dim", "morphtype", "flux(V)")

    tbl = simbad.query_objects(names)
    return tbl  # astropy Table

# usage:
# tbl = simbad_enrich(["M31", "NGC 7000", "M57", "Albireo"])
```

If you implement your own URL-level SIMBAD calls or scripts, the field names for VOTable output include `flux(V)`, `dim_majaxis`, `dim_minaxis`, `mt` (morphological type), and `ids` for identifier lists. citeturn8view0turn12search2  

### WDS double-star data (VizieR via astroquery.vizier)

VizieR hosts the WDS table at catalog `B/wds/wds`, and it includes separation and position angle fields plus magnitudes. citeturn0search11turn0search8  

```python
from astroquery.vizier import Vizier
from astropy.coordinates import SkyCoord
import astropy.units as u

def query_wds_near(ra_deg: float, dec_deg: float, radius_arcmin: float = 5.0):
    v = Vizier(
        # choose columns matching your scoring
        columns=["WDS", "Comp", "RAJ2000", "DEJ2000", "mag1", "mag2", "sep1", "pa1"]
    )
    coord = SkyCoord(ra_deg * u.deg, dec_deg * u.deg, frame="icrs")
    res = v.query_region(coord, radius=radius_arcmin * u.arcmin, catalog="B/wds/wds")
    return res

# usage:
# Albireo is near RA~292.6803 deg, Dec~27.9597 deg if you resolve via SIMBAD first.
# res = query_wds_near(292.6803, 27.9597, radius_arcmin=10)
```

### Solar System “tonight” values via Horizons (online)

Horizons ephemerides include `RA`, `DEC`, `AZ`, `EL`, `V` magnitude, `illumination`, `ang_width`, and many more; use `quantities` to keep responses small and fast. citeturn28view0turn28view1  

```python
from astroquery.jplhorizons import Horizons

def horizons_ephemeris(body: str, location: str, start: str, stop: str, step: str = "10m"):
    obj = Horizons(
        id=body,
        location=location,
        epochs={"start": start, "stop": stop, "step": step},
    )
    eph = obj.ephemerides(
        # quantities codes are Horizons-defined; use small sets for speed
        quantities="1,9,10,13"  # example: RA/Dec + Airmass/Illum/etc depending on Horizons quantity mapping
    )
    return eph

# usage:
# location="568" is Mauna Kea in Horizons examples; use your observer code or geodetic dict.
# eph = horizons_ephemeris("Jupiter", location="568", start="2026-02-11", stop="2026-02-12", step="30m")
```

### Solar System offline computation via Skyfield (local ephemeris)

Skyfield almanac examples demonstrate loading a local ephemeris file (`de421.bsp`) and computing Moon phases and rise/set style events. citeturn27view0  

```python
from skyfield.api import load, wgs84
from skyfield import almanac

def skyfield_moon_phase(ephemeris_path: str, lat: float, lon: float, date_utc_tuple):
    ts = load.timescale()
    eph = load(ephemeris_path)     # e.g. "de421.bsp"
    t0 = ts.utc(*date_utc_tuple)   # (year, month, day, hour, minute)
    f = almanac.moon_phase(eph, t0)
    return float(f.degrees)

# usage:
# phase_deg = skyfield_moon_phase("de421.bsp", lat=52.37, lon=4.90, date_utc_tuple=(2026, 2, 11, 20, 0))
```

## Gotchas and warnings that affect scoring quality

* **SIMBAD is not a homogeneous catalog**; it is a literature-driven compilation and explicitly warns about inhomogeneity. citeturn11search0  
  Practical scoring impact: magnitude, size, and even “main type” can be inconsistent across objects (NGC 7000 being a prime example). citeturn13view0  

* **Main object type vs “other object types” matters.**  
  M31 is shown as “Active Galaxy Nucleus,” yet includes `G` and a spiral morphology string; NGC 7000 is shown as “Cluster of Stars” yet includes `HII`. citeturn14view0turn13view0  
  Practical scoring impact: your classifier must look beyond a single field.

* **Surface brightness is not a single universal definition across catalogs.**  
  OpenNGC’s galaxy SB is “mean SB within 25 mag isophote (B-band).” Your computed SB from integrated magnitude and an apparent area is a different concept, best treated as “average SB estimate.” citeturn24view0turn23search2  

* **Solar System is outside SIMBAD’s scope.** citeturn12search8  
  Practical scoring impact: keep Solar System handling in a dedicated module (Horizons/Skyfield).

* **Horizons output size can be heavy unless constrained.**  
  Astroquery’s Horizons docs note default ephemerides queries ask for most quantities and “might take a while,” and provide a `quantities` option. citeturn28view1  

## Bottom-line answers to your success criteria

✅ **Can you get all must-have fields for the test objects?**  
Yes, with a split approach:
* DSOs: OpenNGC + SIMBAD provide names/IDs, J2000 coordinates, magnitudes, sizes, and types. citeturn24view0turn23search2turn8view0  
* Doubles: WDS gives separation/PA/component mags. citeturn0search11turn0search8  
* Solar System: Horizons provides RA/Dec, magnitude, angular width, illumination, etc.; Skyfield covers offline computation. citeturn28view0turn27view0turn27view1  

✅ **Is classification detailed enough for intelligent scoring?**  
Yes, if you implement a mapper that:
* uses OpenNGC’s DSO type codes when available, citeturn24view0  
* otherwise uses SIMBAD’s multi-type set plus galaxy morphology (`mt`) rather than trusting “main type” alone. citeturn12search6turn14view0turn13view0  

✅ **Can you calculate/obtain surface brightness reliably?**  
* For galaxies, OpenNGC provides a direct SB field (`surf_br_B`). citeturn24view0turn23search2  
* For nebulae/clusters, you will primarily compute an average SB from magnitude and size when available; treat this as an approximate scoring feature. citeturn8view0turn12search2turn23search2  

✅ **Offline fallback when internet is unavailable?**  
OpenNGC local + Skyfield local ephemeris files provide a functional offline core. citeturn23search2turn27view0turn27view1  

✅ **Recommended architecture (primary + backups)?**  
Primary DSO facts: OpenNGC local.  
Enrichment/name resolution: SIMBAD (+ Sesame as resolver front door). citeturn6view0turn11search0  
Double stars: WDS (VizieR). citeturn0search11  
Solar System: Horizons online, Skyfield offline. citeturn28view0turn27view0  

✅ **Showstoppers?**  
No single showstopper, but there are two design-critical realities:
* SIMBAD “headline type” is not reliable enough alone (M31, NGC 7000). citeturn14view0turn13view0  
* Surface brightness for non-galaxy DSOs will often be computed/estimated, not directly cataloged. citeturn24view0turn8view0