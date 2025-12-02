import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import get_db
from app.models import Base
from app.models import CalcType

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@db:5432/postgres")

# reuse fallback helper pattern used in other integration tests
def _create_engine_fallback(url: str):
    try:
        e = create_engine(url)
        conn = e.connect()
        conn.close()
        return e
    except Exception:
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


def test_user_register_and_login():
    payload = {"username": "intuser", "email": "int@example.com", "password": "password123"}
    r = client.post("/users/register", json=payload)
    assert r.status_code == 201
    data = r.json()
    assert data["username"] == "intuser"
    assert "id" in data

    # login
    r2 = client.post("/users/login", json={"username": "intuser", "password": "password123"})
    assert r2.status_code == 200
    data2 = r2.json()
    assert data2["username"] == "intuser"

    # wrong credentials
    r3 = client.post("/users/login", json={"username": "intuser", "password": "wrong"})
    assert r3.status_code == 401


def test_calculation_crud():
    # create a calculation
    payload = {"a": 10, "b": 5, "type": "Divide"}
    r = client.post("/calculations", json=payload)
    assert r.status_code == 201
    data = r.json()
    calc_id = data["id"]
    assert data["result"] == 2

    # read
    r2 = client.get(f"/calculations/{calc_id}")
    assert r2.status_code == 200
    assert r2.json()["result"] == 2

    # list
    r3 = client.get("/calculations")
    assert r3.status_code == 200
    assert any(item["id"] == calc_id for item in r3.json())

    # update
    upd = {"a": 20, "b": 5, "type": "Divide"}
    r4 = client.put(f"/calculations/{calc_id}", json=upd)
    assert r4.status_code == 200
    assert r4.json()["result"] == 4

    # invalid update (divide by zero)
    bad = {"a": 1, "b": 0, "type": "Divide"}
    r5 = client.put(f"/calculations/{calc_id}", json=bad)
    assert r5.status_code == 422 or r5.status_code == 400

    # delete
    r6 = client.delete(f"/calculations/{calc_id}")
    assert r6.status_code == 204

    # confirm deletion
    r7 = client.get(f"/calculations/{calc_id}")
    assert r7.status_code == 404
