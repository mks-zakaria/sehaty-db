# sehaty-db

Schema-of-record for the Sehaty platform: **SQLAlchemy 2.0 ORM models**,
canonical **Pydantic data-definitions**, and **packaged Alembic** migrations.
Imported by `sehaty-core`; never talks HTTP.

## Layout
```
src/sehaty/db/
  base.py            # SehatyBase (DeclarativeBase) + TimestampMixin
  users.py           # User, PatientProfile, DoctorProfile (+ PostGIS geopoint)
  specialties.py     # Specialty, DoctorSpecialty
  __init__.py        # re-exports every domain (autogenerate depends on this)
  _migrations/       # packaged Alembic: env.py, alembic.ini, cli.py, versions/
```

## Develop
```bash
uv sync --all-extras
uv run pytest              # metadata guardrail (no DB needed)
uv run ruff check .
```

## Migrations (needs PostGIS)
```bash
docker compose up -d                       # local PostGIS on :5432
cp env-example .env                        # sets DATABASE_URL
uv run alembic -c src/sehaty/db/_migrations/alembic.ini revision --autogenerate -m "feat: <slug>"
uv run alembic -c src/sehaty/db/_migrations/alembic.ini upgrade head
uv run alembic -c src/sehaty/db/_migrations/alembic.ini check   # must report no drift
```
Downstream services `pip install sehaty-db` and run the `sehaty-migrate`
console script to apply migrations without checking out this repo.

## Conventions
Conventional Commits (enforced via pre-commit); versioning + CHANGELOG via
`python-semantic-release` (`release.yml`). One PR = one issue.
