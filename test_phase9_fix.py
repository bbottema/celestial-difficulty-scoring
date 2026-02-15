#!/usr/bin/env python
"""
Quick test to verify Phase 9.1 fix - test loading and scoring Messier list
"""
import sys
import logging
from pathlib import Path

# Setup paths
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / 'src'))

# Setup logging
logging.basicConfig(level=logging.INFO)

def test_object_list_loading_and_scoring():
    """Test that object lists load without AngularSize comparison errors"""
    from app.object_lists.object_list_loader import ObjectListLoader
    from app.catalog.catalog_service import CatalogService
    from app.domain.services.observability_calculation_service import ObservabilityCalculationService
    from app.orm.model.entities import Telescope, Eyepiece, ObservationSite
    
    print("\n=== Phase 9.1 Fix Verification ===\n")
    
    # Initialize services
    print("1. Initializing services...")
    catalog_service = CatalogService()
    loader = ObjectListLoader(catalog_service=catalog_service)
    observability_service = ObservabilityCalculationService()
    
    # Get available lists
    print("2. Loading available lists...")
    lists = loader.get_available_lists()
    print(f"   Found {len(lists)} available lists:")
    for lst in lists:
        print(f"   - {lst.name} ({lst.object_count} objects)")
    
    # Load Messier list
    print("\n3. Loading Messier catalog...")
    messier_list = loader.load_list('messier_110')
    print(f"   Loaded: {messier_list.metadata.name}")
    print(f"   Items in list: {len(messier_list.objects)}")
    
    # Resolve objects
    print("\n4. Resolving objects via catalog...")
    resolution_result = loader.resolve_objects(messier_list)
    print(f"   Resolved: {len(resolution_result.resolved)} objects")
    print(f"   Failed: {len(resolution_result.failures)} objects")
    
    if resolution_result.failures:
        print("\n   Failed resolutions:")
        for failure in resolution_result.failures[:5]:  # Show first 5
            print(f"   - {failure.name} ({failure.canonical_id}): {failure.reason}")
    
    # Score objects
    print("\n5. Scoring resolved objects...")
    
    # Create minimal context
    from app.domain.model.telescope_type import TelescopeType
    telescope = Telescope(
        name="Test Scope",
        focal_length=1000,
        aperture=200,
        focal_ratio=5.0,
        type=TelescopeType.NEWTONIAN
    )
    eyepiece = Eyepiece(
        name="Test Eyepiece",
        focal_length=10,
        apparent_field_of_view=50,
        barrel_size=1.25
    )
    from app.domain.model.light_pollution import LightPollution
    observation_site = ObservationSite(
        name="Test Site",
        latitude=40.0,
        longitude=-80.0,
        light_pollution=LightPollution.BORTLE_5
    )
    
    try:
        scored_objects = observability_service.score_celestial_objects(
            resolution_result.resolved,
            telescope=telescope,
            eyepiece=eyepiece,
            observation_site=observation_site
        )
        print(f"   Successfully scored {len(scored_objects)} objects")
        
        # Show top 5 scores
        print("\n   Top 5 scored objects:")
        sorted_scores = sorted(scored_objects, key=lambda x: x.score.normalized_score, reverse=True)
        for i, obj in enumerate(sorted_scores[:5], 1):
            print(f"   {i}. {obj.name}: {obj.score.normalized_score:.3f}")
        
        print("\n✅ SUCCESS: Phase 9.1 fix is working!")
        print("   Objects are loading and scoring without AngularSize comparison errors")
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR during scoring: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_object_list_loading_and_scoring()
    sys.exit(0 if success else 1)
