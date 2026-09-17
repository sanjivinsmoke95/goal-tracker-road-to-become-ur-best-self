# Architecture

## Services (docker-compose)
```
frontend  React/TS/Vite  :5173  ──HTTP──▶  backend  FastAPI  :8000  ──▶  db  Postgres 16  :5433
                                              │
                                              ├─ PlatformAdapter → CodeforcesAdapter / LeetCodeAdapter
                                              ├─ LLMProvider     → GeminiProvider / OpenAICompatible / Stub
                                              └─ SkillEngine     → deterministic Python (no LLM-invented scores)
sandbox   isolated code runner (later milestone) — user code never runs in the API process
redis     cache + jobs (optional, milestone-gated)
```

## Key abstractions
- **`PlatformAdapter`** normalises every platform into common `Problem` / `Submission` shapes.
  Everything above the adapter is platform-agnostic. `CodeforcesAdapter` (official public API),
  `LeetCodeAdapter` (unofficial GraphQL + manual-import fallback).
- **`LLMProvider`** — swappable AI backend chosen by `AI_PROVIDER`. Default `stub` (runs with no
  key), `gemini` (native `google-genai`), `openai_compatible` (OpenAI / OpenRouter / local Ollama /
  Gemini's OpenAI endpoint). AI is used for *explanations, code review, tutoring, plan generation* —
  never for computing skill scores.
- **`SkillEngine`** — deterministic, statistical, unit-testable. Estimates difficulty, topic scores,
  candidate ranking. Implements the **Data → Inference → Recommendation** contract.

## Recommendation scoring (Milestone 5+)
Deterministic candidate generation, then a weighted score (weights configurable):
```
candidate_score = 0.40·difficulty_fit + 0.20·topic_relevance + 0.15·novelty
                + 0.10·spaced_repetition + 0.10·recent_performance + 0.05·plan_alignment
                − already_solved_penalty − recently_seen_penalty − excessive_difficulty_penalty
```

## Database schema (planned, normalised)
Milestone 1 ships `users`. Subsequent milestones add:

- **Accounts:** `platform_accounts`, `codeforces_profiles`, `leetcode_profiles`
- **Corpus:** `problems`, `problem_tags`, `problem_tag_links`
- **Activity:** `submissions`, `submission_analysis`
- **Skill:** `user_skill_profile`, `topic_scores`, `skill_history`
- **Mistakes:** `mistakes`, `mistake_occurrences`
- **Learning:** `learning_paths`, `learning_modules`, `learning_resources`
- **Plans:** `uploaded_plans`, `learning_plans`, `plan_days`
- **Habits:** `goals`, `goal_completions`, `study_sessions`, `notes`
- **Recommendation:** `recommendations`, `daily_problems`

FKs to `users.id`; indexes on `(user_id, ts)`, `(platform, rating)`, `(user_id, problem_id)`.
Portable column types until a table genuinely needs JSONB / pgvector (then a Postgres-only test
fixture is added; the M1 suite runs on SQLite).

## External APIs — honest constraints
| Source | Key | Provides | Limitation |
|---|---|---|---|
| Codeforces API | none (public) | rating, contests, submissions, verdicts, tags, ratings, language, timestamps | **No submission source code** — that lives only on the web submission page. Source is optional (paste-in / opt-in scrape later). |
| LeetCode | none (unofficial graphql) | public profile stats, solved counts, recent AC titles/tags | Fragile; no code; behind the adapter + manual import. |
| LLM (Gemini default) | yes (or stub) | code review, explanations, tutoring, plan generation | Provider-agnostic; app runs without it. |
| Sandbox | none | isolated JS/TS/Python/C++ execution | Own Docker service, CPU/mem/time limits. |

## Credentials
- Only an **LLM API key** is optional-but-useful (`GEMINI_API_KEY`). Everything else runs keyless.
- Your **Codeforces handle** is entered in-app (not a secret). No CF/LC API keys exist or are needed.
