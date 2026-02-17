"""
Import/Export functionality for target lists.

Phase 9.2: CSV import/export for target lists.
"""
import csv
import logging
from pathlib import Path
from typing import Optional
from datetime import datetime

from app.orm.model.entities import TargetList, TargetListItem
from app.orm.services.target_list_service import TargetListService
from app.catalog.catalog_service import CatalogService

logger = logging.getLogger(__name__)


class TargetListImportExport:
    """
    Import and export target lists to/from various formats.
    
    Currently supports:
    - CSV export/import
    
    Future:
    - SkySafari observing list format
    - Stellarium format
    """

    def __init__(self, target_list_service: Optional[TargetListService] = None,
                 catalog_service: Optional[CatalogService] = None):
        self._target_list_service = target_list_service
        self._catalog_service = catalog_service

    @property
    def target_list_service(self) -> TargetListService:
        if self._target_list_service is None:
            self._target_list_service = TargetListService()
        return self._target_list_service

    @property
    def catalog_service(self) -> CatalogService:
        if self._catalog_service is None:
            self._catalog_service = CatalogService()
        return self._catalog_service

    def export_csv(self, target_list: TargetList, filepath: Path) -> None:
        """
        Export a target list to CSV format.
        
        CSV columns: Name, Type, RA, Dec, Magnitude, Observed, Observed Date, Notes
        
        Args:
            target_list: TargetList to export
            filepath: Path to output CSV file
        """
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Header
            writer.writerow([
                'Name', 'Canonical ID', 'Type', 'RA', 'Dec', 
                'Magnitude', 'Observed', 'Observed Date', 'Notes'
            ])
            
            # Data rows
            for item in target_list.items:
                observed_date_str = ''
                if item.observed_date:
                    observed_date_str = item.observed_date.strftime('%Y-%m-%d %H:%M')
                
                writer.writerow([
                    item.object_name,
                    item.canonical_id or '',
                    item.object_type or '',
                    f"{item.ra:.6f}" if item.ra else '',
                    f"{item.dec:.6f}" if item.dec else '',
                    f"{item.magnitude:.2f}" if item.magnitude else '',
                    'Yes' if item.observed else 'No',
                    observed_date_str,
                    item.notes or ''
                ])
        
        logger.info(f"Exported {len(target_list.items)} objects to {filepath}")

    def import_csv(self, filepath: Path, list_name: str, 
                   resolve_objects: bool = True) -> tuple[TargetList, list[str]]:
        """
        Import a target list from CSV format.
        
        Expected CSV columns (flexible):
        - Required: Name (or Object, Object Name)
        - Optional: Type, RA, Dec, Magnitude, Notes
        
        Args:
            filepath: Path to input CSV file
            list_name: Name for the new target list
            resolve_objects: Whether to resolve objects via CatalogService
            
        Returns:
            Tuple of (created TargetList, list of failed object names)
        """
        failed = []
        items_data = []
        
        with open(filepath, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            
            # Normalize header names
            fieldnames = {name.lower().strip(): name for name in reader.fieldnames or []}
            
            # Find the name column
            name_column = None
            for possible in ['name', 'object', 'object name', 'object_name', 'target']:
                if possible in fieldnames:
                    name_column = fieldnames[possible]
                    break
            
            if not name_column:
                raise ValueError("CSV must have a 'Name' or 'Object' column")
            
            for row in reader:
                object_name = row.get(name_column, '').strip()
                if not object_name:
                    continue
                
                items_data.append({
                    'name': object_name,
                    'type': row.get(fieldnames.get('type', 'Type'), ''),
                    'ra': row.get(fieldnames.get('ra', 'RA'), ''),
                    'dec': row.get(fieldnames.get('dec', 'Dec'), ''),
                    'magnitude': row.get(fieldnames.get('magnitude', 'Magnitude'), ''),
                    'notes': row.get(fieldnames.get('notes', 'Notes'), '')
                })
        
        # Create the list
        target_list = self.target_list_service.create_list(
            name=list_name,
            description=f"Imported from {filepath.name}",
            category='imported'
        )
        
        # Add objects
        for item_data in items_data:
            object_name = item_data['name']
            
            if resolve_objects:
                # Try to resolve via catalog
                celestial_obj = self.catalog_service.get_object(object_name)
                if celestial_obj:
                    try:
                        self.target_list_service.add_resolved_object(target_list.id, celestial_obj)
                    except ValueError as e:
                        logger.warning(f"Skipping duplicate: {object_name}")
                else:
                    # Add with provided data if resolution fails
                    self._add_unresolved_item(target_list.id, item_data)
                    failed.append(object_name)
            else:
                # Add with provided data without resolution
                self._add_unresolved_item(target_list.id, item_data)
        
        # Refresh the list to get all items
        target_list = self.target_list_service.get_list(target_list.id)
        
        logger.info(f"Imported {len(items_data) - len(failed)}/{len(items_data)} objects to '{list_name}'")
        
        return target_list, failed

    def _add_unresolved_item(self, list_id: int, item_data: dict) -> None:
        """Add an item without catalog resolution."""
        from app.config.database import session_scope
        from app.orm.repositories.target_list_repository import TargetListRepository
        
        repo = TargetListRepository()
        
        # Parse numeric fields
        ra = None
        dec = None
        magnitude = None
        
        try:
            if item_data.get('ra'):
                ra = float(item_data['ra'])
        except ValueError:
            pass
        
        try:
            if item_data.get('dec'):
                dec = float(item_data['dec'])
        except ValueError:
            pass
        
        try:
            if item_data.get('magnitude'):
                magnitude = float(item_data['magnitude'])
        except ValueError:
            pass
        
        with session_scope() as session:
            item = TargetListItem(
                list_id=list_id,
                object_name=item_data['name'],
                canonical_id=None,
                object_type=item_data.get('type') or None,
                ra=ra,
                dec=dec,
                magnitude=magnitude,
                notes=item_data.get('notes') or None
            )
            repo.add_item(session, item)
            session.commit()

    def export_simple_csv(self, target_list: TargetList, filepath: Path) -> None:
        """
        Export a minimal CSV with just object names.
        
        Useful for compatibility with other astronomy software.
        """
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Name'])
            for item in target_list.items:
                writer.writerow([item.object_name])
        
        logger.info(f"Exported {len(target_list.items)} object names to {filepath}")
