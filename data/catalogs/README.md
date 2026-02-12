# Catalog Data Sources

This directory contains astronomical catalog data used by the application.

---

## OpenNGC Catalog

**Source:** https://github.com/mattiaverga/OpenNGC
**License:** CC-BY-SA-4.0
**Files:**
- `NGC.csv` - Main catalog (13,970 NGC/IC objects)
- `addendum.csv` - Non-NGC/IC objects (64 objects)
- `NGC_test.csv` - Test subset for unit tests

### What is OpenNGC?

OpenNGC is a license-friendly database of **NGC (New General Catalogue)** and **IC (Index Catalogue)** objects compiled from multiple sources. It provides:

- Clean object type codes (G=Galaxy, OCl=Open Cluster, GCl=Globular Cluster, PN=Planetary Nebula, etc.)
- Accurate positions (RA/Dec J2000)
- Photometric data (V-mag, B-mag, J/H/K magnitudes)
- Physical properties (size, surface brightness, Hubble type for galaxies)
- Cross-references to other catalogs
- Messier number mappings

### Understanding the Catalog Structure

**IMPORTANT:** OpenNGC is specifically an **NGC + IC catalog**. This means:

✅ **Included in NGC.csv:**
- All NGC objects (NGC 1 - NGC 7840)
- All IC objects (IC 1 - IC 5386)
- Cross-referenced Messier objects that have NGC/IC numbers (e.g., M31 = NGC 224)

❌ **NOT included in NGC.csv:**
- Objects without NGC/IC designations
- Objects known only by other catalog names (Melotte, Collinder, Barnard, etc.)

### The Addendum File

**File:** `addendum.csv`
**Purpose:** Contains famous astronomical objects that don't have NGC or IC numbers

**Why does this exist?**

Some of the most famous objects in amateur astronomy were never assigned NGC or IC numbers:

1. **M45 (Pleiades)** - Known as Melotte 22, no NGC/IC number
2. **M40 (Winnecke 4)** - A double star, no NGC/IC number
3. **Caldwell objects** - Patrick Moore's catalog, many lack NGC/IC numbers
4. **Named objects** - Horsehead Nebula (B033), Large Magellanic Cloud (ESO 056-115)

**Historical Context:**

The New General Catalogue was published in 1888 by John Dreyer. Some objects were:
- Already well-known by other names (like Pleiades)
- Not considered "nebulous" enough for inclusion
- Discovered or catalogued differently

The addendum ensures these popular objects are still available in OpenNGC.

### Discovery Story: M45 Pleiades

**Problem:** During Phase 5 validation, M45 (Pleiades) was not found in the catalog.

**Initial assumption:** "M45 is missing from OpenNGC" ❌

**Investigation:**
1. Searched GitHub issues: [Issue #16](https://github.com/mattiaverga/OpenNGC/issues/16)
2. Found maintainer's response: "M45 and M40 don't have any NGC or IC designation, so they're listed only in the **addendum**"
3. Key insight: OpenNGC is an NGC/IC catalog by definition - objects without NGC/IC numbers belong in the addendum

**Lesson:** When an object seems "missing," first understand **what the catalog is supposed to contain**. Don't assume data is incomplete without investigating the catalog's scope.

**Resolution:**
- Updated `scripts/download_openngc.py` to fetch both NGC.csv and addendum.csv
- Modified `OpenNGCProvider` to load addendum automatically
- Fixed case-sensitivity bug (addendum uses mixed case like "Mel022")

### Addendum Contents (64 objects)

**Messier Objects without NGC/IC:**
- M40 (Winnecke 4) - Double star
- M45 (Pleiades / Melotte 22) - Famous open cluster

**Caldwell Objects:**
- C009 (SH 2-155, Cave Nebula)
- C014 (h & chi Persei, Double Cluster)
- C041 (Hyades)
- C099 (Coalsack Nebula)
- And more...

**Named Deep-Sky Objects:**
- B033 (Horsehead Nebula)
- ESO056-115 (Large Magellanic Cloud)
- ESO097-013 (Circinus Galaxy)
- And more...

### Technical Implementation

**Loading Process (in OpenNGCProvider):**

```python
# Load main NGC/IC catalog
self.df = self._load_csv(csv_path)

# Load addendum (M40, M45, Caldwell objects, named DSOs)
addendum_path = csv_path.parent / 'addendum.csv'
if addendum_path.exists():
    addendum_df = self._load_csv(addendum_path)
    self.df = pd.concat([self.df, addendum_df], ignore_index=True)
```

**Name Resolution:**

The addendum uses different naming conventions:
- Main catalog: `NGC0224` (uppercase, zero-padded)
- Addendum: `Mel022`, `B033`, `C009` (mixed case)

The provider handles both:
1. Try exact case match first (for addendum)
2. Fall back to uppercase match (for NGC/IC)

### CSV Format

Both NGC.csv and addendum.csv use the same format:

**Columns (32 total):**
- Name, Type, RA, Dec, Const (constellation)
- MajAx, MinAx, PosAng (size and position angle)
- B-Mag, V-Mag, J-Mag, H-Mag, K-Mag (photometry)
- SurfBr (surface brightness, mag/arcsec²)
- Hubble (morphological type for galaxies)
- M (Messier number, 3 digits: 031 for M31)
- NGC, IC (cross-references)
- Identifiers, Common names

**Example - M45 Pleiades (from addendum.csv):**
```
Name: Mel022
Type: OCl (Open Cluster)
RA: 03:47:28.6
Dec: +24:06:19
M: 045
V-Mag: 1.20
MajAx: 150.00 (arcmin - about 2.5 degrees!)
Common names: Pleiades
```

---

## Updating the Catalog

**To download/update:**

```bash
pipenv run python scripts/download_openngc.py
```

This will:
1. Download the latest NGC.csv from OpenNGC GitHub
2. Download the latest addendum.csv
3. Report object counts and file sizes

**Update frequency:**
- OpenNGC is updated periodically with corrections and new measurements
- Check the [OpenNGC releases page](https://github.com/mattiaverga/OpenNGC/releases) for updates
- Recommend updating every 6-12 months

---

## Data Provenance

All objects retrieved from OpenNGC include `DataProvenance` tracking:

```python
provenance = DataProvenance(
    source=CatalogSource.OPENNGC,
    confidence=1.0,  # High confidence for published catalog data
    retrieved_at=datetime.now(timezone.utc)
)
```

This allows the application to track which provider supplied each piece of data.

---

## Testing

**Unit tests:** `tests/catalog/test_openngc_provider.py`
- Uses `NGC_test.csv` (small subset for fast tests)
- Tests name resolution (M31 → NGC0224)
- Tests data parsing and coordinate conversion

**Integration validation:** Phase 5 validation scripts
- Validates against Messier 110, Caldwell 109, Herschel 400
- Ensures addendum objects (M40, M45) are retrievable
- Cross-checks data quality (magnitude, size, surface brightness)

---

## References

- **OpenNGC Repository:** https://github.com/mattiaverga/OpenNGC
- **Original NGC:** Dreyer, J. L. E. (1888). "A New General Catalogue of Nebulae and Clusters of Stars"
- **IC Catalogs:** Dreyer (1895, 1908) Index Catalogues I and II
- **Messier Catalog:** Charles Messier (1771-1781)
- **Caldwell Catalog:** Patrick Moore (1995)

---

*Last Updated: 2026-02-12*
*Catalog Version: OpenNGC 20210306*
