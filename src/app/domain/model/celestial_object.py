from dataclasses import dataclass, field
from typing import Optional

from app.domain.model.object_classification import ObjectClassification, AngularSize, SurfaceBrightness
from app.domain.model.data_provenance import DataProvenance


@dataclass
class CelestialObject:
    """Enhanced celestial object model for Phase 8 API integration"""
    # Core identification
    name: str
    canonical_id: str
    aliases: list[str] = field(default_factory=list)

    # Coordinates (J2000)
    ra: float = 0.0  # decimal degrees
    dec: float = 0.0  # declination in decimal degrees

    # Classification (Phase 7)
    classification: Optional[ObjectClassification] = None

    # Observational properties
    magnitude: float = 99.0
    size: Optional[AngularSize] = None
    surface_brightness: Optional[SurfaceBrightness] = None

    # Current observing conditions (ephemeris-dependent)
    altitude: float = 0.0  # Current altitude above horizon

    # Data quality
    provenance: list[DataProvenance] = field(default_factory=list)

    # Double star specific (optional)
    separation_arcsec: Optional[float] = None
    position_angle_deg: Optional[float] = None
    companion_magnitude: Optional[float] = None

    @property
    def object_type(self) -> str:
        """Returns the primary classification type (e.g., 'galaxy', 'nebula', 'planet', 'star')"""
        if self.classification and self.classification.primary_type:
            return self.classification.primary_type
        return "unknown"


@dataclass
class CelestialObjectScore:
    score: float
    normalized_score: float


@dataclass
class ScoredCelestialObject:
    name: str
    object_type: str
    magnitude: float
    size: float
    altitude: float
    observability_score: CelestialObjectScore


CelestialsList = list[CelestialObject]
ScoredCelestialsList = list[ScoredCelestialObject]
