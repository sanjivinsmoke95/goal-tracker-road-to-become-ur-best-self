.PHONY: help up down logs be-install be-dev be-test fe-install fe-dev fe-build migrate

help:
	@echo "up          Start the full stack (db + backend + frontend) via docker-compose"
	@echo "down        Stop the stack"
	@echo "be-install  Create backend venv and install deps"
	@echo "be-dev      Run backend locally (needs a Postgres on DATABASE_URL)"
	@echo "be-test     Run backend tests (uses a throwaway SQLite db, no Postgres needed)"
	@echo "fe-install  Install frontend deps"
	@echo "fe-dev      Run frontend dev server"
	@echo "fe-build    Type-check + production build of the frontend"

up:
	docker compose up --build

down:
	docker compose down

be-install:
	cd backend && python3 -m venv .venv && ./.venv/bin/pip install -U pip && ./.venv/bin/pip install -r requirements.txt

be-dev:
	cd backend && ./.venv/bin/uvicorn app.main:app --reload --port 8000

be-test:
	cd backend && ./.venv/bin/pytest -q

migrate:
	cd backend && ./.venv/bin/alembic upgrade head

fe-install:
	cd frontend && npm install

fe-dev:
	cd frontend && npm run dev

fe-build:
	cd frontend && npm run build
