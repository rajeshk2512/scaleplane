.PHONY: dev dev-api dev-web migrate seed test-backend test-frontend lint setup sdk-export sdk-generate sdk-test

setup:
	cd backend && python3 -m venv .venv && . .venv/bin/activate && pip install -e ".[dev]"
	cd cli && ../backend/.venv/bin/pip install -e .
	cd frontend && npm install
	cd sdks/python && ../../backend/.venv/bin/pip install -e ".[dev]"
	cd sdks/typescript && npm install

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

sdk-export:
	cd backend && . .venv/bin/activate && python ../sdks/codegen/export_openapi.py

sdk-generate:
	SCALEPLANE_PYTHON=$$(pwd)/backend/.venv/bin/python ./sdks/codegen/generate.sh

sdk-test:
	cd sdks/python && ../../backend/.venv/bin/python -m pytest -v
	cd sdks/typescript && npm test
	@if command -v mvn >/dev/null 2>&1; then \
	  if [ -d /opt/homebrew/opt/openjdk@21/libexec/openjdk.jdk/Contents/Home ]; then \
	    export JAVA_HOME=/opt/homebrew/opt/openjdk@21/libexec/openjdk.jdk/Contents/Home; \
	    export PATH="$$JAVA_HOME/bin:$$PATH"; \
	  fi; \
	  cd sdks/java && mvn -q test; \
	else echo "Skipping Java tests (mvn not found)"; fi
