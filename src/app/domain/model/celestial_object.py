from dataclasses import dataclass


@dataclass
class CelestialObject:
    name: str
    object_type: str
    magnitude: float
    size: float
    altitude: float
    ra: float = 0.0  # right ascension in decimal degrees
    dec: float = 0.0  # declination in decimal degrees


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
