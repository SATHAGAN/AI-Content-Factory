import os

os.environ["SECRET_KEY"] = "test-secret-key-that-is-long-enough-123456"
os.environ["DATABASE_URL"] = "sqlite:///./test.db"
os.environ["STORAGE_BACKEND"] = "local"

import pytest
from fastapi.testclient import TestClient

from app.db.base import Base
from app.db.session import engine
from app.main import app


@pytest.fixture(autouse=True)
def clean_db():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def db_session():
    from app.db.session import SessionLocal
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
