# Example of creating a celestial object and calculating its score
from CelestialObject import CelestialObject
from StrategyFactory import calculate_observability_score


def calculate(obj: CelestialObject):
    score = calculate_observability_score(obj)
    print(f"Observability score for {obj.name}: {score}")


calculate(CelestialObject('Sun', 'Sun', -26.74, 31.00, 39.00))
calculate(CelestialObject('Moon', 'Moon', -12.60, 31.00, 39.00))
calculate(CelestialObject('Jupiter', 'Planet', -2.40, 0.77, 43.00))
calculate(CelestialObject('Sirius', 'DeepSky', -1.46, 0.0001, 90.00))
