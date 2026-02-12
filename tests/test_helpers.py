"""Test helpers for creating CelestialObject instances with backward compatibility.

Phase 8 changed CelestialObject to a dataclass with ObjectClassification.
This helper provides a factory function that accepts the old positional arguments
and creates objects with proper classification.
"""

from app.domain.model.celestial_object import CelestialObject
from app.domain.model.object_classification import ObjectClassification


def create_test_celestial_object(
    name: str,
    object_type: str,
    magnitude: float,
    size: float,
    altitude: float,
    ra: float = 0.0,
    dec: float = 0.0
) -> CelestialObject:
    """
    Create a CelestialObject for testing with backward-compatible signature.

    Old signature: CelestialObject(name, object_type, magnitude, size, altitude, ra=0.0, dec=0.0)
    New signature: CelestialObject(name=..., canonical_id=..., classification=..., magnitude=..., size=..., altitude=...)

    Args:
        name: Object name
        object_type: Legacy type string ('DeepSky', 'Planet', 'Moon', 'Sun')
        magnitude: Apparent magnitude
        size: Angular size in arcminutes
        altitude: Current altitude above horizon in degrees
        ra: Right ascension in decimal degrees
        dec: Declination in decimal degrees

    Returns:
        CelestialObject configured for testing with proper ObjectClassification
    """
    # Map legacy test types to ObjectClassification
    classification_map = {
        'Sun': ObjectClassification(primary_type='sun'),
        'Moon': ObjectClassification(primary_type='moon'),
        'Planet': ObjectClassification(primary_type='planet'),
        'DeepSky': ObjectClassification(primary_type='nebula'),  # Generic deep-sky
    }

    classification = classification_map.get(object_type)
    if not classification:
        raise ValueError(f"Unknown legacy object_type: {object_type}")

    return CelestialObject(
        name=name,
        canonical_id=name.replace(' ', '_').lower(),
        magnitude=magnitude,
        size=size,
        altitude=altitude,
        ra=ra,
        dec=dec,
        classification=classification
    )
