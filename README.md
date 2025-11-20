# FastAPI Calculator – Secure User Model & CI/CD

A fully containerized **FastAPI Calculator Web Application** integrated with **PostgreSQL**, extended with a **secure user model, Pydantic validation, password hashing, database tests, and a CI/CD pipeline that builds and pushes a Docker image to Docker Hub**.

---

## Features

### Calculator API

- REST endpoints built with **FastAPI**:
  - `GET /add?a=&b=`
  - `GET /subtract?a=&b=`
  - `GET /multiply?a=&b=`
  - `GET /divide?a=&b=`
- Clear separation between **business logic** and **API layer**
- Containerized with **Docker** and orchestrated with **Docker Compose**
- Backed by a **PostgreSQL** database

> _Note: exact calculator endpoint implementation may live in a separate module (e.g. `operations.py`) depending on how you structured the earlier modules._

---

### Secure User Model & Validation (Module 10)

- **SQLAlchemy `User` model** (`app/models.py`)
  - `id` (primary key)
  - `username` – unique, indexed
  - `email` – unique, indexed
  - `password_hash` – hashed password
  - `created_at` – timestamp defaulting to current UTC time
- **Pydantic schemas** (`app/schemas.py`)
  - `UserCreate` – `username`, `email`, `password`
  - `UserRead` – `id`, `username`, `email`, `created_at` (no password exposed)
  - Email validation using `EmailStr`
- **Secure password hashing** (`app/security.py`)
  - Hashing with `passlib` + `bcrypt`
  - `hash_password(plain_password)`
  - `verify_password(plain_password, password_hash)`
- **User API endpoint** (`app/main.py`)
  - `POST /users/` – create user
  - Validates:
    - Unique `username`
    - Unique `email`
  - Stores only `password_hash` in the database
  - Returns `UserRead` schema (no raw password ever returned)

---

### Testing & CI/CD

- **Unit tests**
  - `tests/unit/test_security.py` – password hashing and verification
  - `tests/unit/test_schemas.py` – Pydantic validation (valid + invalid data)
- **Integration tests**
  - `tests/integration/test_users_integration.py` – `/users/` endpoint:
    - successful creation
    - duplicate username / email rejected
    - runs against a real PostgreSQL database
- **Database for tests**
  - Local: uses `DATABASE_URL` (defaults to Postgres via Docker Compose)
  - CI: GitHub Actions spins up a Postgres service and injects `DATABASE_URL`
- **GitHub Actions CI/CD** (`.github/workflows/ci.yml`)
  - Runs on every `push` and `pull_request`
  - Steps:
    - Check out repo
    - Set up Python 3.12
    - Install dependencies
    - Run unit + integration tests
    - **If tests pass on `main`**:
      - Build Docker image from `Dockerfile`
      - Tag image as `ashikap/fastapi-calculator:latest`
      - Push image to Docker Hub

---

## Architecture

| Service          | Description                                                          |
| ---------------- | -------------------------------------------------------------------- |
| **FastAPI App**  | Hosts calculator and user endpoints                                  |
| **PostgreSQL**   | Stores user data (and optionally calculation history)                |
| **Docker**       | Containerizes the application and database                           |
| **Docker Compose** | Orchestrates app and database containers                           |
| **GitHub Actions** | Runs tests, builds Docker image, and pushes to Docker Hub on pass |

---

## Project Structure

```
fastapi_calculator/
│
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI app, routes, startup
│   ├── database.py      # SQLAlchemy engine, SessionLocal, Base
│   ├── models.py        # SQLAlchemy models (User)
│   ├── schemas.py       # Pydantic models (UserCreate, UserRead)
│   └── security.py      # Password hashing / verification
│
├── tests/
│   ├── unit/
│   │   ├── test_schemas.py
│   │   └── test_security.py
│   └── integration/
│       └── test_users_integration.py
│
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── pytest.ini
├── reflection.md
├── .github/
│   └── workflows/
│       └── ci.yml       # GitHub Actions CI/CD pipeline
└── README.md
```

Local Development Setup (without Docker)

Requires Python 3.9+.

Create and activate virtual environment
```
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

```
Install dependencies
```
pip install --upgrade pip
pip install -r requirements.txt
```

Set database URL (optional, if not using Docker)

export DATABASE_URL=postgresql://postgres:postgres@localhost:5432/postgres
# PowerShell:
# $env:DATABASE_URL="postgresql://postgres:postgres@localhost:5432/postgres"


Run the FastAPI app
```
uvicorn app.main:app --reload

```
Then open:
```
Swagger UI: http://localhost:8000/docs

Health check: http://localhost:8000/health
```
Running with Docker Compose

To run the FastAPI app and PostgreSQL together using Docker Compose:
```
docker-compose up --build
```

This will:

Start a db container (PostgreSQL 16)

Build and start a web container (FastAPI app)

Expected FastAPI logs:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```
Service URLs
Service	URL	Notes
FastAPI App	http://localhost:8000/docs
	Interactive Swagger UI
FastAPI Health	http://localhost:8000/health
	Simple health check endpoint
PostgreSQL	Host: db, Port: 5432	User: postgres, Password: postgres
How to Run Tests Locally

From the project root (with virtualenv activated and Postgres running via docker-compose up -d db):

Run all tests
```
pytest
```
Run tests with coverage:

pytest --cov=app --cov-report=term-missing

output:
```
============================================== tests coverage ==============================================
_____________________________ coverage: platform darwin, python 3.12.4-final-0 _____________________________

Name              Stmts   Miss  Cover   Missing
-----------------------------------------------
app/__init__.py       1      0   100%
app/database.py      12      0   100%   
app/main.py          20      0   100%   
app/models.py        11      0   100%
app/schemas.py       12      0   100%
app/security.py       6      0   100%
-----------------------------------------------
TOTAL                62      0    100%
```
This will show which lines in the app/ package are covered or missing from tests.

CI/CD Pipeline (GitHub Actions → Docker Hub)

Workflow file: .github/workflows/ci.yml

Triggers: push and pull_request

Pipeline Steps

Test job

Spin up PostgreSQL as a service container

Set DATABASE_URL

Install dependencies from requirements.txt

Run pytest

Docker job (only on main and if tests pass)

Log in to Docker Hub using:

DOCKERHUB_USERNAME

DOCKERHUB_TOKEN (personal access token)

Build Docker image from Dockerfile

Tag image:

ashikap/fastapi-calculator:latest

Push image to Docker Hub

Docker Hub Repository

Name: ashikap/fastapi-calculator

URL: https://hub.docker.com/r/ashikap/fastapi-calculator

You can pull and run the image directly:

docker pull ashikap/fastapi-calculator:latest

docker run \
  -e DATABASE_URL=postgresql://postgres:postgres@host.docker.internal:5432/postgres \
  -p 8000:8000 \
  ashikap/fastapi-calculator:latest


The API will be available at:

http://localhost:8000

Swagger docs at http://localhost:8000/docs
