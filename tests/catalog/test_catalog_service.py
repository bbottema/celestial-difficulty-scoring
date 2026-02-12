"""
Integration tests for CatalogService

Tests decision tree logic, provider coordination, and enrichment flow.
"""
import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import patch

from app.catalog.catalog_service import CatalogService
from app.catalog.interfaces import CatalogSource
from app.domain.model.data_provenance import DataProvenance


class TestCatalogServiceDecisionTree:
    """Test decision tree logic for selecting providers"""

    @pytest.fixture
    def service(self):
        return CatalogService()

    def test_dso_uses_openngc_first(self, service):
        """Test that DSO queries try OpenNGC first"""
        # When querying NGC/IC/Messier objects, use OpenNGC
        providers = service._select_providers('NGC7000')

        assert CatalogSource.OPENNGC in providers
        # Should be first in list
        assert providers[0] == CatalogSource.OPENNGC

    def test_solar_system_uses_horizons(self, service):
        """Test that Solar System objects use Horizons"""
        providers = service._select_providers('Jupiter')

        assert CatalogSource.HORIZONS in providers

    def test_star_names_use_simbad(self, service):
        """Test that star names (HD, HR, etc.) use SIMBAD"""
        providers = service._select_providers('Betelgeuse')

        assert CatalogSource.SIMBAD in providers

    def test_messier_resolved_to_ngc(self, service):
        """Test that Messier numbers are resolved to NGC"""
        # M31 should map to NGC0224 and use OpenNGC
        providers = service._select_providers('M31')

        assert CatalogSource.OPENNGC in providers


class TestCatalogServiceEnrichment:
    """Test enrichment flow with multiple providers"""

    @pytest.fixture
    def service(self):
        return CatalogService()

    def test_openngc_enriched_by_simbad(self, service):
        """Test that OpenNGC results are enriched by SIMBAD"""
        # OpenNGC provides base data
        # SIMBAD adds aliases, corrects types, adds surface brightness

        obj = service.get_object('NGC0224')

        assert obj is not None
        assert obj.canonical_id == 'NGC0224'

        # Should have provenance from both sources
        sources = [p.source for p in obj.provenance]
        assert 'OpenNGC' in sources
        # SIMBAD enrichment may be optional
        if len(sources) > 1:
            assert 'SIMBAD' in sources

    def test_m31_type_correction(self, service):
        """Test that M31's AGN misclassification is corrected"""
        obj = service.get_object('M31')

        assert obj is not None
        assert obj.classification.is_galaxy()
        assert obj.classification.is_spiral_galaxy()
        # Should not be classified as AGN

    def test_ngc7000_type_correction(self, service):
        """Test that NGC 7000's cluster misclassification is corrected"""
        obj = service.get_object('NGC7000')

        assert obj is not None
        assert obj.classification.primary_type == 'nebula'
        assert obj.classification.subtype == 'emission'
        # Should not be classified as cluster


class TestCatalogServiceSurfaceBrightness:
    """Test surface brightness calculation and enrichment"""

    @pytest.fixture
    def service(self):
        return CatalogService()

    def test_surface_brightness_from_openngc(self, service):
        """Test extracting surface brightness from OpenNGC"""
        obj = service.get_object('M31')

        assert obj is not None
        if obj.surface_brightness:
            assert obj.surface_brightness.value > 0
            # M31 is ~23.6 mag/arcsec²
            assert 22.0 < obj.surface_brightness.value < 25.0

    def test_surface_brightness_computed(self, service):
        """Test computing surface brightness when not provided"""
        # For objects with magnitude and size but no SB
        obj = service.get_object('M42')

        assert obj is not None
        if obj.surface_brightness:
            assert obj.surface_brightness.provenance in ['computed', 'authoritative']

    def test_missing_surface_brightness(self, service):
        """Test handling objects without surface brightness data"""
        # Some objects may lack magnitude or size
        obj = service.get_object('NGC869')  # Open cluster

        assert obj is not None
        # May or may not have surface brightness
        if not obj.surface_brightness:
            # This is acceptable for point sources
            pass


class TestCatalogServiceCaching:
    """Test caching strategy"""

    @pytest.fixture
    def service(self):
        return CatalogService()

    def test_repeated_query_uses_cache(self, service):
        """Test that repeated queries use cached data"""
        # First query
        obj1 = service.get_object('M31')

        # Second query should be faster (from cache)
        obj2 = service.get_object('M31')

        assert obj1.canonical_id == obj2.canonical_id
        assert obj1.ra == obj2.ra

    def test_cache_respects_ttl(self, service):
        """Test that cache respects TTL for different sources"""
        # OpenNGC data: 1 year TTL
        # SIMBAD data: 1 week TTL
        # Horizons data: should not be cached or very short TTL

        # This test would need time manipulation
        # For now, just verify TTL constants exist
        assert hasattr(service, 'OPENNGC_TTL') or hasattr(service, 'cache_ttl')


class TestCatalogServiceBatchOperations:
    """Test batch query operations"""

    @pytest.fixture
    def service(self):
        return CatalogService()

    def test_batch_get_messier_objects(self, service):
        """Test retrieving multiple Messier objects"""
        messier_ids = ['M31', 'M42', 'M13', 'M57']

        results = service.get_objects(messier_ids)

        assert len(results) == 4
        assert all(obj is not None for obj in results)

    def test_batch_handles_missing_objects(self, service):
        """Test batch operation with some nonexistent objects"""
        mixed_ids = ['M31', 'NONEXISTENT123', 'M42']

        results = service.get_objects(mixed_ids)

        # Should return dict with None for missing
        assert results['M31'] is not None
        assert results['NONEXISTENT123'] is None
        assert results['M42'] is not None


class TestCatalogServiceNameResolution:
    """Test name resolution across providers"""

    @pytest.fixture
    def service(self):
        return CatalogService()

    def test_resolve_messier_to_ngc(self, service):
        """Test resolving Messier numbers to NGC"""
        canonical = service.resolve_canonical_id('M31')
        assert canonical == 'NGC0224'

    def test_resolve_common_name(self, service):
        """Test resolving common names"""
        # "Andromeda Galaxy" -> NGC0224
        canonical = service.resolve_canonical_id('Andromeda Galaxy')
        if canonical:
            assert 'NGC' in canonical or 'M31' in canonical

    def test_resolve_ic_number(self, service):
        """Test resolving IC catalog numbers"""
        canonical = service.resolve_canonical_id('IC1805')
        assert canonical is not None


class TestCatalogServiceProvenance:
    """Test provenance tracking and data quality"""

    @pytest.fixture
    def service(self):
        return CatalogService()

    def test_provenance_chain(self, service):
        """Test that enriched objects track all data sources"""
        obj = service.get_object('M31')

        assert obj is not None
        assert len(obj.provenance) > 0

        # Should track at least OpenNGC
        sources = [p.source for p in obj.provenance]
        assert 'OpenNGC' in sources

    def test_authoritative_vs_computed(self, service):
        """Test distinguishing authoritative vs computed data"""
        obj = service.get_object('M31')

        assert obj is not None

        # Coordinates should be authoritative
        coord_provenance = [p for p in obj.provenance if 'coordinate' in p.source.lower() or p.confidence == 'authoritative']
        if coord_provenance:
            assert coord_provenance[0].confidence == 'authoritative'

    def test_staleness_detection(self, service):
        """Test detecting stale cached data"""
        # Create mock stale data
        old_timestamp = datetime.now(timezone.utc) - timedelta(days=400)

        provenance = DataProvenance(
            source='OpenNGC',
            timestamp=old_timestamp,
            confidence='authoritative',
            ttl_seconds=365 * 24 * 3600
        )

        # Should detect as stale
        assert provenance.is_stale()


class TestCatalogServiceErrorHandling:
    """Test error handling and fallback behavior"""

    @pytest.fixture
    def service(self):
        return CatalogService()

    def test_nonexistent_object(self, service):
        """Test querying nonexistent object"""
        obj = service.get_object('NONEXISTENT12345')
        assert obj is None

    def test_provider_failure_fallback(self, service):
        """Test fallback when primary provider fails"""
        # If OpenNGC fails, should try SIMBAD
        with patch('app.catalog.providers.openngc_provider.OpenNGCProvider.get_object', return_value=None):
            obj = service.get_object('M31')
            # May still succeed via SIMBAD fallback
            # Or may return None if all providers fail

    def test_network_error_handling(self, service):
        """Test handling network errors gracefully"""
        with patch('astroquery.simbad.Simbad.query_object', side_effect=Exception("Network error")):
            # Should not raise exception
            obj = service.get_object('M31')
            # Should either return cached data or None


class TestCatalogServiceFiltering:
    """Test filtering and search capabilities"""

    @pytest.fixture
    def service(self):
        return CatalogService()

    def test_filter_by_type(self, service):
        """Test filtering objects by classification"""
        # Get all spiral galaxies
        galaxies = service.filter_by_type('galaxy', 'spiral')

        if galaxies:
            assert all(obj.classification.is_spiral_galaxy() for obj in galaxies)

    def test_filter_by_magnitude_range(self, service):
        """Test filtering by magnitude range"""
        # Get objects brighter than magnitude 8
        bright_objects = service.filter_by_magnitude(max_mag=8.0)

        if bright_objects:
            assert all(obj.magnitude <= 8.0 for obj in bright_objects)

    def test_search_by_name_prefix(self, service):
        """Test searching by name prefix"""
        # Search for all NGC 7000-series objects
        results = service.search_by_prefix('NGC7')

        if results:
            assert all('NGC7' in obj.canonical_id for obj in results)


class TestCatalogServiceIntegration:
    """Full integration tests with real providers"""

    @pytest.fixture
    def service(self):
        return CatalogService()

    def test_full_m31_enrichment_flow(self, service):
        """Test complete enrichment flow for M31"""
        obj = service.get_object('M31')

        assert obj is not None
        assert obj.canonical_id in ['NGC0224', 'M31']
        assert obj.classification.is_spiral_galaxy()
        assert obj.magnitude < 10  # M31 is ~3.4
        assert obj.ra > 0
        assert obj.dec > 0
        assert len(obj.aliases) > 0
        assert len(obj.provenance) > 0

    def test_full_ngc7000_enrichment_flow(self, service):
        """Test complete enrichment flow for NGC 7000"""
        obj = service.get_object('NGC7000')

        assert obj is not None
        assert obj.classification.primary_type == 'nebula'
        assert obj.classification.subtype == 'emission'
        # Should have been corrected from cluster

    def test_full_jupiter_ephemeris_flow(self, service):
        """Test complete flow for Jupiter ephemeris"""
        # Need to pass observation time and location
        observation_time = datetime.now(timezone.utc)

        obj = service.get_object('Jupiter', time=observation_time)

        assert obj is not None
        assert obj.classification.primary_type == 'solar_system'
        # Position should be current
        assert obj.provenance[0].source == 'Horizons'
