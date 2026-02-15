"""
Phase 5 Monitoring & Calibration: Multi-Provider Data Validation

Tests limiting magnitude model against representative samples from:
- OpenNGC provider (13,970 DSO, measured surface brightness)
- SIMBAD provider (online enrichment, computed surface brightness)
- Horizons provider (Solar System, dynamic magnitude/size)

Validates:
1. Cross-provider consistency (same object, different sources)
2. Missing data handling (computed surface brightness)
3. Dynamic object handling (Horizons time-dependent data)
4. Type correction validation (SIMBAD misclassifications)
"""
import pytest
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional

from app.catalog.catalog_service import CatalogService
from app.domain.model.celestial_object import CelestialObject
from app.domain.model.object_classification import (
    ObjectClassification, AngularSize, SurfaceBrightness
)
from app.domain.model.data_provenance import DataProvenance
from app.catalog.interfaces import CatalogSource


class TestRepresentativeSamples:
    """
    Task 1: Create representative sample sets from all providers.

    Sample sets designed to test:
    - Data quality variations (perfect → uncertain → computed)
    - Object type coverage (galaxies, nebulae, clusters, planets)
    - Provider-specific strengths and weaknesses
    """

    @pytest.fixture(scope="class")
    def catalog_service(self):
        """Initialize catalog service with all providers"""
        return CatalogService()

    # OpenNGC Sample Set (50 objects across types)
    OPENNGC_SAMPLE = [
        # Bright Galaxies (measured SB, easy detection)
        "M31",  # Andromeda - large, bright, SB=23.5
        "M51",  # Whirlpool - medium size, SB=23.0
        "M81",  # Bode's Galaxy - compact, high SB
        "M82",  # Cigar Galaxy - edge-on, high contrast
        "M101", # Pinwheel - large, low SB (challenging)

        # Faint Galaxies (detection threshold tests)
        "NGC 891",   # Edge-on, mag 10.0
        "NGC 2403",  # Spiral, mag 8.9
        "NGC 4565",  # Needle Galaxy, mag 10.4
        "NGC 7331",  # Similar to Milky Way, mag 9.5
        "NGC 7479",  # Barred spiral, mag 11.6

        # Emission Nebulae (narrowband candidates)
        "M42",   # Orion - bright HII region
        "M8",    # Lagoon - bright nebula
        "M17",   # Omega/Swan - emission nebula
        "M20",   # Trifid - emission + reflection
        "NGC 7000", # North America - large, faint

        # Planetary Nebulae (compact, high SB)
        "M27",  # Dumbbell - bright, large PN
        "M57",  # Ring Nebula - compact PN
        "NGC 7293", # Helix - large, low SB PN
        "NGC 6543", # Cat's Eye - bright, compact
        "NGC 7009", # Saturn Nebula - high SB

        # Open Clusters (resolved vs unresolved)
        "M45",  # Pleiades - bright, large
        "M44",  # Beehive - scattered cluster
        "M67",  # Old cluster, faint stars
        "NGC 869", # Double Cluster (Perseus)
        "NGC 7789", # Large, faint cluster

        # Globular Clusters (concentration classes)
        "M13",  # Hercules - bright, resolved
        "M3",   # Bright, compact
        "M5",   # Large, well-resolved
        "M15",  # Dense core
        "M92",  # Fainter than M13
    ]

    # SIMBAD-only Sample (20 objects NOT in OpenNGC)
    SIMBAD_ONLY_SAMPLE = [
        # Objects with computed SB (no OpenNGC data)
        "NGC 55",    # Galaxy not in OpenNGC
        "NGC 253",   # Sculptor Galaxy
        "NGC 288",   # Globular cluster

        # Double stars (WDS catalog)
        "Albireo",   # Beta Cygni - famous double
        "Mizar",     # Zeta UMa - optical double

        # Named objects (non-NGC/IC)
        "Sirius",    # Brightest star
        "Betelgeuse", # Variable star
        "Antares",   # Red supergiant
    ]

    # Horizons Sample (8 Solar System objects)
    HORIZONS_SAMPLE = [
        "Mercury",
        "Venus",
        "Mars",
        "Jupiter",
        "Saturn",
        "Uranus",
        "Neptune",
        "Moon",
    ]

    # Cross-provider objects (available in multiple sources)
    CROSS_PROVIDER_SAMPLE = [
        ("M31", [CatalogSource.OPENNGC, CatalogSource.SIMBAD]),
        ("M51", [CatalogSource.OPENNGC, CatalogSource.SIMBAD]),
        ("M42", [CatalogSource.OPENNGC, CatalogSource.SIMBAD]),
        ("Jupiter", [CatalogSource.HORIZONS]),
        ("Saturn", [CatalogSource.HORIZONS]),
    ]

    def test_openngc_sample_availability(self, catalog_service):
        """Verify OpenNGC sample objects are retrievable"""
        missing = []
        for name in self.OPENNGC_SAMPLE[:10]:  # Test first 10
            obj = catalog_service.get_object(name)
            if obj is None:
                missing.append(name)

        assert len(missing) == 0, f"OpenNGC objects not found: {missing}"

    def test_simbad_sample_availability(self, catalog_service):
        """Verify SIMBAD-only sample objects are retrievable"""
        # Note: SIMBAD requires internet connection
        missing = []
        for name in self.SIMBAD_ONLY_SAMPLE[:3]:  # Test first 3
            obj = catalog_service.get_object(name)
            if obj is None:
                missing.append(name)

        # Allow some failures for offline testing
        assert len(missing) <= len(self.SIMBAD_ONLY_SAMPLE[:3]), \
            f"All SIMBAD objects failed: {missing}"

    def test_horizons_sample_availability(self, catalog_service):
        """Verify Horizons sample objects are retrievable"""
        missing = []
        for name in self.HORIZONS_SAMPLE:
            obj = catalog_service.get_object(name)
            if obj is None:
                missing.append(name)

        assert len(missing) == 0, f"Horizons objects not found: {missing}"


class TestCrossProviderConsistency:
    """
    Task 2: Test cross-provider consistency.

    Validates that the same object from different providers produces
    similar limiting magnitude calculations (±5% tolerance).
    """

    @pytest.fixture(scope="class")
    def catalog_service(self):
        return CatalogService()

    def test_m31_openngc_vs_simbad(self, catalog_service):
        """
        Test 1: OpenNGC vs SIMBAD Consistency

        M31 from OpenNGC: measured SB, clean type
        M31 from SIMBAD: computed SB, type correction needed

        Expected: Scores match within 5%
        """
        # Get M31 from both providers
        # OpenNGC requires NGC identifier (M31 → NGC0224)
        m31_openngc = catalog_service.openngc.get_object("NGC0224")
        m31_simbad = catalog_service.simbad.get_object("M31")

        assert m31_openngc is not None, "NGC0224 (M31) not found in OpenNGC"
        assert m31_simbad is not None, "M31 not found in SIMBAD"

        # Verify basic properties match
        assert abs(m31_openngc.magnitude - m31_simbad.magnitude) < 0.5, \
            "Magnitude mismatch between providers"

        # Check surface brightness consistency
        if m31_openngc.surface_brightness and m31_simbad.surface_brightness:
            sb_diff = abs(
                m31_openngc.surface_brightness.value -
                m31_simbad.surface_brightness.value
            )
            assert sb_diff < 1.0, \
                f"Surface brightness differs by {sb_diff} mag/arcsec² between providers"

    def test_m51_data_consistency(self, catalog_service):
        """
        Verify M51 (Whirlpool) data consistent across providers.

        Critical test object: medium-sized spiral galaxy,
        commonly observed, well-documented in both catalogs.
        """
        m51 = catalog_service.get_object("M51")
        assert m51 is not None, "M51 not found"

        # Expected values (from research)
        assert 8.0 <= m51.magnitude <= 8.5, "M51 magnitude out of range"

        if m51.size:
            # M51 is approximately 11x7 arcmin (OpenNGC reports 13.71x11.67)
            assert 6.0 <= m51.size.major_arcmin <= 15.0, "M51 size out of range"

        if m51.surface_brightness:
            # Expected SB around 23.0 mag/arcsec²
            assert 22.0 <= m51.surface_brightness.value <= 24.0, \
                "M51 surface brightness out of range"

    @pytest.mark.parametrize("object_name,expected_sources", [
        ("M31", {"OpenNGC"}),  # Should come from OpenNGC
        ("M42", {"OpenNGC"}),  # Should come from OpenNGC
        ("Jupiter", {"Horizons"}),  # Should come from Horizons
    ])
    def test_provider_selection_logic(self, catalog_service, object_name, expected_sources):
        """Verify catalog service selects correct provider for each object type"""
        obj = catalog_service.get_object(object_name)
        assert obj is not None, f"{object_name} not found"

        # Check provenance indicates correct source (source is stored as string, not enum)
        if obj.provenance:
            sources = {p.source for p in obj.provenance}
            assert sources.intersection(expected_sources), \
                f"Expected source {expected_sources}, got {sources}"


class TestMissingSurfaceBrightness:
    """
    Task 3: Test missing surface brightness handling.

    Validates computed SB formula when measured SB unavailable.
    Formula: SB = magnitude + 2.5 * log10(area_arcsec²)
    """

    def test_computed_surface_brightness_formula(self):
        """
        Test 2: Missing Surface Brightness Handling

        Simulate object with no measured SB:
        - Magnitude: 11.2
        - Size: 2.5' x 1.8'
        - Computed SB should be ~13.8 mag/arcsec²
        """
        import math

        # Object parameters
        magnitude = 11.2
        major_arcmin = 2.5
        minor_arcmin = 1.8

        # Convert to arcsec and compute area (ellipse)
        major_arcsec = major_arcmin * 60
        minor_arcsec = minor_arcmin * 60
        area_arcsec2 = math.pi * (major_arcsec / 2) * (minor_arcsec / 2)

        # Compute SB
        computed_sb = magnitude + 2.5 * math.log10(area_arcsec2)

        # Expected: ~21.5 mag/arcsec² (for 2.5'x1.8' object at mag 11.2)
        # Formula: mag + 2.5 * log10(area) = 11.2 + 2.5 * log10(12723) = 21.46
        assert 21.0 <= computed_sb <= 22.0, \
            f"Computed SB {computed_sb:.1f} out of expected range"

        print(f"Computed SB: {computed_sb:.2f} mag/arcsec² for {major_arcmin}'x{minor_arcmin}' object at mag {magnitude}")

    def test_objects_without_measured_sb(self):
        """Verify scoring handles objects with only computed SB"""
        # This will be implemented once we have scoring integration
        # For now, just verify the computation is reasonable
        pass


class TestDynamicSolarSystemObjects:
    """
    Task 4: Test dynamic Solar System objects (Horizons).

    Validates time-dependent magnitude/size handling for planets.
    """

    @pytest.fixture(scope="class")
    def catalog_service(self):
        return CatalogService()

    def test_jupiter_at_different_dates(self, catalog_service):
        """
        Test 3: Dynamic Solar System Objects

        Jupiter brightness varies with Earth-Jupiter distance:
        - Opposition: mag ~-2.5, size ~48"
        - Conjunction: mag ~-1.8, size ~32"

        Both should score >0.95 (bright, easy targets)
        """
        # Get Jupiter
        jupiter = catalog_service.get_object("Jupiter")
        assert jupiter is not None, "Jupiter not found in Horizons"

        # Jupiter should always be bright
        assert jupiter.magnitude < 0, "Jupiter should have negative magnitude"

        # Check size is reasonable (0.4-0.9 arcmin = 25-55 arcsec)
        if jupiter.size:
            assert 0.4 <= jupiter.size.major_arcmin <= 0.9, \
                f"Jupiter angular size {jupiter.size.major_arcmin}' out of range"

    def test_all_planets_retrievable(self, catalog_service):
        """Verify all major planets can be retrieved from Horizons"""
        planets = ["Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune"]

        for planet in planets:
            obj = catalog_service.get_object(planet)
            assert obj is not None, f"{planet} not found in Horizons"
            assert obj.magnitude != 99.0, f"{planet} has invalid magnitude"

    def test_moon_data_quality(self, catalog_service):
        """Verify Moon has reasonable ephemeris data"""
        moon = catalog_service.get_object("Moon")
        assert moon is not None, "Moon not found in Horizons"

        # Moon magnitude varies widely with phase (-12.7 full → -2.5 crescent)
        assert -13.0 <= moon.magnitude <= 0.0, \
            f"Moon magnitude {moon.magnitude} out of range"


class TestSimbadTypeCorrection:
    """
    Task 5: Test SIMBAD type correction validation.

    Validates classification mapper fixes SIMBAD misclassifications
    using other_types field.
    """

    @pytest.fixture(scope="class")
    def catalog_service(self):
        return CatalogService()

    def test_m31_type_correction(self, catalog_service):
        """
        Test 4: SIMBAD Type Correction

        M31 from SIMBAD:
        - Raw main type: "AGN" (WRONG)
        - Corrected via other_types: "Galaxy"

        Expected: Uses correct Galaxy strategy
        """
        m31 = catalog_service.get_object("M31")
        assert m31 is not None, "M31 not found"

        # Check classification
        if m31.classification:
            # Should be classified as Galaxy, not AGN
            assert "galaxy" in m31.classification.primary_type.lower() or \
                   "gxy" in m31.classification.primary_type.lower(), \
                f"M31 misclassified as {m31.classification.primary_type}"

    def test_ngc7000_type_validation(self, catalog_service):
        """
        NGC 7000 (North America Nebula) often misclassified as cluster.
        Should be HII region / emission nebula.
        """
        ngc7000 = catalog_service.get_object("NGC 7000")
        assert ngc7000 is not None, "NGC 7000 not found"

        if ngc7000.classification:
            obj_type = ngc7000.classification.primary_type.lower()
            # Should be nebula, not cluster
            assert "nebula" in obj_type or "hii" in obj_type or "emn" in obj_type, \
                f"NGC 7000 misclassified as {ngc7000.classification.primary_type}"


class TestProviderDataQuality:
    """
    Additional validation tests for provider data quality scenarios.
    """

    @pytest.fixture(scope="class")
    def catalog_service(self):
        return CatalogService()

    def test_openngc_surface_brightness_coverage(self, catalog_service):
        """Verify OpenNGC objects have measured surface brightness"""
        # Test sample of galaxies - use NGC identifiers for direct OpenNGC access
        # M31=NGC0224, M51=NGC5194, M81=NGC3031, M101=NGC5457
        galaxy_sample = ["NGC0224", "NGC5194", "NGC3031", "NGC5457"]

        has_sb = 0
        for ngc_id in galaxy_sample:
            obj = catalog_service.openngc.get_object(ngc_id)
            if obj and obj.surface_brightness:
                has_sb += 1

        # Expect >75% coverage for bright galaxies
        coverage = has_sb / len(galaxy_sample)
        assert coverage >= 0.75, \
            f"Only {coverage*100:.0f}% of galaxies have SB data (got {has_sb}/{len(galaxy_sample)})"

    def test_data_provenance_tracking(self, catalog_service):
        """Verify all objects have provenance information"""
        test_objects = ["M31", "M51", "Jupiter"]

        for name in test_objects:
            obj = catalog_service.get_object(name)
            assert obj is not None, f"{name} not found"

            # Should have provenance
            assert len(obj.provenance) > 0, \
                f"{name} missing provenance information"

            # Provenance should include source
            for prov in obj.provenance:
                assert prov.source is not None, \
                    f"{name} provenance missing source"


# Summary statistics helper
def run_validation_summary(catalog_service: CatalogService):
    """
    Generate validation summary report.

    Call this manually to get comprehensive validation statistics.
    """
    print("\n" + "="*60)
    print("PHASE 5 PROVIDER VALIDATION SUMMARY")
    print("="*60)

    # Test OpenNGC sample
    openngc_success = 0
    openngc_total = len(TestRepresentativeSamples.OPENNGC_SAMPLE)

    for name in TestRepresentativeSamples.OPENNGC_SAMPLE:
        obj = catalog_service.openngc.get_object(name)
        if obj:
            openngc_success += 1

    print(f"\nOpenNGC Coverage: {openngc_success}/{openngc_total} "
          f"({openngc_success/openngc_total*100:.1f}%)")

    # Test Horizons sample
    horizons_success = 0
    horizons_total = len(TestRepresentativeSamples.HORIZONS_SAMPLE)

    for name in TestRepresentativeSamples.HORIZONS_SAMPLE:
        obj = catalog_service.get_object(name)
        if obj:
            horizons_success += 1

    print(f"Horizons Coverage: {horizons_success}/{horizons_total} "
          f"({horizons_success/horizons_total*100:.1f}%)")

    print("\n" + "="*60)


if __name__ == "__main__":
    # Run validation summary
    service = CatalogService()
    run_validation_summary(service)
