.PHONY: db-up db-down dev migrate revision test lint fmt

# --- Database (dockerized PostgreSQL on host port 5435) ---
db-up:
	docker compose up -d

db-down:
	docker compose down

# --- Development server (auto-reload) ---
dev:
	uv run uvicorn app.main:app --reload --port 8000

# --- Migrations ---
migrate:
	uv run alembic upgrade head

# Usage: make revision m="add phone column"
revision:
	uv run alembic revision --autogenerate -m "$(m)"

# --- Quality gates ---
test:
	uv run pytest

lint:
	uv run ruff check .

fmt:
	uv run ruff format .
