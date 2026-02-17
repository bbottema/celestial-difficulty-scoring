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
from app.domain.services.strategies.strategy_utils import get_size_arcmin
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
        # Extract size as float (handle both float and AngularSize)
        size_arcmin = celestial_object.size
        if hasattr(size_arcmin, 'major_arcmin'):
            size_arcmin = size_arcmin.major_arcmin

        score = self._calculate_observability_score(celestial_object, telescope, eyepiece, observation_site, weather, moon_conditions)
        
        scored = ScoredCelestialObject(
            name=celestial_object.name,
            object_type=celestial_object.object_type,
            magnitude=celestial_object.magnitude,
            size=size_arcmin,
            altitude=celestial_object.altitude,
            observability_score=score
        )
        
        return scored

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
        obj_type = celestial_object.object_type

        # Sun gets dedicated strategy (safety-first)
        if obj_type == 'sun':
            return SunStrategy()

        # Moon uses physics-based reflected light strategy
        elif obj_type == 'moon':
            return ReflectedLightStrategy()

        # Planets, asteroids, comets use reflected light strategy
        elif obj_type in ['planet', 'asteroid', 'comet']:
            return ReflectedLightStrategy()

        # Deep-sky objects: galaxies, nebulae, clusters, stars
        elif obj_type in ['galaxy', 'nebula', 'cluster', 'star', 'double_star', 'variable_star']:
            # Get size value (handle both float and AngularSize object)
            size_arcmin = get_size_arcmin(celestial_object)

            # Large extended objects need special handling
            if size_arcmin and size_arcmin > LARGE_OBJECT_SIZE_THRESHOLD:
                return LargeFaintObjectScoringStrategy()
            else:
                return DeepSkyScoringStrategy()

        # Unknown type: treat as deep-sky object with conservative scoring
        # This allows objects with unrecognized classification to still be scored
        elif obj_type == 'unknown' or obj_type is None:
            size_arcmin = get_size_arcmin(celestial_object)
            if size_arcmin and size_arcmin > LARGE_OBJECT_SIZE_THRESHOLD:
                return LargeFaintObjectScoringStrategy()
            else:
                return DeepSkyScoringStrategy()

        else:
            raise ValueError(f'Unknown celestial object type: {obj_type}')
