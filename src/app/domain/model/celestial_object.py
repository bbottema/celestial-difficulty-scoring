from dataclasses import dataclass


@dataclass
class CelestialObject:
    name: str
    object_type: str
    magnitude: float
    size: float
    altitude: float


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
