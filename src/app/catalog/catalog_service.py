"""
Catalog service - high-level interface for object resolution and retrieval.

Implements the research-validated decision tree:
1. Name resolution: Solar System → OpenNGC → SIMBAD
2. Object retrieval: OpenNGC primary → SIMBAD fallback → Horizons for Solar System
3. Surface brightness: Direct (OpenNGC/Horizons) → Computed fallback

This service abstracts catalog complexity from domain code.
"""
import logging
from typing import Optional
from pathlib import Path

from app.catalog.providers.openngc_provider import OpenNGCProvider
from app.catalog.providers.simbad_provider import SimbadProvider
from app.catalog.providers.horizons_provider import HorizonsProvider
from app.domain.model.celestial_object import CelestialObject
from app.catalog.interfaces import CatalogSource

try:
    from app.config.autowire import component
except ImportError:
    # For testing environments without dependency injection
    def component(cls):
        return cls

logger = logging.getLogger(__name__)


@component
class CatalogService:
    """
    High-level catalog service implementing multi-source strategy.

    Used by domain code to fetch celestial objects without needing
    to know about specific catalog APIs.
    """

    def __init__(self):
        """
        Initialize catalog service with default providers.

        Simplified initialization that creates providers directly.
        """
        # Initialize providers
        ngc_path = Path(__file__).parent.parent.parent.parent / 'data' / 'catalogs' / 'NGC.csv'
        
        if not ngc_path.exists():
            logger.error(f"NGC.csv not found at: {ngc_path}")
            raise FileNotFoundError(f"NGC catalog file not found: {ngc_path}")
        
        logger.debug(f"Loading NGC catalog from: {ngc_path}")
        self.openngc = OpenNGCProvider(ngc_path)
        self.simbad = SimbadProvider()
        self.horizons = HorizonsProvider()

        # Solar System object names
        self.solar_system_names = {
            'mercury', 'venus', 'mars', 'jupiter', 'saturn',
            'uranus', 'neptune', 'moon', 'sun'
        }

    def _select_providers(self, name: str) -> list[CatalogSource]:
        """
        Select which providers to try based on object name.

        Args:
            name: Object name

        Returns:
            List of CatalogSource enum values in priority order
        """
        name_lower = name.lower().strip()

        # Solar System objects → Horizons only
        if name_lower in self.solar_system_names:
            return [CatalogSource.HORIZONS]

        # NGC/IC/Messier → OpenNGC first, then SIMBAD fallback
        if any(name_lower.startswith(prefix) for prefix in ['ngc', 'ic', 'm', 'messier']):
            return [CatalogSource.OPENNGC, CatalogSource.SIMBAD]

        # Everything else → SIMBAD (comprehensive name resolver)
        return [CatalogSource.SIMBAD]

    def resolve_canonical_id(self, name: str) -> Optional[str]:
        """Alias for resolve_name for compatibility"""
        return self.resolve_name(name)

    def resolve_name(self, name: str) -> Optional[str]:
        """
        Resolve user input to canonical identifier.

        DECISION TREE (from research):
        1. If looks like Solar System object → Horizons
        2. If looks like NGC/IC/M → OpenNGC
        3. Else fallback → SIMBAD (comprehensive name resolver)

        Args:
            name: User input (e.g., "M31", "Andromeda", "Jupiter")

        Returns:
            Canonical identifier or None
        """
        providers = self._select_providers(name)

        for source in providers:
            if source == CatalogSource.OPENNGC:
                canonical_id = self.openngc.resolve_name(name)
                if canonical_id:
                    return canonical_id
            elif source == CatalogSource.SIMBAD:
                canonical_id = self.simbad.resolve_name(name)
                if canonical_id:
                    return canonical_id
            elif source == CatalogSource.HORIZONS:
                # For Horizons, the name itself is the canonical ID
                return name

        return None

    def get_object(self, identifier: str, time: Optional[object] = None) -> Optional[CelestialObject]:
        """
        Retrieve object with multi-source fallback strategy.

        RETRIEVAL STRATEGY (from research):
        1. Try to resolve name if not already canonical
        2. Determine object type (Solar System vs DSO)
        3. For DSOs: Try OpenNGC first, fallback to SIMBAD
        4. For Solar System: Use Horizons with current ephemeris

        Args:
            identifier: Object identifier (can be M31, NGC0224, Jupiter, etc.)
            time: Optional observation time (for Horizons)

        Returns:
            CelestialObject or None
        """
        # Try to get object directly first
        providers = self._select_providers(identifier)

        for source in providers:
            try:
                if source == CatalogSource.OPENNGC:
                    obj = self.openngc.get_object(identifier)
                    if obj:
                        return obj
                elif source == CatalogSource.SIMBAD:
                    obj = self.simbad.get_object(identifier)
                    if obj:
                        return obj
                elif source == CatalogSource.HORIZONS:
                    obj = self.horizons.get_object(identifier, time)
                    if obj:
                        return obj
            except Exception as e:
                # Log the exception for debugging
                logger.debug(f"Provider {source} failed for '{identifier}': {e}")
                continue

        # If direct fetch failed, try resolving name first
        canonical_id = self.resolve_name(identifier)
        if canonical_id and canonical_id != identifier:
            logger.debug(f"Resolved '{identifier}' to canonical_id '{canonical_id}'")
            # Try again with canonical ID
            for source in providers:
                try:
                    if source == CatalogSource.OPENNGC:
                        obj = self.openngc.get_object(canonical_id)
                        if obj:
                            return obj
                    elif source == CatalogSource.SIMBAD:
                        obj = self.simbad.get_object(canonical_id)
                        if obj:
                            return obj
                    elif source == CatalogSource.HORIZONS:
                        obj = self.horizons.get_object(canonical_id, time)
                        if obj:
                            return obj
                except Exception as e:
                    logger.debug(f"Provider {source} failed for canonical '{canonical_id}': {e}")
                    continue

        logger.debug(f"Could not resolve object: '{identifier}'")
        return None

    def get_objects(self, identifiers: list[str]) -> dict[str, Optional[CelestialObject]]:
        """
        Batch retrieve multiple objects.

        Args:
            identifiers: List of canonical identifiers

        Returns:
            Dict mapping identifier → CelestialObject (or None if not found)
        """
        results = {}
        for identifier in identifiers:
            results[identifier] = self.get_object(identifier)
        return results

    def filter_by_type(self, primary_type: str, subtype: Optional[str] = None) -> list[CelestialObject]:
        """
        Filter objects by classification type.

        Args:
            primary_type: Primary classification (e.g., 'galaxy', 'nebula')
            subtype: Optional subtype (e.g., 'spiral', 'emission')

        Returns:
            List of matching CelestialObjects
        """
        # This would require catalog-wide queries, not implemented yet
        raise NotImplementedError("Type filtering requires full catalog implementation")

    def filter_by_magnitude(self, max_mag: float) -> list[CelestialObject]:
        """
        Filter objects by maximum magnitude.

        Args:
            max_mag: Maximum magnitude (brighter objects have lower magnitudes)

        Returns:
            List of CelestialObjects brighter than max_mag
        """
        # This would require catalog-wide queries, not implemented yet
        raise NotImplementedError("Magnitude filtering requires full catalog implementation")

    def search_by_prefix(self, prefix: str) -> list[CelestialObject]:
        """
        Search objects by name prefix.

        Args:
            prefix: Name prefix (e.g., 'NGC7')

        Returns:
            List of matching CelestialObjects
        """
        # This would require catalog-wide queries, not implemented yet
        raise NotImplementedError("Prefix search requires full catalog implementation")
