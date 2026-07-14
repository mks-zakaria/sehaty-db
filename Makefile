.PHONY: install lint format test revision upgrade downgrade check current up down

install:
	uv sync --all-extras

lint:
	uv run ruff check .
	uv run ruff format --check .

format:
	uv run ruff format .

test:
	uv run pytest -q

# --- Alembic (source .env or export DATABASE_URL first) ---
revision:
	uv run alembic -c src/sehaty/db/_migrations/alembic.ini revision --autogenerate -m "$(m)"

upgrade:
	uv run alembic -c src/sehaty/db/_migrations/alembic.ini upgrade head

downgrade:
	uv run alembic -c src/sehaty/db/_migrations/alembic.ini downgrade -1

check:
	uv run alembic -c src/sehaty/db/_migrations/alembic.ini check

current:
	uv run alembic -c src/sehaty/db/_migrations/alembic.ini current --verbose

# --- Local dev PostGIS ---
up:
	docker compose up -d

down:
	docker compose down
