"""
Unit tests for OpenNGC adapter.

Tests type mapping, DTO conversion, and field extraction.
"""
import pandas as pd

from app.catalog.providers.openngc_provider import OpenNGCAdapter
from app.catalog.interfaces import ProviderDTO


class TestOpenNGCTypeMapping:
    """Test OpenNGC type code → domain classification mapping"""

    def setup_method(self):
        self.adapter = OpenNGCAdapter()

    def test_spiral_galaxy_mapping(self):
        """Test spiral galaxy type mapping (G + SA/SB/SAB)"""
        classification = self.adapter._map_type('G', 'SA(s)b')

        assert classification.primary_type == 'galaxy'
        assert classification.subtype == 'spiral'
        assert classification.morphology == 'SA(s)b'

    def test_elliptical_galaxy_mapping(self):
        """Test elliptical galaxy type mapping (G + E)"""
        classification = self.adapter._map_type('G', 'E3')

        assert classification.primary_type == 'galaxy'
        assert classification.subtype == 'elliptical'
        assert classification.morphology == 'E3'

    def test_lenticular_galaxy_mapping(self):
        """Test lenticular galaxy type mapping (G + S0)"""
        classification = self.adapter._map_type('G', 'S0')

        assert classification.primary_type == 'galaxy'
        assert classification.subtype == 'lenticular'
        assert classification.morphology == 'S0'

    def test_emission_nebula_mapping_hii(self):
        """Test emission nebula type mapping (HII)"""
        classification = self.adapter._map_type('HII', None)

        assert classification.primary_type == 'nebula'
        assert classification.subtype == 'emission'

    def test_emission_nebula_mapping_emn(self):
        """Test emission nebula type mapping (EmN)"""
        classification = self.adapter._map_type('EmN', None)

        assert classification.primary_type == 'nebula'
        assert classification.subtype == 'emission'

    def test_reflection_nebula_mapping(self):
        """Test reflection nebula type mapping (RfN)"""
        classification = self.adapter._map_type('RfN', None)

        assert classification.primary_type == 'nebula'
        assert classification.subtype == 'reflection'

    def test_dark_nebula_mapping(self):
        """Test dark nebula type mapping (DrkN)"""
        classification = self.adapter._map_type('DrkN', None)

        assert classification.primary_type == 'nebula'
        assert classification.subtype == 'dark'

    def test_planetary_nebula_mapping(self):
        """Test planetary nebula type mapping (PN)"""
        classification = self.adapter._map_type('PN', None)

        assert classification.primary_type == 'nebula'
        assert classification.subtype == 'planetary'

    def test_open_cluster_mapping(self):
        """Test open cluster type mapping (OCl)"""
        classification = self.adapter._map_type('OCl', None)

        assert classification.primary_type == 'cluster'
        assert classification.subtype == 'open'

    def test_globular_cluster_mapping(self):
        """Test globular cluster type mapping (GCl)"""
        classification = self.adapter._map_type('GCl', None)

        assert classification.primary_type == 'cluster'
        assert classification.subtype == 'globular'

    def test_supernova_remnant_mapping(self):
        """Test supernova remnant type mapping (SNR)"""
        classification = self.adapter._map_type('SNR', None)

        assert classification.primary_type == 'nebula'
        assert classification.subtype == 'supernova_remnant'

    def test_unknown_type_mapping(self):
        """Test unknown type handling"""
        classification = self.adapter._map_type('Dup', None)

        assert classification.primary_type == 'unknown'


class TestGalaxySubtypeParsing:
    """Test Hubble type → galaxy subtype parsing"""

    def setup_method(self):
        self.adapter = OpenNGCAdapter()

    def test_spiral_unbarred(self):
        """Test unbarred spiral classification (SA)"""
        subtype = self.adapter._parse_galaxy_subtype('SA(s)b')
        assert subtype == 'spiral'

    def test_spiral_barred(self):
        """Test barred spiral classification (SB)"""
        subtype = self.adapter._parse_galaxy_subtype('SB(rs)c')
        assert subtype == 'spiral'

    def test_spiral_weakly_barred(self):
        """Test weakly barred spiral classification (SAB)"""
        subtype = self.adapter._parse_galaxy_subtype('SAB(r)bc')
        assert subtype == 'spiral'

    def test_elliptical(self):
        """Test elliptical classification (E)"""
        for hubble_type in ['E0', 'E3', 'E5', 'E7']:
            subtype = self.adapter._parse_galaxy_subtype(hubble_type)
            assert subtype == 'elliptical', f"Failed for {hubble_type}"

    def test_lenticular(self):
        """Test lenticular classification (S0)"""
        for hubble_type in ['S0', 'SA0', 'SB0', 'S0-']:
            subtype = self.adapter._parse_galaxy_subtype(hubble_type)
            assert subtype == 'lenticular', f"Failed for {hubble_type}"

    def test_irregular(self):
        """Test irregular classification (I/Irr)"""
        for hubble_type in ['I', 'Irr', 'IB(s)m']:
            subtype = self.adapter._parse_galaxy_subtype(hubble_type)
            assert subtype == 'irregular', f"Failed for {hubble_type}"

    def test_none_input(self):
        """Test None input handling"""
        subtype = self.adapter._parse_galaxy_subtype(None)
        assert subtype is None


class TestOpenNGCDTOConversion:
    """Test DTO → CelestialObject conversion"""

    def setup_method(self):
        self.adapter = OpenNGCAdapter()

    def test_m31_conversion(self):
        """Test M31 (Andromeda Galaxy) conversion"""
        dto = ProviderDTO(
            raw_data={
                'name': 'NGC0224',
                'obj_type': 'G',
                'hubble_type': 'SA(s)b',
                'ra': 10.6847,
                'dec': 41.2687,
                'maj_arcmin': 177.83,
                'min_arcmin': 69.66,
                'pos_ang': 35.0,
                'mag_v': 3.44,
                'mag_b': 4.36,
                'surf_br': 23.63,
                'messier_nr': '031',
                'comname': 'Andromeda Galaxy',
                'other_id': '2MASX J00424433+4116074,M 31'
            },
            source='openngc'
        )

        obj = self.adapter.to_domain(dto)

        assert obj.name == 'Andromeda Galaxy'
        assert obj.canonical_id == 'NGC0224'
        assert obj.classification.is_spiral_galaxy()
        assert obj.classification.morphology == 'SA(s)b'
        assert obj.magnitude == 3.44
        assert obj.size.major_arcmin == 177.83
        assert obj.size.minor_arcmin == 69.66
        assert obj.surface_brightness is not None
        assert obj.surface_brightness.value == 23.63
        assert obj.surface_brightness.source == 'openngc_surf_br'
        assert 'M031' in obj.aliases
        assert 'Andromeda Galaxy' in obj.aliases

    def test_ngc7000_conversion(self):
        """Test NGC 7000 (North America Nebula) conversion"""
        dto = ProviderDTO(
            raw_data={
                'name': 'NGC7000',
                'obj_type': 'HII',
                'hubble_type': '',
                'ra': 312.5,
                'dec': 44.52,
                'maj_arcmin': 120.0,
                'min_arcmin': pd.NA,
                'pos_ang': pd.NA,
                'mag_v': pd.NA,
                'mag_b': pd.NA,
                'surf_br': pd.NA,
                'messier_nr': '',
                'comname': 'North America Nebula',
                'other_id': ''
            },
            source='openngc'
        )

        obj = self.adapter.to_domain(dto)

        assert obj.name == 'North America Nebula'
        assert obj.canonical_id == 'NGC7000'
        assert obj.classification.is_emission_nebula()
        assert obj.magnitude == 99.0  # Default for missing
        assert obj.size.major_arcmin == 120.0
        assert obj.size.minor_arcmin is None
        assert obj.surface_brightness is None

    def test_m57_conversion(self):
        """Test M57 (Ring Nebula) conversion"""
        dto = ProviderDTO(
            raw_data={
                'name': 'NGC6720',
                'obj_type': 'PN',
                'hubble_type': '',
                'ra': 283.3967,
                'dec': 33.0292,
                'maj_arcmin': 1.4,
                'min_arcmin': 1.4,
                'pos_ang': pd.NA,
                'mag_v': 8.8,
                'mag_b': 9.7,
                'surf_br': pd.NA,
                'messier_nr': '057',
                'comname': 'Ring Nebula',
                'other_id': 'M 57'
            },
            source='openngc'
        )

        obj = self.adapter.to_domain(dto)

        assert obj.name == 'Ring Nebula'
        assert obj.canonical_id == 'NGC6720'
        assert obj.classification.is_planetary_nebula()
        assert obj.magnitude == 8.8
        assert 'M057' in obj.aliases

    def test_provenance_tracking(self):
        """Test provenance is properly tracked"""
        dto = ProviderDTO(
            raw_data={
                'name': 'NGC0001',
                'obj_type': 'G',
                'hubble_type': 'Sb',
                'ra': 1.0,
                'dec': 1.0,
                'maj_arcmin': 1.0,
                'min_arcmin': pd.NA,
                'pos_ang': pd.NA,
                'mag_v': 13.0,
                'mag_b': 14.0,
                'surf_br': pd.NA,
                'messier_nr': '',
                'comname': '',
                'other_id': ''
            },
            source='openngc'
        )

        obj = self.adapter.to_domain(dto)

        assert len(obj.provenance) == 1
        assert obj.provenance[0].source == 'OpenNGC'
        assert obj.provenance[0].catalog_version == '2023-12-13'
        assert obj.provenance[0].confidence == 1.0
