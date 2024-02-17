from contextlib import contextmanager

from sqlalchemy.exc import SQLAlchemyError

from db.database import session_local


@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    session = session_local()  # Assume session_local is defined elsewhere to provide a Session
    try:
        yield session
        session.commit()
    except SQLAlchemyError as e:
        session.rollback()
        # rais error with text "A database error occurred."
        raise Exception("A database error occurred.")
    finally:
        session.close()
