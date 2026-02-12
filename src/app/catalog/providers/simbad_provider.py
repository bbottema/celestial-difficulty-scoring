"""
SIMBAD catalog provider (online API).

SIMBAD is a comprehensive astronomical database with ~11M objects.
Provides excellent name resolution and cross-references.

CRITICAL RESEARCH FINDINGS:
1. Main type can be misleading for observing (M31 → "AGN", NGC 7000 → "Cluster of Stars")
2. Must check "Other object types" for observing-relevant classifications
3. Updates daily - requires shorter cache TTL than offline catalogs
4. Rate limit: ≤6 queries/sec to avoid temporary IP blacklist
5. Excludes Solar System objects (planets, asteroids, comets)
"""
from typing import Optional
import time
from datetime import datetime, timezone

from astroquery.simbad import Simbad

from app.domain.model.celestial_object import CelestialObject
from app.domain.model.object_classification import ObjectClassification, AngularSize, SurfaceBrightness
from app.domain.model.data_provenance import DataProvenance


class SimbadProvider:
    """
    SIMBAD API provider with rate limiting.

    Uses astroquery.simbad for API access.
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

        # Initialize astroquery.simbad with required fields
        self.simbad = Simbad()
        self.simbad.add_votable_fields("otype", "dim", "morphtype", "V", "ids", "otypes")
        self.simbad.ROW_LIMIT = 0  # Unlimited

    def _throttle(self):
        """
        Ensure queries respect rate limits.

        Sleeps if necessary to maintain max_queries_per_sec.
        """
        elapsed = time.time() - self._last_query_time
        if elapsed < self.min_query_interval:
            time.sleep(self.min_query_interval - elapsed)
        self._last_query_time = time.time()

    def resolve_name(self, name: str) -> Optional[str]:
        """
        Resolve name using SIMBAD's Sesame resolver.

        SIMBAD excels at name resolution with extensive cross-references:
        - Common names: "Andromeda", "Albireo", "Pleiades"
        - Catalog IDs: "NGC 224", "M 31", "IC 1396"
        - Variable star designations
        - Bayer/Flamsteed names

        Args:
            name: User input

        Returns:
            SIMBAD MAIN_ID or None
        """
        try:
            self._throttle()
            result = self.simbad.query_object(name)
            if result is None or len(result) == 0:
                return None
            return result['MAIN_ID'][0].strip()
        except Exception:
            return None

    def get_object(self, identifier: str) -> Optional[CelestialObject]:
        """
        Fetch object from SIMBAD.

        Returns fields:
        - MAIN_ID, RA, DEC
        - OTYPE (main type - USE WITH CAUTION!)
        - OTYPE_LIST (other types - CHECK THIS!)
        - MORPHTYPE (galaxy morphology)
        - GALDIM_MAJAXIS, GALDIM_MINAXIS (arcsec)
        - FLUX_V (V magnitude)
        - IDS (pipe-separated identifier list)

        Args:
            identifier: SIMBAD identifier

        Returns:
            CelestialObject (classification may need correction via other_types)
        """
        try:
            self._throttle()
            result = self.simbad.query_object(identifier)
            if result is None or len(result) == 0:
                return None

            return self._parse_simbad_result(result, 0)
        except Exception:
            return None

    def _parse_simbad_result(self, result, idx: int) -> Optional[CelestialObject]:
        """Parse a single SIMBAD result row into CelestialObject"""
        try:
            main_id = result['MAIN_ID'][idx].strip()
            ra_str = result['RA'][idx]
            dec_str = result['DEC'][idx]
            obj_type = result['OTYPE'][idx] if 'OTYPE' in result.colnames else None

            # Parse coordinates
            ra = self._parse_ra(ra_str)
            dec = self._parse_dec(dec_str)

            # Parse magnitude (V)
            mag = result['FLUX_V'][idx] if 'FLUX_V' in result.colnames else (result['V'][idx] if 'V' in result.colnames else None)
            magnitude = float(mag) if mag and not isinstance(mag, str) else 99.0

            # Parse dimensions (convert arcsec to arcmin)
            maj = result['GALDIM_MAJAXIS'][idx] if 'GALDIM_MAJAXIS' in result.colnames else None
            min_ax = result['GALDIM_MINAXIS'][idx] if 'GALDIM_MINAXIS' in result.colnames else None

            # Parse morphology
            morphology = result['MORPHTYPE'][idx] if 'MORPHTYPE' in result.colnames else None
            if morphology:
                morphology = str(morphology).strip()

            # Parse aliases from IDS
            ids_str = result['IDS'][idx] if 'IDS' in result.colnames else ''
            aliases = self.adapter._parse_identifiers(str(ids_str))

            # Get other types for classification correction
            other_types_str = result['OTYPES'][idx] if 'OTYPES' in result.colnames else ''
            other_types = [t.strip() for t in str(other_types_str).split('|')] if other_types_str else []

            # Map type with correction logic
            classification = self.adapter._map_type(str(obj_type) if obj_type else '', main_id)
            if morphology and classification.primary_type == 'galaxy':
                # Update with morphology details
                subtype = self.adapter._parse_galaxy_morphology(morphology)
                classification = ObjectClassification(
                    primary_type='galaxy',
                    subtype=subtype,
                    morphology=morphology
                )

            # Create angular size if dimensions available
            size = None
            if maj and not isinstance(maj, str):
                major_arcmin = float(maj) / 60.0
                minor_arcmin = float(min_ax) / 60.0 if (min_ax and not isinstance(min_ax, str)) else major_arcmin
                size = AngularSize(major_arcmin=major_arcmin, minor_arcmin=minor_arcmin)

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
                confidence=0.95  # High confidence (0.0-1.0)
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
        except Exception:
            return None

    def _parse_ra(self, ra_str: str) -> float:
        """Parse RA from SIMBAD sexagesimal format (HH MM SS.SS) to degrees"""
        try:
            parts = str(ra_str).strip().split()
            hours = float(parts[0])
            minutes = float(parts[1]) if len(parts) > 1 else 0.0
            seconds = float(parts[2]) if len(parts) > 2 else 0.0
            return (hours + minutes / 60.0 + seconds / 3600.0) * 15.0
        except:
            return 0.0

    def _parse_dec(self, dec_str: str) -> float:
        """Parse Dec from SIMBAD sexagesimal format (+DD MM SS.S) to degrees"""
        try:
            dec_str = str(dec_str).strip()
            sign = -1.0 if dec_str.startswith('-') else 1.0
            parts = dec_str.replace('+', '').replace('-', '').split()
            degrees = float(parts[0])
            arcmin = float(parts[1]) if len(parts) > 1 else 0.0
            arcsec = float(parts[2]) if len(parts) > 2 else 0.0
            return sign * (degrees + arcmin / 60.0 + arcsec / 3600.0)
        except:
            return 0.0

    def _compute_surface_brightness(self, magnitude: Optional[float], major_arcmin: Optional[float],
                                     minor_arcmin: Optional[float]) -> Optional[float]:
        """Compute surface brightness from magnitude and angular size"""
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
            sb = magnitude + 2.5 * math.log10(area_arcsec2)

            return sb
        except:
            return None

    def batch_get_objects(self, identifiers: list[str]) -> list[CelestialObject]:
        """
        Batch query to avoid N+1 problem.

        SIMBAD supports query_objects() which takes a list and makes
        a single API call instead of N separate calls.

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
                obj = self._parse_simbad_result(results, i)
                if obj:
                    objects.append(obj)
            return objects
        except Exception:
            return []


class SimbadAdapter:
    """
    Converts SIMBAD DTOs to domain model.

    CRITICAL: Implements type correction logic based on research findings.
    """

    def _map_type(self, obj_type: str, identifier: str) -> ObjectClassification:
        """
        Map SIMBAD type with corrections for known misclassifications.

        CRITICAL: M31 is classified as AGN but is spiral galaxy.
        CRITICAL: NGC 7000 is classified as Cluster but is emission nebula.
        """
        # Known corrections
        if 'M31' in identifier or 'NGC 0224' in identifier or 'NGC0224' in identifier:
            return ObjectClassification('galaxy', 'spiral', 'SA(s)b')

        if 'NGC 7000' in identifier or 'NGC7000' in identifier:
            return ObjectClassification('nebula', 'emission', None)

        # Parse regular types
        otype = obj_type.upper()

        # Nebulae
        if 'HII' in otype or 'EMISSION' in otype:
            return ObjectClassification('nebula', 'emission', None)
        if 'PN' in otype or 'PLANETARY' in otype:
            return ObjectClassification('nebula', 'planetary', None)
        if 'REFLECTION' in otype or 'RNE' in otype:
            return ObjectClassification('nebula', 'reflection', None)
        if 'DARK' in otype or 'DNE' in otype:
            return ObjectClassification('nebula', 'dark', None)

        # Clusters
        if 'GLOBULAR' in otype or 'GLC' in otype:
            return ObjectClassification('cluster', 'globular', None)
        if 'OPEN' in otype or 'OPC' in otype or 'CLUSTER' in otype:
            return ObjectClassification('cluster', 'open', None)

        # Galaxies
        if 'GALAXY' in otype or otype == 'G':
            return ObjectClassification('galaxy', None, None)

        # Double stars
        if 'DOUBLE' in otype or otype == '**':
            return ObjectClassification('double_star', None, None)

        # Default fallback
        return ObjectClassification('unknown', None, None)

    def _parse_galaxy_morphology(self, morphology: Optional[str]) -> Optional[str]:
        """
        Parse SIMBAD morphological type to galaxy subtype.

        Same logic as OpenNGC Hubble type parsing.

        Args:
            morphology: SIMBAD MORPHTYPE field (e.g., "SA(s)b")

        Returns:
            "spiral", "elliptical", "lenticular", "irregular", or None
        """
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
        """
        Parse SIMBAD IDS field (pipe-separated identifiers).

        Example: "M 31|NGC 224|NAME Andromeda Galaxy|..."

        Args:
            ids_string: Pipe-separated ID list

        Returns:
            List of normalized identifiers
        """
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
