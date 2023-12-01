from CelestialObject import CelestialObject
from StrategyFactory import calculate_observability_score

observability_score_sun = calculate_observability_score(CelestialObject('Sun', 'Sun', -26.74, 31.00, 39.00))
observability_score_moon = calculate_observability_score(CelestialObject('Moon', 'Moon', -12.60, 31.00, 39.00))
observability_score_jupiter = calculate_observability_score(CelestialObject('Jupiter', 'Planet', -2.40, 0.77, 43.00))
observability_score_sirius = calculate_observability_score(CelestialObject('Sirius', 'DeepSky', -1.46, 0.0001, 90.00))
observability_score_betelgeuse = calculate_observability_score(CelestialObject('Betelgeuse', 'DeepSky', 0.5, 0.0001, 45.00))
observability_score_vega = calculate_observability_score(CelestialObject('Vega', 'DeepSky', 0.03, 0.0001, 50.00))
observability_score_andromeda = calculate_observability_score(CelestialObject('Andromeda Galaxy', 'DeepSky', 3.44, 190.00, 60.00))
observability_score_veil = calculate_observability_score(CelestialObject('Veil Nebula', 'DeepSky', 7.0, 180.00, 55.00))

print(f"Observability score for Sun: {observability_score_sun}")
print(f"Observability score for Moon: {observability_score_moon}")
print(f"Observability score for Jupiter: {observability_score_jupiter}")
print(f"Observability score for Sirius: {observability_score_sirius}")
print(f"Observability score for Betelgeuse: {observability_score_betelgeuse}")
print(f"Observability score for Vega: {observability_score_vega}")
print(f"Observability score for Andromeda: {observability_score_andromeda}")
print(f"Observability score for Veil: {observability_score_veil}")