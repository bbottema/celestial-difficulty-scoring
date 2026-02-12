"""
Unit tests for OpenNGC provider.

Tests name resolution, CSV loading, and coordinate conversion.
"""
import pytest
from pathlib import Path

from app.catalog.providers.openngc_provider import OpenNGCProvider


class TestOpenNGCNameResolution:
    """Test name resolution logic"""

    @pytest.fixture
    def provider(self):
        """Load test subset of OpenNGC data"""
        test_csv = Path(__file__).parent.parent.parent / 'data' / 'catalogs' / 'NGC_test.csv'
        return OpenNGCProvider(test_csv)

    def test_resolve_messier_number(self, provider):
        """Test Messier number resolution (M31 → NGC0224)"""
        assert provider.resolve_name('M31') == 'NGC0224'
        assert provider.resolve_name('M42') == 'NGC1976'
        assert provider.resolve_name('M57') == 'NGC6720'
        assert provider.resolve_name('M13') == 'NGC6205'

    def test_resolve_messier_case_insensitive(self, provider):
        """Test case-insensitive Messier resolution"""
        assert provider.resolve_name('m31') == 'NGC0224'
        assert provider.resolve_name('M31') == 'NGC0224'

    def test_resolve_ngc_with_space(self, provider):
        """Test NGC with space resolution (NGC 224 → NGC0224)"""
        assert provider.resolve_name('NGC 224') == 'NGC0224'
        assert provider.resolve_name('NGC 7000') == 'NGC7000'

    def test_resolve_ngc_without_space(self, provider):
        """Test NGC without space resolution (NGC224 → NGC0224)"""
        assert provider.resolve_name('NGC224') == 'NGC0224'
        assert provider.resolve_name('NGC7000') == 'NGC7000'

    def test_resolve_ngc_padded(self, provider):
        """Test NGC with padding (NGC0224 → NGC0224)"""
        assert provider.resolve_name('NGC0224') == 'NGC0224'

    def test_resolve_common_name(self, provider):
        """Test common name resolution"""
        # Note: OpenNGC uses exact common name matching
        assert provider.resolve_name('North America Nebula') == 'NGC7000'
        assert provider.resolve_name('Ring Nebula') == 'NGC6720'

    def test_resolve_nonexistent_object(self, provider):
        """Test resolution of non-existent object returns None"""
        assert provider.resolve_name('M999') is None
        assert provider.resolve_name('NGC9999999') is None


class TestOpenNGCCoordinateConversion:
    """Test sexagesimal → decimal coordinate conversion"""

    @pytest.fixture
    def provider(self):
        test_csv = Path(__file__).parent.parent.parent / 'data' / 'catalogs' / 'NGC_test.csv'
        return OpenNGCProvider(test_csv)

    def test_ra_conversion(self, provider):
        """Test RA conversion (00:42:44.35 → 10.6848°)"""
        ra_result = provider._sex_to_deg_ra('00:42:44.35')
        assert abs(ra_result - 10.6848) < 0.01

    def test_dec_conversion_positive(self, provider):
        """Test positive Dec conversion (+41:16:08.6 → 41.2691°)"""
        dec_result = provider._sex_to_deg_dec('+41:16:08.6')
        assert abs(dec_result - 41.2691) < 0.01

    def test_dec_conversion_negative(self, provider):
        """Test negative Dec conversion (-05:23:28.0 → -5.3911°)"""
        dec_result = provider._sex_to_deg_dec('-05:23:28.0')
        assert abs(dec_result - (-5.3911)) < 0.01

    def test_coordinate_conversion_in_dataframe(self, provider):
        """Test coordinates are properly converted in loaded DataFrame"""
        # M31 should have RA~10.68°, Dec~41.27°
        row = provider.df[provider.df['name'] == 'NGC0224'].iloc[0]

        assert abs(row['ra'] - 10.68) < 0.1
        assert abs(row['dec'] - 41.27) < 0.1


class TestOpenNGCObjectRetrieval:
    """Test object retrieval and DTO conversion"""

    @pytest.fixture
    def provider(self):
        test_csv = Path(__file__).parent.parent.parent / 'data' / 'catalogs' / 'NGC_test.csv'
        return OpenNGCProvider(test_csv)

    def test_get_m31(self, provider):
        """Test retrieving M31"""
        obj = provider.get_object('NGC0224')

        assert obj is not None
        assert obj.canonical_id == 'NGC0224'
        assert obj.name == 'Andromeda Galaxy'
        assert obj.classification.is_spiral_galaxy()
        assert abs(obj.ra - 10.68) < 0.1
        assert abs(obj.dec - 41.27) < 0.1
        assert obj.magnitude == 3.44

    def test_get_ngc7000(self, provider):
        """Test retrieving NGC 7000 (emission nebula)"""
        obj = provider.get_object('NGC7000')

        assert obj is not None
        assert obj.canonical_id == 'NGC7000'
        assert obj.classification.is_emission_nebula()

    def test_get_nonexistent_object(self, provider):
        """Test retrieving non-existent object returns None"""
        obj = provider.get_object('NGC9999999')
        assert obj is None

    def test_batch_get_objects(self, provider):
        """Test batch retrieval"""
        objects = provider.batch_get_objects(['NGC0224', 'NGC7000', 'NGC6720'])

        assert len(objects) == 3
        canonical_ids = [obj.canonical_id for obj in objects]
        assert 'NGC0224' in canonical_ids
        assert 'NGC7000' in canonical_ids
        assert 'NGC6720' in canonical_ids


class TestOpenNGCCSVLoading:
    """Test CSV loading and normalization"""

    def test_csv_loads_successfully(self):
        """Test CSV loads without errors"""
        test_csv = Path(__file__).parent.parent.parent / 'data' / 'catalogs' / 'NGC_test.csv'
        provider = OpenNGCProvider(test_csv)

        assert len(provider.df) == 7
        assert 'name' in provider.df.columns
        assert 'obj_type' in provider.df.columns
        assert 'ra' in provider.df.columns
        assert 'dec' in provider.df.columns

    def test_numeric_fields_converted(self):
        """Test numeric fields are properly converted"""
        test_csv = Path(__file__).parent.parent.parent / 'data' / 'catalogs' / 'NGC_test.csv'
        provider = OpenNGCProvider(test_csv)

        row = provider.df[provider.df['name'] == 'NGC0224'].iloc[0]

        # Should be numeric, not strings
        assert isinstance(row['ra'], (float, int))
        assert isinstance(row['dec'], (float, int))
        assert isinstance(row['mag_v'], (float, int))
        assert isinstance(row['maj_arcmin'], (float, int))

    def test_string_fields_fillna(self):
        """Test string fields have NaN filled with empty strings"""
        test_csv = Path(__file__).parent.parent.parent / 'data' / 'catalogs' / 'NGC_test.csv'
        provider = OpenNGCProvider(test_csv)

        # NGC 7000 has no Messier number
        row = provider.df[provider.df['name'] == 'NGC7000'].iloc[0]
        assert row['messier_nr'] == ''  # Not NaN
