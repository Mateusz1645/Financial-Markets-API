import pytest
import sys
import os
from fastapi.testclient import TestClient

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "app")))

os.environ["DATABASE_URL"] = "sqlite:///./test.db"

from main import app
from db import Base, engine, SessionLocal
from services.inflation_service import load_inflation_from_custom_csv
from services.market_data_services import import_all_forex_once, import_all_equities_once


@pytest.fixture(scope="session", autouse=True)
def create_test_db():
    """
    Create all database tables once per test session.
    Drops all tables after the session ends.
    """
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """
    Provide a database session for a single test.
    Each test gets a fresh session and the session is closed after the test.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        db.rollback()


@pytest.fixture(scope="function", autouse=True)
def populate_db(db_session):
    """
    Populate the database with initial test data before each test.
    This fixture runs automatically for every test function.
    """
    load_inflation_from_custom_csv(db_session, "app/data/inflation.csv")
    import_all_forex_once(db_session)
    import_all_equities_once(db_session)
    db_session.commit()
    yield
    for table in reversed(Base.metadata.sorted_tables):
        db_session.execute(table.delete())
    db_session.commit()


@pytest.fixture()
def client():
    """
    Create a FastAPI TestClient for API testing.
    """
    return TestClient(app)

