import pytest
import sys
import os
from fastapi.testclient import TestClient
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "app")))

os.environ["DATABASE_URL"] = "sqlite:///./test.db"

from main import app
from db import Base, engine, SessionLocal
from services.inflation_service import load_inflation_from_custom_csv
from services.market_data_services import import_all_equities_once, import_all_forex_once


@pytest.fixture(scope="session", autouse=True)
def create_test_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    load_inflation_from_custom_csv(db, "app/data/inflation.csv")
    # import_all_equities_once(db)
    import_all_forex_once(db)
    db.close()
    yield

@pytest.fixture()
def client():
    return TestClient(app)
