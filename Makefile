.PHONY: dev dev-api dev-web migrate seed test-backend test-frontend lint setup

setup:
	cd backend && python3 -m venv .venv && . .venv/bin/activate && pip install -e ".[dev]"
	cd cli && ../backend/.venv/bin/pip install -e .
	cd frontend && npm install

dev-api:
	cd backend && . .venv/bin/activate && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev-web:
	cd frontend && npm run dev

dev:
	@echo "Run 'make dev-api' and 'make dev-web' in separate terminals"

migrate:
	cd backend && . .venv/bin/activate && alembic upgrade head

seed:
	cd backend && . .venv/bin/activate && python -m app.seed

test-backend:
	cd backend && . .venv/bin/activate && pytest -v

test-frontend:
	cd frontend && npm run build

lint:
	cd backend && . .venv/bin/activate && ruff check app tests
