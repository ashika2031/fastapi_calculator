from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session

from . import models, schemas
from .database import get_db, engine, Base
from .security import hash_password
from .security import verify_password
from .calc import compute
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


@app.post("/users/register", response_model=schemas.UserRead, status_code=status.HTTP_201_CREATED)
def register_user(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    """Compatibility endpoint for registration."""
    return create_user(user_in, db)


# Backwards-compatible aliases: some environments/tests may call these alternate paths.
@app.post("/register", response_model=schemas.UserRead, status_code=status.HTTP_201_CREATED)
def register_user_alias(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    return create_user(user_in, db)


@app.post("/users/signup", response_model=schemas.UserRead, status_code=status.HTTP_201_CREATED)
def register_user_signup(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    return create_user(user_in, db)


@app.post("/users/login")
def login_user(payload: dict, db: Session = Depends(get_db)):
    """Simple login endpoint. Expects {"username":..., "password":...}.
    Returns basic user info on success.
    """
    username = payload.get("username")
    password = payload.get("password")
    if not username or not password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="username and password required")

    user = db.query(models.User).filter(models.User.username == username).first()
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid credentials")

    return {"id": user.id, "username": user.username}


# Calculation endpoints (BREAD)
@app.post("/calculations", response_model=schemas.CalculationRead, status_code=status.HTTP_201_CREATED)
def add_calculation(calc_in: schemas.CalculationCreate, db: Session = Depends(get_db)):
    # compute result using factory and store
    res = compute(calc_in.type, calc_in.a, calc_in.b)
    calc = models.Calculation(a=calc_in.a, b=calc_in.b, type=calc_in.type.value, result=res, user_id=calc_in.user_id)
    db.add(calc)
    db.commit()
    db.refresh(calc)
    return calc


@app.get("/calculations", response_model=list[schemas.CalculationRead])
def browse_calculations(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items = db.query(models.Calculation).offset(skip).limit(limit).all()
    return items


@app.get("/calculations/{calc_id}", response_model=schemas.CalculationRead)
def read_calculation(calc_id: int, db: Session = Depends(get_db)):
    calc = db.query(models.Calculation).filter(models.Calculation.id == calc_id).first()
    if not calc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="calculation not found")
    return calc


@app.put("/calculations/{calc_id}", response_model=schemas.CalculationRead)
def update_calculation(calc_id: int, calc_in: schemas.CalculationCreate, db: Session = Depends(get_db)):
    calc = db.query(models.Calculation).filter(models.Calculation.id == calc_id).first()
    if not calc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="calculation not found")
    # recompute
    res = compute(calc_in.type, calc_in.a, calc_in.b)
    calc.a = calc_in.a
    calc.b = calc_in.b
    calc.type = calc_in.type.value
    calc.result = res
    calc.user_id = calc_in.user_id
    db.add(calc)
    db.commit()
    db.refresh(calc)
    return calc


@app.delete("/calculations/{calc_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_calculation(calc_id: int, db: Session = Depends(get_db)):
    calc = db.query(models.Calculation).filter(models.Calculation.id == calc_id).first()
    if not calc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="calculation not found")
    db.delete(calc)
    db.commit()
    return {}
