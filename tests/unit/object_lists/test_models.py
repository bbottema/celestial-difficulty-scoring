"""
Unit tests for object list data models.
"""
import pytest
from app.object_lists.models import (
    ObjectListItem,
    ObjectListMetadata,
    ObjectList,
    ResolutionFailure,
    ResolutionResult,
)


class TestObjectListItem:
    """Tests for ObjectListItem dataclass"""

    def test_from_dict_complete(self):
        """Test parsing a complete object entry"""
        data = {
            'name': 'M31',
            'canonical_id': 'NGC0224',
            'type': 'galaxy',
            'ra': 10.6847,
            'dec': 41.2689,
            'magnitude': 3.4
        }
        item = ObjectListItem.from_dict(data)

        assert item.name == 'M31'
        assert item.canonical_id == 'NGC0224'
        assert item.object_type == 'galaxy'
        assert item.ra == 10.6847
        assert item.dec == 41.2689
        assert item.magnitude == 3.4

    def test_from_dict_minimal(self):
        """Test parsing with only required fields"""
        data = {
            'name': 'Jupiter',
            'canonical_id': 'Jupiter'
        }
        item = ObjectListItem.from_dict(data)

        assert item.name == 'Jupiter'
        assert item.canonical_id == 'Jupiter'
        assert item.object_type == 'unknown'
        assert item.ra == 0.0
        assert item.dec == 0.0
        assert item.magnitude == 99.0

    def test_from_dict_string_numbers(self):
        """Test that string numbers are converted to floats"""
        data = {
            'name': 'M42',
            'canonical_id': 'NGC1976',
            'ra': '83.8208',
            'dec': '-5.3911',
            'magnitude': '4.0'
        }
        item = ObjectListItem.from_dict(data)

        assert item.ra == 83.8208
        assert item.dec == -5.3911
        assert item.magnitude == 4.0


class TestObjectListMetadata:
    """Tests for ObjectListMetadata dataclass"""

    def test_from_dict_complete(self):
        """Test parsing complete metadata"""
        data = {
            'list_id': 'messier_110',
            'name': 'Messier Catalog',
            'description': 'The classic 110 deep-sky objects',
            'category': 'named_catalog',
            'version': '1.0',
            'objects': [{'name': 'M1'}, {'name': 'M2'}, {'name': 'M3'}]
        }
        metadata = ObjectListMetadata.from_dict(data, 'messier_110')

        assert metadata.list_id == 'messier_110'
        assert metadata.name == 'Messier Catalog'
        assert metadata.description == 'The classic 110 deep-sky objects'
        assert metadata.category == 'named_catalog'
        assert metadata.version == '1.0'
        assert metadata.object_count == 3

    def test_from_dict_minimal(self):
        """Test parsing with minimal data"""
        data = {'name': 'Test List'}
        metadata = ObjectListMetadata.from_dict(data, 'test_list')

        assert metadata.list_id == 'test_list'
        assert metadata.name == 'Test List'
        assert metadata.description == ''
        assert metadata.category == 'named_catalog'
        assert metadata.object_count == 0


class TestObjectList:
    """Tests for ObjectList dataclass"""

    def test_from_dict_complete(self):
        """Test parsing a complete object list"""
        data = {
            'name': 'Test Catalog',
            'description': 'Test description',
            'category': 'named_catalog',
            'version': '1.0',
            'objects': [
                {'name': 'M31', 'canonical_id': 'NGC0224', 'type': 'galaxy'},
                {'name': 'M42', 'canonical_id': 'NGC1976', 'type': 'nebula'}
            ]
        }
        obj_list = ObjectList.from_dict(data, 'test_catalog')

        assert obj_list.metadata.list_id == 'test_catalog'
        assert obj_list.metadata.name == 'Test Catalog'
        assert obj_list.metadata.object_count == 2
        assert len(obj_list.objects) == 2
        assert obj_list.objects[0].name == 'M31'
        assert obj_list.objects[1].name == 'M42'

    def test_from_dict_empty_objects(self):
        """Test parsing a list with no objects"""
        data = {'name': 'Empty List'}
        obj_list = ObjectList.from_dict(data, 'empty')

        assert obj_list.metadata.object_count == 0
        assert len(obj_list.objects) == 0


class TestResolutionResult:
    """Tests for ResolutionResult dataclass"""

    def test_success_count(self):
        """Test success_count property"""
        from app.domain.model.celestial_object import CelestialObject

        result = ResolutionResult(
            resolved=[
                CelestialObject(name='M31', canonical_id='NGC0224'),
                CelestialObject(name='M42', canonical_id='NGC1976'),
            ],
            failures=[]
        )
        assert result.success_count == 2
        assert result.failure_count == 0
        assert result.total_count == 2

    def test_failure_count(self):
        """Test failure_count property"""
        result = ResolutionResult(
            resolved=[],
            failures=[
                ResolutionFailure(name='BadObject', canonical_id='BAD001', reason='Not found'),
            ]
        )
        assert result.success_count == 0
        assert result.failure_count == 1
        assert result.total_count == 1

    def test_success_rate_all_success(self):
        """Test success_rate when all objects resolve"""
        from app.domain.model.celestial_object import CelestialObject

        result = ResolutionResult(
            resolved=[
                CelestialObject(name='M31', canonical_id='NGC0224'),
            ],
            failures=[]
        )
        assert result.success_rate == 100.0

    def test_success_rate_partial(self):
        """Test success_rate with partial failures"""
        from app.domain.model.celestial_object import CelestialObject

        result = ResolutionResult(
            resolved=[
                CelestialObject(name='M31', canonical_id='NGC0224'),
                CelestialObject(name='M42', canonical_id='NGC1976'),
                CelestialObject(name='M45', canonical_id='Mel022'),
            ],
            failures=[
                ResolutionFailure(name='BadObject', canonical_id='BAD001', reason='Not found'),
            ]
        )
        assert result.success_rate == 75.0

    def test_success_rate_empty(self):
        """Test success_rate with no objects"""
        result = ResolutionResult(resolved=[], failures=[])
        assert result.success_rate == 100.0  # Edge case: empty = success
