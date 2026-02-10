import math
from typing import Optional

from app.domain.model.celestial_object import CelestialObjectScore, ScoredCelestialObject, CelestialsList, \
    ScoredCelestialsList, CelestialObject
from app.domain.model.moon_conditions import MoonConditions
from app.domain.model.scoring_context import ScoringContext
from app.domain.services.strategies.base_strategy import IObservabilityScoringStrategy
from app.domain.services.strategies.deep_sky_strategy import DeepSkyScoringStrategy
from app.domain.services.strategies.large_faint_object_strategy import LargeFaintObjectScoringStrategy
from app.domain.services.strategies.reflected_light_strategy import ReflectedLightStrategy
from app.domain.services.strategies.sun_strategy import SunStrategy
from app.orm.model.entities import Telescope, Eyepiece, ObservationSite
from app.utils.scoring_constants import LARGE_OBJECT_SIZE_THRESHOLD


class ObservabilityCalculationService:

    def score_celestial_objects(self,
                                celestial_objects: CelestialsList,
                                telescope: Optional[Telescope] = None,
                                eyepiece: Optional[Eyepiece] = None,
                                observation_site: Optional[ObservationSite] = None,
                                weather: Optional[dict] = None,
                                moon_conditions: Optional[MoonConditions] = None) -> ScoredCelestialsList:
        return [self.score_celestial_object(celestial_object, telescope, eyepiece, observation_site, weather, moon_conditions)
                for celestial_object in celestial_objects]

    def score_celestial_object(self,
                               celestial_object: CelestialObject,
                               telescope: Optional[Telescope] = None,
                               eyepiece: Optional[Eyepiece] = None,
                               observation_site: Optional[ObservationSite] = None,
                               weather: Optional[dict] = None,
                               moon_conditions: Optional[MoonConditions] = None) -> ScoredCelestialObject:
        return ScoredCelestialObject(celestial_object.name, celestial_object.object_type, celestial_object.magnitude,
                                     celestial_object.size, celestial_object.altitude,
                                     self._calculate_observability_score(celestial_object, telescope, eyepiece, observation_site, weather, moon_conditions))

    def _calculate_observability_score(self,
                                       celestial_object: CelestialObject,
                                       telescope: Optional[Telescope] = None,
                                       eyepiece: Optional[Eyepiece] = None,
                                       observation_site: Optional[ObservationSite] = None,
                                       weather: Optional[dict] = None,
                                       moon_conditions: Optional[MoonConditions] = None) -> CelestialObjectScore:
        # Build scoring context with equipment and site data
        context = ScoringContext(
            telescope=telescope,
            eyepiece=eyepiece,
            observation_site=observation_site,
            altitude=celestial_object.altitude,
            weather=weather,
            moon_conditions=moon_conditions
        )

        strategy = self._determine_scoring_strategy(celestial_object)
        raw_score = strategy.calculate_score(celestial_object, context)
        normalized_score = strategy.normalize_score(raw_score)

        return CelestialObjectScore(raw_score, normalized_score)

    @staticmethod
    def _determine_scoring_strategy(celestial_object: CelestialObject) -> IObservabilityScoringStrategy:
        # Sun gets dedicated strategy (safety-first)
        if celestial_object.object_type == 'Sun':
            return SunStrategy()
        # Moon and Planets use physics-based reflected light strategy
        elif celestial_object.object_type in ['Planet', 'Moon']:
            return ReflectedLightStrategy()
        # Deep-sky objects (stars, galaxies, nebulae)
        elif celestial_object.object_type == 'DeepSky':
            if celestial_object.size > LARGE_OBJECT_SIZE_THRESHOLD:
                return LargeFaintObjectScoringStrategy()
            else:
                return DeepSkyScoringStrategy()
        else:
            raise ValueError(f'Unknown celestial object type: {celestial_object.object_type}')
