"""Shared test fixtures.

DB strategy: tests run against the dockerized Postgres on the dedicated
`career_platform_mvp_test` database — pinned below *before any app import*
so this process can never touch a real database. Migrations are applied
once per session (exercising the Alembic chain on every test run), then
the 50 seed opportunities are upserted. `user_profiles` and
`shortlist_items` are truncated after each test; `opportunities` is
immutable reference data and persists.
"""

import os
from pathlib import Path

# Pin every connection in this process to the throwaway test database, and
# mark the environment as test (NullPool engine — see core/database.py).
# Must happen before the first `app.*` import (settings are cached).
os.environ["ENVIRONMENT"] = "test"
os.environ["POSTGRES_DB"] = "career_platform_mvp_test"

import psycopg2
import pytest
from alembic import command
from alembic.config import Config as AlembicConfig
from httpx import ASGITransport, AsyncClient

from app.core.config import settings
from app.main import app

PROJECT_ROOT = Path(__file__).resolve().parents[1]
TEST_DB_NAME = "career_platform_mvp_test"


def _admin_connect(dbname: str):
    """Sync psycopg2 connection — test tooling (migrations, cleanup) stays
    sync on purpose so no asyncio event-loop scoping is involved."""
    return psycopg2.connect(
        host=settings.POSTGRES_HOST,
        port=settings.POSTGRES_PORT,
        user=settings.POSTGRES_USER,
        password=settings.POSTGRES_PASSWORD,
        dbname=dbname,
    )


@pytest.fixture(scope="session", autouse=True)
def _prepare_database():
    """(Re)create the throwaway test database, apply migrations, seed the
    50 fictional opportunities."""
    conn = _admin_connect("postgres")
    conn.autocommit = True
    with conn.cursor() as cur:
        cur.execute(f"DROP DATABASE IF EXISTS {TEST_DB_NAME} WITH (FORCE)")
        cur.execute(f"CREATE DATABASE {TEST_DB_NAME}")
    conn.close()

    alembic_cfg = AlembicConfig(PROJECT_ROOT / "alembic.ini")
    alembic_cfg.set_main_option("script_location", str(PROJECT_ROOT / "alembic"))
    command.upgrade(alembic_cfg, "head")

    import asyncio

    from app.core.database import AsyncSessionLocal
    from app.services.seed_service import ensure_opportunities

    async def _seed() -> None:
        async with AsyncSessionLocal() as session:
            await ensure_opportunities(session)
            await session.commit()

    asyncio.run(_seed())
    yield


@pytest.fixture
async def client():
    """Async HTTP client bound to the app (ASGI transport, no network)."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture(autouse=True)
def _clean_tables():
    """Empty profile-owned tables after every test (identity sequences
    restart). Opportunities stay (static reference data)."""
    yield
    conn = _admin_connect(TEST_DB_NAME)
    conn.autocommit = True
    with conn.cursor() as cur:
        cur.execute("TRUNCATE TABLE shortlist_items, user_profiles RESTART IDENTITY CASCADE")
    conn.close()
