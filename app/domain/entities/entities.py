from sqlalchemy import Column, Integer, String, Float, ForeignKey, Enum, Table
from sqlalchemy.orm import declarative_base, relationship

from domain.light_pollution import LightPollution

Base = declarative_base()

# Association table
observation_site_telescope_association = Table(
    'observation_site_telescope', Base.metadata,
    Column('observation_site_id', Integer, ForeignKey('observation_sites.id')),
    Column('telescope_id', Integer, ForeignKey('telescopes.id')))


class ObservationSite(Base):
    __tablename__ = 'observation_sites'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    light_pollution = Column(Enum(LightPollution))

    telescopes = relationship("Telescope", secondary=observation_site_telescope_association, back_populates="observation_sites")

    def __post_init__(self):
        self.validate_coordinates()

    def validate_coordinates(self):
        if self.latitude is not None and not (-90 <= self.latitude <= 90):
            raise ValueError("Latitude must be between -90 and 90 degrees.")
        if self.longitude is not None and not (-180 <= self.longitude <= 180):
            raise ValueError("Longitude must be between -180 and 180 degrees.")


class Telescope(Base):
    __tablename__ = 'telescopes'

    id = Column(Integer, primary_key=True)
    name = Column(String)

    observation_sites = relationship("ObservationSite", secondary=observation_site_telescope_association, back_populates="telescopes")
