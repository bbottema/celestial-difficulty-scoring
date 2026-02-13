"""
Data models for pre-curated object lists.

These models represent the JSON structure for object list files
stored in data/object_lists/*.json
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from app.domain.model.celestial_object import CelestialObject


@dataclass
class ObjectListItem:
    """
    A single object entry in a pre-curated list.
    
    Attributes:
        name: Display name (e.g., "M31", "Crab Nebula")
        canonical_id: ID for CatalogService lookup (e.g., "NGC0224", "Jupiter")
        object_type: Classification hint (e.g., "galaxy", "planet")
        ra: Right Ascension in decimal degrees (J2000)
        dec: Declination in decimal degrees (J2000)
        magnitude: Visual magnitude
    """
    name: str
    canonical_id: str
    object_type: str = "unknown"
    ra: float = 0.0
    dec: float = 0.0
    magnitude: float = 99.0

    @classmethod
    def from_dict(cls, data: dict) -> 'ObjectListItem':
        """Create ObjectListItem from JSON dict"""
        return cls(
            name=data.get('name', ''),
            canonical_id=data.get('canonical_id', ''),
            object_type=data.get('type', 'unknown'),
            ra=float(data.get('ra', 0.0)),
            dec=float(data.get('dec', 0.0)),
            magnitude=float(data.get('magnitude', 99.0))
        )


@dataclass
class ObjectListMetadata:
    """
    Metadata for an object list (displayed in UI dropdown).
    
    Attributes:
        list_id: Unique identifier (filename without .json)
        name: Human-readable name
        description: Brief description
        category: Classification (named_catalog, seasonal, equipment_specific)
        version: Data version for future updates
        object_count: Number of objects in the list
    """
    list_id: str
    name: str
    description: str = ""
    category: str = "named_catalog"
    version: str = "1.0"
    object_count: int = 0

    @classmethod
    def from_dict(cls, data: dict, list_id: str) -> 'ObjectListMetadata':
        """Create ObjectListMetadata from JSON dict"""
        objects = data.get('objects', [])
        return cls(
            list_id=list_id,
            name=data.get('name', list_id),
            description=data.get('description', ''),
            category=data.get('category', 'named_catalog'),
            version=data.get('version', '1.0'),
            object_count=len(objects)
        )


@dataclass
class ObjectList:
    """
    A complete object list with metadata and items.
    """
    metadata: ObjectListMetadata
    objects: list[ObjectListItem] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict, list_id: str) -> 'ObjectList':
        """Create ObjectList from JSON dict"""
        metadata = ObjectListMetadata.from_dict(data, list_id)
        objects = [ObjectListItem.from_dict(obj) for obj in data.get('objects', [])]
        return cls(metadata=metadata, objects=objects)


@dataclass
class ResolutionFailure:
    """
    Details about a failed object resolution.
    
    Attributes:
        name: Original object name from the list
        canonical_id: The canonical_id that was attempted
        reason: Human-readable failure reason
    """
    name: str
    canonical_id: str
    reason: str


@dataclass
class ResolutionResult:
    """
    Result of resolving objects from a list.
    
    Attributes:
        resolved: Successfully resolved CelestialObject instances
        failures: List of objects that could not be resolved
    """
    resolved: list = field(default_factory=list)  # list[CelestialObject]
    failures: list[ResolutionFailure] = field(default_factory=list)

    @property
    def success_count(self) -> int:
        return len(self.resolved)

    @property
    def failure_count(self) -> int:
        return len(self.failures)

    @property
    def total_count(self) -> int:
        return self.success_count + self.failure_count

    @property
    def success_rate(self) -> float:
        """Returns success rate as percentage (0-100)"""
        if self.total_count == 0:
            return 100.0
        return (self.success_count / self.total_count) * 100
