"""Alembic migration environment (sync psycopg2 engine, app settings driven).

The database URL comes from app settings (.env) — never hardcode it here.
Autogenerate detects models via `app.models` (which imports all model
modules) and `Base.metadata`. The application itself runs on asyncpg; only
migrations use the sync driver.
"""

from logging.config import fileConfig

from alembic import context
from sqlalchemy import create_engine, pool
from sqlalchemy.engine import Connection

import app.models  # noqa: F401  (aggregate model import; keep after Base import)
from app.core.config import settings
from app.core.database import Base

config = context.config

# Migrations run over the sync (psycopg2) URL from app settings.
config.set_main_option("sqlalchemy.url", settings.sync_database_url)

if config.config_file_name is not None:
    # Keep already-created loggers alive: the default (True) silently
    # disables every app.* logger when tests run migrations in-process.
    fileConfig(config.config_file_name, disable_existing_loggers=False)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode (emit SQL to stdout)."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations against a live database (settings-driven sync URL)."""
    connectable = create_engine(settings.sync_database_url, poolclass=pool.NullPool)

    with connectable.connect() as connection:
        do_run_migrations(connection)


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
