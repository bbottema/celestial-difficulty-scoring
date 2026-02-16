"""
SIMBAD catalog provider (online API).

SIMBAD is a comprehensive astronomical database with ~11M objects.
Provides excellent name resolution and cross-references.

Uses astroquery.simbad which queries via the SIMBAD script interface
(https://simbad.cds.unistra.fr/simbad/sim-script), NOT the TAP interface.

CRITICAL RESEARCH FINDINGS:
1. Main type can be misleading for observing (M31 → "AGN", NGC 7000 → "Cluster of Stars")
2. Must check "Other object types" for observing-relevant classifications
3. Updates daily - requires shorter cache TTL than offline catalogs
4. Rate limit: ≤6 queries/sec to avoid temporary IP blacklist
5. Excludes Solar System objects (planets, asteroids, comets)
"""
from typing import Optional
import time
import logging
from datetime import datetime, timezone

import numpy as np
from astroquery.simbad import Simbad

from app.domain.model.celestial_object import CelestialObject
from app.domain.model.object_classification import ObjectClassification, AngularSize, SurfaceBrightness
from app.domain.model.data_provenance import DataProvenance

logger = logging.getLogger(__name__)


class SimbadProvider:
    """
    SIMBAD API provider with rate limiting.

    Uses astroquery.simbad for API access (script interface, not TAP).
    Implements throttling to stay within rate limits.
    """

    def __init__(self, max_queries_per_sec: float = 5.0):
        """
        Initialize SIMBAD provider.

        Args:
            max_queries_per_sec: Rate limit (research recommends ≤6/sec)
        """
        self.max_queries_per_sec = max_queries_per_sec
        self.min_query_interval = 1.0 / max_queries_per_sec
        self._last_query_time = 0.0
        self.adapter = SimbadAdapter()

        # Initialize astroquery.simbad (uses script interface, not TAP)
        # See: https://simbad.u-strasbg.fr/Pages/guide/sim-q.htx
        self.simbad = Simbad()
        
        # Add votable fields for additional data
        # Note: "V" is the new notation for "flux(V)" since astroquery 0.4.8
        # Column names are lowercase in 0.4.8+ (except filter names like "V")
        try:
            self.simbad.add_votable_fields("otype", "dim", "morphtype", "V", "ids", "alltypes")
        except Exception as e:
            logger.warning(f"add_votable_fields failed: {e}; proceeding with defaults")
        
        # CRITICAL: ROW_LIMIT = -1 means "max capability" (unlimited)
        # ROW_LIMIT = 0 means "schema only / empty table" - this was our bug!
        self.simbad.ROW_LIMIT = -1

    def _throttle(self):
        """
        Ensure queries respect rate limits.

        SIMBAD will rate-limit/blacklist if you exceed ~5-10 queries/sec.
        See: https://astroquery.readthedocs.io/en/latest/simbad/simbad.html

        Sleeps if necessary to maintain max_queries_per_sec.
        """
        elapsed = time.time() - self._last_query_time
        if elapsed < self.min_query_interval:
            time.sleep(self.min_query_interval - elapsed)
        self._last_query_time = time.time()

    def resolve_name(self, name: str) -> Optional[str]:
        """
        Resolve name using SIMBAD's name resolver.

        Args:
            name: User input (e.g., "M31", "Andromeda", "NGC 224")

        Returns:
            SIMBAD main_id or None
        """
        try:
            self._throttle()
            result = self.simbad.query_object(name)
            if result is None or len(result) == 0:
                return None
            # Try lowercase first (0.4.8+), then uppercase for compatibility
            for col_name in ['main_id', 'MAIN_ID']:
                if col_name in result.colnames:
                    val = result[col_name][0]
                    if not np.ma.is_masked(val):
                        return str(val).strip()
            return None
        except Exception as e:
            logger.debug(f"SIMBAD resolve_name failed for '{name}': {e}")
            return None

    def get_object(self, identifier: str) -> Optional[CelestialObject]:
        """
        Fetch object from SIMBAD.

        Args:
            identifier: SIMBAD identifier (e.g., "M31", "NGC 224")

        Returns:
            CelestialObject or None if not found
        """
        try:
            self._throttle()
            logger.debug(f"Querying SIMBAD for: {identifier}")
            result = self.simbad.query_object(identifier)
            
            if result is None or len(result) == 0:
                logger.debug(f"SIMBAD returned no results for: {identifier}")
                return None

            logger.debug(f"SIMBAD result columns: {result.colnames}")
            return self._parse_result(result, 0, identifier)
            
        except Exception as e:
            logger.warning(f"SIMBAD query failed for {identifier}: {e}")
            return None

    def _parse_result(self, result, idx: int, identifier: str) -> Optional[CelestialObject]:
        """Parse a SIMBAD result row into CelestialObject."""
        try:
            # Helper to safely get column value, trying multiple possible names
            # astroquery 0.4.8+ uses lowercase column names (except filter names like "V")
            def get_col(*names: str):
                for name in names:
                    if name in result.colnames:
                        val = result[name][idx]
                        # Check for masked values
                        if np.ma.is_masked(val):
                            continue
                        return val
                return None
            
            # main_id is required (lowercase in 0.4.8+)
            main_id = get_col('main_id', 'MAIN_ID')
            if main_id is None:
                logger.warning(f"No main_id in SIMBAD result. Columns: {result.colnames}")
                return None
            main_id = str(main_id).strip()
            
            # Get coordinates (required) - lowercase in 0.4.8+
            ra_str = get_col('ra', 'RA')
            dec_str = get_col('dec', 'DEC')
            if ra_str is None or dec_str is None:
                logger.warning(f"No coordinates in SIMBAD result for {main_id}")
                return None
            
            ra = self._parse_ra(str(ra_str))
            dec = self._parse_dec(str(dec_str))
            
            # Get object type - lowercase in 0.4.8+
            obj_type = get_col('otype', 'OTYPE')
            obj_type_str = str(obj_type).strip() if obj_type else ''
            
            # Get magnitude - "V" stays uppercase (filter names are case-sensitive)
            magnitude = 99.0
            flux_v = get_col('V', 'FLUX_V', 'v', 'flux_v')
            if flux_v is not None:
                try:
                    magnitude = float(flux_v)
                except (ValueError, TypeError):
                    pass
            
            # Get dimensions - lowercase in 0.4.8+
            size = None
            maj = get_col('galdim_majaxis', 'GALDIM_MAJAXIS')
            min_ax = get_col('galdim_minaxis', 'GALDIM_MINAXIS')
            if maj is not None:
                try:
                    # SIMBAD returns dimensions in arcmin
                    major_arcmin = float(maj)
                    minor_arcmin = float(min_ax) if min_ax is not None else major_arcmin
                    size = AngularSize(major_arcmin=major_arcmin, minor_arcmin=minor_arcmin)
                except (ValueError, TypeError):
                    pass
            
            # Get morphology - lowercase in 0.4.8+
            morphology = get_col('morphtype', 'MORPHTYPE')
            morphology_str = str(morphology).strip() if morphology else None
            
            # Get aliases from IDS - lowercase in 0.4.8+
            ids_str = get_col('ids', 'IDS')
            aliases = self.adapter._parse_identifiers(str(ids_str)) if ids_str else []
            
            # Map type with correction logic
            classification = self.adapter._map_type(obj_type_str, main_id)
            if morphology_str and classification.primary_type == 'galaxy':
                subtype = self.adapter._parse_galaxy_morphology(morphology_str)
                classification = ObjectClassification(
                    primary_type='galaxy',
                    subtype=subtype,
                    morphology=morphology_str
                )
            
            # Compute surface brightness if possible
            surface_brightness = None
            if magnitude < 90 and size:
                sb_value = self._compute_surface_brightness(magnitude, size.major_arcmin, size.minor_arcmin)
                if sb_value:
                    surface_brightness = SurfaceBrightness(
                        value=sb_value,
                        source='computed',
                        band='V'
                    )
            
            # Create provenance
            provenance = [DataProvenance(
                source='SIMBAD',
                fetched_at=datetime.now(timezone.utc),
                confidence=0.95
            )]
            
            return CelestialObject(
                name=main_id,
                canonical_id=main_id,
                aliases=aliases,
                ra=ra,
                dec=dec,
                classification=classification,
                magnitude=magnitude,
                size=size,
                surface_brightness=surface_brightness,
                provenance=provenance
            )
            
        except Exception as e:
            logger.warning(f"Failed to parse SIMBAD result: {e}", exc_info=True)
            return None

    def _parse_ra(self, ra_str: str) -> float:
        """Parse RA from SIMBAD sexagesimal format (HH MM SS.SS) to degrees."""
        try:
            parts = ra_str.strip().split()
            hours = float(parts[0])
            minutes = float(parts[1]) if len(parts) > 1 else 0.0
            seconds = float(parts[2]) if len(parts) > 2 else 0.0
            return (hours + minutes / 60.0 + seconds / 3600.0) * 15.0
        except Exception:
            return 0.0

    def _parse_dec(self, dec_str: str) -> float:
        """Parse Dec from SIMBAD sexagesimal format (+DD MM SS.S) to degrees."""
        try:
            dec_str = dec_str.strip()
            sign = -1.0 if dec_str.startswith('-') else 1.0
            parts = dec_str.replace('+', '').replace('-', '').split()
            degrees = float(parts[0])
            arcmin = float(parts[1]) if len(parts) > 1 else 0.0
            arcsec = float(parts[2]) if len(parts) > 2 else 0.0
            return sign * (degrees + arcmin / 60.0 + arcsec / 3600.0)
        except Exception:
            return 0.0

    def _compute_surface_brightness(self, magnitude: float, major_arcmin: float,
                                     minor_arcmin: float) -> Optional[float]:
        """Compute surface brightness from magnitude and angular size."""
        import math
        try:
            if magnitude is None or major_arcmin is None or major_arcmin <= 0:
                return None
            
            minor = minor_arcmin if minor_arcmin else major_arcmin
            # Area in square arcminutes
            area_arcmin2 = math.pi * major_arcmin * minor / 4.0
            # Convert to square arcseconds
            area_arcsec2 = area_arcmin2 * 3600.0
            # Surface brightness in mag/arcsec²
            return magnitude + 2.5 * math.log10(area_arcsec2)
        except Exception:
            return None

    def batch_get_objects(self, identifiers: list[str]) -> list[CelestialObject]:
        """
        Batch query to avoid N+1 problem.

        Args:
            identifiers: List of SIMBAD identifiers

        Returns:
            List of CelestialObjects
        """
        try:
            self._throttle()
            results = self.simbad.query_objects(identifiers)
            if results is None or len(results) == 0:
                return []

            objects = []
            for i in range(len(results)):
                obj = self._parse_result(results, i, identifiers[i] if i < len(identifiers) else "unknown")
                if obj:
                    objects.append(obj)
            return objects
        except Exception as e:
            logger.warning(f"SIMBAD batch query failed: {e}")
            return []


class SimbadAdapter:
    """
    Converts SIMBAD data to domain model.

    Implements type correction logic based on research findings.
    """

    def _map_type(self, obj_type: str, identifier: str) -> ObjectClassification:
        """
        Map SIMBAD type with corrections for known misclassifications.

        CRITICAL: M31 is classified as AGN but is spiral galaxy.
        CRITICAL: NGC 7000 is classified as Cluster but is emission nebula.
        """
        # Normalize identifier for comparison (remove extra whitespace)
        id_normalized = ' '.join(identifier.split()).upper()
        
        # Known corrections (check normalized identifier)
        if 'M 31' in id_normalized or 'M31' in id_normalized or 'NGC 224' in id_normalized or 'NGC0224' in id_normalized:
            return ObjectClassification('galaxy', 'spiral', 'SA(s)b')

        if 'NGC 7000' in id_normalized or 'NGC7000' in id_normalized:
            return ObjectClassification('nebula', 'emission', None)

        # Parse regular types from SIMBAD otype
        otype = obj_type.upper() if obj_type else ''

        # Galaxies - SIMBAD uses various codes
        # G = Galaxy, GiG = Galaxy in Group, GiC = Galaxy in Cluster
        # AGN = Active Galactic Nucleus (still a galaxy)
        # Sy1/Sy2 = Seyfert galaxies, QSO = Quasar
        if otype in ['G', 'GAL', 'GIG', 'GIC', 'GIP', 'GPAIR', 'GGROUP'] or \
           'GALAXY' in otype or 'AGN' in otype or otype.startswith('SY') or otype == 'QSO':
            return ObjectClassification('galaxy', None, None)

        # Nebulae
        if 'HII' in otype or otype == 'ISM' or 'EMISSION' in otype:
            return ObjectClassification('nebula', 'emission', None)
        if 'PN' in otype or 'PLANETARY' in otype:
            return ObjectClassification('nebula', 'planetary', None)
        if 'REFLECTION' in otype or 'RNE' in otype:
            return ObjectClassification('nebula', 'reflection', None)
        if 'DARK' in otype or 'DNE' in otype:
            return ObjectClassification('nebula', 'dark', None)

        # Clusters
        if 'GLOBULAR' in otype or otype == 'GLC' or otype == 'GCL':
            return ObjectClassification('cluster', 'globular', None)
        if 'OPEN' in otype or otype == 'OPC' or otype == 'OCL' or otype == 'CL*' or 'CLUSTER' in otype:
            return ObjectClassification('cluster', 'open', None)

        # Double stars
        if 'DOUBLE' in otype or otype == '**':
            return ObjectClassification('double_star', None, None)

        # Default fallback
        return ObjectClassification('unknown', None, None)

    def _parse_galaxy_morphology(self, morphology: Optional[str]) -> Optional[str]:
        """Parse SIMBAD morphological type to galaxy subtype."""
        if not morphology:
            return None

        morph = str(morphology).upper()

        if morph.startswith('E'):
            return 'elliptical'
        elif morph.startswith('S0'):
            return 'lenticular'
        elif any(morph.startswith(p) for p in ['SA', 'SB', 'SAB', 'S']):
            return 'spiral'
        elif morph.startswith('I') or 'IRR' in morph:
            return 'irregular'

        return None

    def _parse_identifiers(self, ids_string: str) -> list[str]:
        """Parse SIMBAD IDS field (pipe-separated identifiers)."""
        if not ids_string:
            return []

        aliases = []
        for id_part in str(ids_string).split('|'):
            id_part = id_part.strip()
            if id_part.startswith('NAME '):
                id_part = id_part[5:]
            if id_part:
                aliases.append(id_part)

        return aliases
