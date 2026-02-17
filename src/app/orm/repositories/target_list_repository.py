"""
Repository for TargetList and TargetListItem persistence.

Phase 9.2: Custom target list management.
"""
import logging
from typing import Optional
from datetime import datetime, timezone

from sqlalchemy import Column
from sqlalchemy.orm import Session

from app.orm.model.entities import TargetList, TargetListItem
from app.utils.orm_util import eager_load_all_relationships

logger = logging.getLogger(__name__)


class TargetListRepository:
    """
    Repository for TargetList CRUD operations.
    
    Handles persistence of user-created target lists and their items.
    """

    def __init__(self):
        self.entity = TargetList

    # ----- TargetList CRUD -----

    def add(self, session: Session, target_list: TargetList) -> TargetList:
        """Add a new target list."""
        session.add(target_list)
        session.flush()
        return target_list

    def get_all(self, session: Session) -> list[TargetList]:
        """Get all target lists with their items."""
        load_options = eager_load_all_relationships(TargetList)
        return session.query(TargetList).options(*load_options).order_by(TargetList.name).all()

    def get_by_id(self, session: Session, list_id: int) -> Optional[TargetList]:
        """Get a target list by ID with all items."""
        load_options = eager_load_all_relationships(TargetList)
        return session.query(TargetList).filter(TargetList.id == list_id).options(*load_options).first()

    def get_by_name(self, session: Session, name: str) -> Optional[TargetList]:
        """Get a target list by name."""
        load_options = eager_load_all_relationships(TargetList)
        return session.query(TargetList).filter(TargetList.name == name).options(*load_options).first()

    def update(self, session: Session, list_id: int, name: str, description: Optional[str]) -> TargetList:
        """Update target list metadata."""
        target_list = self.get_by_id(session, list_id)
        if not target_list:
            raise ValueError(f"TargetList with ID {list_id} not found")
        
        target_list.name = name
        target_list.description = description
        target_list.modified_at = datetime.now(timezone.utc)
        return target_list

    def delete(self, session: Session, list_id: int) -> None:
        """Delete a target list and all its items (cascade)."""
        target_list = self.get_by_id(session, list_id)
        if target_list:
            session.delete(target_list)

    # ----- TargetListItem CRUD -----

    def add_item(self, session: Session, item: TargetListItem) -> TargetListItem:
        """Add an item to a target list."""
        # Set sort_order to end of list
        max_order = session.query(TargetListItem.sort_order)\
            .filter(TargetListItem.list_id == item.list_id)\
            .order_by(TargetListItem.sort_order.desc())\
            .first()
        item.sort_order = (max_order[0] + 1) if max_order else 0
        
        session.add(item)
        session.flush()
        
        # Update list modified_at
        self._touch_list(session, item.list_id)
        
        return item

    def add_items(self, session: Session, items: list[TargetListItem]) -> list[TargetListItem]:
        """Add multiple items to a target list."""
        if not items:
            return []
        
        list_id = items[0].list_id
        
        # Get current max sort_order
        max_order = session.query(TargetListItem.sort_order)\
            .filter(TargetListItem.list_id == list_id)\
            .order_by(TargetListItem.sort_order.desc())\
            .first()
        start_order = (max_order[0] + 1) if max_order else 0
        
        for i, item in enumerate(items):
            item.sort_order = start_order + i
            session.add(item)
        
        session.flush()
        self._touch_list(session, list_id)
        
        return items

    def get_item_by_id(self, session: Session, item_id: int) -> Optional[TargetListItem]:
        """Get a target list item by ID."""
        return session.query(TargetListItem).filter(TargetListItem.id == item_id).first()

    def get_items_for_list(self, session: Session, list_id: int) -> list[TargetListItem]:
        """Get all items for a target list, ordered by sort_order."""
        return session.query(TargetListItem)\
            .filter(TargetListItem.list_id == list_id)\
            .order_by(TargetListItem.sort_order)\
            .all()

    def remove_item(self, session: Session, item_id: int) -> None:
        """Remove an item from a target list."""
        item = self.get_item_by_id(session, item_id)
        if item:
            list_id = item.list_id
            session.delete(item)
            self._touch_list(session, list_id)

    def update_item(self, session: Session, item_id: int, **kwargs) -> TargetListItem:
        """Update item fields."""
        item = self.get_item_by_id(session, item_id)
        if not item:
            raise ValueError(f"TargetListItem with ID {item_id} not found")
        
        for key, value in kwargs.items():
            if hasattr(item, key):
                setattr(item, key, value)
        
        self._touch_list(session, item.list_id)
        return item

    def mark_observed(self, session: Session, item_id: int, observed: bool, 
                      observed_date: Optional[datetime] = None, notes: Optional[str] = None) -> TargetListItem:
        """Mark an item as observed or unobserved."""
        item = self.get_item_by_id(session, item_id)
        if not item:
            raise ValueError(f"TargetListItem with ID {item_id} not found")
        
        item.observed = observed
        item.observed_date = observed_date if observed else None
        if notes is not None:
            item.notes = notes
        
        self._touch_list(session, item.list_id)
        return item

    def reorder_items(self, session: Session, list_id: int, item_ids_in_order: list[int]) -> None:
        """Reorder items in a list."""
        for i, item_id in enumerate(item_ids_in_order):
            session.query(TargetListItem)\
                .filter(TargetListItem.id == item_id)\
                .update({TargetListItem.sort_order: i})
        
        self._touch_list(session, list_id)

    def item_exists_in_list(self, session: Session, list_id: int, canonical_id: str) -> bool:
        """Check if an object already exists in a list."""
        return session.query(TargetListItem)\
            .filter(TargetListItem.list_id == list_id)\
            .filter(TargetListItem.canonical_id == canonical_id)\
            .first() is not None

    def _touch_list(self, session: Session, list_id: int) -> None:
        """Update the modified_at timestamp of a list."""
        session.query(TargetList)\
            .filter(TargetList.id == list_id)\
            .update({TargetList.modified_at: datetime.now(timezone.utc)})
