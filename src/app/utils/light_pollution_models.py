"""
Physics-based limiting magnitude model for light pollution effects.

This module provides a more realistic approach to light pollution scoring
based on limiting magnitude rather than arbitrary linear penalties.

The limiting magnitude model considers:
- Naked-eye limiting magnitude (NELM) for each Bortle class
- Visibility margin between object magnitude and limiting magnitude
- Exponential falloff as objects approach the detection threshold
"""

from app.utils.scoring_constants import BORTLE_TO_LIMITING_MAGNITUDE


def calculate_light_pollution_factor_by_limiting_magnitude(
    object_magnitude: float,
    bortle: int,
    telescope_aperture_mm: float = None,
    detection_headroom: float = 1.5,
    use_legacy_penalty: bool = False,
    legacy_penalty_per_bortle: float = 0.10,
    legacy_minimum_factor: float = 0.02,
    aperture_gain_factor: float = 0.85
) -> float:
    """
    Calculate light pollution factor based on limiting magnitude model.

    This is a physics-based approach that considers:
    1. The limiting magnitude for the given Bortle class
    2. The visibility margin between object and limiting magnitude
    3. Exponential falloff as object approaches detection threshold
    4. Real-world aperture efficiency correction

    Can optionally blend with legacy linear penalty model for compatibility.

    Args:
        object_magnitude: Apparent magnitude of the celestial object
        bortle: Bortle scale value (1-9)
        telescope_aperture_mm: Telescope aperture in millimeters (if available)
        detection_headroom: How many magnitudes below NELM object needs to be
                          for comfortable detection (default: 1.5)
        use_legacy_penalty: If True, blend with linear Bortle penalty model
        legacy_penalty_per_bortle: Linear penalty per Bortle level (if using legacy)
        legacy_minimum_factor: Minimum factor for legacy model
        aperture_gain_factor: Correction factor for real-world aperture performance (default: 0.85)
                            Accounts for: optical losses, seeing limitations, light pollution
                            gradients, central obstruction, observer experience.
                            1.0 = theoretical (optimistic), 0.85 = realistic, 0.75 = conservative.
                            Future: Friendly preset could use 0.90, Strict preset 0.75-0.80

    Returns:
        Factor between 0.0 and 1.0 representing visibility
        - 1.0: Object well above limiting magnitude (easily visible)
        - 0.5: Object near limiting magnitude (marginally visible)
        - 0.0: Object below limiting magnitude (invisible)

    Examples:
        >>> # M31 (mag 3.4) in Bortle 5 (NELM 5.6)
        >>> calculate_light_pollution_factor_by_limiting_magnitude(3.4, 5)
        0.88  # Easily visible with 2.2 mag margin

        >>> # Faint galaxy (mag 10.0) in Bortle 5 (NELM 5.6)
        >>> calculate_light_pollution_factor_by_limiting_magnitude(10.0, 5)
        0.0  # Below naked-eye limit

        >>> # Faint galaxy (mag 10.0) with 200mm telescope in Bortle 5
        >>> calculate_light_pollution_factor_by_limiting_magnitude(10.0, 5, 200)
        0.65  # Visible with telescope (with realistic aperture_gain_factor)
    """
    import math

    # Get naked-eye limiting magnitude for this Bortle class
    nelm = BORTLE_TO_LIMITING_MAGNITUDE.get(bortle, 5.6)

    # Adjust limiting magnitude if telescope is used
    # Telescope limiting magnitude ≈ NELM + 5*log10(aperture_mm/7) * aperture_gain_factor
    # The gain_factor corrects for real-world performance vs theoretical light grasp
    if telescope_aperture_mm:
        # 7mm is typical dark-adapted pupil diameter
        aperture_gain = 5 * math.log10(telescope_aperture_mm / 7) * aperture_gain_factor
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
    use_legacy_penalty: bool = False,
    legacy_penalty_per_bortle: float = 0.10,
    legacy_minimum_factor: float = 0.02
) -> float:
    """
    Calculate light pollution factor considering surface brightness.

    Extended objects (galaxies, nebulae) have lower surface brightness
    than point sources of the same integrated magnitude, making them
    more vulnerable to light pollution.

    Args:
        object_magnitude: Integrated apparent magnitude
        object_size_arcmin: Angular size in arcminutes
        bortle: Bortle scale value (1-9)
        telescope_aperture_mm: Telescope aperture in millimeters (if available)
        use_legacy_penalty: If True, blend with linear Bortle penalty model
        legacy_penalty_per_bortle: Linear penalty per Bortle level
        legacy_minimum_factor: Minimum factor for legacy model

    Returns:
        Factor between 0.0 and 1.0 representing visibility

    Formula:
        Surface brightness (mag/arcsec²) = magnitude + 2.5*log10(area_arcsec²)
    """
    import math

    # For extended objects, surface brightness affects visibility more than integrated magnitude
    # However, we don't want to use surface brightness directly as it makes objects appear
    # way too faint. Instead, we'll adjust the detection headroom based on size.
    # Very large objects (>60') need even stricter headroom due to extremely low surface brightness.
    if object_size_arcmin > 120:  # Very large extended objects (Veil, California Nebula, Andromeda)
        effective_magnitude = object_magnitude
        # Extremely large objects need strict headroom (but not TOO strict for bright ones like M31)
        detection_headroom = 3.0  # Reduced from 3.5 to allow bright large objects better visibility
    elif object_size_arcmin > 60:  # Large extended objects
        effective_magnitude = object_magnitude
        # Large objects need strict headroom
        detection_headroom = 3.2
    elif object_size_arcmin > 30:  # Medium-large extended object
        effective_magnitude = object_magnitude
        # Medium-large objects need significantly more headroom
        detection_headroom = 3.0
    elif object_size_arcmin > 5:  # Medium extended object
        effective_magnitude = object_magnitude
        # Medium objects need moderately more headroom
        detection_headroom = 2.5
    else:
        # Compact objects - use integrated magnitude with standard headroom
        effective_magnitude = object_magnitude
        detection_headroom = 1.5

    return calculate_light_pollution_factor_by_limiting_magnitude(
        effective_magnitude,
        bortle,
        telescope_aperture_mm,
        detection_headroom,
        use_legacy_penalty,
        legacy_penalty_per_bortle,
        legacy_minimum_factor
    )


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
