"""FastAPI application factory.

Run in development:
    uv run uvicorn app.main:app --reload --port 8000
Run in production:
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import api_v1_router
from app.core.config import settings
from app.core.database import AsyncSessionLocal, engine
from app.core.exception_handlers import register_exception_handlers
from app.services.seed_service import ensure_seeded

logger = logging.getLogger("app.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup/shutdown lifecycle: seed reference data, then serve."""
    logging.basicConfig(
        level=logging.DEBUG if settings.DEBUG else logging.INFO,
        format="%(asctime)s %(levelname)-7s %(name)s — %(message)s",
    )
    logger.info(
        "Starting %s v%s (%s)", settings.PROJECT_NAME, settings.VERSION, settings.ENVIRONMENT
    )
    if not settings.is_testing:
        # Tests seed their own fixtures (no lifespan under ASGITransport);
        # dev/prod boot with the 50 opportunities ready. User profiles are
        # never seeded — only API-created profiles exist.
        try:
            async with AsyncSessionLocal() as session:
                await ensure_seeded(session)
                await session.commit()
        except Exception:
            logger.exception("Seeding failed — run `uv run alembic upgrade head` and restart.")
    yield
    logger.info("Shutting down — closing database connections")
    await engine.dispose()


def create_app() -> FastAPI:
    """Build and configure the FastAPI application."""
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description="Career Platform MVP backend API: user profile management.",
        openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
        # Interactive docs stay out of production by default (attack-surface
        # hygiene); DOCS_IN_PRODUCTION=true opts in for hands-on testing.
        # The OpenAPI document itself always remains available for client
        # generation.
        docs_url="/docs" if settings.api_docs_enabled else None,
        redoc_url="/redoc" if settings.api_docs_enabled else None,
        lifespan=lifespan,
        # Envelope responses are produced by handlers/routers; these defaults
        # keep the OpenAPI document honest for client generation.
        responses={
            422: {"description": "Validation error (standard error envelope)"},
            500: {"description": "Internal server error (standard error envelope)"},
        },
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_exception_handlers(app)

    app.include_router(api_v1_router, prefix=settings.API_V1_PREFIX)

    @app.get("/", include_in_schema=False)
    async def root() -> dict:
        payload = {
            "name": settings.PROJECT_NAME,
            "version": settings.VERSION,
            "environment": settings.ENVIRONMENT,
            "api_prefix": settings.API_V1_PREFIX,
        }
        if not settings.is_production:
            payload["docs"] = "/docs"  # /docs is disabled in production
        return payload

    return app


app = create_app()
