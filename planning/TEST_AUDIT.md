# Test Suite Audit - Phase 6

**Generated:** Automated analysis
**Total Tests:** 131

---

## Core Unit Tests

### TestAltitudeImpact (4 tests)

**test_andromeda_high_beats_low**
- **Category:** Tier 1: Physics Ordering
- **Description:** Andromeda at 60° should beat Andromeda at 20°.

**test_below_horizon_is_zero**
- **Category:** Tier 4: Edge Case/Sanity
- **Description:** Objects below horizon should score zero.

**test_jupiter_high_beats_low**
- **Category:** Tier 1: Physics Ordering
- **Description:** Jupiter at 70° should beat Jupiter at 15°.

**test_moon_high_beats_low**
- **Category:** Tier 1: Physics Ordering
- **Description:** Moon at 80° should beat Moon at 10°.

### TestApertureImpactOnFaintObjects (5 tests)

**test_aperture_helps_horsehead**
- **Category:** Tier 3: Equipment/Mixed
- **Description:** Horsehead (mag 10) should score much higher with large aperture.

**test_aperture_helps_ring_nebula**
- **Category:** Tier 3: Equipment/Mixed
- **Description:** Ring Nebula (mag 8.8) should score higher with large aperture.

**test_aperture_helps_whirlpool**
- **Category:** Tier 3: Equipment/Mixed
- **Description:** Whirlpool Galaxy should benefit from large aperture.

**test_aperture_minor_impact_on_jupiter**
- **Category:** Tier 3: Equipment/Mixed
- **Description:** Jupiter should only slightly benefit from aperture (already bright).

**test_aperture_minor_impact_on_moon**
- **Category:** Tier 3: Equipment/Mixed
- **Description:** Moon should barely benefit from aperture.

### TestComprehensiveSanityChecks (3 tests)

**test_brighter_always_better**
- **Category:** Tier 3: Equipment/Mixed
- **Description:** For same object type/size, brighter magnitude should always win.

**test_positive_scores**
- **Category:** Tier 4: Edge Case/Sanity
- **Description:** All visible objects should have positive scores.

**test_sun_always_highest**
- **Category:** Tier 4: Edge Case/Sanity
- **Description:** Sun should rank highest among all objects.

### TestDeepSkyMagnitudeOrdering (6 tests)

**test_andromeda_beats_orion_nebula**
- **Category:** Tier 1: Physics Ordering
- **Description:** Andromeda (mag 3.44) should beat Orion Nebula (mag 4.0).

**test_dumbbell_beats_ring_nebula**
- **Category:** Tier 1: Physics Ordering
- **Description:** Dumbbell (mag 7.5) should beat Ring Nebula (mag 8.8).

**test_ic_1396_beats_horsehead**
- **Category:** Tier 1: Physics Ordering
- **Description:** IC 1396 (mag 9.5) should beat Horsehead (mag 10.0).

**test_orion_nebula_beats_veil_nebula**
- **Category:** Tier 1: Physics Ordering
- **Description:** Orion Nebula (mag 4.0) should beat Veil Nebula (mag 7.0).

**test_pleiades_beats_andromeda**
- **Category:** Tier 1: Physics Ordering
- **Description:** Pleiades (mag 1.6) should beat Andromeda (mag 3.44).

**test_whirlpool_beats_ic_1396**
- **Category:** Tier 1: Physics Ordering
- **Description:** Whirlpool (mag 8.4) should beat IC 1396 (mag 9.5).

### TestLightPollutionGradient (2 tests)

**test_orion_nebula_gradient**
- **Category:** Tier 3: Equipment/Mixed
- **Description:** Orion Nebula: dark > suburban > city.

**test_whirlpool_gradient**
- **Category:** Tier 3: Equipment/Mixed
- **Description:** Whirlpool Galaxy: dark > suburban > city.

### TestLightPollutionImpactOnDeepSky (4 tests)

**test_andromeda_hurt_by_suburbs**
- **Category:** Tier 5: Arbitrary Threshold
- **Description:** Andromeda should lose 30-50% in suburbs.

**test_horsehead_devastated_by_city_light**
- **Category:** Tier 5: Arbitrary Threshold
- **Description:** Horsehead (very faint) should lose 70%+ in city.

**test_orion_nebula_moderately_affected**
- **Category:** Tier 5: Arbitrary Threshold
- **Description:** Orion Nebula (bright DSO) should be moderately affected.

**test_ring_nebula_hurt_by_city_light**
- **Category:** Tier 5: Arbitrary Threshold
- **Description:** Ring Nebula should lose 50%+ score in city.

### TestLightPollutionImpactOnPlanets (3 tests)

**test_jupiter_resilient_to_light_pollution**
- **Category:** Tier 5: Arbitrary Threshold
- **Description:** Jupiter should be 90%+ visible even in city.

**test_moon_unaffected_by_light_pollution**
- **Category:** Tier 5: Arbitrary Threshold
- **Description:** Moon should be essentially unaffected by light pollution.

**test_saturn_resilient_to_light_pollution**
- **Category:** Tier 5: Arbitrary Threshold
- **Description:** Saturn should remain visible in city.

### TestMagnificationImpactOnLargeObjects (3 tests)

**test_andromeda_prefers_low_magnification**
- **Category:** Tier 3: Equipment/Mixed
- **Description:** Andromeda (190 arcmin) should prefer low magnification.

**test_pleiades_prefers_low_magnification**
- **Category:** Tier 3: Equipment/Mixed
- **Description:** Pleiades (110 arcmin) should prefer very low magnification.

**test_veil_nebula_prefers_low_magnification**
- **Category:** Tier 3: Equipment/Mixed
- **Description:** Veil Nebula (180 arcmin) should prefer low magnification.

### TestMagnificationImpactOnPlanets (2 tests)

**test_jupiter_prefers_medium_magnification_over_low**
- **Category:** Tier 3: Equipment/Mixed
- **Description:** Jupiter should score better with medium magnification than low.

**test_saturn_prefers_high_magnification**
- **Category:** Tier 3: Equipment/Mixed
- **Description:** Saturn should score better with higher magnification.

### TestMoonVsOtherObjectTypes (7 tests)

**test_moon_beats_andromeda**
- **Category:** Tier 1: Physics Ordering
- **Description:** Moon should score higher than Andromeda Galaxy.

**test_moon_beats_brightest_star**
- **Category:** Tier 1: Physics Ordering
- **Description:** Moon should score higher than Sirius (brightest star).

**test_moon_beats_horsehead**
- **Category:** Tier 1: Physics Ordering
- **Description:** Moon should score higher than Horsehead Nebula (very faint).

**test_moon_beats_orion_nebula**
- **Category:** Tier 1: Physics Ordering
- **Description:** Moon should score higher than Orion Nebula.

**test_moon_beats_pleiades**
- **Category:** Tier 1: Physics Ordering
- **Description:** Moon should score higher than Pleiades.

**test_moon_beats_ring_nebula**
- **Category:** Tier 1: Physics Ordering
- **Description:** Moon should score higher than Ring Nebula.

**test_moon_beats_vega**
- **Category:** Tier 1: Physics Ordering
- **Description:** Moon should score higher than Vega.

### TestNoEquipmentPenalty (5 tests)

**test_horsehead_needs_equipment**
- **Category:** Tier 5: Arbitrary Threshold
- **Description:** Horsehead should score < 30% without equipment.

**test_jupiter_okay_without_equipment**
- **Category:** Tier 5: Arbitrary Threshold
- **Description:** Jupiter should still be visible naked eye (> 70% score).

**test_moon_excellent_without_equipment**
- **Category:** Tier 5: Arbitrary Threshold
- **Description:** Moon should be 90%+ visible naked eye.

**test_ring_nebula_needs_equipment**
- **Category:** Tier 5: Arbitrary Threshold
- **Description:** Ring Nebula should score much lower without equipment.

**test_sirius_visible_naked_eye**
- **Category:** Tier 5: Arbitrary Threshold
- **Description:** Sirius should be 80%+ visible naked eye.

### TestPlanetsVsStars (4 tests)

**test_jupiter_beats_sirius**
- **Category:** Tier 1: Physics Ordering
- **Description:** Jupiter (mag -2.4) should score higher than Sirius (mag -1.46).

**test_jupiter_beats_vega**
- **Category:** Tier 1: Physics Ordering
- **Description:** Jupiter (mag -2.4) should score higher than Vega (mag 0.03).

**test_sirius_beats_saturn**
- **Category:** Tier 1: Physics Ordering
- **Description:** Sirius (mag -1.46) should score higher than Saturn (mag 0.5).

**test_vega_beats_saturn**
- **Category:** Tier 1: Physics Ordering
- **Description:** Vega (mag 0.03) should score higher than Saturn (mag 0.5).

### TestSolarSystemBrightnessOrdering (8 tests)

**test_jupiter_beats_saturn**
- **Category:** Tier 1: Physics Ordering
- **Description:** Jupiter (mag -2.4) should score higher than Saturn (mag 0.5).

**test_mars_beats_saturn**
- **Category:** Tier 1: Physics Ordering
- **Description:** Mars (mag -1.0) should score higher than Saturn (mag 0.5).

**test_moon_beats_jupiter**
- **Category:** Tier 1: Physics Ordering
- **Description:** Moon should always score higher than Jupiter.

**test_moon_beats_venus**
- **Category:** Tier 1: Physics Ordering
- **Description:** Moon should score higher than Venus.

**test_saturn_beats_uranus**
- **Category:** Tier 1: Physics Ordering
- **Description:** Saturn (mag 0.5) should score higher than Uranus (mag 5.7).

**test_sun_beats_moon**
- **Category:** Tier 1: Physics Ordering
- **Description:** Sun should always score higher than Moon (both at same altitude).

**test_uranus_beats_neptune**
- **Category:** Tier 1: Physics Ordering
- **Description:** Uranus (mag 5.7) should score higher than Neptune (mag 7.8).

**test_venus_beats_jupiter**
- **Category:** Tier 1: Physics Ordering
- **Description:** Venus (mag -4) should score higher than Jupiter (mag -2.4).

### TestStarsVsDeepSkyObjects (4 tests)

**test_sirius_beats_orion_nebula**
- **Category:** Tier 1: Physics Ordering
- **Description:** Sirius (mag -1.46) should beat Orion Nebula (mag 4.0).

**test_sirius_beats_ring_nebula**
- **Category:** Tier 1: Physics Ordering
- **Description:** Sirius (mag -1.46) should beat Ring Nebula (mag 8.8).

**test_vega_beats_andromeda**
- **Category:** Tier 1: Physics Ordering
- **Description:** Vega (mag 0.03) should beat Andromeda (mag 3.44).

**test_vega_beats_horsehead**
- **Category:** Tier 1: Physics Ordering
- **Description:** Vega should beat Horsehead Nebula (very faint).

---

## Advanced Scenarios

### TestCombinedAdversity (2 tests)

**test_bright_object_survives_adversity**
- **Category:** Tier 5: Arbitrary Threshold
- **Description:** Jupiter should remain observable even in moderate adversity.

**test_faint_object_near_moon_in_clouds**
- **Category:** Tier 5: Arbitrary Threshold
- **Description:** Faint object near moon in cloudy weather should be nearly impossible.

### TestEdgeCases (7 tests)

**test_extremely_bright_object**
- **Category:** Tier 3: Equipment/Mixed
- **Description:** Extremely bright object should score very high.

**test_extremely_faint_object**
- **Category:** Tier 3: Equipment/Mixed
- **Description:** Extremely faint object (mag 15) should score low but not zero.

**test_huge_extended_object**
- **Category:** Tier 3: Equipment/Mixed
- **Description:** Huge object (300 arcmin) should prefer very low mag.

**test_object_at_zenith**
- **Category:** Tier 3: Equipment/Mixed
- **Description:** Object at 90° altitude should score well.

**test_object_below_horizon_zero**
- **Category:** Tier 3: Equipment/Mixed
- **Description:** Object below horizon should score exactly zero.

**test_object_just_above_horizon**
- **Category:** Tier 3: Equipment/Mixed
- **Description:** Object at 1° altitude should score poorly but not zero.

**test_tiny_object**
- **Category:** Tier 3: Equipment/Mixed
- **Description:** Tiny object (0.01 arcmin) should benefit from high mag.

### TestMoonOccultation (2 tests)

**test_barely_past_moon_still_very_hard**
- **Category:** Tier 5: Arbitrary Threshold
- **Description:** Object 0.5° from moon edge should be nearly impossible.

**test_occultation_zero_score**
- **Category:** Tier 3: Equipment/Mixed
- **Description:** Object at 0° separation (behind moon) should score zero.

### TestMoonProximityBasic (2 tests)

**test_object_near_full_moon_severe_penalty**
- **Category:** Tier 5: Arbitrary Threshold
- **Description:** Object 10° from full moon should lose 70%+ score.

**test_object_very_close_to_full_moon**
- **Category:** Tier 5: Arbitrary Threshold
- **Description:** Object 5° from full moon should be nearly impossible.

### TestMoonProximityByPhase (3 tests)

**test_crescent_moon_minor_penalty**
- **Category:** Tier 3: Equipment/Mixed
- **Description:** Crescent moon (10% illumination) should have minor penalty.

**test_new_moon_no_penalty**
- **Category:** Tier 3: Equipment/Mixed
- **Description:** New moon (0% illumination) should not penalize nearby objects.

**test_quarter_moon_moderate_penalty**
- **Category:** Tier 3: Equipment/Mixed
- **Description:** Quarter moon (50% illumination) should have moderate penalty.

### TestMoonProximityBySeparation (2 tests)

**test_double_separation_significant_improvement**
- **Category:** Tier 3: Equipment/Mixed
- **Description:** Doubling separation should significantly improve score.

**test_separation_gradient**
- **Category:** Tier 3: Equipment/Mixed
- **Description:** Score should increase with separation from full moon.

### TestMoonProximityOnBrightObjects (2 tests)

**test_faint_object_devastated_by_moon**
- **Category:** Tier 5: Arbitrary Threshold
- **Description:** Faint object should lose 80%+ near moon.

**test_jupiter_resilient_to_moon**
- **Category:** Tier 5: Arbitrary Threshold
- **Description:** Jupiter should maintain 60%+ score even near moon.

### TestScoreNormalization (2 tests)

**test_normalized_scores_in_range**
- **Category:** Tier 3: Equipment/Mixed
- **Description:** Normalized scores should be in reasonable range (0-100ish).

**test_raw_scores_positive_for_visible**
- **Category:** Tier 3: Equipment/Mixed
- **Description:** Raw scores should be positive for visible objects.

### TestWeatherGradient (1 tests)

**test_weather_gradient_jupiter**
- **Category:** Tier 3: Equipment/Mixed
- **Description:** Jupiter: clear > light clouds > heavy clouds > overcast.

### TestWeatherImpactClear (1 tests)

**test_clear_weather_no_penalty**
- **Category:** Tier 3: Equipment/Mixed
- **Description:** Clear weather should not reduce score.

### TestWeatherImpactCloudy (3 tests)

**test_overcast_devastates_jupiter**
- **Category:** Tier 5: Arbitrary Threshold
- **Description:** Even Jupiter should be nearly invisible in overcast.

**test_overcast_devastates_moon**
- **Category:** Tier 5: Arbitrary Threshold
- **Description:** Even Moon should be barely visible in overcast.

**test_overcast_kills_faint_objects**
- **Category:** Tier 3: Equipment/Mixed
- **Description:** Faint objects should be impossible in overcast.

### TestWeatherImpactPartialClouds (2 tests)

**test_25_percent_clouds**
- **Category:** Tier 5: Arbitrary Threshold
- **Description:** 25% cloud cover should reduce score by ~25%.

**test_partial_clouds_proportional_penalty**
- **Category:** Tier 5: Arbitrary Threshold
- **Description:** 50% cloud cover should reduce score by ~50%.

---

## Limiting Magnitude Model

### TestApertureDoubleCountingIssue (1 tests)

**test_aperture_double_counting_documented**
- **Category:** Tier 3: Equipment/Mixed
- **Description:** Document that aperture influences both equipment and site factors.

This is by design but needs monitoring to ensure the combined effect
doesn't make "bigger scope always wins" regardless of conditions.

Proper balance:
- Aperture in site_factor: handles visibility threshold (can you see it?)
- Equipment_factor: should focus more on magnification, framing, etc.

### TestDoublePenaltyIssue (1 tests)

**test_large_object_not_overly_crushed**
- **Category:** Tier 5: Arbitrary Threshold
- **Description:** Andromeda (190') in dark skies should still score well.

The headroom adjustment (3.5 for size >120') appropriately makes it harder,
but we shouldn't apply an ADDITIONAL 15% size penalty on top of that.

### TestIntegratedBehavior (2 tests)

**test_aperture_extends_limiting_magnitude**
- **Category:** Tier 5: Arbitrary Threshold
- **Description:** Larger aperture should extend the limiting magnitude,
making fainter objects visible.

**test_physics_model_provides_hard_cutoff**
- **Category:** Tier 3: Equipment/Mixed
- **Description:** The physics-based model should provide hard visibility cutoffs.
Objects below limiting magnitude should return zero visibility.

### TestLegacyCompatibilityMode (2 tests)

**test_legacy_mode_maintains_linear_penalty**
- **Category:** Tier 3: Equipment/Mixed
- **Description:** Legacy mode should apply linear Bortle penalty.

**test_legacy_mode_still_enforces_visibility_cutoff**
- **Category:** Tier 3: Equipment/Mixed
- **Description:** Legacy mode should still return 0.0 for invisible objects.

### TestLimitingMagnitudePhysics (5 tests)

**test_aperture_makes_faint_objects_visible**
- **Category:** Tier 5: Arbitrary Threshold
- **Description:** Telescope aperture should make previously invisible objects visible.

**test_bright_object_always_visible**
- **Category:** Tier 5: Arbitrary Threshold
- **Description:** Bright objects (mag < 0) should be visible even in Bortle 9.

**test_exponential_falloff_near_threshold**
- **Category:** Tier 5: Arbitrary Threshold
- **Description:** Visibility should fall off exponentially as object approaches limiting magnitude.

**test_larger_aperture_better_than_smaller**
- **Category:** Tier 3: Equipment/Mixed
- **Description:** Larger aperture should give better visibility for same object.

**test_object_below_limiting_magnitude_invisible**
- **Category:** Tier 3: Equipment/Mixed
- **Description:** Objects fainter than limiting magnitude should score zero (invisible).

### TestPresetIntegration (2 tests)

**test_preset_should_control_aperture_gain**
- **Category:** Tier 3: Equipment/Mixed
- **Description:** Future enhancement: Presets should control aperture_gain_factor.

Friendly: 0.90 (optimistic)
Strict: 0.75 (conservative)
Default: 0.85 (realistic)

**test_preset_should_control_headroom_multiplier**
- **Category:** Tier 3: Equipment/Mixed
- **Description:** Future enhancement: Presets could scale detection_headroom.

Friendly: base headroom * 0.9
Strict: base headroom * 1.1

### TestRealisticOptimismGuards (4 tests)

**test_200mm_scope_bortle6_mag11_galaxy_documents_optimism**
- **Category:** Tier 5: Arbitrary Threshold
Error loading test_limiting_magnitude_model: 'charmap' codec can't encode character '\u2192' in position 197: character maps to <undefined>

## Benchmark Objects

### TestApertureImpactOnBenchmarks (2 tests)

**test_aperture_does_not_overcome_terrible_light_pollution**
- **Category:** Tier 5: Arbitrary Threshold
- **Description:** Even 300mm shouldn't make M51 excellent in Bortle 8

**test_large_aperture_helps_faint_galaxy_in_dark_skies**
- **Category:** Tier 3: Equipment/Mixed
- **Description:** M51 should be significantly better with 300mm vs 150mm in Bortle 4

### TestChallengingTierBenchmarks (3 tests)

**test_california_nebula_requires_excellent_conditions**
- **Category:** Tier 5: Arbitrary Threshold
- **Description:** California Nebula (mag 6.0, 150') is extremely challenging

**test_north_america_nebula_invisible_in_bortle_5**
- **Category:** Tier 5: Arbitrary Threshold
- **Description:** NGC 7000 (mag 4.0, 120') has extremely low surface brightness

**test_veil_nebula_needs_dark_skies**
- **Category:** Tier 5: Arbitrary Threshold
- **Description:** Veil Nebula (mag 7.0, 180') needs Bortle 3 to be visible

### TestCompactHighSurfaceBrightness (2 tests)

**test_compact_galaxies_benefit_from_concentration**
- **Category:** Tier 5: Arbitrary Threshold
- **Description:** M32 (mag 8.08, 8.7') should be visible in Bortle 6 despite moderate magnitude

**test_planetary_nebula_easier_than_galaxy_same_magnitude**
- **Category:** Tier 3: Equipment/Mixed
- **Description:** NGC 6572 (mag 8.1, 0.2') should be easier than M51 (mag 8.4, 11') despite similar magnitude

### TestEasyTierBenchmarks (3 tests)

**test_m13_visible_in_bortle_6_with_medium_scope**
- **Category:** Tier 5: Arbitrary Threshold
- **Description:** M13 (mag 5.8, 16.5') should be visible in Bortle 6 with 200mm

**test_m31_visible_in_bortle_5_with_small_scope**
- **Category:** Tier 5: Arbitrary Threshold
- **Description:** M31 (mag 3.44, 190') should be visible in Bortle 5 with 80mm scope

**test_m42_excellent_in_bortle_3_with_medium_scope**
- **Category:** Tier 5: Arbitrary Threshold
- **Description:** M42 (mag 4.0, 65') should score excellent in Bortle 3 with 200mm

### TestModerateTierBenchmarks (3 tests)

**test_m27_good_in_bortle_4_with_large_scope**
- **Category:** Tier 5: Arbitrary Threshold
- **Description:** M27 (mag 7.4, 8') should be good in Bortle 4 with large aperture

**test_m33_challenging_in_bortle_5**
- **Category:** Tier 5: Arbitrary Threshold
- **Description:** M33 (mag 5.72, 73') has very low surface brightness - challenging even in Bortle 5

**test_m51_invisible_in_bortle_7**
- **Category:** Tier 5: Arbitrary Threshold
- **Description:** M51 (mag 8.4, 11') should be invisible/marginal in Bortle 7

---

## Magnitude Constants

### TestMagnitudeConstants (7 tests)

**test_magnitude_offset_applied_correctly**
- **Category:** Tier 3: Equipment/Mixed
- **Description:** Verify that MAGNITUDE_OFFSET_DEEPSKY (12) is applied correctly.

The offset is used to bring deep-sky objects (typically mag 5-15)
into a scoreable range by shifting them toward brighter values.

**test_magnitude_score_formula_consistency**
- **Category:** Tier 3: Equipment/Mixed
- **Description:** Test that magnitude score formula produces expected relative scaling.

Brightness ratio between two objects should follow inverse logarithmic scale:
ratio = 10^(0.4 * (mag2 - mag1))

Example: 5 magnitude difference = 100× brightness difference

**test_precomputed_values_are_floats**
- **Category:** Tier 3: Equipment/Mixed
- **Description:** Ensure precomputed constants are float type (not int or string).

**test_precomputed_values_are_positive**
- **Category:** Tier 3: Equipment/Mixed
- **Description:** All magnitude scores should be positive.

**test_sirius_deepsky_magnitude_score**
- **Category:** Tier 3: Equipment/Mixed
Error loading test_magnitude_constants: 'charmap' codec can't encode character '\u2248' in position 269: character maps to <undefined>

## Summary by Tier

- **Tier 1: Physics Ordering:** 32 tests
- **Tier 3: Equipment/Mixed:** 46 tests
- **Tier 4: Edge Case/Sanity:** 3 tests
- **Tier 5: Arbitrary Threshold:** 40 tests

**Total:** 121 tests
