# FastAPI Calculator – Module 10 Secure User Model

This project extends a FastAPI application with a secure `User` model, Pydantic validation,
password hashing, unit & integration tests, and a CI/CD pipeline that builds and pushes a
Docker image to Docker Hub.

## Running Locally

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# start Postgres
docker-compose up -d db

# set DATABASE_URL if you want to override default
export DATABASE_URL=postgresql://postgres:postgres@localhost:5432/postgres

# run tests
pytest --cov=app
```

## Docker

Build and run locally:

```bash
docker build -t your-username/fastapi-calculator:latest .
docker run -p 8000:8000 --env DATABASE_URL=postgresql://postgres:postgres@host.docker.internal:5432/postgres your-username/fastapi-calculator:latest
```

## Docker Hub

Update this section with your actual Docker Hub repository:

- https://hub.docker.com/r/your-username/fastapi-calculator
