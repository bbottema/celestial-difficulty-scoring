"""
Catalog service interfaces and protocols.

Defines contracts for catalog providers and services to ensure
consistent behavior across different data sources.
"""
from typing import Protocol, Optional
from enum import Enum
from dataclasses import dataclass

from app.domain.model.celestial_object import CelestialObject


class CatalogSource(Enum):
    """Available catalog data sources"""
    OPENNGC = "openngc"
    SIMBAD = "simbad"
    HORIZONS = "horizons"
    SKYFIELD = "skyfield"
    WDS = "wds"


@dataclass
class ProviderDTO:
    """
    Internal DTO used between providers and adapters.

    Keeps raw API response for debugging while providing normalized access.
    """
    raw_data: dict  # Original API response
    source: str     # Provider name for provenance


class ICatalogProvider(Protocol):
    """
    Interface for all catalog providers.

    Each provider (OpenNGC, SIMBAD, Horizons, etc.) must implement this interface.
    Providers handle API-specific communication and return ProviderDTOs.
    """

    def resolve_name(self, name: str) -> Optional[str]:
        """
        Resolve user input name to canonical identifier.

        Args:
            name: User input (e.g., "M31", "Andromeda", "NGC 224")

        Returns:
            Canonical ID (e.g., "NGC 224") or None if not found
        """
        ...

    def get_object(self, identifier: str) -> Optional[CelestialObject]:
        """
        Fetch object data by canonical identifier.

        Args:
            identifier: Canonical ID from resolve_name()

        Returns:
            CelestialObject with all available fields populated
        """
        ...

    def batch_get_objects(self, identifiers: list[str]) -> list[CelestialObject]:
        """
        Fetch multiple objects efficiently (avoid N+1 problem).

        Args:
            identifiers: List of canonical IDs

        Returns:
            List of CelestialObjects (may be shorter if some not found)
        """
        ...


class ICatalogService(Protocol):
    """
    Service interface for high-level catalog operations.

    Used by domain code to fetch and enrich celestial objects without
    knowing about specific catalog sources.
    """

    def resolve_name(self, name: str) -> Optional[str]:
        """
        Resolve user input to canonical ID using decision tree:
        1. Check cache
        2. Solar System → Horizons
        3. NGC/IC/M → OpenNGC
        4. Fallback → SIMBAD

        Args:
            name: User input name

        Returns:
            Canonical identifier or None
        """
        ...

    def get_object(self, canonical_id: str,
                   prefer_source: Optional[CatalogSource] = None) -> Optional[CelestialObject]:
        """
        Retrieve object with multi-source fallback strategy:
        1. Check cache (with TTL)
        2. OpenNGC primary for DSOs
        3. SIMBAD for enrichment
        4. WDS for double stars
        5. Compute surface brightness if needed

        Args:
            canonical_id: Canonical identifier
            prefer_source: Hint for preferred data source

        Returns:
            Fully enriched CelestialObject or None
        """
        ...

    def enrich_object(self, obj: CelestialObject,
                      sources: list[CatalogSource]) -> CelestialObject:
        """
        Add missing fields from additional sources.

        Args:
            obj: Partially populated object
            sources: Data sources to query for enrichment

        Returns:
            Enriched object with additional fields populated
        """
        ...

    def batch_get_objects(self, canonical_ids: list[str]) -> list[CelestialObject]:
        """
        Efficient bulk retrieval for observing lists.

        Args:
            canonical_ids: List of canonical identifiers

        Returns:
            List of CelestialObjects
        """
        ...
