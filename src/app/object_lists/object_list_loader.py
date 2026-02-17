"""
ObjectListLoader service for loading and resolving pre-curated object lists.

Loads JSON files from data/object_lists/ and resolves objects via CatalogService.
Includes in-memory caching for resolved objects (session-scoped).

Note: This cache is temporary; Phase 9.2+ will introduce SQLite persistence.
"""
import json
import logging
from pathlib import Path
from typing import Optional

from app.object_lists.models import (
    ObjectList,
    ObjectListMetadata,
    ObjectListItem,
    ResolutionResult,
    ResolutionFailure,
)
from app.domain.model.celestial_object import CelestialObject
from app.catalog.catalog_service import CatalogService

try:
    from app.config.autowire import component
except ImportError:
    def component(cls):
        return cls

logger = logging.getLogger(__name__)


@component
class ObjectListLoader:
    """
    Load and manage pre-curated object lists from JSON files.
    
    Provides:
    - Discovery of available lists
    - Loading list data from JSON
    - Resolution of objects via CatalogService with in-memory caching
    
    Cache Strategy (Phase 9.1):
    - Simple dict cache keyed by canonical_id
    - Session-scoped (cleared on app restart)
    - Will be replaced by SQLite cache in Phase 9.2+
    """

    def __init__(
        self,
        lists_dir: Optional[Path] = None,
        catalog_service: Optional[CatalogService] = None
    ):
        """
        Initialize ObjectListLoader.
        
        Args:
            lists_dir: Directory containing JSON list files.
                       Defaults to data/object_lists/
            catalog_service: CatalogService for object resolution.
                            Created lazily if not provided.
        """
        if lists_dir is None:
            # Default: project_root/data/object_lists/
            lists_dir = Path(__file__).parent.parent.parent.parent / 'data' / 'object_lists'
        
        self.lists_dir = lists_dir
        self._catalog_service = catalog_service
        
        # In-memory cache for resolved objects (Phase 9.1 temporary solution)
        # Key: canonical_id, Value: CelestialObject
        # Note: Will be replaced by SQLite persistence in Phase 9.2+
        self._resolution_cache: dict[str, CelestialObject] = {}

    @property
    def catalog_service(self) -> CatalogService:
        """Lazy initialization of CatalogService"""
        if self._catalog_service is None:
            self._catalog_service = CatalogService()
        return self._catalog_service

    def get_available_lists(self) -> list[ObjectListMetadata]:
        """
        Scan directory and return metadata for all available lists.
        
        Returns:
            List of ObjectListMetadata sorted by name
        """
        if not self.lists_dir.exists():
            logger.warning(f"Object lists directory not found: {self.lists_dir}")
            return []

        metadata_list = []
        for json_file in self.lists_dir.glob('*.json'):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                list_id = json_file.stem  # filename without .json
                metadata = ObjectListMetadata.from_dict(data, list_id)
                metadata_list.append(metadata)
            except (json.JSONDecodeError, IOError) as e:
                logger.error(f"Failed to load list metadata from {json_file}: {e}")
                continue

        # Sort by display name
        return sorted(metadata_list, key=lambda m: m.name)

    def load_list(self, list_id: str) -> ObjectList:
        """
        Load a specific list from JSON file.
        
        Args:
            list_id: List identifier (filename without .json)
            
        Returns:
            ObjectList with metadata and items
            
        Raises:
            FileNotFoundError: If list file doesn't exist
            ValueError: If JSON is invalid
        """
        json_path = self.lists_dir / f"{list_id}.json"
        
        if not json_path.exists():
            raise FileNotFoundError(f"Object list not found: {list_id}")

        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in {list_id}.json: {e}")

        return ObjectList.from_dict(data, list_id)

    def resolve_objects(
        self,
        object_list: ObjectList,
        progress_callback: Optional[callable] = None
    ) -> ResolutionResult:
        """
        Resolve object names to full CelestialObject instances.
        
        Resolution strategy:
        1. Check in-memory cache first
        2. Try canonical_id via CatalogService.get_object()
        3. Fall back to name if canonical_id fails
        4. Cache successful resolutions
        
        Args:
            object_list: ObjectList to resolve
            progress_callback: Optional callback(current, total) for progress updates
            
        Returns:
            ResolutionResult with resolved objects and failures
        """
        resolved: list[CelestialObject] = []
        failures: list[ResolutionFailure] = []
        total = len(object_list.objects)

        for i, item in enumerate(object_list.objects):
            # Progress callback
            if progress_callback:
                progress_callback(i + 1, total)

            # Try cache first
            cached = self._resolution_cache.get(item.canonical_id)
            if cached is not None:
                resolved.append(cached)
                continue

            # Try resolution
            obj = self._resolve_single_object(item)
            
            if obj is not None:
                # Cache and add to resolved
                self._resolution_cache[item.canonical_id] = obj
                resolved.append(obj)
            else:
                # Record failure
                failures.append(ResolutionFailure(
                    name=item.name,
                    canonical_id=item.canonical_id,
                    reason=f"Not found in catalog (tried: {item.canonical_id}, {item.name})"
                ))

        return ResolutionResult(resolved=resolved, failures=failures)

    def _resolve_single_object(self, item: ObjectListItem) -> Optional[CelestialObject]:
        """
        Attempt to resolve a single object list item.
        
        Args:
            item: ObjectListItem to resolve
            
        Returns:
            CelestialObject if found, None otherwise
        """
        # Try canonical_id first
        try:
            obj = self.catalog_service.get_object(item.canonical_id)
            if obj is not None:
                logger.debug(f"Resolved {item.name} via canonical_id '{item.canonical_id}' -> {obj.name}")
                return obj
        except Exception as e:
            logger.warning(f"Exception resolving {item.name} via canonical_id '{item.canonical_id}': {e}")

        # Fall back to name if different from canonical_id
        if item.name != item.canonical_id:
            try:
                obj = self.catalog_service.get_object(item.name)
                if obj is not None:
                    logger.debug(f"Resolved {item.name} via name fallback -> {obj.name}")
                    return obj
            except Exception as e:
                logger.warning(f"Exception resolving {item.name} via name: {e}")

        logger.warning(f"Failed to resolve: {item.name} (canonical_id: {item.canonical_id})")
        return None

    def clear_cache(self) -> None:
        """Clear the in-memory resolution cache."""
        self._resolution_cache.clear()
        logger.debug("Object resolution cache cleared")

    def get_cache_stats(self) -> dict:
        """
        Get cache statistics for debugging.
        
        Returns:
            Dict with cache_size and cached_ids
        """
        return {
            'cache_size': len(self._resolution_cache),
            'cached_ids': list(self._resolution_cache.keys())
        }
