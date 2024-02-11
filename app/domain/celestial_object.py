from dataclasses import dataclass
from typing import TypedDict, List


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
class CelestialObjectData:
    name: str
    object_type: str
    magnitude: float
    size: float
    altitude: float
    observability_score: CelestialObjectScore


CelestialsList = List[CelestialObjectData]
