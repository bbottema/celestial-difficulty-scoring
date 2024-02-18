from abc import abstractmethod, ABC

from utils.constants import *


class IObservabilityScoringStrategy(ABC):
    @abstractmethod
    def calculate_score(self, celestial_object) -> float:
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


class LargeFaintObjectScoringStrategy(IObservabilityScoringStrategy):
    def calculate_score(self, celestial_object):
        # Adjust the magnitude score to increase with faintness
        magnitude_score = max(0, (celestial_object.magnitude - faint_object_magnitude_baseline))

        # Adjust the size score to increase with size
        size_score = min(celestial_object.size / max_deepsky_size, 1)  # Cap the size score at 1

        # Combine scores
        combined_score = (0.4 * magnitude_score) + (0.6 * size_score)

        # Normalize the combined score to fit within the desired range (e.g., 0-25)
        return min(combined_score, max_observable_score) / 10
