# Adaptive Learning OS

A **personal** adaptive learning + competitive-programming platform for one programmer.
It learns from your real Codeforces / LeetCode activity and coding history, builds an
evolving skill profile, and answers one question every day: **"What should I do today?"**

> **Design principle — no fake data.** Every number is either *Data* (what your real
> history shows), *Inference* (an estimate derived from that data, always labelled), or
> *Recommendation* (a suggestion). Estimates are never presented as measurements.

## Tech stack

| Layer | Choice |
|---|---|
| Frontend | React + TypeScript + Vite + Tailwind + TanStack Query + Framer Motion + Monaco |
| Backend | Python + FastAPI + Pydantic + SQLAlchemy |
| Database | PostgreSQL 16 (+ pgvector, used only when embeddings are needed) |
| AI | Provider-agnostic layer (default **Gemini**; OpenAI-compatible + **stub** fallback) |
| Infra | Docker + docker-compose, Alembic migrations, `.env` config |

## Quick start

### Option A — Docker (full stack)
```bash
cp .env.example .env          # then edit SECRET_KEY etc.
make up                       # db + backend (:8000) + frontend (:5173)
```

### Option B — Run locally
```bash
# Backend
make be-install               # creates backend/.venv, installs deps
make be-test                  # runs the test suite (SQLite, no Postgres needed)
# start Postgres (or `docker compose up db`) then:
make migrate                  # apply Alembic migrations
make be-dev                   # http://localhost:8000  (docs at /docs)

# Frontend
make fe-install
make fe-dev                   # http://localhost:5173
```

## Milestone status

| # | Milestone | State |
|---|---|---|
| **1** | **Project setup + auth + dashboard shell** | ✅ **done & tested** |
| 2 | Daily goal tracker + streak + animations | ▢ next |
| 3 | Codeforces integration (API, profile, submissions, problem DB, sync) | ▢ |
| 4 | Skill engine (topic analysis, difficulty estimation, confidence) | ▢ |
| 5 | Problem of the Day (deterministic candidate scoring + AI explanation) | ▢ |
| 6 | Submission AI analysis + historical mistake tracking | ▢ |
| 7 | Adaptive recommendation engine | ▢ |
| 8 | Learning system (frontend/backend curriculum, theory, docs, exercises) | ▢ |
| 9 | Code playground (isolated sandbox) | ▢ |
| 10 | Schedule upload (CSV/Excel/JSON/PDF) | ▢ |
| 11 | Adaptive learning plans | ▢ |
| 12 | LeetCode integration (adapter) | ▢ |

## What Milestone 1 delivered
- Dockerised monorepo (`backend/`, `frontend/`, `docker-compose.yml`).
- FastAPI backend: config, logging, SQLAlchemy + Alembic, JWT auth (register / login / me),
  and a `/dashboard` endpoint that returns an **honest empty shell** (no invented stats).
- React frontend: dark/light theme, protected routing, sidebar for every planned section,
  auth screens, a real dashboard wired to the API, and useful "coming in Milestone N" empty states.
- **Tests that actually run:** 10 backend tests pass; the frontend type-checks and builds.

See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for the full design, DB schema, and the
honest external-API constraints (e.g. the Codeforces API does **not** return submission source).
