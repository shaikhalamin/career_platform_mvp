"""Opportunities API tests: browse, filter, detail, taxonomy."""

OPPS_API = "/api/v1/opportunities"


async def test_list_returns_50_seeded_opportunities(client):
    resp = await client.get(OPPS_API, params={"page_size": 50})
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert body["meta"]["total_items"] == 50
    assert len(body["data"]) == 50
    sample = body["data"][0]
    assert sample["skills"]["required"]  # grouped requirement shape
    assert "eligibility" in sample


async def test_list_filters(client):
    by_country = await client.get(OPPS_API, params={"country": "Singapore", "page_size": 50})
    assert by_country.status_code == 200
    items = by_country.json()["data"]
    assert items and all(item["country"] == "Singapore" for item in items)

    by_search = await client.get(OPPS_API, params={"search": "fintech", "page_size": 50})
    assert by_search.status_code == 200
    assert any("Kestrel" in item["organisation"] for item in by_search.json()["data"])

    internships = await client.get(
        OPPS_API, params={"employment_type": "internship", "page_size": 50}
    )
    assert internships.status_code == 200
    assert all(item["employment_type"] == "internship" for item in internships.json()["data"])
    assert {item["id"] for item in internships.json()["data"]} == {"J031", "J050"}


async def test_list_unknown_country_filter_422(client):
    resp = await client.get(OPPS_API, params={"country": "Atlantis"})
    assert resp.status_code == 422
    body = resp.json()
    assert body["error"]["code"] == "VALIDATION_ERROR"
    assert body["error"]["details"][0]["field"] == "country"


async def test_get_opportunity_detail(client):
    resp = await client.get(f"{OPPS_API}/J012")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["title"] == "Local-Hire Project Coordinator"
    assert data["country"] == "Singapore"
    assert data["eligibility"]["local_work_authorization_required"] is True
    assert data["languages_required"] == {"English": "professional"}

    resp = await client.get(f"{OPPS_API}/NOPE")
    assert resp.status_code == 404
    assert resp.json()["error"]["code"] == "OPPORTUNITY_NOT_FOUND"


async def test_match_endpoint_explains_score(client):
    from tests.api.test_recommendations import CANDIDATE_PAYLOAD

    created = await client.post("/api/v1/profiles", json=CANDIDATE_PAYLOAD)
    profile_id = created.json()["data"]["id"]

    resp = await client.get(f"{OPPS_API}/J008/match", params={"profile_id": profile_id})
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["total_score"] == 100.0
    assert data["cosine_similarity"] > 0
    assert len(data["score_breakdown"]) == 6
    assert data["eligibility"]["status"] == "eligible"
    assert "not a legal determination" in data["disclaimer"]

    resp = await client.get(f"{OPPS_API}/J012/match", params={"profile_id": profile_id})
    assert resp.json()["data"]["eligibility"]["status"] == "needs_verification"


async def test_taxonomy_endpoint(client):
    resp = await client.get("/api/v1/meta/taxonomy")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["weights"] == {
        "skills": 35,
        "experience": 20,
        "education": 15,
        "location": 15,
        "language": 10,
        "interests": 5,
    }
    assert "bachelors" in {level["value"] for level in data["degree_levels"]}
    assert "English" in data["languages"]
    assert "excel" in data["skills"]
    assert sorted(data["work_auth_values"]) == ["authorized", "not_authorized", "unknown"]
