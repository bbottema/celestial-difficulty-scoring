import math

from app.services.strategies import *


def calculate_observability_score(celestial_object: CelestialObject) -> dict[str, float]:
    strategy = _determine_scoring_strategy(celestial_object)
    base_score = strategy.calculate_score(celestial_object)
    altitude_adjusted_score = base_score  # adjust_for_altitude(base_score, celestial_object.altitude)

    return {
        'score': altitude_adjusted_score,
        'normalized_score': normalize_score(altitude_adjusted_score)
    }


def _determine_scoring_strategy(celestial_object: CelestialObject) -> IObservabilityScoringStrategy:
    if celestial_object.object_type in ['Planet', 'Moon', 'Sun']:
        return SolarSystemScoringStrategy()
    elif celestial_object.object_type == 'DeepSky':
        if celestial_object.size > large_object_size_threshold:
            return LargeFaintObjectScoringStrategy()
        else:
            return DeepSkyScoringStrategy()
    else:
        raise ValueError("Unknown celestial object type")


def adjust_for_altitude(score, altitude):
    # Assuming altitude is given in degrees from the horizon.
    # Exponential decay factor can be adjusted based on observational preferences.
    altitude_factor = math.exp(-0.03 * (optimal_altitude - altitude))
    return score * altitude_factor


def normalize_score(score) -> float:
    if score > 10:
        transformed_score = math.log10(score + 1) ** 2  # More aggressive transformation for higher scores
    else:
        transformed_score = math.log(score + 1, 1.5)  # Less aggressive transformation for lower scores

    max_transformed_score = 2  # Adjust based on observed transformed score range
    rescaled_score = (transformed_score / max_transformed_score) * 25  # Rescaling to a 0-25 scale
    return rescaled_score