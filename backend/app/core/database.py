"""Async SQLAlchemy engine, session factory, and declarative base."""

from collections.abc import AsyncGenerator

from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import NullPool

from app.core.config import settings

#: Deterministic constraint names so Alembic can diff/add/drop them safely.
NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    """Declarative base shared by every ORM model.

    Model modules must import `Base` from here and register their models in
    `app.models.__init__` so Alembic autogenerate can see them.
    """

    metadata = MetaData(naming_convention=NAMING_CONVENTION)


def _create_engine() -> AsyncEngine:
    if settings.is_testing:
        # Tests run each test in its own event loop and pooled asyncpg
        # connections are loop-bound — they explode when reused across
        # loops. NullPool (fresh connection per checkout, closed on
        # release) is safe everywhere at test scale.
        return create_async_engine(
            settings.async_database_url,
            echo=False,  # set True temporarily to inspect SQL during debugging
            poolclass=NullPool,
        )
    return create_async_engine(
        settings.async_database_url,
        echo=False,  # set True temporarily to inspect SQL during debugging
        pool_pre_ping=True,
        pool_size=settings.DB_POOL_SIZE,
        max_overflow=settings.DB_MAX_OVERFLOW,
    )


engine: AsyncEngine = _create_engine()

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession]:
    """FastAPI dependency yielding a database session.

    Commits on success, rolls back on any exception. Services receive the
    session; they must not open their own engine connections for request
    work. Services flush (never commit) so constraint violations surface
    inside the request where they can be mapped to clean error envelopes.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
