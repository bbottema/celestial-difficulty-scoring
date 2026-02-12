"""
JPL Horizons provider for Solar System ephemerides (online API).

Horizons provides accurate, up-to-date ephemeris data for:
- Planets (Mercury through Neptune)
- Dwarf planets (Pluto, Ceres, etc.)
- Natural satellites (Moon, moons of other planets)
- Minor planets / asteroids
- Comets
- Spacecraft

Fields available:
- RA/DEC (apparent and astrometric)
- AZ/EL (observer-specific)
- V magnitude
- Angular width
- Illumination percentage
- Surface brightness
- Phase angle

Research finding: Use `quantities` parameter to limit output size and speed.
"""
from typing import Optional
from datetime import datetime, timezone

from astroquery.jplhorizons import Horizons

from app.domain.model.celestial_object import CelestialObject
from app.domain.model.object_classification import ObjectClassification, AngularSize
from app.domain.model.data_provenance import DataProvenance


class HorizonsProvider:
    """
    JPL Horizons API provider via astroquery.

    Provides current ephemeris data for Solar System objects.
    Requires observer location (lat/lon or MPC code).
    """

    def __init__(self, observer_location: str = "500"):
        """
        Initialize Horizons provider.

        Args:
            observer_location: MPC observatory code or geodetic coordinates
                             "500" = geocenter
                             {"lon": -122.0, "lat": 37.0, "elevation": 0.0}
        """
        self.observer_location = observer_location
        self.adapter = HorizonsAdapter()
        self._last_query_time = 0.0

        # Planet name to Horizons ID mapping
        self.planet_ids = {
            'mercury': '199',
            'venus': '299',
            'mars': '499',
            'jupiter': '599',
            'saturn': '699',
            'uranus': '799',
            'neptune': '899',
            'moon': '301'
        }

    def _get_horizons_id(self, name: str) -> Optional[str]:
        """Map common names to Horizons IDs"""
        name_lower = name.lower().strip()
        return self.planet_ids.get(name_lower)

    def _format_location(self, observer_lat: float, observer_lon: float) -> str:
        """Format observer location for Horizons"""
        return f"{observer_lon:.6f},{observer_lat:.6f},0.0"

    def _format_time(self, observation_time: datetime) -> str:
        """Format observation time for Horizons"""
        return observation_time.strftime('%Y-%m-%d %H:%M')

    def get_object(self, identifier: str, time: Optional[datetime] = None) -> Optional[CelestialObject]:
        """
        Fetch current ephemeris for Solar System object.

        Queries Horizons for ephemeris data at specified time.

        Args:
            identifier: Horizons target ID or planet name
            time: Observation time (defaults to now)

        Returns:
            CelestialObject with current position, magnitude, size
        """
        try:
            # Resolve name to ID if needed
            horizons_id = self._get_horizons_id(identifier)
            if not horizons_id:
                horizons_id = identifier

            # Query for specified or current time
            if time is None:
                time = datetime.now(timezone.utc)

            time_str = self._format_time(time)

            obj = Horizons(
                id=horizons_id,
                location=self.observer_location,
                epochs={'start': time_str, 'stop': time_str, 'step': '1m'}
            )

            # Request specific quantities to limit output size
            # quantities: 1=RA/Dec, 9=V mag, 13=ang width, 20=illum%
            eph = obj.ephemerides(quantities='1,9,13,20')

            if eph is None or len(eph) == 0:
                return None

            return self._parse_horizons_result(eph, 0, identifier)
        except Exception:
            return None

    def _parse_horizons_result(self, result, idx: int, name: str) -> Optional[CelestialObject]:
        """Parse Horizons ephemeris result into CelestialObject"""
        try:
            ra = float(result['RA'][idx])
            dec = float(result['DEC'][idx])

            # Magnitude
            mag = result['V'][idx] if 'V' in result.colnames else None
            magnitude = float(mag) if mag and not isinstance(mag, str) else 99.0

            # Angular width (arcsec)
            ang_width = result['ang_width'][idx] if 'ang_width' in result.colnames else None

            # Create angular size
            size = None
            if ang_width and not isinstance(ang_width, str):
                # Convert arcsec to arcmin
                size_arcmin = float(ang_width) / 60.0
                size = AngularSize(major_arcmin=size_arcmin, minor_arcmin=size_arcmin)

            # Classification
            classification = self.adapter._classify_object(name)

            # Provenance
            provenance = [DataProvenance(
                source='Horizons',
                fetched_at=datetime.now(timezone.utc),
                confidence=1.0  # Authoritative ephemeris data
            )]

            return CelestialObject(
                name=name,
                canonical_id=name,
                aliases=[],
                ra=ra,
                dec=dec,
                classification=classification,
                magnitude=magnitude,
                size=size,
                provenance=provenance
            )
        except Exception:
            return None

    def _calculate_angular_size(self, ang_width_arcsec: float, name: str) -> AngularSize:
        """Calculate angular size from Horizons ang_width field"""
        size_arcmin = ang_width_arcsec / 60.0
        return AngularSize(major_arcmin=size_arcmin, minor_arcmin=size_arcmin)

    def batch_get_objects(self, identifiers: list[str], time: Optional[datetime] = None) -> list[CelestialObject]:
        """
        Batch query for multiple Solar System objects.

        Note: Horizons doesn't have true batch API, so this queries serially.
        For observing lists with many planets, consider caching.

        Args:
            identifiers: List of Horizons target IDs
            time: Observation time (defaults to now)

        Returns:
            List of CelestialObjects with current ephemerides
        """
        objects = []
        for identifier in identifiers:
            obj = self.get_object(identifier, time)
            if obj:
                objects.append(obj)
        return objects


class HorizonsAdapter:
    """
    Converts Horizons DTOs to domain model.

    Maps ephemeris fields to CelestialObject with Solar System classification.
    """

    def _classify_object(self, target_name: str) -> ObjectClassification:
        """
        Classify Solar System object by name.

        Simple heuristics:
        - "Moon" → moon
        - Mercury/Venus/Mars/Jupiter/Saturn/Uranus/Neptune → planet
        - Pluto, Ceres, etc. → dwarf_planet
        - Numbered objects → asteroid
        - "C/" prefix → comet

        Args:
            target_name: Horizons target name

        Returns:
            ObjectClassification with solar_system primary type
        """
        name_lower = target_name.lower()
        planets = ['mercury', 'venus', 'mars', 'jupiter', 'saturn', 'uranus', 'neptune']

        if 'moon' in name_lower:
            return ObjectClassification('solar_system', 'moon', None)
        elif any(p in name_lower for p in planets):
            return ObjectClassification('solar_system', 'planet', None)
        elif target_name.startswith('C/'):
            return ObjectClassification('solar_system', 'comet', None)
        elif target_name.isdigit():
            return ObjectClassification('solar_system', 'asteroid', None)
        else:
            return ObjectClassification('solar_system', 'minor_body', None)
