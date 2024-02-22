from dataclasses import dataclass

from sqlalchemy import Column, Integer, String, Float, ForeignKey, Enum, Table
from sqlalchemy.orm import declarative_base, relationship

from app.domain.model.light_pollution import LightPollution
from app.domain.model.telescope_type import TelescopeType

Base = declarative_base()

# Association table
observation_site_telescope_association = Table(
    'observation_site_telescope', Base.metadata,
    Column('observation_site_id', Integer, ForeignKey('observation_sites.id')),
    Column('telescope_id', Integer, ForeignKey('telescopes.id')))


@dataclass
class ObservationSite(Base):
    __tablename__ = 'observation_sites'

    id: int = Column(Integer, primary_key=True)
    name: str = Column(String, unique=True, nullable=False)
    latitude: float | None = Column(Float, nullable=True)
    longitude: float | None = Column(Float, nullable=True)
    light_pollution: LightPollution = Column(Enum(LightPollution), nullable=False)

    telescopes = relationship("Telescope", secondary=observation_site_telescope_association, back_populates="observation_sites")

    def __post_init__(self):
        self.validate_coordinates()

    def validate_coordinates(self):
        if self.latitude is not None and not (-90 <= self.latitude <= 90):
            raise ValueError("Latitude must be between -90 and 90 degrees.")
        if self.longitude is not None and not (-180 <= self.longitude <= 180):
            raise ValueError("Longitude must be between -180 and 180 degrees.")


@dataclass
class Telescope(Base):
    __tablename__ = 'telescopes'

    id: int = Column(Integer, primary_key=True)  # type: ignore
    name: str = Column(String, unique=True, nullable=False)  # type: ignore
    type: TelescopeType = Column(Enum(TelescopeType), nullable=False)  # type: ignore
    aperture: float = Column(Float, nullable=False)  # in mm  # type: ignore
    focal_length: float = Column(Float, nullable=False)  # in mm  # type: ignore
    focal_ratio: float = Column(Float, nullable=False)  # f/number  # type: ignore

    observation_sites = relationship("ObservationSite", secondary=observation_site_telescope_association, back_populates="telescopes")
