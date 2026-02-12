 # Phase 8: API Integration - Implementation Guide

**Status:** Skeleton complete, ready for implementation
**Estimated:** 3-4 days

---

## File Structure

```
domain/model/
├── object_classification.py  ✅ Complete
└── data_provenance.py        ✅ Complete

catalog/
├── interfaces.py              🔨 Stubbed
├── catalog_service.py         🔨 Stubbed (decision tree logic in comments)
├── catalog_repository.py      🔨 Stubbed (cache + DB entities)
├── classification_mapper.py   🔨 Stubbed (type corrections + SB calculator)
└── providers/
    ├── openngc_provider.py    🔨 Stubbed (offline CSV)
    ├── simbad_provider.py     🔨 Stubbed (online API + rate limiting)
    └── horizons_provider.py   🔨 Stubbed (Solar System ephemeris)
```

🔨 = All methods raise `NotImplementedError` with detailed TODO comments

---

## Implementation Order (3-4 days)

**Day 1:** OpenNGC + SIMBAD providers (CSV loading, type mapping, adapters)
**Day 2:** CatalogService + CatalogRepository (decision trees, cache, DB migration)
**Day 3:** Classification mapper + integration tests
**Day 4:** Legacy adapter + cleanup (buffer)

---

## Key Research Findings

**Data Sources:**
- OpenNGC (primary DSO) → SIMBAD (enrichment) → WDS (doubles) → Horizons (Solar System)

**CRITICAL:** SIMBAD main type unreliable (M31→"AGN", NGC 7000→"Cluster")
- **Fix:** Check `other_types` field FIRST

**Cache TTL:** OpenNGC 1yr, SIMBAD 1wk, WDS 1mo, Horizons never

**Dependencies:**
```bash
pip install astroquery astropy pandas skyfield pyvo
```

---

**Full research:** `PHASE_8_RESEARCH_CONCLUSION.md` + `phase-8_research-result.md`
**Code = Documentation:** All implementation logic in inline TODO comments
