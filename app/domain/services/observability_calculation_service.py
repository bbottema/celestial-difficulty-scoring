import math

from domain.model.celestial_object import CelestialObjectScore
from domain.services.strategies import *


class ObservabilityCalculationService:

    def calculate_observability_score(self, celestial_object: CelestialObject) -> CelestialObjectScore:
        strategy = self._determine_scoring_strategy(celestial_object)
        base_score = strategy.calculate_score(celestial_object)
        altitude_adjusted_score = base_score  # adjust_for_altitude(base_score, celestial_object.altitude)

        return CelestialObjectScore(altitude_adjusted_score, self._normalize_score(altitude_adjusted_score))

    @staticmethod
    def _determine_scoring_strategy(celestial_object: CelestialObject) -> IObservabilityScoringStrategy:
        if celestial_object.object_type in ['Planet', 'Moon', 'Sun']:
            return SolarSystemScoringStrategy()
        elif celestial_object.object_type == 'DeepSky':
            if celestial_object.size > large_object_size_threshold_in_arcminutes:
                return LargeFaintObjectScoringStrategy()
            else:
                return DeepSkyScoringStrategy()
        else:
            raise ValueError(f'Unknown celestial object type: {celestial_object.object_type}')

    # TODO: incorporate altitude into scoring
    @staticmethod
    def _adjust_for_altitude(score, altitude):
        # Assuming altitude is given in degrees from the horizon.
        # Exponential decay factor can be adjusted based on observational preferences.
        altitude_factor = math.exp(-0.03 * (optimal_altitude - altitude))
        return score * altitude_factor

    @staticmethod
    def _normalize_score(score) -> float:
        if score > 10:
            transformed_score = math.log10(score + 1) ** 2  # More aggressive transformation for higher scores
        else:
            transformed_score = math.log(score + 1, 1.5)  # Less aggressive transformation for lower scores

        max_transformed_score = 2  # Adjust based on observed transformed score range
        rescaled_score = (transformed_score / max_transformed_score) * 25  # Rescaling to a 0-25 scale
        return rescaled_score
