"""Shortlist API tests: save, list, remove, duplicate, 404s — and the
shortlisted flag surfacing in opportunities/recommendations."""

SHORTLIST_API = "/api/v1/shortlist"

PROFILE_PAYLOAD = {
    "name": "Nusrat Jahan",
    "email": "nusrat.jahan@example.com",
    "education_level": "bachelors",
    "education_field": "Business Administration",
    "experience_years": 2,
    "skills": ["Excel", "reporting", "project coordination"],
    "languages": {"English": "professional"},
    "preferred_locations": ["Germany"],
}


async def _profile_id(client) -> int:
    resp = await client.post("/api/v1/profiles", json=PROFILE_PAYLOAD)
    assert resp.status_code == 201
    return resp.json()["data"]["id"]


async def test_shortlist_roundtrip(client):
    profile_id = await _profile_id(client)

    resp = await client.post(
        SHORTLIST_API, json={"profile_id": profile_id, "opportunity_id": "J001"}
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["message"] == "Opportunity shortlisted."
    assert body["data"]["opportunity"]["id"] == "J001"
    assert body["data"]["note"] is None

    resp = await client.get(SHORTLIST_API, params={"profile_id": profile_id})
    assert resp.status_code == 200
    items = resp.json()["data"]
    assert [item["opportunity"]["id"] for item in items] == ["J001"]

    resp = await client.delete(f"{SHORTLIST_API}/{profile_id}/J001")
    assert resp.status_code == 200
    assert (await client.get(SHORTLIST_API, params={"profile_id": profile_id})).json()["data"] == []


async def test_shortlist_note_preserved(client):
    profile_id = await _profile_id(client)
    resp = await client.post(
        SHORTLIST_API,
        json={"profile_id": profile_id, "opportunity_id": "J003", "note": "Great fit"},
    )
    assert resp.status_code == 201
    assert resp.json()["data"]["note"] == "Great fit"


async def test_duplicate_shortlist_conflict(client):
    profile_id = await _profile_id(client)
    await client.post(SHORTLIST_API, json={"profile_id": profile_id, "opportunity_id": "J001"})
    resp = await client.post(
        SHORTLIST_API, json={"profile_id": profile_id, "opportunity_id": "J001"}
    )
    assert resp.status_code == 409
    assert resp.json()["error"]["code"] == "SHORTLIST_ALREADY_EXISTS"


async def test_shortlist_validation_and_404s(client):
    profile_id = await _profile_id(client)

    # Unknown opportunity -> OPPORTUNITY_NOT_FOUND.
    resp = await client.post(
        SHORTLIST_API, json={"profile_id": profile_id, "opportunity_id": "NOPE"}
    )
    assert resp.status_code == 404
    assert resp.json()["error"]["code"] == "OPPORTUNITY_NOT_FOUND"

    # Unknown profile -> PROFILE_NOT_FOUND.
    resp = await client.post(SHORTLIST_API, json={"profile_id": 999, "opportunity_id": "J001"})
    assert resp.status_code == 404
    assert resp.json()["error"]["code"] == "PROFILE_NOT_FOUND"

    # Removing something not shortlisted -> SHORTLIST_NOT_FOUND.
    resp = await client.delete(f"{SHORTLIST_API}/{profile_id}/J002")
    assert resp.status_code == 404
    assert resp.json()["error"]["code"] == "SHORTLIST_NOT_FOUND"

    # Invalid work-auth-style payload constraints (bad body) -> 422.
    resp = await client.post(SHORTLIST_API, json={"profile_id": profile_id})
    assert resp.status_code == 422


async def test_shortlisted_flag_surfaces_in_lists(client):
    profile_id = await _profile_id(client)
    await client.post(SHORTLIST_API, json={"profile_id": profile_id, "opportunity_id": "J003"})

    resp = await client.get(
        "/api/v1/opportunities", params={"profile_id": profile_id, "page_size": 50}
    )
    flags = {item["id"]: item["shortlisted"] for item in resp.json()["data"]}
    assert flags["J003"] is True
    assert flags["J001"] is False

    resp = await client.get(
        "/api/v1/recommendations", params={"profile_id": profile_id, "top_k": 50}
    )
    recs = {item["opportunity"]["id"]: item["shortlisted"] for item in resp.json()["data"]["items"]}
    assert recs["J003"] is True
    assert recs["J001"] is False
