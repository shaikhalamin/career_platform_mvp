# Technical Note — PathPilot (career_platform_mvp)

Brief technical overview of the PathPilot MVP: an international career mobility
platform. A user describes their education, experience, skills, languages and
location preferences in a **career profile**; the platform compares it against a
seeded catalog of **50 international opportunities** and returns ranked,
fully explained recommendations plus a **shortlist** of saved roles.

Full details live in [README.md](README.md), [backend/README.md](backend/README.md)
and [frontend/README.md](frontend/README.md).

## 1. System overview

Monorepo with two independently runnable projects:

| Project  | Path         | Role                                                            |
| -------- | ------------ | --------------------------------------------------------------- |
| Backend  | `backend/`   | FastAPI + PostgreSQL REST API, recommendation engine            |
| Frontend | `frontend/`  | TanStack Start (React 19) SSR web app                           |

```
frontend (port 3000) ──HTTP JSON──▶ backend /api/v1 (port 8000) ──▶ PostgreSQL 17 (host port 5435)
        ▲                                                                               │
        └──────────── OpenAPI spec → Kubb → typed client in frontend/src/gen ◀───────────┘
```

The contract between the two is the backend's live OpenAPI document. Kubb
generates a fully typed client (axios functions, TanStack Query hooks, zod
schemas, TS types) into `frontend/src/gen/` — API calls are never hand-written.
Regenerate after backend API changes with `npm run gen:api` (backend must be
running on :8000). `src/gen/` is generated code; do not edit.

## 2. Tech stack

| Layer      | Backend                                  | Frontend                                |
| ---------- | ---------------------------------------- | --------------------------------------- |
| Language   | Python 3.13 (uv, `uv.lock`)              | TypeScript 6                            |
| Framework  | FastAPI, SQLAlchemy 2 (async), Alembic   | TanStack Start, React 19, Vite 8        |
| Data       | PostgreSQL 17 (Docker), FAISS-cpu, NumPy | —                                       |
| Validation | Pydantic v2, pydantic-settings           | zod v4 (generated schemas)              |
| UI         | —                                        | Tailwind CSS v4, shadcn/ui, Radix, lucide |
| Quality    | pytest, pytest-asyncio, ruff             | ESLint 9, Prettier                      |

## 3. Backend architecture (`backend/app/`)

- `main.py` — app factory; CORS middleware, exception handlers, lifespan hook
  that seeds the 50 opportunities on startup (skipped under test). User profiles
  are never seeded — only API-created profiles exist.
- `api/v1/` — routers: `health`, `meta` (taxonomy), `profiles`, `opportunities`,
  `recommendations`, `shortlist`. All mounted under `/api/v1`; every response
  uses a shared `ApiResponse` envelope, and 422/500 use a standard error envelope.
- `core/` — `config.py` (central pydantic-settings; the only module reading env
  vars), `database.py` (async engine + sessions), `dependencies.py`,
  `exception_handlers.py`, `responses.py` (envelope helpers).
- `models/` — SQLAlchemy ORM: `UserProfile`, `Opportunity`, `ShortlistItem`.
- `schemas/` — Pydantic v2 request/response models (single source for OpenAPI).
- `services/` — business logic (see §4): `recommender`, `retrieval` (FAISS),
  `scoring`, `eligibility`, `normalization`, `vectors`, `taxonomy`,
  `seed_service`, plus CRUD services for profiles/opportunities/shortlist.
- `seed_data/` — the 50-opportunity seed catalog.
- `alembic/` — migrations (`uv run alembic upgrade head`).

### Recommendation pipeline (per request, no stale cache)

1. **Retrieval** — rule-generated feature vectors feed an in-memory FAISS
   cosine-similarity index that narrows opportunities to the top-K candidates.
   The index is cached and rebuilt only when the opportunity set changes.
2. **Scoring** — fixed six-part weighted score, 100 points total:

   | Dimension  | Points | Notes                                        |
   | ---------- | ------ | -------------------------------------------- |
   | skills     | 35     | 80% required + 20% optional coverage         |
   | experience | 20     | 14 yrs-alignment + 6 area overlap            |
   | education  | 15     | 10 level alignment + 5 field relevance       |
   | location   | 15     | preferred country 15 / same region 8         |
   | language   | 10     | mean ratio of user rank vs required rank     |
   | interests  | 5      | overlap with the role's career tracks        |

   Each dimension returns evidence (matched/missing items, notes), surfaced as
   per-dimension strengths and gaps.
3. **Eligibility** — independent, evidence-based evaluation of hard constraints
   with three outcomes: `eligible`, `needs_verification`, `ineligible`
   (constrained roles stay visible instead of being silently dropped).

Ranking: eligibility tier first, then total score, then cosine similarity, then
id (deterministic ties). Results are computed from live data on every request,
so profile updates are reflected immediately.

## 4. Frontend architecture (`frontend/src/`)

- `routes/` — file-based TanStack Router pages: home, `profiles/` (list, new,
  edit), `recommendations`, `opportunities/` (list + detail with match view),
  `shortlist`, `about`, `__root.tsx` (layout, query provider).
- `gen/` — Kubb-generated API client (do not edit; see §1).
- `components/` — app components (career profile form, match card, score gauge,
  shortlist button, skeletons…) and `ui/` shadcn primitives.
- `hooks/`, `lib/` — form logic, active-profile state, API error handling.
- SSR via TanStack Start; TanStack Query for server state, TanStack Form +
  zod for the profile form.

## 5. Configuration & environment (backend)

- Copy `backend/.env.example` → `backend/.env`; values are validated at startup
  (fail fast) by `app/core/config.py`.
- `ENVIRONMENT` = `development` | `test` | `production` (docs UI off in prod
  unless `DOCS_IN_PRODUCTION=true`; OpenAPI JSON always served).
- `DATABASE_URL` — full-DSN override for managed Postgres (e.g. Railway);
  empty = assemble from `POSTGRES_*` discrete parts (local Docker, host 5435).
- `CORS_ORIGINS` — explicit allowlist only (wildcards rejected at startup);
  defaults cover `localhost:3000` / `127.0.0.1:3000` (and :5173) — both hostname
  spellings matter, browsers treat them as different origins.

## 6. Running locally

Prerequisites: Docker, uv, Node.js 20+ with npm.

```bash
# 1) Backend
cd backend
docker compose up -d                # PostgreSQL 17 on host port 5435
uv sync                             # creates .venv from uv.lock
cp .env.example .env
uv run alembic upgrade head         # migrations
uv run uvicorn app.main:app --reload --port 8000   # seeds 50 opportunities

# 2) Frontend (new terminal)
cd frontend
npm install
npm run dev                         # http://localhost:3000

# 3) Only after backend API changes
npm run gen:api                     # regenerate typed client (backend on :8000)
```

## 7. Testing & quality

- Backend: `uv run pytest` — unit tests (scoring, eligibility, retrieval,
  normalization, taxonomy) + API tests against a throwaway test DB
  (tests seed their own fixtures; app lifespan seeding is skipped).
  Ruff (E/W/F/I/B/UP/SIM/RUF, line length 100); Alembic versions excluded.
- Frontend: `npm run lint` (ESLint), `npm run check` / `npm run format`
  (Prettier).

## 8. Key design decisions (quick reference)

- OpenAPI-first contract: backend schemas are the single source of truth;
  frontend consumes generated code only.
- Explainability over opacity: every score point carries evidence; hard
  constraints yield `needs_verification` / `ineligible` rather than guesses.
- Recommendations computed live per request — no cache invalidation logic.
- Centralized, validated configuration with startup-time safety checks
  (no wildcard CORS, DEBUG forbidden in production).
