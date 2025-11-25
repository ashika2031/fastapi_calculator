from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session

from . import models, schemas
from .database import get_db, engine, Base
from .security import hash_password
# creating tables at import time may fail when DB is not available (tests, cold envs).
# guard to avoid hard import-time failures — tests will create/drop as needed.
try:
    Base.metadata.create_all(bind=engine)
except Exception:
    # best-effort only; the application will still run and tests that need the DB
    # should create the schema explicitly via fixtures.
    pass

app = FastAPI(title="FastAPI Calculator with Secure User Model")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/users/", response_model=schemas.UserRead, status_code=status.HTTP_201_CREATED)
def create_user(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(
        (models.User.username == user_in.username) |
        (models.User.email == user_in.email)
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered",
        )

    user = models.User(
        username=user_in.username,
        email=user_in.email,
        password_hash=hash_password(user_in.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
