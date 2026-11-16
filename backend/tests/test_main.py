"""Application root endpoint tests."""

from app.core.config import settings


async def test_root(client):
    resp = await client.get("/")
    assert resp.status_code == 200
    body = resp.json()
    assert body["name"] == settings.PROJECT_NAME
    assert body["version"] == settings.VERSION
    assert body["api_prefix"] == settings.API_V1_PREFIX
    assert body["docs"] == "/docs"  # development environment
