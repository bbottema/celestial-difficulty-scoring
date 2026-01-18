import logging
from contextlib import contextmanager
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker

from app.orm.model.entities import Base
from app.config.event_bus_config import database_ready_bus


def get_project_root() -> Path:
    # This file lives at: <root>/src/app/config/database.py
    return Path(__file__).resolve().parents[3]


def get_database_path() -> Path:
    return get_project_root() / "data" / "celestial.db"


def get_database_url() -> str:
    # Use an absolute SQLite file path so the DB location is independent of CWD.
    db_path = get_database_path()
    return f"sqlite:///{db_path.as_posix()}"


_db_path = get_database_path()
_db_path.parent.mkdir(parents=True, exist_ok=True)

_engine = create_engine(get_database_url(), echo=False, future=True)
_session_local = sessionmaker(expire_on_commit=False, bind=_engine)
_logger = logging.getLogger(__name__)


def initialize_database():
    Base.metadata.create_all(bind=_engine)
    database_ready_bus.on_next('DATABASE_READY')
    _logger.info("Database initialized.")


@contextmanager
def session_scope():
    session = _session_local()
    try:
        yield session
        session.commit()
    except SQLAlchemyError as e:
        session.rollback()
        raise e
    finally:
        session.close()
