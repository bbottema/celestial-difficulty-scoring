from dataclasses import dataclass

from app.domain.light_pollution import LightPollution


@dataclass
class ObservationSite:
    id: int | None = None
    name: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    light_pollution: LightPollution | None = None

    def __post_init__(self):
        self.validate_coordinates()

    def validate_coordinates(self):
        if self.latitude is not None and not (-90 <= self.latitude <= 90):
            raise ValueError("Latitude must be between -90 and 90 degrees.")
        if self.longitude is not None and not (-180 <= self.longitude <= 180):
            raise ValueError("Longitude must be between -180 and 180 degrees.")
