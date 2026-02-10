from dataclasses import dataclass
import math


@dataclass
class MoonConditions:
    """
    Represents current moon state and position.
    """
    phase: float              # 0-1 (0=new, 0.5=full, 1=new)
    illumination: float       # 0-100 percentage
    altitude: float           # degrees above horizon (-90 to +90)
    ra: float                 # right ascension (decimal degrees)
    dec: float                # declination (decimal degrees)

    def calculate_separation(self, target_ra: float, target_dec: float) -> float:
        """
        Calculate angular separation between moon and target in degrees.
        Uses spherical law of cosines.
        """
        ra1, dec1 = math.radians(self.ra), math.radians(self.dec)
        ra2, dec2 = math.radians(target_ra), math.radians(target_dec)

        cos_separation = (math.sin(dec1) * math.sin(dec2) +
                         math.cos(dec1) * math.cos(dec2) *
                         math.cos(ra1 - ra2))

        # Clamp to avoid floating point errors with acos
        cos_separation = max(-1.0, min(1.0, cos_separation))

        return math.degrees(math.acos(cos_separation))

    def is_above_horizon(self) -> bool:
        """Check if the moon is currently visible"""
        return self.altitude > 0
