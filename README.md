# DevTrack AI

A personal developer-learning and competitive-programming platform. It learns from your
real Codeforces / LeetCode activity, builds an evolving **skill profile**, recommends what
to practice, plans your day, teaches with a **RAG-grounded AI tutor**, analyzes your code,
and lets you compare with a friend — all answering one question: **"What should I do today?"**

> **Design principle — no fake data.** Every number is either **Data** (your real history),
> **Inference** (an estimate derived from that data, always labelled), or **Recommendation**
> (a suggestion). The LLM *explains, teaches, and reviews*; it never invents your scores or
> picks your problems — deterministic engines do that.

The folder is named `adaptive-learning-os` for historical reasons; the product is **DevTrack AI**.

---

## What it does

| Area | Feature | How it works (real, not fake) |
|---|---|---|
| **Coding** | Codeforces + LeetCode integration | Codeforces public API; LeetCode community GraphQL + `submitStatsGlobal` counts, with manual-import fallback. Adapter abstraction (`PlatformAdapter`) so new platforms slot in. |
| **Profile** | Unified skill/weakness engine | Deterministic per-topic success rates, attempts, and bands (Strong / Developing / Needs-reinforcement / **Insufficient-data**). No single "IQ score". |
| **Recommend** | Problem of the Day + recommendations | Weighted candidate scoring (difficulty-fit / topic / novelty / spaced / recent / plan). LLM only phrases the *why*. |
| **Analyze** | Submission patterns + code analysis | Recurring-mistake detection; `/code/analyze` estimates time/space complexity from loop nesting + sorts + recursion, flags likely TLE / overflow / slow-IO, and answers "why is this slow?" grounded in docs **and your code**. |
| **Planner** | Daily planner | Recurring routines that auto-fill each day, paste/upload tasks, and per-task **missed-task carry-over** (move to today / dismiss). Streaks derived from real completions. |
| **Learn** | W3Schools-style curriculum | 8 paths (DSA, JavaScript, TypeScript, React, Backend, Python, SQL, Git), each topic with theory, example, exercise, and **official-docs** links. |
| **AI Tutor** | Progressive hints + **RAG** | 5-level hints (never instant solutions) + "Ask the Docs": retrieval over a curated corpus (chunk → embed → cosine → LLM) with **citations**. Keyless by default. |
| **Compare** | Friend comparison | Consent-based friendships; neutral comparison (your / shared / friend's strengths, growth areas) with a personalized report. **No overall winner.** |
| **Personalize** | Preferences | Daily hours, target ratings, practice focus, goals, and the comparison-consent flag. |

---

## Tech stack

| Layer | Choice |
|---|---|
| Frontend | React + TypeScript + Vite + Tailwind + TanStack Query + Framer Motion + Monaco + Recharts |
| Backend | Python + FastAPI + Pydantic + SQLAlchemy 2.0 + Alembic |
| Database | PostgreSQL (production) / SQLite (local dev & tests — zero setup) |
| AI | Provider-agnostic (`LLMProvider`): **Gemini** when keyed, deterministic **stub** fallback |
| RAG | TF-IDF retriever (keyless, deterministic) → Gemini embeddings optional; vectors stored as JSON (no pgvector needed) |

---

## Quick start (local, zero external services)

Everything runs **keyless** on SQLite — no Postgres, no API keys required.

### Backend → http://localhost:8020
```bash
cd backend
python3 -m venv .venv && ./.venv/bin/pip install -r requirements.txt
DATABASE_URL="sqlite:///./dev.db" ./.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8020
# API docs at http://localhost:8020/docs
```
> Port **8020** is used because 8000 is often taken. The RAG corpus auto-indexes on first start.

### Frontend → http://localhost:5173
```bash
cd frontend
npm install
echo "VITE_API_URL=http://localhost:8020" > .env   # point the UI at the backend
npm run dev
```

### Tests
```bash
cd backend && ./.venv/bin/python -m pytest -q     # 87 tests, offline, SQLite in-memory
cd frontend && npx tsc --noEmit                    # type-check
```

---

## Configuration (`backend/.env`)

Copy `backend/.env.example` → `backend/.env`. **Everything works with defaults / no keys.**
`.env` is gitignored — never commit real secrets.

| Variable | Default | What it's for | Manual step? |
|---|---|---|---|
| `DATABASE_URL` | Postgres on :5433 | DB connection. Use `sqlite:///./dev.db` for local dev. | Set for local (as above) |
| `SECRET_KEY` | dev insecure | JWT signing. **Change for any real deployment.** | ⚠️ change before deploying |
| `AI_PROVIDER` | `stub` | `stub` (keyless) or `gemini`. | Optional |
| `GEMINI_API_KEY` | *(empty)* | Enables LLM answers/tutoring/review + optional semantic embeddings. Get one free at Google AI Studio. | ⚠️ **you provide this** |
| `GEMINI_MODEL` | `gemini-3.6-flash` | Gemini model id. | Optional |
| `CODEFORCES_API_BASE` | official API | No key needed — Codeforces API is public. | No |

**To enable full AI** (LLM-synthesised tutoring, code review, and RAG answers with citations):
```bash
# backend/.env
AI_PROVIDER=gemini
GEMINI_API_KEY=<your key from https://aistudio.google.com/apikey>
```
Then optionally `POST /rag/reindex?prefer_gemini=true` to switch retrieval to semantic embeddings.
Without a key the app stays fully functional on the deterministic stub + TF-IDF retrieval.

### Connecting your accounts (in the app → Settings / Codeforces / LeetCode)
- **Codeforces:** enter your handle (e.g. from `codeforces.com/profile/<handle>`). Public API, no key.
- **LeetCode:** enter your username. If the community endpoint can't return data, use the manual import.

---

## Architecture

```
User activity (CF / LC)                    Learning
      │ adapters (public APIs)                  │ curriculum (authored + official docs)
      ▼                                         ▼
  Submissions / Problems DB              TopicCompletion
      │                                         │
      ▼                                         ▼
  Skill engine  ──►  Recommendation engine  ──► Daily planner  ──► you solve more ──► profile updates
 (deterministic)     (deterministic, weighted)   (routines + carry-over)

RAG (separate):  corpus → chunk → embed → store → retrieve → LLM (cites sources)
Compare (consent): metrics_for(you) + metrics_for(friend) → neutral buckets + report
```

- **Backend** `backend/app/`: `models/`, `schemas/`, `services/` (skill_engine, recommendation_engine,
  planner_service, code_analysis, comparison_service, `rag/`, `ai/`), `api/routers/`, `alembic/`.
- **Frontend** `frontend/src/`: `pages/`, `components/`, `lib/` (typed hooks per feature).
- **AI** is behind `LLMProvider` (`services/ai/`); **RAG** is behind `services/rag/`. The recommendation
  engine and the RAG engine are deliberately separate — the LLM never secretly decides recommendations.

---

## Key API endpoints
`/auth/*` · `/dashboard` · `/platforms/{codeforces,leetcode}/connect|sync` · `/codeforces/*` · `/leetcode/*`
· `/skills` · `/problems/today` · `/recommendations` · `/planner/{day,tasks,missed,routines}` · `/goals`
· `/learning/*` · `/code/{run,analyze}` · `/tutor/*` · `/rag/{ask,status,reindex}` · `/friends/*` · `/preferences`
· `/progress`

---

## Notes & honest limitations
- **LeetCode** exposes solved *counts* reliably but often an empty *recent-submissions* list, so the
  LeetCode Problem-of-the-Day can't always exclude problems you've already solved. This is stated, not hidden.
- **Complexity analysis** is a transparent static heuristic (labelled *Inference*), not a proof — braceless
  single-statement loops aren't counted.
- **Sandbox** runs user code in a subprocess with CPU/memory/time limits — never inside the API process.
- This is a **single-user** personal build: the frontend auto-signs into one local account, so there is no
  login screen. Multi-user auth is fully implemented in the backend if you want to re-enable it.
