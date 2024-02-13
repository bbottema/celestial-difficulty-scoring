from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from domain.entities.entities import Base
from utils.event_bus_config import database_ready_bus

DATABASE_URL = "sqlite:///celestial.db"
engine = create_engine(DATABASE_URL, echo=True, future=True)
session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def initialize_database():
    Base.metadata.create_all(bind=engine)
    database_ready_bus.on_next('DATABASE_READY')
    print("Database initialized.")
