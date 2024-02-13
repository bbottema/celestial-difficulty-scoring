from dataclasses import dataclass

from domain.entities.observation_site import ObservationSite


@dataclass
class Telescope:
    id: int | None = None
    name: str | None = None
    observation_site: ObservationSite | None = None
