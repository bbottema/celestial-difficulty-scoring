"""
Unit tests for catalog domain models.

Tests ObjectClassification, AngularSize, SurfaceBrightness, and DataProvenance.
"""
from datetime import datetime, timedelta

from app.domain.model.object_classification import (
    ObjectClassification, AngularSize, SurfaceBrightness
)
from app.domain.model.data_provenance import DataProvenance


class TestObjectClassification:
    """Test hierarchical object classification"""

    def test_galaxy_classification(self):
        """Test galaxy classification and helper methods"""
        classification = ObjectClassification('galaxy', 'spiral', 'SA(s)b')

        assert classification.is_galaxy()
        assert classification.is_spiral_galaxy()
        assert not classification.is_elliptical_galaxy()
        assert not classification.is_nebula()

    def test_emission_nebula_classification(self):
        """Test emission nebula classification"""
        classification = ObjectClassification('nebula', 'emission', None)

        assert classification.is_nebula()
        assert classification.is_emission_nebula()
        assert not classification.is_planetary_nebula()
        assert not classification.is_galaxy()

    def test_planetary_nebula_classification(self):
        """Test planetary nebula classification"""
        classification = ObjectClassification('nebula', 'planetary', None)

        assert classification.is_nebula()
        assert classification.is_planetary_nebula()
        assert not classification.is_emission_nebula()

    def test_dark_nebula_classification(self):
        """Test dark nebula classification"""
        classification = ObjectClassification('nebula', 'dark', None)

        assert classification.is_nebula()
        assert classification.is_dark_nebula()

    def test_globular_cluster_classification(self):
        """Test globular cluster classification"""
        classification = ObjectClassification('cluster', 'globular', None)

        assert classification.is_cluster()
        assert classification.is_globular_cluster()
        assert not classification.is_open_cluster()

    def test_open_cluster_classification(self):
        """Test open cluster classification"""
        classification = ObjectClassification('cluster', 'open', None)

        assert classification.is_cluster()
        assert classification.is_open_cluster()
        assert not classification.is_globular_cluster()

    def test_double_star_classification(self):
        """Test double star classification"""
        classification = ObjectClassification('double_star', None, None)

        assert classification.is_double_star()
        assert not classification.is_cluster()

    def test_solar_system_classification(self):
        """Test solar system object classification"""
        planet = ObjectClassification('planet', None, None)
        moon = ObjectClassification('moon', None, None)

        assert planet.is_solar_system()
        assert moon.is_solar_system()


class TestAngularSize:
    """Test angular size calculations"""

    def test_circular_object(self):
        """Test circular object detection"""
        size = AngularSize(major_arcmin=10.0)
        assert size.is_circular()

    def test_elliptical_object(self):
        """Test elliptical object"""
        size = AngularSize(major_arcmin=100.0, minor_arcmin=50.0, position_angle_deg=45.0)
        assert not size.is_circular()

    def test_area_calculation_circular(self):
        """Test area calculation for circular object"""
        import math
        size = AngularSize(major_arcmin=10.0)

        # Area = π * r² = π * 5²
        expected_area = math.pi * 5.0 * 5.0
        assert abs(size.area_sq_arcmin() - expected_area) < 0.01

    def test_area_calculation_elliptical(self):
        """Test area calculation for elliptical object"""
        import math
        size = AngularSize(major_arcmin=100.0, minor_arcmin=50.0)

        # Area = π * a * b = π * 50 * 25
        expected_area = math.pi * 50.0 * 25.0
        assert abs(size.area_sq_arcmin() - expected_area) < 0.01

    def test_area_in_arcsec(self):
        """Test area conversion to arcseconds"""
        size = AngularSize(major_arcmin=1.0)

        # 1 arcmin² = 3600 arcsec²
        area_arcmin = size.area_sq_arcmin()
        area_arcsec = size.area_sq_arcsec()

        assert abs(area_arcsec - area_arcmin * 3600) < 0.01


class TestSurfaceBrightness:
    """Test surface brightness with provenance"""

    def test_openngc_surface_brightness(self):
        """Test OpenNGC galaxy surface brightness"""
        sb = SurfaceBrightness(value=22.44, source='openngc_surf_br', band='B')

        assert sb.value == 22.44
        assert sb.source == 'openngc_surf_br'
        assert sb.band == 'B'

    def test_computed_surface_brightness(self):
        """Test computed surface brightness"""
        sb = SurfaceBrightness(value=25.0, source='computed_mag_size', band='V')

        assert sb.value == 25.0
        assert sb.source == 'computed_mag_size'
        assert sb.band == 'V'


class TestDataProvenance:
    """Test data provenance tracking"""

    def test_authoritative_provenance(self):
        """Test authoritative data provenance"""
        provenance = DataProvenance(
            source='openngc',
            fetched_at=datetime.now(),
            catalog_version='2023-12-13',
            confidence=1.0
        )

        assert provenance.is_authoritative()
        assert provenance.source == 'openngc'

    def test_computed_provenance(self):
        """Test computed data provenance (lower confidence)"""
        provenance = DataProvenance(
            source='computed',
            fetched_at=datetime.now(),
            confidence=0.7
        )

        assert not provenance.is_authoritative()
        assert provenance.confidence == 0.7

    def test_staleness_check_fresh(self):
        """Test staleness check for fresh data"""
        provenance = DataProvenance(
            source='openngc',
            fetched_at=datetime.now(),
            confidence=1.0
        )

        assert not provenance.is_stale(24)  # 24 hours

    def test_staleness_check_stale(self):
        """Test staleness check for stale data"""
        old_time = datetime.now() - timedelta(hours=48)
        provenance = DataProvenance(
            source='simbad',
            fetched_at=old_time,
            confidence=1.0
        )

        assert provenance.is_stale(24)  # 24 hours
        assert not provenance.is_stale(72)  # 72 hours
