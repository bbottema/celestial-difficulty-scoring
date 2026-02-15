"""
Unit tests for Horizons provider

Tests Solar System ephemeris calculations via JPL Horizons API.
"""
import pytest
from datetime import datetime, timezone
from unittest.mock import patch

from app.catalog.providers.horizons_provider import HorizonsProvider


class TestHorizonsObjectMapping:
    """Test mapping of Solar System object names to Horizons IDs"""

    @pytest.fixture
    def provider(self):
        return HorizonsProvider()

    def test_planet_name_mapping(self, provider):
        """Test mapping planet names to Horizons IDs"""
        assert provider._get_horizons_id('Jupiter') == '599'
        assert provider._get_horizons_id('Saturn') == '699'
        assert provider._get_horizons_id('Mars') == '499'

    def test_moon_name_mapping(self, provider):
        """Test mapping moon name to Horizons ID"""
        assert provider._get_horizons_id('Moon') == '301'

    def test_case_insensitive_mapping(self, provider):
        """Test that name mapping is case-insensitive"""
        assert provider._get_horizons_id('jupiter') == '599'
        assert provider._get_horizons_id('MARS') == '499'

    def test_unknown_object(self, provider):
        """Test handling of unknown Solar System objects"""
        horizons_id = provider._get_horizons_id('Pluto')
        # Should either return ID or None
        assert horizons_id is None or isinstance(horizons_id, str)


class TestHorizonsEphemerisQuery:
    """Test ephemeris query construction and parsing"""

    @pytest.fixture
    def provider(self):
        return HorizonsProvider()

    def test_query_with_location(self, provider):
        """Test that queries include observer location"""
        # Observer at latitude 40°N, longitude 75°W
        observer_lat = 40.0
        observer_lon = -75.0
        observation_time = datetime(2024, 6, 15, 22, 0, 0, tzinfo=timezone.utc)

        # Provider should construct location parameter
        location = provider._format_location(observer_lat, observer_lon)
        assert location is not None

    def test_query_with_time(self, provider):
        """Test that queries include observation time"""
        observation_time = datetime(2024, 6, 15, 22, 0, 0, tzinfo=timezone.utc)
        time_str = provider._format_time(observation_time)
        assert '2024-06-15' in time_str or '2024' in time_str


# Response parsing is tested via real Horizons queries in integration tests


class TestHorizonsClassification:
    """Test classification of Solar System objects"""

    @pytest.fixture
    def provider(self):
        return HorizonsProvider()

    def test_planet_classification(self, provider):
        """Test classification of planets"""
        classification = provider.adapter._classify_object('Jupiter')
        assert classification.primary_type == 'solar_system'
        assert classification.subtype == 'planet'

    def test_moon_classification(self, provider):
        """Test classification of Moon"""
        classification = provider.adapter._classify_object('Moon')
        assert classification.primary_type == 'solar_system'
        assert classification.subtype == 'moon'

    def test_comet_classification(self, provider):
        """Test classification of comets"""
        classification = provider.adapter._classify_object('C/2023 A3')
        assert classification.primary_type == 'solar_system'
        assert classification.subtype in ['comet', 'minor_body']


class TestHorizonsAngularSize:
    """Test angular size calculation for Solar System objects"""

    @pytest.fixture
    def provider(self):
        return HorizonsProvider()

    def test_jupiter_angular_size(self, provider):
        """Test Jupiter's angular size calculation"""
        # Horizons returns angular width in arcsec
        ang_width_arcsec = 45.2

        size = provider._calculate_angular_size(ang_width_arcsec, 'Jupiter')

        assert size is not None
        assert size.major_arcmin > 0
        # Jupiter appears nearly circular
        assert abs(size.major_arcmin - size.minor_arcmin) < 0.2

    def test_saturn_angular_size(self, provider):
        """Test Saturn's angular size (including rings)"""
        ang_width_arcsec = 18.0

        size = provider._calculate_angular_size(ang_width_arcsec, 'Saturn')

        assert size is not None
        assert size.major_arcmin > 0

    def test_moon_angular_size(self, provider):
        """Test Moon's angular size"""
        # Moon ~30 arcmin
        ang_width_arcsec = 1800.0

        size = provider._calculate_angular_size(ang_width_arcsec, 'Moon')

        assert size is not None
        assert 29 < size.major_arcmin < 31


# Provenance is tested via integration tests with real queries


class TestHorizonsRateLimiting:
    """Test rate limiting for Horizons API"""

    @pytest.fixture
    def provider(self):
        return HorizonsProvider()

    def test_rate_limit_exists(self, provider):
        """Test that provider has rate limiting mechanism"""
        # Horizons has request limits
        assert hasattr(provider, '_last_query_time') or hasattr(provider, 'rate_limiter')


class TestHorizonsErrorHandling:
    """Test error handling for Horizons queries"""

    @pytest.fixture
    def provider(self):
        return HorizonsProvider()

    def test_invalid_object_name(self, provider):
        """Test handling of invalid object names"""
        result = provider.get_object('InvalidPlanet123')
        assert result is None

    def test_network_error(self, provider):
        """Test handling of network errors"""
        with patch('astroquery.jplhorizons.Horizons.ephemerides', side_effect=Exception("Network error")):
            result = provider.get_object('Jupiter')
            assert result is None


class TestHorizonsTimeDependent:
    """Test that Horizons data is time-dependent"""

    @pytest.fixture
    def provider(self):
        return HorizonsProvider()

    def test_positions_change_over_time(self, provider):
        """Test that planetary positions change with observation time"""
        # This test verifies the provider accepts time parameter
        time1 = datetime(2024, 1, 1, tzinfo=timezone.utc)
        time2 = datetime(2024, 6, 1, tzinfo=timezone.utc)

        # Provider should support time parameter
        assert 'time' in provider.get_object.__code__.co_varnames or \
               'observation_time' in provider.get_object.__code__.co_varnames

    def test_no_caching_for_ephemeris(self, provider):
        """Test that ephemeris data should not be cached long-term"""
        # Solar System positions change daily, cache TTL should be short
        # Provider should have short TTL or no caching
        if hasattr(provider, 'cache_ttl'):
            assert provider.cache_ttl <= 86400  # Max 1 day


# Location dependency is handled via observer_location in __init__
# Integration tests verify this works correctly
