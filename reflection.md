# Module 10 Reflection

In this module, I learned how to design a secure user model in FastAPI using SQLAlchemy and Pydantic. Implementing password hashing with `passlib` helped me understand why raw passwords should never be stored in the database. Email validation with `EmailStr` in Pydantic made it clear how much validation can be pushed to the schema layer instead of scattering checks across the codebase.

One of the biggest hurdles was configuring tests to run against a real Postgres instance in GitHub Actions. I had to debug environment variables, service health checks, and connection URLs before the integration tests would pass reliably. Another challenge was getting Docker Hub authentication working inside the CI pipeline; creating a Docker Hub access token and wiring it up as GitHub secrets solved this issue.

Overall, this module connected several concepts from previous weeks—Docker, databases, and testing—into a single CI/CD workflow. Now I have a repeatable pipeline where every push runs tests and publishes a container image automatically, which is a key skill I can reuse for future projects and my final course project.
