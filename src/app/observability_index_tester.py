from app.domain.model.celestial_object import CelestialObject
from app.domain.model.object_classification import ObjectClassification, AngularSize
from app.domain.services.observability_calculation_service import ObservabilityCalculationService

if __name__ == '__main__':
    observability_calculation_service = ObservabilityCalculationService()

    observability_score_sun = observability_calculation_service.score_celestial_object(
        CelestialObject(name='Sun', canonical_id='Sun', classification=ObjectClassification(primary_type='sun'), magnitude=-26.74, size=AngularSize(31.00, 31.00), altitude=39.00))
    observability_score_moon = observability_calculation_service.score_celestial_object(
        CelestialObject(name='Moon', canonical_id='Moon', classification=ObjectClassification(primary_type='moon'), magnitude=-12.60, size=AngularSize(31.00, 31.00), altitude=39.00))
    observability_score_jupiter = observability_calculation_service.score_celestial_object(
        CelestialObject(name='Jupiter', canonical_id='Jupiter', classification=ObjectClassification(primary_type='planet'), magnitude=-2.40, size=AngularSize(0.77, 0.77), altitude=43.00))
    observability_score_sirius = observability_calculation_service.score_celestial_object(
        CelestialObject(name='Sirius', canonical_id='Sirius', classification=ObjectClassification(primary_type='star'), magnitude=-1.46, size=AngularSize(0.0001, 0.0001), altitude=90.00))
    observability_score_betelgeuse = observability_calculation_service.score_celestial_object(
        CelestialObject(name='Betelgeuse', canonical_id='Betelgeuse', classification=ObjectClassification(primary_type='star'), magnitude=0.5, size=AngularSize(0.0001, 0.0001), altitude=45.00))
    observability_score_vega = observability_calculation_service.score_celestial_object(
        CelestialObject(name='Vega', canonical_id='Vega', classification=ObjectClassification(primary_type='star'), magnitude=0.03, size=AngularSize(0.0001, 0.0001), altitude=50.00))
    observability_score_andromeda = observability_calculation_service.score_celestial_object(
        CelestialObject(name='Andromeda Galaxy', canonical_id='M31', classification=ObjectClassification(primary_type='galaxy', subtype='spiral'), magnitude=3.44, size=AngularSize(190.00, 190.00), altitude=60.00))
    observability_score_veil = observability_calculation_service.score_celestial_object(
        CelestialObject(name='Veil Nebula', canonical_id='NGC6992', classification=ObjectClassification(primary_type='nebula', subtype='supernova_remnant'), magnitude=7.0, size=AngularSize(180.00, 180.00), altitude=55.00))

    print(f"Observability score for Sun: {observability_score_sun}")
    print(f"Observability score for Moon: {observability_score_moon}")
    print(f"Observability score for Jupiter: {observability_score_jupiter}")
    print(f"Observability score for Sirius: {observability_score_sirius}")
    print(f"Observability score for Betelgeuse: {observability_score_betelgeuse}")
    print(f"Observability score for Vega: {observability_score_vega}")
    print(f"Observability score for Andromeda: {observability_score_andromeda}")
    print(f"Observability score for Veil: {observability_score_veil}")
