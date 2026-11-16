# career_platform_mvp

**PathPilot — International Career Mobility Platform (MVP)**

PathPilot helps people plan international career moves. A user describes their
education, work experience, skills, languages and location preferences in a
**career profile**; the platform then compares that profile against a seeded
catalog of **50 international opportunities**, returns a ranked list of
**recommendations** where every point of every match is explained, flags hard
constraints that make a role **ineligible** or **needs verification** (instead of
guessing), and lets the user keep a **shortlist** of the roles they like.

This monorepo contains the two projects that make up the MVP:

| Project    | Path         | What it is                                                                    |
| ---------- | ------------ | ----------------------------------------------------------------------------- |
| Backend    | [`backend/`](backend/README.md)  | FastAPI + PostgreSQL REST API: profiles, opportunities, two-stage recommendation engine (FAISS retrieval → weighted scoring → eligibility), shortlist |
| Frontend   | [`frontend/`](frontend/README.md) | TanStack Start (React 19) SSR web app: profile forms, ranked matches, opportunity explorer, shortlist |

Each project has its own README with full details:

- ➡️ [backend/README.md](backend/README.md) — API reference, run instructions, architecture
- ➡️ [frontend/README.md](frontend/README.md) — pages, generated API client, run instructions

## How the two projects work together

```
┌─ frontend/ (TanStack Start, port 3000) ─────────────────────────┐
│                                                                 │
│  UI pages: profile form · recommendations · opportunities ·     │
│            shortlist                                            │
│       │                                                         │
│       ▼                                                         │
│  src/gen/ — Kubb-generated typed client                         │
│  (axios + TanStack Query + zod)                                 │
│                                                                 │
└───────────────┬─────────────────────────────────────────────────┘
                │  HTTP JSON (ApiResponse envelope)   ▲
                │                                     ┆
                │                                     ┆ OpenAPI spec
                │                                     ┆ → kubb generate
                ▼                                     ┆ → regenerates src/gen/
┌─ backend/ (FastAPI, port 8000) ─────────────────────────────────┐
│                                                                 │
│  /api/v1 REST endpoints                                         │
│       │                                                         │
│       ▼                                                         │
│  recommendation pipeline                                        │
│    1. FAISS cosine retrieval (top-K)                            │
│    2. six-part weighted score                                   │
│    3. evidence-based eligibility                                │
│       │                                                         │
│       ▼                                                         │
│  PostgreSQL 17 — profiles · opportunities · shortlist           │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

The frontend never hand-writes API calls: the backend's live OpenAPI document is
fed to [Kubb](https://kubb.dev/), which generates a fully typed client
(axios functions, TanStack Query hooks, zod schemas, TS types) into
`frontend/src/gen/`.

## Tech stack at a glance

| Layer     | Backend                                            | Frontend                                              |
| --------- | -------------------------------------------------- | ----------------------------------------------------- |
| Language  | Python 3.13 (uv)                                   | TypeScript                                            |
| Framework | FastAPI, SQLAlchemy 2 (async), Alembic             | TanStack Start (Router/Query/Form), React 19, Vite    |
| Data      | PostgreSQL 17 (Docker), FAISS, NumPy               | —                                                     |
| Styling   | —                                                  | Tailwind CSS v4, shadcn/ui, Radix UI                  |
| Validation| Pydantic v2 (requests, responses, env)             | zod v4 (generated schemas)                            |
| Quality   | pytest, pytest-asyncio, ruff                       | ESLint, Prettier                                      |

## Running the full stack (in order)

Prerequisites: [Docker](https://docs.docker.com/), [uv](https://docs.astral.sh/uv/),
Node.js 20+ with npm.

```bash
# 1. Backend: start PostgreSQL (host port 5435) and install deps
cd backend
docker compose up -d            # Postgres 17
uv sync                         # creates .venv from uv.lock

# 2. Backend: configure, migrate, run
cp .env.example .env
uv run alembic upgrade head     # apply migrations
uv run uvicorn app.main:app --reload --port 8000
                                # → http://127.0.0.1:8000 (auto-reload)
                                # → seeds 50 opportunities on startup

# 3. Frontend: install and run (new terminal)
cd ../frontend
npm install
npm run dev         # http://localhost:3000

# 4. (only if the backend API changed) regenerate the typed client
npm run gen:api     # requires the backend running on :8000
```

Detailed instructions and troubleshooting: see the sub-project READMEs.

## Repository layout

```
career_platform_mvp/
├── backend/          # FastAPI REST API + recommendation engine
│   ├── app/          # main.py, api/v1, core, models, schemas, services, seed_data
│   ├── alembic/      # DB migrations
│   ├── tests/        # pytest (unit + API tests, throwaway test DB)
│   └── docker-compose.yml
└── frontend/         # TanStack Start web app
    ├── src/routes/   # file-based routes (home, profiles, opportunities, …)
    ├── src/gen/      # Kubb-generated API client (do not edit)
    ├── src/components/, src/lib/, src/hooks/
    └── kubb.config.ts
```
