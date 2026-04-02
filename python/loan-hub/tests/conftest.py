import os

# Set TEST_MODE before any imports
os.environ["TEST_MODE"] = "true"

import pytest
from database import Base, engine, get_db
from main import app
from fastapi.testclient import TestClient

@pytest.fixture(scope="session", autouse=True)
def setup_database():
    # Ensure tables are created in SQLite
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="session")
def client():
    with TestClient(app) as c:
        yield c
