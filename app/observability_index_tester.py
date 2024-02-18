from domain.model.celestial_object import CelestialObject
from domain.services.observability_calculation_service import ObservabilityCalculationService

if __name__ == '__main__':
    observability_calculation_service = ObservabilityCalculationService()

    observability_score_sun = observability_calculation_service.calculate_observability_score(CelestialObject('Sun', 'Sun', -26.74, 31.00, 39.00))
    observability_score_moon = observability_calculation_service.calculate_observability_score(CelestialObject('Moon', 'Moon', -12.60, 31.00, 39.00))
    observability_score_jupiter = observability_calculation_service.calculate_observability_score(CelestialObject('Jupiter', 'Planet', -2.40, 0.77, 43.00))
    observability_score_sirius = observability_calculation_service.calculate_observability_score(CelestialObject('Sirius', 'DeepSky', -1.46, 0.0001, 90.00))
    observability_score_betelgeuse = observability_calculation_service.calculate_observability_score(CelestialObject('Betelgeuse', 'DeepSky', 0.5, 0.0001, 45.00))
    observability_score_vega = observability_calculation_service.calculate_observability_score(CelestialObject('Vega', 'DeepSky', 0.03, 0.0001, 50.00))
    observability_score_andromeda = observability_calculation_service.calculate_observability_score(CelestialObject('Andromeda Galaxy', 'DeepSky', 3.44, 190.00, 60.00))
    observability_score_veil = observability_calculation_service.calculate_observability_score(CelestialObject('Veil Nebula', 'DeepSky', 7.0, 180.00, 55.00))

    print(f"Observability score for Sun: {observability_score_sun}")
    print(f"Observability score for Moon: {observability_score_moon}")
    print(f"Observability score for Jupiter: {observability_score_jupiter}")
    print(f"Observability score for Sirius: {observability_score_sirius}")
    print(f"Observability score for Betelgeuse: {observability_score_betelgeuse}")
    print(f"Observability score for Vega: {observability_score_vega}")
    print(f"Observability score for Andromeda: {observability_score_andromeda}")
    print(f"Observability score for Veil: {observability_score_veil}")
