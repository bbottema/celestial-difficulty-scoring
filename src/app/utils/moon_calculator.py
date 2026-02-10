import ephem
import math
from datetime import datetime
from app.domain.model.moon_conditions import MoonConditions


def calculate_moon_conditions(
    date: datetime,
    latitude: float,
    longitude: float
) -> MoonConditions:
    """
    Calculate moon position and phase for given date/location.

    Args:
        date: The observation date/time (UTC)
        latitude: Observer latitude in decimal degrees
        longitude: Observer longitude in decimal degrees

    Returns:
        MoonConditions object with phase, illumination, position
    """
    observer = ephem.Observer()
    observer.lat = str(latitude)
    observer.lon = str(longitude)
    observer.date = date

    moon = ephem.Moon(observer)

    return MoonConditions(
        phase=moon.moon_phase,
        illumination=moon.moon_phase * 100,
        altitude=math.degrees(moon.alt),
        ra=math.degrees(moon.ra),
        dec=math.degrees(moon.dec)
    )
