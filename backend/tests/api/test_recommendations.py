"""Recommendation API tests: the full two-stage pipeline over HTTP,
ranking contracts, explainability, and profile-update recalculation."""

PROFILE_API = "/api/v1/profiles"
RECS_API = "/api/v1/recommendations"

#: Hybrid-form payload mirroring the assessment's sample candidate.
CANDIDATE_PAYLOAD = {
    "name": "Nusrat Jahan",
    "email": "nusrat.jahan@example.com",
    "education_level": "bachelors",
    "education_field": "Business Administration",
    "experience_years": 2,
    "experience_areas": ["business operations", "project support"],
    "skills": [
        "Excel",
        "research",
        "stakeholder communication",
        "reporting",
        "project coordination",
    ],
    "languages": {"English": "professional", "Bengali": "native"},
    "preferred_locations": ["Germany", "Canada", "Singapore"],
    "career_interests": ["Programme support", "business operations", "project coordination"],
    "work_authorisation": {"Germany": "unknown", "Canada": "unknown", "Singapore": "unknown"},
    "citizenship": None,
    "currently_enrolled": None,
}


async def _create_candidate(client) -> dict:
    resp = await client.post(PROFILE_API, json=CANDIDATE_PAYLOAD)
    assert resp.status_code == 201
    return resp.json()["data"]


async def test_recommendations_pipeline_and_contract(client):
    profile = await _create_candidate(client)
    resp = await client.get(RECS_API, params={"profile_id": profile["id"], "top_k": 50})
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    data = body["data"]

    assert data["profile_id"] == profile["id"]
    assert data["top_k"] == 50
    assert data["total_opportunities"] == 50
    assert len(data["items"]) == 50
    assert "not a legal determination" in data["disclaimer"]

    # Ranks are 1..N in order.
    assert [item["rank"] for item in data["items"]] == list(range(1, 51))

    # Eligibility tiers sort eligible -> needs_verification -> ineligible.
    tier_order = {"eligible": 0, "needs_verification": 1, "ineligible": 2}
    tiers = [tier_order[item["eligibility"]["status"]] for item in data["items"]]
    assert tiers == sorted(tiers)

    # Within each tier, scores are non-increasing.
    for i in range(1, len(data["items"])):
        if tiers[i] == tiers[i - 1]:
            assert data["items"][i]["total_score"] <= data["items"][i - 1]["total_score"]

    top = data["items"][0]
    assert top["total_score"] == 100.0
    assert top["eligibility"]["status"] == "eligible"
    assert len(top["score_breakdown"]) == 6
    assert {dimension["key"] for dimension in top["score_breakdown"]} == {
        "skills",
        "experience",
        "education",
        "location",
        "language",
        "interests",
    }
    breakdown_sum = round(sum(d["score"] for d in top["score_breakdown"]), 1)
    assert breakdown_sum == top["total_score"]
    assert top["shortlisted"] is False


async def test_sample_job_j012_flagged_needs_verification(client):
    """The assessment's sample job: strong score, but unknown Singapore
    work authorisation must surface as 'requires verification' — never a
    confirmed status."""
    profile = await _create_candidate(client)
    resp = await client.get(RECS_API, params={"profile_id": profile["id"], "top_k": 50})
    item = next(
        item for item in resp.json()["data"]["items"] if item["opportunity"]["id"] == "J012"
    )
    assert item["eligibility"]["status"] == "needs_verification"
    assert item["eligibility"]["eligible"] is False
    assert item["eligibility"]["status_label"] == "Requires verification"
    work_auth = next(
        check for check in item["eligibility"]["checks"] if check["code"] == "WORK_AUTHORIZATION"
    )
    assert work_auth["requires_verification"] is True
    assert "unknown" in work_auth["evidence"].lower()
    assert "verified" in work_auth["evidence"].lower()
    # It scores highly yet sorts below every clean match.
    assert item["total_score"] >= 90
    # It sorts below every clean match (not in the eligible tier's ranks).
    eligible_ranks = [
        i["rank"] for i in resp.json()["data"]["items"] if i["eligibility"]["status"] == "eligible"
    ]
    assert item["rank"] > max(eligible_ranks)


async def test_constrained_roles_stay_visible_with_evidence(client):
    profile = await _create_candidate(client)
    resp = await client.get(RECS_API, params={"profile_id": profile["id"], "top_k": 50})
    items = {item["opportunity"]["id"]: item for item in resp.json()["data"]["items"]}

    # J018: strict German requirement -> ineligible with language evidence.
    j018 = items["J018"]
    assert j018["eligibility"]["status"] == "ineligible"
    language = next(
        c for c in j018["eligibility"]["checks"] if c["code"] == "LANGUAGE_REQUIREMENTS"
    )
    assert "German" in language["evidence"]

    # J025: Canadian-citizenship role, citizenship not stated -> verify.
    j025 = items["J025"]
    assert j025["eligibility"]["status"] == "needs_verification"

    # J037: strict 6+ years vs 2 years -> ineligible.
    j037 = items["J037"]
    assert j037["eligibility"]["status"] == "ineligible"

    # J031: enrollment-gated internship, enrollment not stated -> verify.
    j031 = items["J031"]
    assert j031["eligibility"]["status"] == "needs_verification"

    # Poor matches still appear (bottom of the eligible tier).
    assert "J033" in items  # Data Scientist, unrelated skills


async def test_top_k_limits_retrieval(client):
    profile = await _create_candidate(client)
    resp = await client.get(RECS_API, params={"profile_id": profile["id"], "top_k": 5})
    data = resp.json()["data"]
    assert data["retrieved_count"] == 5
    assert len(data["items"]) == 5

    resp = await client.get(RECS_API, params={"profile_id": profile["id"], "top_k": 0})
    assert resp.status_code == 422
    resp = await client.get(RECS_API, params={"profile_id": profile["id"], "top_k": 51})
    assert resp.status_code == 422


async def test_profile_update_recalculates_recommendations(client):
    """Recommendations are computed from live data: after changing the
    preferred locations and skills, the ranking responds immediately."""
    profile = await _create_candidate(client)
    before = (await client.get(RECS_API, params={"profile_id": profile["id"], "top_k": 50})).json()[
        "data"
    ]
    top_before = before["items"][0]

    resp = await client.patch(
        f"{PROFILE_API}/{profile['id']}",
        json={
            "preferred_locations": ["Japan"],
            "skills": ["Python", "SQL", "data analysis", "data visualization"],
            "career_interests": ["Data analytics"],
            "languages": {"English": "fluent", "German": "native"},
        },
    )
    assert resp.status_code == 200

    after = (await client.get(RECS_API, params={"profile_id": profile["id"], "top_k": 50})).json()[
        "data"
    ]
    assert after["items"][0]["opportunity"]["id"] != top_before["opportunity"]["id"]
    # The data-science role now leads for the re-skilled profile.
    assert after["items"][0]["opportunity"]["id"] in {"J033", "J046"}


async def test_missing_profile_404(client):
    resp = await client.get(RECS_API, params={"profile_id": 999})
    assert resp.status_code == 404
    assert resp.json()["error"]["code"] == "PROFILE_NOT_FOUND"
