import logging
from dataclasses import dataclass
from typing import Any, cast, Protocol

from sqlalchemy import Column, Integer, String, Float, ForeignKey, Enum, Table
from sqlalchemy.orm import declarative_base, relationship, DeclarativeMeta

from app.domain.model.light_pollution import LightPollution
from app.domain.model.telescope_type import TelescopeType

logger = logging.getLogger(__name__)


class NamedEntity(Protocol):
    id: int | None
    name: str


class SQLAlchemyProtocolResolverMeta(type(NamedEntity), DeclarativeMeta):  # type: ignore
    pass


Base: Any = declarative_base(metaclass=SQLAlchemyProtocolResolverMeta)

# Association table
observation_site_telescope_association = Table('observation_site_telescope', Base.metadata,
                                               Column('observation_site_id', Integer, ForeignKey('observation_sites.id')),
                                               Column('telescope_id', Integer, ForeignKey('telescopes.id')))
observation_site_eyepiece_association = Table('observation_site_eyepiece', Base.metadata,
                                              Column('observation_site_id', Integer, ForeignKey('observation_sites.id')),
                                              Column('eyepiece_id', Integer, ForeignKey('eyepieces.id')))
observation_site_optical_aid_association = Table('observation_site_optical_aid', Base.metadata,
                                                 Column('observation_site_id', Integer, ForeignKey('observation_sites.id')),
                                                 Column('optical_aid_id', Integer, ForeignKey('optical_aids.id')))
observation_site_filter_association = Table('observation_site_filter', Base.metadata,
                                            Column('observation_site_id', Integer, ForeignKey('observation_sites.id')),
                                            Column('filter_id', Integer, ForeignKey('filters.id')))
observation_site_imager_association = Table('observation_site_imager', Base.metadata,
                                            Column('observation_site_id', Integer, ForeignKey('observation_sites.id')),
                                            Column('imager_id', Integer, ForeignKey('imagers.id')))


@dataclass
class ObservationSite(Base):
    __tablename__ = 'observation_sites'

    id: int | None = cast(int, Column(Integer, primary_key=True))
    name: str = cast(str, Column(String, unique=True, nullable=False))
    latitude: float | None = cast(float, Column(Float, nullable=True))
    longitude: float | None = cast(float, Column(Float, nullable=True))
    light_pollution: LightPollution = cast(LightPollution, Column(Enum(LightPollution), nullable=False))

    telescopes = relationship("Telescope", secondary=observation_site_telescope_association, back_populates="observation_sites")
    eyepieces = relationship("Eyepiece", secondary=observation_site_eyepiece_association, back_populates="observation_sites")
    optical_aids = relationship("OpticalAid", secondary=observation_site_optical_aid_association, back_populates="observation_sites")
    filters = relationship("Filter", secondary=observation_site_filter_association, back_populates="observation_sites")
    imagers = relationship("Imager", secondary=observation_site_imager_association, back_populates="observation_sites")

    def __post_init__(self):
        self.validate_coordinates()

    def validate_coordinates(self):
        if self.latitude is not None and not (-90 <= self.latitude <= 90):
            raise ValueError("Latitude must be between -90 and 90 degrees.")
        if self.longitude is not None and not (-180 <= self.longitude <= 180):
            raise ValueError("Longitude must be between -180 and 180 degrees.")


class EquipmentEntity(NamedEntity, Protocol):
    observation_sites: list[ObservationSite]

    def __contains__(self, other_site: ObservationSite):
        return any(own_site.name == other_site.name for own_site in self.observation_sites)


@dataclass
class Telescope(Base, EquipmentEntity):
    __tablename__ = 'telescopes'

    id: int | None = cast(int, Column(Integer, primary_key=True))
    name: str = cast(str, Column(String, unique=True, nullable=False))
    type: TelescopeType = cast(TelescopeType, Column(Enum(TelescopeType), nullable=False))
    aperture: int = cast(int, Column(Integer, nullable=False))  # in mm
    focal_length: int = cast(int, Column(Integer, nullable=False))  # in mm
    focal_ratio: float = cast(float, Column(Float, nullable=False))  # f/number

    observation_sites = cast(list[ObservationSite],
                             relationship("ObservationSite", secondary=observation_site_telescope_association, back_populates="telescopes"))


@dataclass
class Eyepiece(Base, EquipmentEntity):
    __tablename__ = 'eyepieces'

    id: int | None = cast(int, Column(Integer, primary_key=True))
    name: str = cast(str, Column(String, unique=True, nullable=False))

    observation_sites = cast(list[ObservationSite],
                             relationship("ObservationSite", secondary=observation_site_eyepiece_association, back_populates="eyepieces"))


@dataclass
class OpticalAid(Base, EquipmentEntity):
    __tablename__ = 'optical_aids'

    id: int | None = cast(int, Column(Integer, primary_key=True))
    name: str = cast(str, Column(String, unique=True, nullable=False))

    observation_sites = cast(list[ObservationSite],
                             relationship("ObservationSite", secondary=observation_site_optical_aid_association, back_populates="optical_aids"))


@dataclass
class Filter(Base, EquipmentEntity):
    __tablename__ = 'filters'

    id: int | None = cast(int, Column(Integer, primary_key=True))
    name: str = cast(str, Column(String, unique=True, nullable=False))

    observation_sites = cast(list[ObservationSite], relationship("ObservationSite", secondary=observation_site_filter_association, back_populates="filters"))


@dataclass
class Imager(Base, EquipmentEntity):
    __tablename__ = 'imagers'

    id: int | None = cast(int, Column(Integer, primary_key=True))
    name: str = cast(str, Column(String, unique=True, nullable=False))

    observation_sites = cast(list[ObservationSite], relationship("ObservationSite", secondary=observation_site_imager_association, back_populates="imagers"))
