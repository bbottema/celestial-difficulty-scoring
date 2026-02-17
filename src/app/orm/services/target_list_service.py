"""
Service layer for TargetList management.

Phase 9.2: Custom target list management with object resolution.
"""
import logging
from typing import Optional
from datetime import datetime, timezone

from app.config.database import session_scope
from app.config.event_bus_config import bus, NightGuideEvent
from app.orm.model.entities import TargetList, TargetListItem
from app.orm.repositories.target_list_repository import TargetListRepository
from app.catalog.catalog_service import CatalogService
from app.domain.model.celestial_object import CelestialObject

try:
    from app.config.autowire import component
except ImportError:
    def component(cls):
        return cls

logger = logging.getLogger(__name__)


@component
class TargetListService:
    """
    Service for managing user target lists.
    
    Handles business logic for:
    - Creating and managing target lists
    - Adding objects with automatic resolution
    - Tracking observation status
    - Event bus notifications
    """

    def __init__(self, catalog_service: Optional[CatalogService] = None):
        self.repository = TargetListRepository()
        self._catalog_service = catalog_service

    @property
    def catalog_service(self) -> CatalogService:
        """Lazy initialization of CatalogService."""
        if self._catalog_service is None:
            self._catalog_service = CatalogService()
        return self._catalog_service

    # ----- List Operations -----

    def create_list(self, name: str, description: Optional[str] = None, 
                    category: str = 'custom') -> TargetList:
        """
        Create a new target list.
        
        Args:
            name: Unique name for the list
            description: Optional description
            category: 'custom', 'imported', or 'generated'
            
        Returns:
            Created TargetList
            
        Raises:
            ValueError: If name already exists
        """
        with session_scope() as session:
            # Check for duplicate name
            existing = self.repository.get_by_name(session, name)
            if existing:
                raise ValueError(f"A list named '{name}' already exists")
            
            target_list = TargetList(
                name=name,
                description=description,
                category=category,
                created_at=datetime.now(timezone.utc),
                modified_at=datetime.now(timezone.utc)
            )
            
            result = self.repository.add(session, target_list)
            session.commit()
            
            bus.emit(NightGuideEvent.TARGET_LIST_CREATED, result)
            logger.info(f"Created target list: {name}")
            
            return result

    def get_all_lists(self) -> list[TargetList]:
        """Get all target lists with metadata."""
        with session_scope() as session:
            return self.repository.get_all(session)

    def get_list(self, list_id: int) -> Optional[TargetList]:
        """Get a target list by ID with all items."""
        with session_scope() as session:
            return self.repository.get_by_id(session, list_id)

    def get_list_by_name(self, name: str) -> Optional[TargetList]:
        """Get a target list by name."""
        with session_scope() as session:
            return self.repository.get_by_name(session, name)

    def update_list(self, list_id: int, name: str, description: Optional[str] = None) -> TargetList:
        """Update target list name and description."""
        with session_scope() as session:
            # Check for duplicate name (excluding self)
            existing = self.repository.get_by_name(session, name)
            if existing and existing.id != list_id:
                raise ValueError(f"A list named '{name}' already exists")
            
            result = self.repository.update(session, list_id, name, description)
            session.commit()
            
            bus.emit(NightGuideEvent.TARGET_LIST_UPDATED, result)
            return result

    def delete_list(self, list_id: int) -> None:
        """Delete a target list and all its items."""
        with session_scope() as session:
            target_list = self.repository.get_by_id(session, list_id)
            if target_list:
                name = target_list.name
                self.repository.delete(session, list_id)
                session.commit()
                
                bus.emit(NightGuideEvent.TARGET_LIST_DELETED, {'id': list_id, 'name': name})
                logger.info(f"Deleted target list: {name}")

    def copy_list(self, list_id: int, new_name: str) -> TargetList:
        """Create a copy of a target list with a new name."""
        with session_scope() as session:
            source_list = self.repository.get_by_id(session, list_id)
            if not source_list:
                raise ValueError(f"TargetList with ID {list_id} not found")
            
            # Create new list
            new_list = TargetList(
                name=new_name,
                description=f"Copy of {source_list.name}",
                category=source_list.category,
                created_at=datetime.now(timezone.utc),
                modified_at=datetime.now(timezone.utc)
            )
            new_list = self.repository.add(session, new_list)
            session.flush()
            
            # Copy items
            for item in source_list.items:
                new_item = TargetListItem(
                    list_id=new_list.id,
                    object_name=item.object_name,
                    canonical_id=item.canonical_id,
                    object_type=item.object_type,
                    ra=item.ra,
                    dec=item.dec,
                    magnitude=item.magnitude,
                    observed=False,  # Reset observed status
                    sort_order=item.sort_order
                )
                session.add(new_item)
            
            session.commit()
            
            bus.emit(NightGuideEvent.TARGET_LIST_CREATED, new_list)
            logger.info(f"Copied target list '{source_list.name}' to '{new_name}'")
            
            return new_list

    # ----- Item Operations -----

    def add_object(self, list_id: int, object_name: str) -> Optional[TargetListItem]:
        """
        Add an object to a target list by name.
        
        Resolves the object via CatalogService and stores resolved data.
        
        Args:
            list_id: Target list ID
            object_name: Object name or identifier (e.g., "M31", "NGC 7000")
            
        Returns:
            Created TargetListItem, or None if resolution failed
        """
        # Resolve object
        celestial_obj = self.catalog_service.get_object(object_name)
        if not celestial_obj:
            logger.warning(f"Could not resolve object: {object_name}")
            return None
        
        return self.add_resolved_object(list_id, celestial_obj)

    def add_resolved_object(self, list_id: int, celestial_obj: CelestialObject) -> TargetListItem:
        """
        Add an already-resolved CelestialObject to a target list.
        
        Args:
            list_id: Target list ID
            celestial_obj: Resolved CelestialObject
            
        Returns:
            Created TargetListItem
        """
        with session_scope() as session:
            # Check if already in list
            if self.repository.item_exists_in_list(session, list_id, celestial_obj.canonical_id):
                raise ValueError(f"'{celestial_obj.name}' is already in this list")
            
            # Extract size as float
            size_val = None
            if celestial_obj.size:
                size_val = celestial_obj.size.major_arcmin if hasattr(celestial_obj.size, 'major_arcmin') else celestial_obj.size
            
            item = TargetListItem(
                list_id=list_id,
                object_name=celestial_obj.name,
                canonical_id=celestial_obj.canonical_id,
                object_type=celestial_obj.object_type,
                ra=celestial_obj.ra,
                dec=celestial_obj.dec,
                magnitude=celestial_obj.magnitude if celestial_obj.magnitude < 99 else None
            )
            
            result = self.repository.add_item(session, item)
            session.commit()
            
            bus.emit(NightGuideEvent.TARGET_LIST_ITEM_ADDED, result)
            logger.debug(f"Added '{celestial_obj.name}' to list {list_id}")
            
            return result

    def add_objects_batch(self, list_id: int, object_names: list[str]) -> tuple[list[TargetListItem], list[str]]:
        """
        Add multiple objects to a target list.
        
        Args:
            list_id: Target list ID
            object_names: List of object names to add
            
        Returns:
            Tuple of (successfully added items, failed object names)
        """
        added = []
        failed = []
        
        for name in object_names:
            try:
                item = self.add_object(list_id, name)
                if item:
                    added.append(item)
                else:
                    failed.append(name)
            except ValueError as e:
                logger.warning(f"Failed to add '{name}': {e}")
                failed.append(name)
        
        return added, failed

    def remove_object(self, item_id: int) -> None:
        """Remove an object from a target list."""
        with session_scope() as session:
            item = self.repository.get_item_by_id(session, item_id)
            if item:
                self.repository.remove_item(session, item_id)
                session.commit()
                
                bus.emit(NightGuideEvent.TARGET_LIST_ITEM_REMOVED, {'id': item_id})

    def mark_observed(self, item_id: int, observed: bool = True, 
                      notes: Optional[str] = None) -> TargetListItem:
        """
        Mark an item as observed or unobserved.
        
        Args:
            item_id: Target list item ID
            observed: True to mark as observed, False to unmark
            notes: Optional observation notes
            
        Returns:
            Updated TargetListItem
        """
        with session_scope() as session:
            observed_date = datetime.now(timezone.utc) if observed else None
            result = self.repository.mark_observed(session, item_id, observed, observed_date, notes)
            session.commit()
            
            bus.emit(NightGuideEvent.TARGET_LIST_ITEM_UPDATED, result)
            return result

    def reorder_items(self, list_id: int, item_ids_in_order: list[int]) -> None:
        """Reorder items in a list."""
        with session_scope() as session:
            self.repository.reorder_items(session, list_id, item_ids_in_order)
            session.commit()
            
            bus.emit(NightGuideEvent.TARGET_LIST_UPDATED, {'id': list_id})

    def get_unobserved_items(self, list_id: int) -> list[TargetListItem]:
        """Get only unobserved items from a list."""
        with session_scope() as session:
            items = self.repository.get_items_for_list(session, list_id)
            return [item for item in items if not item.observed]
