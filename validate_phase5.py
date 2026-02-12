"""
Manual validation script for Phase 5 multi-provider testing.

Run with: pipenv run python validate_phase5.py
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from app.catalog.catalog_service import CatalogService

def test_openngc_samples():
    """Test OpenNGC sample objects"""
    print("\n" + "="*60)
    print("TESTING OPENNGC SAMPLE OBJECTS")
    print("="*60)

    service = CatalogService()

    sample = ["M31", "M51", "M42", "M27", "M13", "M45"]

    for name in sample:
        try:
            obj = service.get_object(name)
            if obj:
                print(f"\n[OK] {name}")
                print(f"  Magnitude: {obj.magnitude:.2f}")
                if obj.size:
                    print(f"  Size: {obj.size.major_arcmin:.1f}' x {obj.size.minor_arcmin:.1f}'")
                if obj.surface_brightness:
                    print(f"  Surface Brightness: {obj.surface_brightness.value:.1f} mag/arcsec²")
                if obj.classification:
                    print(f"  Type: {obj.classification.primary_type}")
                if obj.provenance:
                    sources = [p.source.value for p in obj.provenance]
                    print(f"  Source: {', '.join(sources)}")
            else:
                print(f"\n[FAIL] {name} - NOT FOUND")
        except Exception as e:
            print(f"\n[ERROR] {name} - {e}")

def test_horizons_samples():
    """Test Horizons (Solar System) objects"""
    print("\n" + "="*60)
    print("TESTING HORIZONS SAMPLE OBJECTS")
    print("="*60)

    service = CatalogService()

    sample = ["Jupiter", "Saturn", "Mars", "Venus", "Moon"]

    for name in sample:
        try:
            obj = service.get_object(name)
            if obj:
                print(f"\n[OK] {name}")
                print(f"  Magnitude: {obj.magnitude:.2f}")
                if obj.size:
                    print(f"  Size: {obj.size.major_arcsec:.1f}\"")
                if obj.provenance:
                    sources = [p.source.value for p in obj.provenance]
                    print(f"  Source: {', '.join(sources)}")
            else:
                print(f"\n[FAIL] {name} - NOT FOUND")
        except Exception as e:
            print(f"\n[ERROR] {name} - {e}")

def test_cross_provider_consistency():
    """Test same object from different providers"""
    print("\n" + "="*60)
    print("TESTING CROSS-PROVIDER CONSISTENCY")
    print("="*60)

    service = CatalogService()

    # Get M31 from OpenNGC
    print("\nM31 Comparison:")
    print("-" * 40)

    try:
        m31_openngc = service.openngc.get_object_by_name("M31")
        if m31_openngc:
            print(f"OpenNGC:")
            print(f"  Magnitude: {m31_openngc.magnitude:.2f}")
            if m31_openngc.surface_brightness:
                print(f"  SB: {m31_openngc.surface_brightness.value:.1f} mag/arcsec²")
            if m31_openngc.size:
                print(f"  Size: {m31_openngc.size.major_arcmin:.1f}' x {m31_openngc.size.minor_arcmin:.1f}'")
    except Exception as e:
        print(f"OpenNGC ERROR: {e}")

    # Note: SIMBAD requires internet, may not work offline
    try:
        m31_simbad = service.simbad.get_object("M31")
        if m31_simbad:
            print(f"\nSIMBAD:")
            print(f"  Magnitude: {m31_simbad.magnitude:.2f}")
            if m31_simbad.surface_brightness:
                print(f"  SB: {m31_simbad.surface_brightness.value:.1f} mag/arcsec²")
            if m31_simbad.size:
                print(f"  Size: {m31_simbad.size.major_arcmin:.1f}' x {m31_simbad.size.minor_arcmin:.1f}'")
    except Exception as e:
        print(f"\nSIMBAD (skipped - requires internet): {e}")

def test_computed_surface_brightness():
    """Test computed surface brightness formula"""
    print("\n" + "="*60)
    print("TESTING COMPUTED SURFACE BRIGHTNESS")
    print("="*60)

    import math

    # Test object with known SB
    magnitude = 11.2
    major_arcmin = 2.5
    minor_arcmin = 1.8

    # Convert to arcsec
    major_arcsec = major_arcmin * 60
    minor_arcsec = minor_arcmin * 60

    # Compute area (ellipse)
    area_arcsec2 = math.pi * (major_arcsec / 2) * (minor_arcsec / 2)

    # Compute SB
    computed_sb = magnitude + 2.5 * math.log10(area_arcsec2)

    print(f"\nObject: {major_arcmin}' x {minor_arcmin}' at magnitude {magnitude}")
    print(f"Area: {area_arcsec2:.0f} arcsec²")
    print(f"Computed SB: {computed_sb:.2f} mag/arcsec²")
    print(f"Expected: ~13.8 mag/arcsec²")

    if 13.0 <= computed_sb <= 14.5:
        print("[OK] Computation within expected range")
    else:
        print("[FAIL] Computation out of range!")

def main():
    """Run all validation tests"""
    print("\n" + "="*60)
    print("PHASE 5 MULTI-PROVIDER VALIDATION")
    print("="*60)

    try:
        test_openngc_samples()
        test_horizons_samples()
        test_cross_provider_consistency()
        test_computed_surface_brightness()

        print("\n" + "="*60)
        print("VALIDATION COMPLETE")
        print("="*60 + "\n")

    except Exception as e:
        print(f"\n\nFATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())
