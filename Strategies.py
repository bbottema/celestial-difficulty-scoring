from abc import abstractmethod, ABC

from Constants import *


class IObservabilityScoringStrategy(ABC):
    @abstractmethod
    def calculate_score(self, celestial_object):
        pass


class SolarSystemScoringStrategy(IObservabilityScoringStrategy):
    def calculate_score(self, celestial_object):
        magnitude_score = self._normalize_magnitude(10 ** (-0.4 * celestial_object.magnitude))
        size_score = self._normalize_size(celestial_object.size)
        return (magnitude_score + size_score) / 2

    # normalize to 0-10 scale
    @staticmethod
    def _normalize_magnitude(score) -> float:
        return (score / sun_solar_magnitude_score) * max_observable_score

    @staticmethod
    def _normalize_size(score) -> float:
        return (score / max_solar_size) * max_observable_score


class DeepSkyScoringStrategy(IObservabilityScoringStrategy):
    def calculate_score(self, celestial_object):
        magnitude_score = self._normalize_magnitude(10 ** (-0.4 * (celestial_object.magnitude + 12)))
        size_score = self._normalize_size(celestial_object.size)
        return (magnitude_score + size_score) / 2

    @staticmethod
    def _normalize_magnitude(score) -> float:
        return (score / sirius_deepsky_magnitude_score) * max_observable_score

    @staticmethod
    def _normalize_size(score) -> float:
        return (score / max_deepsky_size) * max_observable_score
