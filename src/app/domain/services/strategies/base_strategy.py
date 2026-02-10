from abc import abstractmethod, ABC

from app.domain.model.scoring_context import ScoringContext


class IObservabilityScoringStrategy(ABC):
    @abstractmethod
    def calculate_score(self, celestial_object, context: 'ScoringContext') -> float:
        pass
