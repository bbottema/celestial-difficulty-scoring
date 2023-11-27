from CelestialObject import CelestialObject
from Strategies import *


def calculate_observability_score(celestial_object: CelestialObject) -> float:
    strategy = _determine_scoring_strategy(celestial_object)
    return strategy.calculate_score(celestial_object)


def _determine_scoring_strategy(celestial_object: CelestialObject) -> IObservabilityScoringStrategy:
    if celestial_object.object_type in ['Planet', 'Moon', 'Sun']:
        return SolarSystemScoringStrategy()
    elif celestial_object.object_type == 'DeepSky':
        return DeepSkyScoringStrategy()
    else:
        raise ValueError("Unknown celestial object type")
