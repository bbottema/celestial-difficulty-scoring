import logging
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker

from orm.entities import Base
from utils.event_bus_config import database_ready_bus

_engine = create_engine("sqlite:///celestial.db", echo=False, future=True)
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
        # rais error with text "A database error occurred."
        raise Exception("A database error occurred.")
    finally:
        session.close()
