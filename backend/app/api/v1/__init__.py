"""API v1 router aggregation — include every versioned router here."""

from fastapi import APIRouter

from app.api.v1 import health, meta, opportunities, profiles, recommendations, shortlist

api_v1_router = APIRouter()
api_v1_router.include_router(health.router)
api_v1_router.include_router(meta.router)
api_v1_router.include_router(profiles.router)
api_v1_router.include_router(opportunities.router)
api_v1_router.include_router(recommendations.router)
api_v1_router.include_router(shortlist.router)
