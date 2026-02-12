"""
Physics-based limiting magnitude model for light pollution effects.

This module provides a more realistic approach to light pollution scoring
based on limiting magnitude rather than arbitrary linear penalties.

The limiting magnitude model considers:
- Naked-eye limiting magnitude (NELM) for each Bortle class
- Visibility margin between object magnitude and limiting magnitude
- Exponential falloff as objects approach the detection threshold

Phase 6.5: Integrated split aperture gain factor model for more accurate
telescope performance modeling.

Phase 7: Object-type-aware scoring with tailored detection headroom values
based on actual object classification (planetary nebula, spiral galaxy, etc.)
rather than generic size-based heuristics.
"""

from typing import Optional
from app.utils.scoring_constants import BORTLE_TO_LIMITING_MAGNITUDE
from app.utils.aperture_models import calculate_aperture_gain_factor
from app.domain.model.telescope_type import TelescopeType
from app.domain.model.object_classification import ObjectClassification


# Phase 7: Object-type-aware detection headroom values
# Lower headroom = easier to detect (high surface brightness, concentrated)
# Higher headroom = harder to detect (low surface brightness, diffuse)
HEADROOM_BY_OBJECT_TYPE = {
    # Planetary nebulae - compact, high surface brightness
    'planetary_nebula': 1.3,

    # Clusters - concentrated vs resolved
    'globular_cluster': 1.5,      # Concentrated core, easier
    'open_cluster': 1.7,           # Resolved stars, needs dark sky

    # Nebulae - emission vs reflection vs dark
    'emission_nebula': 2.5,        # Moderate SB (H-alpha emission)
    'reflection_nebula': 2.8,      # Fainter than emission
    'supernova_remnant': 3.2,      # Very faint, extended (Veil, Crab)
    'dark_nebula': 3.5,            # Extremely low contrast

    # Galaxies - spiral vs elliptical
    'spiral_galaxy': 3.0,          # Low SB, extended structure
    'elliptical_galaxy': 2.8,      # Slightly higher SB than spiral
    'lenticular_galaxy': 2.9,      # Between elliptical and spiral
    'irregular_galaxy': 2.9,       # Similar to lenticular

    # Fallback
    'default': 2.5                 # For unknown/unclassified objects
}


def calculate_light_pollution_factor_by_limiting_magnitude(
    object_magnitude: float,
    bortle: int,
    telescope_aperture_mm: float = None,
    telescope_type: TelescopeType = None,
    altitude: float = 45.0,
    observer_skill: str = 'intermediate',
    detection_headroom: float = 1.5,
    use_legacy_penalty: bool = False,
    legacy_penalty_per_bortle: float = 0.10,
    legacy_minimum_factor: float = 0.02,
    aperture_gain_factor: float = None  # Phase 6.5: Deprecated, use split model
) -> float:
    """
    Calculate light pollution factor based on limiting magnitude model.

    This is a physics-based approach that considers:
    1. The limiting magnitude for the given Bortle class
    2. The visibility margin between object and limiting magnitude
    3. Exponential falloff as object approaches detection threshold
    4. Real-world aperture efficiency correction (Phase 6.5: split model)

    Can optionally blend with legacy linear penalty model for compatibility.

    Phase 6.5: Aperture gain factor now calculated dynamically from telescope
    type, altitude, and observer skill instead of using single constant.

    Args:
        object_magnitude: Apparent magnitude of the celestial object
        bortle: Bortle scale value (1-9)
        telescope_aperture_mm: Telescope aperture in millimeters (if available)
        telescope_type: Type of telescope (for optical efficiency calculation)
        altitude: Object altitude in degrees (for seeing calculation)
        observer_skill: Observer experience level: 'beginner', 'intermediate', 'expert'
        detection_headroom: How many magnitudes below NELM object needs to be
                          for comfortable detection (default: 1.5)
        use_legacy_penalty: If True, blend with linear Bortle penalty model
        legacy_penalty_per_bortle: Linear penalty per Bortle level (if using legacy)
        legacy_minimum_factor: Minimum factor for legacy model
        aperture_gain_factor: DEPRECATED - Phase 6.5 uses split model instead.
                            If provided, overrides split model (for backward compatibility).

    Returns:
        Factor between 0.0 and 1.0 representing visibility
        - 1.0: Object well above limiting magnitude (easily visible)
        - 0.5: Object near limiting magnitude (marginally visible)
        - 0.0: Object below limiting magnitude (invisible)

    Examples:
        >>> # M31 (mag 3.4) in Bortle 5 (NELM 5.6) - naked eye
        >>> calculate_light_pollution_factor_by_limiting_magnitude(3.4, 5)
        0.88  # Easily visible with 2.2 mag margin

        >>> # Faint galaxy (mag 10.0) with 200mm Dobsonian at 45° altitude
        >>> calculate_light_pollution_factor_by_limiting_magnitude(
        ...     10.0, 5, 200, TelescopeType.DOBSONIAN, 45, 'intermediate'
        ... )
        ~0.50  # Marginally visible (Phase 6.5 split model)
    """
    import math

    # Get naked-eye limiting magnitude for this Bortle class
    nelm = BORTLE_TO_LIMITING_MAGNITUDE.get(bortle, 5.6)

    # Adjust limiting magnitude if telescope is used
    # Telescope limiting magnitude ≈ NELM + 5*log10(aperture_mm/7) * aperture_gain_factor
    # Phase 6.5: Calculate gain_factor dynamically from telescope properties
    if telescope_aperture_mm:
        # Calculate aperture gain factor
        if aperture_gain_factor is not None:
            # Backward compatibility: use provided factor if given
            gain_factor = aperture_gain_factor
        elif telescope_type is not None and altitude is not None:
            # Phase 6.5: Use split model (optical + seeing + observer)
            gain_factor = calculate_aperture_gain_factor(
                telescope_type, altitude, None, observer_skill
            )
        else:
            # Fallback to Phase 5 default if no telescope info
            gain_factor = 0.85

        # 7mm is typical dark-adapted pupil diameter
        aperture_gain = 5 * math.log10(telescope_aperture_mm / 7) * gain_factor
        limiting_magnitude = nelm + aperture_gain
    else:
        limiting_magnitude = nelm

    # Calculate visibility margin
    # Positive margin = object brighter than limit (visible)
    # Negative margin = object fainter than limit (invisible)
    visibility_margin = limiting_magnitude - object_magnitude

    # Objects fainter than limiting magnitude are invisible
    if visibility_margin < 0:
        return 0.0

    # If using legacy penalty model, blend the two approaches
    if use_legacy_penalty:
        # Calculate legacy linear penalty
        legacy_factor = 1.0 - (bortle * legacy_penalty_per_bortle)
        legacy_factor = max(legacy_factor, legacy_minimum_factor)

        # Calculate physics-based factor
        physics_factor = 1.0 - math.exp(-visibility_margin / detection_headroom)

        # Blend: use physics factor to modulate legacy factor
        # This preserves test expectations while adding visibility cutoff
        factor = legacy_factor * physics_factor
    else:
        # Pure physics-based model
        # Use exponential curve: factor = 1 - exp(-visibility_margin / headroom)
        # This creates smooth falloff as object approaches detection threshold
        factor = 1.0 - math.exp(-visibility_margin / detection_headroom)

    # Clamp to [0, 1] range
    return max(0.0, min(1.0, factor))


def calculate_light_pollution_factor_with_surface_brightness(
    object_magnitude: float,
    object_size_arcmin: float,
    bortle: int,
    telescope_aperture_mm: float = None,
    telescope_type: TelescopeType = None,
    altitude: float = 45.0,
    observer_skill: str = 'intermediate',
    object_classification: Optional[ObjectClassification] = None,  # Phase 7: NEW parameter
    use_legacy_penalty: bool = False,
    legacy_penalty_per_bortle: float = 0.10,
    legacy_minimum_factor: float = 0.02
) -> float:
    """
    Calculate light pollution factor considering surface brightness.

    Extended objects (galaxies, nebulae) have lower surface brightness
    than point sources of the same integrated magnitude, making them
    more vulnerable to light pollution.

    Phase 6.5: Passes telescope properties through to limiting magnitude function.
    Phase 7: Uses object classification for type-aware headroom selection.

    Args:
        object_magnitude: Integrated apparent magnitude
        object_size_arcmin: Angular size in arcminutes
        bortle: Bortle scale value (1-9)
        telescope_aperture_mm: Telescope aperture in millimeters (if available)
        telescope_type: Type of telescope (Phase 6.5 - for split aperture model)
        altitude: Object altitude in degrees (Phase 6.5 - for seeing calculation)
        observer_skill: Observer experience level (Phase 6.5)
        object_classification: ObjectClassification with type info (Phase 7)
        use_legacy_penalty: If True, blend with linear Bortle penalty model
        legacy_penalty_per_bortle: Linear penalty per Bortle level
        legacy_minimum_factor: Minimum factor for legacy model

    Returns:
        Factor between 0.0 and 1.0 representing visibility

    Formula:
        Surface brightness (mag/arcsec²) = magnitude + 2.5*log10(area_arcsec²)
    """
    import math

    # Phase 7: Type-aware headroom selection
    detection_headroom = _get_detection_headroom(object_classification, object_size_arcmin)

    return calculate_light_pollution_factor_by_limiting_magnitude(
        object_magnitude,
        bortle,
        telescope_aperture_mm,
        telescope_type,
        altitude,
        observer_skill,
        detection_headroom,
        use_legacy_penalty,
        legacy_penalty_per_bortle,
        legacy_minimum_factor
    )


def _get_detection_headroom(
    classification: Optional[ObjectClassification],
    size_arcmin: float
) -> float:
    """
    Determine detection headroom based on object classification.

    Phase 7: Primary logic - use classification-based headroom.
    Phase 5 fallback: Use size-based heuristic when classification unavailable.

    Args:
        classification: Object classification (if available)
        size_arcmin: Object size in arcminutes (fallback)

    Returns:
        Detection headroom magnitude value
    """
    # Phase 7: Try type-aware headroom first
    if classification:
        # Planetary nebulae
        if classification.is_planetary_nebula():
            return HEADROOM_BY_OBJECT_TYPE['planetary_nebula']

        # Clusters
        if classification.is_globular_cluster():
            return HEADROOM_BY_OBJECT_TYPE['globular_cluster']
        if classification.is_open_cluster():
            return HEADROOM_BY_OBJECT_TYPE['open_cluster']

        # Nebulae (non-planetary)
        if classification.is_emission_nebula():
            return HEADROOM_BY_OBJECT_TYPE['emission_nebula']
        if classification.is_reflection_nebula():
            return HEADROOM_BY_OBJECT_TYPE['reflection_nebula']
        if classification.is_dark_nebula():
            return HEADROOM_BY_OBJECT_TYPE['dark_nebula']

        # Supernova remnants (check primary type + subtype)
        if classification.primary_type == 'nebula' and classification.subtype == 'supernova_remnant':
            return HEADROOM_BY_OBJECT_TYPE['supernova_remnant']

        # Galaxies
        if classification.is_spiral_galaxy():
            return HEADROOM_BY_OBJECT_TYPE['spiral_galaxy']
        if classification.is_elliptical_galaxy():
            return HEADROOM_BY_OBJECT_TYPE['elliptical_galaxy']
        if classification.is_lenticular_galaxy():
            return HEADROOM_BY_OBJECT_TYPE['lenticular_galaxy']
        if classification.primary_type == 'galaxy' and classification.subtype == 'irregular':
            return HEADROOM_BY_OBJECT_TYPE['irregular_galaxy']

        # Generic galaxy (no subtype)
        if classification.is_galaxy():
            return HEADROOM_BY_OBJECT_TYPE['spiral_galaxy']  # Default to spiral

        # Other classified objects - use default
        return HEADROOM_BY_OBJECT_TYPE['default']

    # Phase 5 fallback: Size-based heuristic when classification unavailable
    if size_arcmin > 120:
        return 3.0  # Very large extended objects
    elif size_arcmin > 60:
        return 3.2  # Large extended objects
    elif size_arcmin > 30:
        return 3.0  # Medium-large extended objects
    elif size_arcmin > 5:
        return 2.5  # Medium extended objects
    else:
        return 1.5  # Compact objects


def get_visibility_status(
    object_magnitude: float,
    bortle: int,
    telescope_aperture_mm: float = None
) -> str:
    """
    Get human-readable visibility status for an object.

    Args:
        object_magnitude: Apparent magnitude of the celestial object
        bortle: Bortle scale value (1-9)
        telescope_aperture_mm: Telescope aperture in millimeters (if available)

    Returns:
        String describing visibility: "Excellent", "Good", "Marginal", or "Invisible"
    """
    factor = calculate_light_pollution_factor_by_limiting_magnitude(
        object_magnitude, bortle, telescope_aperture_mm
    )

    if factor >= 0.8:
        return "Excellent"
    elif factor >= 0.5:
        return "Good"
    elif factor > 0.0:
        return "Marginal"
    else:
        return "Invisible"
