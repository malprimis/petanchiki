import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base


@pytest.fixture(scope="session")
def engine():
    """Session-wide test database engine (SQLite in-memory)."""
    return create_engine("sqlite:///:memory:", future=True)


@pytest.fixture(scope="session", autouse=True)
def create_tables(engine):
    """Create all tables before tests and drop after."""
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)


@pytest.fixture(scope="function")
def db_session(engine):
    """Creates a new database session for a test, rolls back at teardown."""
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
    session = SessionLocal()
    session.echo = True
    try:
        yield session
    finally:
        session.rollback()
        session.close()


# from fastapi.testclient import TestClient
# from ..app.main import app
# from ..app.db.session import get_db
#
#
# @pytest.fixture(scope="function")
# def client(db_session):
#     """FastAPI TestClient with overridden DB dependency."""
#     app.dependency_overrides[get_db] = lambda: db_session
#     client = TestClient(app)
#     yield client
#     app.dependency_overrides.clear()
