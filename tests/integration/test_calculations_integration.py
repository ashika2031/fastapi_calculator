import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import get_db
from app.models import Base, Calculation
from app.calc import compute
from app.models import CalcType

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@db:5432/postgres")

def _create_engine_fallback(url: str):
    try:
        e = create_engine(url)
        conn = e.connect()
        conn.close()
        return e
    except Exception:
        # fall back to a local file-backed sqlite DB so the test client and
        # the test runner can share the same DB across threads/connections
        return create_engine("sqlite:///./test_integration.db", connect_args={"check_same_thread": False})

engine = _create_engine_fallback(DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


def test_insert_calculation_and_store_result(tmp_path, monkeypatch):
    # create tables in the test database
    Base.metadata.create_all(bind=engine)

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)

    # create a calculation object and insert directly using the DB session
    db = next(override_get_db())
    a, b = 6.0, 7.0
    t = CalcType.Multiply
    res = compute(t, a, b)

    calc = Calculation(a=a, b=b, type=t.value, result=res)
    db.add(calc)
    db.commit()
    db.refresh(calc)

    assert calc.id is not None
    assert calc.result == 42.0

    # cleanup
    Base.metadata.drop_all(bind=engine)
