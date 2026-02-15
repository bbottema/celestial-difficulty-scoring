"""
Unit tests for ObjectListLoader service.
"""
import json
import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import tempfile
import os

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from app.object_lists.object_list_loader import ObjectListLoader
from app.object_lists.models import ObjectList, ObjectListMetadata, ResolutionResult
from app.domain.model.celestial_object import CelestialObject
from app.domain.model.object_classification import ObjectClassification


@pytest.fixture
def temp_lists_dir():
    """Create a temporary directory with test JSON files"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_list_json():
    """Sample JSON data for a test list"""
    return {
        "name": "Test Catalog",
        "description": "A test catalog for unit tests",
        "category": "named_catalog",
        "version": "1.0",
        "objects": [
            {
                "name": "M31",
                "canonical_id": "NGC0224",
                "type": "galaxy",
                "ra": 10.6847,
                "dec": 41.2689,
                "magnitude": 3.4
            },
            {
                "name": "M42",
                "canonical_id": "NGC1976",
                "type": "nebula",
                "ra": 83.8208,
                "dec": -5.3911,
                "magnitude": 4.0
            }
        ]
    }


@pytest.fixture
def mock_catalog_service():
    """Mock CatalogService that returns test objects"""
    mock = Mock()
    
    def get_object_side_effect(identifier):
        objects = {
            'NGC0224': CelestialObject(
                name='M31 - Andromeda Galaxy',
                canonical_id='NGC0224',
                classification=ObjectClassification(primary_type='galaxy', subtype='spiral'),
                magnitude=3.4,
                ra=10.6847,
                dec=41.2689
            ),
            'NGC1976': CelestialObject(
                name='M42 - Orion Nebula',
                canonical_id='NGC1976',
                classification=ObjectClassification(primary_type='nebula', subtype='emission'),
                magnitude=4.0,
                ra=83.8208,
                dec=-5.3911
            ),
            'Jupiter': CelestialObject(
                name='Jupiter',
                canonical_id='Jupiter',
                classification=ObjectClassification(primary_type='planet'),
                magnitude=-2.5
            ),
        }
        return objects.get(identifier)
    
    mock.get_object.side_effect = get_object_side_effect
    return mock


class TestObjectListLoaderGetAvailableLists:
    """Tests for get_available_lists()"""

    def test_finds_json_files(self, temp_lists_dir, sample_list_json):
        """Test that JSON files are discovered"""
        # Create test files
        (temp_lists_dir / 'test_catalog.json').write_text(
            json.dumps(sample_list_json), encoding='utf-8'
        )
        (temp_lists_dir / 'another_list.json').write_text(
            json.dumps({"name": "Another List", "objects": []}), encoding='utf-8'
        )

        loader = ObjectListLoader(lists_dir=temp_lists_dir)
        lists = loader.get_available_lists()

        assert len(lists) == 2
        list_ids = [m.list_id for m in lists]
        assert 'test_catalog' in list_ids
        assert 'another_list' in list_ids

    def test_returns_sorted_by_name(self, temp_lists_dir):
        """Test that lists are sorted by display name"""
        (temp_lists_dir / 'z_list.json').write_text(
            json.dumps({"name": "Zebra List", "objects": []}), encoding='utf-8'
        )
        (temp_lists_dir / 'a_list.json').write_text(
            json.dumps({"name": "Alpha List", "objects": []}), encoding='utf-8'
        )

        loader = ObjectListLoader(lists_dir=temp_lists_dir)
        lists = loader.get_available_lists()

        assert lists[0].name == "Alpha List"
        assert lists[1].name == "Zebra List"

    def test_empty_directory(self, temp_lists_dir):
        """Test handling of empty directory"""
        loader = ObjectListLoader(lists_dir=temp_lists_dir)
        lists = loader.get_available_lists()

        assert lists == []

    def test_missing_directory(self):
        """Test handling of non-existent directory"""
        loader = ObjectListLoader(lists_dir=Path('/nonexistent/path'))
        lists = loader.get_available_lists()

        assert lists == []

    def test_skips_invalid_json(self, temp_lists_dir, sample_list_json):
        """Test that invalid JSON files are skipped"""
        (temp_lists_dir / 'valid.json').write_text(
            json.dumps(sample_list_json), encoding='utf-8'
        )
        (temp_lists_dir / 'invalid.json').write_text(
            '{not valid json}', encoding='utf-8'
        )

        loader = ObjectListLoader(lists_dir=temp_lists_dir)
        lists = loader.get_available_lists()

        assert len(lists) == 1
        assert lists[0].list_id == 'valid'

    def test_metadata_includes_object_count(self, temp_lists_dir, sample_list_json):
        """Test that object count is extracted from metadata"""
        (temp_lists_dir / 'test.json').write_text(
            json.dumps(sample_list_json), encoding='utf-8'
        )

        loader = ObjectListLoader(lists_dir=temp_lists_dir)
        lists = loader.get_available_lists()

        assert lists[0].object_count == 2


class TestObjectListLoaderLoadList:
    """Tests for load_list()"""

    def test_loads_valid_list(self, temp_lists_dir, sample_list_json):
        """Test loading a valid list"""
        (temp_lists_dir / 'test_catalog.json').write_text(
            json.dumps(sample_list_json), encoding='utf-8'
        )

        loader = ObjectListLoader(lists_dir=temp_lists_dir)
        obj_list = loader.load_list('test_catalog')

        assert obj_list.metadata.list_id == 'test_catalog'
        assert obj_list.metadata.name == 'Test Catalog'
        assert len(obj_list.objects) == 2
        assert obj_list.objects[0].name == 'M31'
        assert obj_list.objects[0].canonical_id == 'NGC0224'

    def test_raises_on_missing_list(self, temp_lists_dir):
        """Test error handling for missing list"""
        loader = ObjectListLoader(lists_dir=temp_lists_dir)

        with pytest.raises(FileNotFoundError) as exc_info:
            loader.load_list('nonexistent')

        assert 'nonexistent' in str(exc_info.value)

    def test_raises_on_invalid_json(self, temp_lists_dir):
        """Test error handling for invalid JSON"""
        (temp_lists_dir / 'broken.json').write_text(
            '{invalid json', encoding='utf-8'
        )

        loader = ObjectListLoader(lists_dir=temp_lists_dir)

        with pytest.raises(ValueError) as exc_info:
            loader.load_list('broken')

        assert 'Invalid JSON' in str(exc_info.value)


class TestObjectListLoaderResolveObjects:
    """Tests for resolve_objects()"""

    def test_resolves_all_objects(self, temp_lists_dir, sample_list_json, mock_catalog_service):
        """Test successful resolution of all objects"""
        (temp_lists_dir / 'test.json').write_text(
            json.dumps(sample_list_json), encoding='utf-8'
        )

        loader = ObjectListLoader(
            lists_dir=temp_lists_dir,
            catalog_service=mock_catalog_service
        )
        obj_list = loader.load_list('test')
        result = loader.resolve_objects(obj_list)

        assert result.success_count == 2
        assert result.failure_count == 0
        assert result.success_rate == 100.0

    def test_handles_partial_failures(self, temp_lists_dir, mock_catalog_service):
        """Test handling of partial resolution failures"""
        data = {
            "name": "Mixed List",
            "objects": [
                {"name": "M31", "canonical_id": "NGC0224"},
                {"name": "FakeObject", "canonical_id": "FAKE0001"},
            ]
        }
        (temp_lists_dir / 'mixed.json').write_text(
            json.dumps(data), encoding='utf-8'
        )

        loader = ObjectListLoader(
            lists_dir=temp_lists_dir,
            catalog_service=mock_catalog_service
        )
        obj_list = loader.load_list('mixed')
        result = loader.resolve_objects(obj_list)

        assert result.success_count == 1
        assert result.failure_count == 1
        assert result.success_rate == 50.0

        # Check failure details
        failure = result.failures[0]
        assert failure.name == 'FakeObject'
        assert failure.canonical_id == 'FAKE0001'
        assert 'Not found' in failure.reason

    def test_uses_cache_on_repeat_resolution(self, temp_lists_dir, sample_list_json, mock_catalog_service):
        """Test that cache is used for repeated resolutions"""
        (temp_lists_dir / 'test.json').write_text(
            json.dumps(sample_list_json), encoding='utf-8'
        )

        loader = ObjectListLoader(
            lists_dir=temp_lists_dir,
            catalog_service=mock_catalog_service
        )
        obj_list = loader.load_list('test')

        # First resolution
        result1 = loader.resolve_objects(obj_list)
        call_count_after_first = mock_catalog_service.get_object.call_count

        # Second resolution - should use cache
        result2 = loader.resolve_objects(obj_list)
        call_count_after_second = mock_catalog_service.get_object.call_count

        # No additional API calls should have been made
        assert call_count_after_second == call_count_after_first
        assert result1.success_count == result2.success_count

    def test_progress_callback(self, temp_lists_dir, sample_list_json, mock_catalog_service):
        """Test that progress callback is called"""
        (temp_lists_dir / 'test.json').write_text(
            json.dumps(sample_list_json), encoding='utf-8'
        )

        loader = ObjectListLoader(
            lists_dir=temp_lists_dir,
            catalog_service=mock_catalog_service
        )
        obj_list = loader.load_list('test')

        progress_calls = []
        def callback(current, total):
            progress_calls.append((current, total))

        loader.resolve_objects(obj_list, progress_callback=callback)

        assert len(progress_calls) == 2
        assert progress_calls[0] == (1, 2)
        assert progress_calls[1] == (2, 2)

    def test_fallback_to_name_resolution(self, temp_lists_dir):
        """Test fallback to name when canonical_id fails"""
        data = {
            "name": "Fallback Test",
            "objects": [
                {"name": "Jupiter", "canonical_id": "WRONG_ID"},
            ]
        }
        (temp_lists_dir / 'fallback.json').write_text(
            json.dumps(data), encoding='utf-8'
        )

        # Mock that returns None for WRONG_ID but succeeds for Jupiter
        mock_service = Mock()
        def get_object_side_effect(identifier):
            if identifier == 'Jupiter':
                return CelestialObject(name='Jupiter', canonical_id='Jupiter')
            return None
        mock_service.get_object.side_effect = get_object_side_effect

        loader = ObjectListLoader(
            lists_dir=temp_lists_dir,
            catalog_service=mock_service
        )
        obj_list = loader.load_list('fallback')
        result = loader.resolve_objects(obj_list)

        assert result.success_count == 1
        assert result.failure_count == 0


class TestObjectListLoaderCache:
    """Tests for cache management"""

    def test_clear_cache(self, temp_lists_dir, sample_list_json, mock_catalog_service):
        """Test cache clearing"""
        (temp_lists_dir / 'test.json').write_text(
            json.dumps(sample_list_json), encoding='utf-8'
        )

        loader = ObjectListLoader(
            lists_dir=temp_lists_dir,
            catalog_service=mock_catalog_service
        )
        obj_list = loader.load_list('test')

        # Populate cache
        loader.resolve_objects(obj_list)
        assert loader.get_cache_stats()['cache_size'] == 2

        # Clear cache
        loader.clear_cache()
        assert loader.get_cache_stats()['cache_size'] == 0

    def test_get_cache_stats(self, temp_lists_dir, sample_list_json, mock_catalog_service):
        """Test cache statistics"""
        (temp_lists_dir / 'test.json').write_text(
            json.dumps(sample_list_json), encoding='utf-8'
        )

        loader = ObjectListLoader(
            lists_dir=temp_lists_dir,
            catalog_service=mock_catalog_service
        )
        obj_list = loader.load_list('test')

        # Before resolution
        stats = loader.get_cache_stats()
        assert stats['cache_size'] == 0

        # After resolution
        loader.resolve_objects(obj_list)
        stats = loader.get_cache_stats()
        assert stats['cache_size'] == 2
        assert 'NGC0224' in stats['cached_ids']
        assert 'NGC1976' in stats['cached_ids']
