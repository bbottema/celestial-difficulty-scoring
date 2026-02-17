"""
Unit tests for TargetListService.

Phase 9.2: Custom target list management.
"""
import pytest
from datetime import datetime, timezone
from unittest.mock import Mock, MagicMock, patch
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.orm.model.entities import Base, TargetList, TargetListItem
from app.orm.repositories.target_list_repository import TargetListRepository
from app.orm.services.target_list_service import TargetListService
from app.domain.model.celestial_object import CelestialObject
from app.domain.model.object_classification import ObjectClassification, AngularSize


@pytest.fixture
def in_memory_db():
    """Create an in-memory SQLite database for testing."""
    engine = create_engine('sqlite:///:memory:', echo=False)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session


@pytest.fixture
def mock_catalog_service():
    """Create a mock CatalogService."""
    mock = Mock()
    
    # Set up mock return values for common objects
    m31 = CelestialObject(
        name="Andromeda Galaxy",
        canonical_id="NGC0224",
        classification=ObjectClassification("galaxy", "spiral"),
        magnitude=3.44,
        size=AngularSize(178.0, 63.0),
        ra=10.68,
        dec=41.27
    )
    
    m42 = CelestialObject(
        name="Orion Nebula",
        canonical_id="NGC1976",
        classification=ObjectClassification("nebula", "emission"),
        magnitude=4.0,
        size=AngularSize(65.0, 60.0),
        ra=83.82,
        dec=-5.39
    )
    
    def get_object_side_effect(name):
        lookup = {
            "M31": m31,
            "NGC0224": m31,
            "M42": m42,
            "NGC1976": m42,
        }
        return lookup.get(name)
    
    mock.get_object = Mock(side_effect=get_object_side_effect)
    return mock


class TestTargetListRepository:
    """Tests for TargetListRepository."""

    def test_create_target_list(self, in_memory_db):
        """Test creating a target list."""
        repo = TargetListRepository()
        
        with in_memory_db() as session:
            target_list = TargetList(
                name="Test List",
                description="A test list",
                category="custom"
            )
            result = repo.add(session, target_list)
            session.commit()
            
            assert result.id is not None
            assert result.name == "Test List"
            assert result.description == "A test list"
            assert result.category == "custom"

    def test_get_all_lists(self, in_memory_db):
        """Test retrieving all target lists."""
        repo = TargetListRepository()
        
        with in_memory_db() as session:
            # Create two lists
            repo.add(session, TargetList(name="List 1"))
            repo.add(session, TargetList(name="List 2"))
            session.commit()
            
            lists = repo.get_all(session)
            assert len(lists) == 2

    def test_add_item_to_list(self, in_memory_db):
        """Test adding an item to a target list."""
        repo = TargetListRepository()
        
        with in_memory_db() as session:
            # Create a list
            target_list = TargetList(name="My List")
            repo.add(session, target_list)
            session.flush()
            
            # Add an item
            item = TargetListItem(
                list_id=target_list.id,
                object_name="M31",
                canonical_id="NGC0224",
                object_type="galaxy",
                magnitude=3.44
            )
            result = repo.add_item(session, item)
            session.commit()
            
            assert result.id is not None
            assert result.object_name == "M31"
            assert result.sort_order == 0

    def test_add_multiple_items_increments_sort_order(self, in_memory_db):
        """Test that adding items increments sort_order."""
        repo = TargetListRepository()
        
        with in_memory_db() as session:
            target_list = TargetList(name="My List")
            repo.add(session, target_list)
            session.flush()
            
            item1 = TargetListItem(list_id=target_list.id, object_name="M31")
            item2 = TargetListItem(list_id=target_list.id, object_name="M42")
            item3 = TargetListItem(list_id=target_list.id, object_name="M45")
            
            repo.add_item(session, item1)
            repo.add_item(session, item2)
            repo.add_item(session, item3)
            session.commit()
            
            items = repo.get_items_for_list(session, target_list.id)
            assert len(items) == 3
            assert items[0].sort_order == 0
            assert items[1].sort_order == 1
            assert items[2].sort_order == 2

    def test_mark_item_observed(self, in_memory_db):
        """Test marking an item as observed."""
        repo = TargetListRepository()
        
        with in_memory_db() as session:
            target_list = TargetList(name="My List")
            repo.add(session, target_list)
            session.flush()
            
            item = TargetListItem(list_id=target_list.id, object_name="M31")
            repo.add_item(session, item)
            session.flush()
            
            # Mark as observed
            observed_date = datetime.now(timezone.utc)
            repo.mark_observed(session, item.id, True, observed_date, "Great view!")
            session.commit()
            
            # Verify
            updated_item = repo.get_item_by_id(session, item.id)
            assert updated_item.observed is True
            assert updated_item.observed_date is not None
            assert updated_item.notes == "Great view!"

    def test_delete_list_cascades_to_items(self, in_memory_db):
        """Test that deleting a list also deletes its items."""
        repo = TargetListRepository()
        
        with in_memory_db() as session:
            target_list = TargetList(name="My List")
            repo.add(session, target_list)
            session.flush()
            
            item = TargetListItem(list_id=target_list.id, object_name="M31")
            repo.add_item(session, item)
            session.commit()
            
            list_id = target_list.id
            item_id = item.id
            
            # Delete the list
            repo.delete(session, list_id)
            session.commit()
            
            # Verify list and item are gone
            assert repo.get_by_id(session, list_id) is None
            assert repo.get_item_by_id(session, item_id) is None

    def test_item_exists_in_list(self, in_memory_db):
        """Test checking if an item exists in a list."""
        repo = TargetListRepository()
        
        with in_memory_db() as session:
            target_list = TargetList(name="My List")
            repo.add(session, target_list)
            session.flush()
            
            item = TargetListItem(
                list_id=target_list.id,
                object_name="M31",
                canonical_id="NGC0224"
            )
            repo.add_item(session, item)
            session.commit()
            
            # Check existence
            assert repo.item_exists_in_list(session, target_list.id, "NGC0224") is True
            assert repo.item_exists_in_list(session, target_list.id, "NGC9999") is False


class TestTargetListServiceMocked:
    """Tests for TargetListService with mocked dependencies."""

    @patch('app.orm.services.target_list_service.session_scope')
    def test_add_object_resolves_via_catalog(self, mock_session_scope, mock_catalog_service):
        """Test that add_object uses catalog service to resolve objects."""
        # Setup mock session
        mock_session = MagicMock()
        mock_session_scope.return_value.__enter__.return_value = mock_session
        
        # Create service with mock catalog
        service = TargetListService(catalog_service=mock_catalog_service)
        service.repository = Mock()
        service.repository.item_exists_in_list.return_value = False
        service.repository.add_item.return_value = TargetListItem(
            id=1, list_id=1, object_name="Andromeda Galaxy"
        )
        
        # Add object
        result = service.add_object(list_id=1, object_name="M31")
        
        # Verify catalog was called
        mock_catalog_service.get_object.assert_called_once_with("M31")
        assert result is not None

    @patch('app.orm.services.target_list_service.session_scope')
    def test_add_object_returns_none_for_unknown_object(self, mock_session_scope, mock_catalog_service):
        """Test that add_object returns None for unknown objects."""
        service = TargetListService(catalog_service=mock_catalog_service)
        
        # Try to add unknown object
        result = service.add_object(list_id=1, object_name="UnknownObject123")
        
        # Should return None
        assert result is None
        mock_catalog_service.get_object.assert_called_once_with("UnknownObject123")
