"""
Object classification models for Phase 7 object-type-aware scoring.

These models support hierarchical classification (primary type → subtype → morphology)
to enable intelligent scoring based on object characteristics.
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class ObjectClassification:
    """
    Hierarchical classification for celestial objects.

    Examples:
        - Galaxy: primary_type="galaxy", subtype="spiral", morphology="SA(s)b"
        - Nebula: primary_type="nebula", subtype="emission", morphology=None
        - Cluster: primary_type="cluster", subtype="globular", morphology=None
    """
    primary_type: str      # "galaxy", "nebula", "cluster", "double_star", "planet"
    subtype: Optional[str] = None  # "spiral", "emission", "globular", etc.
    morphology: Optional[str] = None  # Hubble type for galaxies: "SA(s)b"

    # Galaxy classification helpers
    def is_galaxy(self) -> bool:
        return self.primary_type == "galaxy"

    def is_spiral_galaxy(self) -> bool:
        return self.is_galaxy() and self.subtype == "spiral"

    def is_elliptical_galaxy(self) -> bool:
        return self.is_galaxy() and self.subtype == "elliptical"

    def is_lenticular_galaxy(self) -> bool:
        return self.is_galaxy() and self.subtype == "lenticular"

    # Nebula classification helpers
    def is_nebula(self) -> bool:
        return self.primary_type == "nebula"

    def is_emission_nebula(self) -> bool:
        return self.is_nebula() and self.subtype == "emission"

    def is_reflection_nebula(self) -> bool:
        return self.is_nebula() and self.subtype == "reflection"

    def is_dark_nebula(self) -> bool:
        return self.is_nebula() and self.subtype == "dark"

    def is_planetary_nebula(self) -> bool:
        return self.is_nebula() and self.subtype == "planetary"

    # Cluster classification helpers
    def is_cluster(self) -> bool:
        return self.primary_type == "cluster"

    def is_globular_cluster(self) -> bool:
        return self.is_cluster() and self.subtype == "globular"

    def is_open_cluster(self) -> bool:
        return self.is_cluster() and self.subtype == "open"

    # Other types
    def is_double_star(self) -> bool:
        return self.primary_type == "double_star"

    def is_solar_system(self) -> bool:
        return self.primary_type in ["planet", "moon", "sun", "comet", "asteroid"]


@dataclass
class SurfaceBrightness:
    """
    Surface brightness with provenance tracking.

    Different sources provide different surface brightness definitions:
    - OpenNGC: Mean SB within 25 mag isophote (B-band) for galaxies
    - Computed: Average SB from integrated mag + apparent area
    - Horizons: Surface brightness for Solar System bodies
    """
    value: float  # mag/arcsec²
    source: str   # "openngc_surf_br_B", "computed_mag_size", "horizons"
    band: Optional[str] = "V"  # Photometric band: "B", "V", "R", etc.


@dataclass
class AngularSize:
    """
    Angular dimensions for extended objects.

    Supports both circular (single dimension) and elliptical (major/minor axes)
    objects with optional position angle for orientation.
    """
    major_arcmin: float
    minor_arcmin: Optional[float] = None  # For elliptical objects
    position_angle_deg: Optional[float] = None  # East of North

    def is_circular(self) -> bool:
        """Check if object is approximately circular"""
        if self.minor_arcmin is None:
            return True
        return abs(self.major_arcmin - self.minor_arcmin) < 0.1

    def area_sq_arcmin(self) -> float:
        """Calculate approximate area assuming ellipse"""
        import math
        minor = self.minor_arcmin if self.minor_arcmin else self.major_arcmin
        # Area = π * a * b where a,b are semi-major/minor axes
        return math.pi * (self.major_arcmin / 2.0) * (minor / 2.0)

    def area_sq_arcsec(self) -> float:
        """Calculate area in square arcseconds"""
        return self.area_sq_arcmin() * 3600.0  # 1 arcmin² = 3600 arcsec²
