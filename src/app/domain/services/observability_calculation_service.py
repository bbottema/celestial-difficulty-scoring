import math
from typing import Optional

from app.domain.model.celestial_object import CelestialObjectScore, ScoredCelestialObject, CelestialsList, \
    ScoredCelestialsList
from app.domain.model.scoring_context import ScoringContext
from app.domain.services.strategies import *
from app.orm.model.entities import Telescope, Eyepiece, ObservationSite


class ObservabilityCalculationService:

    def score_celestial_objects(self,
                                celestial_objects: CelestialsList,
                                telescope: Optional[Telescope] = None,
                                eyepiece: Optional[Eyepiece] = None,
                                observation_site: Optional[ObservationSite] = None,
                                weather: Optional[dict] = None) -> ScoredCelestialsList:
        return [self.score_celestial_object(celestial_object, telescope, eyepiece, observation_site, weather)
                for celestial_object in celestial_objects]

    def score_celestial_object(self,
                               celestial_object: CelestialObject,
                               telescope: Optional[Telescope] = None,
                               eyepiece: Optional[Eyepiece] = None,
                               observation_site: Optional[ObservationSite] = None,
                               weather: Optional[dict] = None) -> ScoredCelestialObject:
        return ScoredCelestialObject(celestial_object.name, celestial_object.object_type, celestial_object.magnitude,
                                     celestial_object.size, celestial_object.altitude,
                                     self._calculate_observability_score(celestial_object, telescope, eyepiece, observation_site, weather))

    def _calculate_observability_score(self,
                                       celestial_object: CelestialObject,
                                       telescope: Optional[Telescope] = None,
                                       eyepiece: Optional[Eyepiece] = None,
                                       observation_site: Optional[ObservationSite] = None,
                                       weather: Optional[dict] = None) -> CelestialObjectScore:
        # Build scoring context with equipment and site data
        context = ScoringContext(
            telescope=telescope,
            eyepiece=eyepiece,
            observation_site=observation_site,
            altitude=celestial_object.altitude,
            weather=weather
        )

        strategy = self._determine_scoring_strategy(celestial_object)
        final_score = strategy.calculate_score(celestial_object, context)

        return CelestialObjectScore(final_score, self._normalize_score(final_score))

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

    @staticmethod
    def _normalize_score(score) -> float:
        if score > 10:
            transformed_score = math.log10(score + 1) ** 2  # More aggressive transformation for higher scores
        else:
            transformed_score = math.log(score + 1, 1.5)  # Less aggressive transformation for lower scores

        max_transformed_score = 2  # Adjust based on observed transformed score range
        rescaled_score = (transformed_score / max_transformed_score) * 25  # Rescaling to a 0-25 scale
        return rescaled_score
