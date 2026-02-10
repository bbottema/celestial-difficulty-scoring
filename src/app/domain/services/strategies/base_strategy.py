from abc import abstractmethod, ABC

from app.domain.model.scoring_context import ScoringContext


class IObservabilityScoringStrategy(ABC):
    @abstractmethod
    def calculate_score(self, celestial_object, context: 'ScoringContext') -> float:
        """Calculate raw observability score for the given object and context."""
        pass

    @abstractmethod
    def normalize_score(self, raw_score: float) -> float:
        """
        Normalize raw score to 0-25 scale for display.

        Each strategy defines its own normalization based on typical score ranges.
        This preserves ordering within object types while providing consistent scale.

        Args:
            raw_score: Raw score from calculate_score()

        Returns:
            Normalized score in 0-25 range
        """
        pass
