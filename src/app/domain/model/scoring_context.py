from dataclasses import dataclass
from typing import Optional

from app.orm.model.entities import Telescope, Eyepiece, ObservationSite


@dataclass
class ScoringContext:
    """
    Context object containing all environmental and equipment factors
    needed to score celestial object observability.
    """
    telescope: Optional[Telescope]
    eyepiece: Optional[Eyepiece]
    observation_site: Optional[ObservationSite]
    altitude: float  # Object's current altitude in degrees

    def has_equipment(self) -> bool:
        """Check if minimum required equipment is present for scoring"""
        return self.telescope is not None and self.eyepiece is not None

    def get_magnification(self) -> float:
        """Calculate magnification from telescope and eyepiece"""
        if not self.has_equipment():
            return 0.0
        return self.telescope.focal_length / self.eyepiece.focal_length

    def get_aperture_mm(self) -> int:
        """Get telescope aperture in millimeters"""
        return self.telescope.aperture if self.telescope else 0

    def get_bortle_number(self) -> int:
        """Extract Bortle scale number from observation site (1-9)"""
        if not self.observation_site:
            return 5  # Default to suburban (middle of scale)

        # Extract number from enum like "BORTLE_4"
        light_pollution_name = self.observation_site.light_pollution.name
        if light_pollution_name == "UNKNOWN":
            return 5  # Default to middle

        # Extract number from "BORTLE_X"
        try:
            return int(light_pollution_name.split('_')[1])
        except (IndexError, ValueError):
            return 5  # Fallback
