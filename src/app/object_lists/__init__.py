"""
Object Lists module for pre-curated celestial object lists.

Phase 9.1: Pre-Curated Object Lists
- Messier, Caldwell, Solar System catalogs
- JSON-based storage in data/object_lists/
- Resolution via CatalogService
"""
from .models import ObjectList, ObjectListMetadata, ObjectListItem, ResolutionResult, ResolutionFailure
from .object_list_loader import ObjectListLoader

__all__ = [
    'ObjectList',
    'ObjectListMetadata',
    'ObjectListItem',
    'ResolutionResult',
    'ResolutionFailure',
    'ObjectListLoader',
]
