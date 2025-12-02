from fastapi.testclient import TestClient
from app.main import app
from app.database import get_db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test_integration.db")
# Only pass sqlite-specific connect_args when using sqlite, otherwise create a normal engine.
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


def test_create_user_duplicate():
    payload = {"username": "dupuser", "email": "dup@example.com", "password": "pass123"}
    r1 = client.post("/users/register", json=payload)
    assert r1.status_code == 201
    r2 = client.post("/users/register", json=payload)
    assert r2.status_code == 400


def test_login_missing_fields():
    r = client.post("/users/login", json={})
    assert r.status_code == 400


def test_calc_not_found_and_update_delete_not_found():
    r = client.get("/calculations/99999")
    assert r.status_code == 404
    r2 = client.put("/calculations/99999", json={"a":1,"b":2,"type":"Add"})
    assert r2.status_code == 404
    r3 = client.delete("/calculations/99999")
    assert r3.status_code == 404
