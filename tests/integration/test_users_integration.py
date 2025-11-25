import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import get_db
from app.models import Base

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@db:5432/postgres")

# try to create the engine for the requested DATABASE_URL; if the host is not
# resolvable in the current environment (common when running locally without
# a postgres service), fall back to an in-memory SQLite DB so tests can run.
def _create_engine_fallback(url: str):
    try:
        e = create_engine(url)
        # try a quick connect to validate
        conn = e.connect()
        conn.close()
        return e
    except Exception:
        # fall back to a local file-backed sqlite DB so the test client and
        # the test runner can share the same DB across threads/connections
        return create_engine("sqlite:///./test_integration.db", connect_args={"check_same_thread": False})

engine = _create_engine_fallback(DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session", autouse=True)
def create_test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

def test_create_user_and_uniqueness():
    payload = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "password123"
    }
    r1 = client.post("/users/", json=payload)
    assert r1.status_code == 201
    data1 = r1.json()
    assert data1["username"] == "testuser"
    assert "id" in data1

    r2 = client.post("/users/", json=payload)
    assert r2.status_code == 400
