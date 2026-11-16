"""Application configuration loaded from environment variables / .env file.

All settings are centralized here. Every module imports `settings` from this
module; nothing else may read environment variables directly.
"""

from functools import lru_cache
from pathlib import Path
from typing import Annotated

from pydantic import Field, ValidationInfo, field_validator, model_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict
from sqlalchemy.engine import make_url
from sqlalchemy.exc import ArgumentError

#: Project root (backend/) — anchors the .env lookup so the app behaves the
#: same regardless of the working directory it was started from.
BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    """Central application settings (validated with pydantic-settings)."""

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        env_ignore_empty=True,
        extra="ignore",
        case_sensitive=False,
    )

    # --- Application ---
    ENVIRONMENT: str = "development"  # development | test | production
    #: Serve /docs and /redoc even when ENVIRONMENT=production; keep them off
    #: by default in prod (attack-surface hygiene) and flip to `true` only
    #: for hands-on testing against a production deployment.
    DOCS_IN_PRODUCTION: bool = False
    DEBUG: bool = True
    PROJECT_NAME: str = "Career Platform MVP API"
    API_V1_PREFIX: str = "/api/v1"
    VERSION: str = "0.1.0"

    # --- PostgreSQL ---
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5435
    POSTGRES_USER: str = "career_user"
    POSTGRES_PASSWORD: str = "career_password"
    POSTGRES_DB: str = "career_platform_mvp"
    #: Full-DSN override for managed Postgres (Railway & co. hand out one
    #: URL): `postgres://user:password@host:port/db`, query params like
    #: ?sslmode=require preserved. Takes precedence over the discrete parts
    #: above. The driver scheme is rewritten per consumer (+asyncpg for the
    #: app, +psycopg2 for Alembic), so any pasted +driver suffix is fine.
    #: Empty = local dev (discrete parts).
    DATABASE_URL: str = ""
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20

    # --- CORS ---
    # NoDecode: accept a plain comma-separated string from .env (pydantic-
    # settings would otherwise try to JSON-parse complex types); split in
    # the validator.
    CORS_ORIGINS: Annotated[list[str], NoDecode] = Field(
        default_factory=lambda: ["http://localhost:3000", "http://localhost:5173"]
    )

    # ------------------------------------------------------------------
    # Derived values
    # ------------------------------------------------------------------
    @property
    def async_database_url(self) -> str:
        """Asyncpg URL used by the application engine."""
        return self._database_url("asyncpg")

    @property
    def sync_database_url(self) -> str:
        """Psycopg2 URL used by Alembic migrations and test tooling."""
        return self._database_url("psycopg2")

    def _database_url(self, driver: str) -> str:
        """Resolve the connection URL for `driver` (asyncpg | psycopg2).

        DATABASE_URL wins when set and is normalized to the requested
        driver — the postgres:// alias and any pasted +driver suffix are
        replaced, credentials and query params are preserved verbatim.
        Otherwise the URL is assembled from the discrete parts (local dev).
        """
        if not self.DATABASE_URL:
            return (
                f"postgresql+{driver}://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
                f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
            )
        return (
            make_url(self.DATABASE_URL)
            .set(drivername=f"postgresql+{driver}")
            .render_as_string(hide_password=False)
        )

    @property
    def is_testing(self) -> bool:
        return self.ENVIRONMENT == "test"

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"

    @property
    def api_docs_enabled(self) -> bool:
        """Interactive Swagger/ReDoc UI availability (OpenAPI JSON stays on)."""
        return not self.is_production or self.DOCS_IN_PRODUCTION

    # ------------------------------------------------------------------
    # Validators
    # ------------------------------------------------------------------
    @field_validator("ENVIRONMENT")
    @classmethod
    def _validate_environment(cls, v: str) -> str:
        allowed = {"development", "test", "production"}
        v = v.strip().lower()
        if v not in allowed:
            raise ValueError(f"ENVIRONMENT must be one of {allowed}, got {v!r}")
        return v

    @field_validator("POSTGRES_PORT", "DB_POOL_SIZE", "DB_MAX_OVERFLOW")
    @classmethod
    def _validate_positive_int(cls, v: int, info: ValidationInfo) -> int:
        if v < 1:
            raise ValueError(f"{info.field_name} must be >= 1, got {v!r}")
        return v

    @field_validator("DATABASE_URL")
    @classmethod
    def _validate_database_url(cls, v: str) -> str:
        # Fail fast on a copy-paste mistake (mysql://, https://…) or a
        # malformed URL — otherwise it only explodes inside create_engine,
        # far from the misconfigured environment.
        if not v:
            return v
        try:
            drivername = make_url(v).drivername
        except ArgumentError as exc:
            raise ValueError(f"DATABASE_URL is not a parseable URL: {v!r}") from exc
        if drivername.split("+", 1)[0] not in {"postgres", "postgresql"}:
            raise ValueError(f"DATABASE_URL must be a postgres:// or postgresql:// DSN, got {v!r}")
        return v

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def _parse_cors_origins(cls, v):
        """Allow comma-separated string in env, e.g. CORS_ORIGINS=a,b."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    @model_validator(mode="after")
    def _validate_config(self) -> "Settings":
        """Cross-field rules: never boot an unsafe or nonsensical config."""
        if "*" in self.CORS_ORIGINS:
            # allow_credentials=True + wildcard origin is rejected by
            # browsers anyway and would mean "any site" — never intended.
            raise ValueError("CORS_ORIGINS must be an explicit allowlist (no '*').")
        if self.is_production and self.DEBUG:
            raise ValueError("DEBUG must be false in production.")
        return self


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance (import this everywhere)."""
    return Settings()


settings = get_settings()
