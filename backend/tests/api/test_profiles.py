"""User profile CRUD API tests — happy paths, validation, conflict, 404s,
career-field validation, and the standard envelope contract."""

API = "/api/v1/profiles"

CAREER_FIELDS = {
    "education_level": "bachelors",
    "education_field": "Business Administration",
    "experience_years": 2,
    "experience_areas": ["business operations", "project support"],
    "skills": ["Excel", "research", "stakeholder communication", "reporting"],
    "languages": {"English": "professional", "Bengali": "native"},
    "preferred_locations": ["Germany", "Canada", "Singapore"],
    "career_interests": ["Programme support", "project coordination"],
    "work_authorisation": {"Singapore": "unknown"},
    "citizenship": None,
    "currently_enrolled": None,
}


def _payload(**overrides) -> dict:
    payload = {"name": "Ada Lovelace", "email": "ada@example.com", **CAREER_FIELDS}
    payload.update(overrides)
    return payload


async def _create(client, **overrides) -> dict:
    resp = await client.post(API, json=_payload(**overrides))
    assert resp.status_code == 201
    return resp.json()["data"]


# --- Create ------------------------------------------------------------------


async def test_create_profile(client):
    resp = await client.post(API, json=_payload(name="  Grace Hopper  ", email="Grace@Example.COM"))
    assert resp.status_code == 201
    body = resp.json()
    assert body["success"] is True
    assert body["message"] == "Profile created."
    data = body["data"]
    assert data["id"] == 1
    assert data["name"] == "Grace Hopper"  # trimmed
    assert data["email"] == "grace@example.com"  # lowercased
    assert data["education_level"] == "bachelors"
    assert data["experience_years"] == 2.0
    assert data["preferred_locations"] == ["Germany", "Canada", "Singapore"]
    assert data["languages"]["English"] == "professional"
    assert data["work_authorisation"] == {"Singapore": "unknown"}
    assert data["created_at"]


async def test_create_normalizes_loose_input(client):
    """Aliases/casing are canonicalized at the boundary."""
    resp = await client.post(
        API,
        json=_payload(
            preferred_locations=["USA", "U.K.", "singapore", "bangladesh"],
            languages={"english": "native"},
            work_authorisation={"CANADA": "authorized"},
        ),
    )
    assert resp.status_code == 201
    data = resp.json()["data"]
    assert data["preferred_locations"] == [
        "United States",
        "United Kingdom",
        "Singapore",
        "Bangladesh",
    ]
    assert data["languages"] == {"English": "native"}
    assert data["work_authorisation"] == {"Canada": "authorized"}


async def test_create_duplicate_email_conflict(client):
    await _create(client)
    resp = await client.post(API, json=_payload(name="Second Person"))
    assert resp.status_code == 409
    body = resp.json()
    assert body["success"] is False
    assert body["error"]["code"] == "EMAIL_ALREADY_REGISTERED"
    assert body["error"]["details"][0]["field"] == "email"


async def test_create_invalid_email_unprocessable(client):
    resp = await client.post(API, json=_payload(email="not-an-email"))
    assert resp.status_code == 422
    body = resp.json()
    assert body["success"] is False
    assert body["error"]["code"] == "VALIDATION_ERROR"
    assert "email" in {detail["field"] for detail in body["error"]["details"]}


async def test_create_career_field_validation(client):
    # Bad degree level enum.
    resp = await client.post(API, json=_payload(education_level="phd_lite"))
    assert resp.status_code == 422
    assert "education_level" in {d["field"] for d in resp.json()["error"]["details"]}

    # Unknown preferred country.
    resp = await client.post(API, json=_payload(preferred_locations=["Atlantis"]))
    assert resp.status_code == 422
    assert "preferred_locations" in {d["field"] for d in resp.json()["error"]["details"]}

    # Bad work-authorisation value.
    resp = await client.post(API, json=_payload(work_authorisation={"Germany": "maybe"}))
    assert resp.status_code == 422
    fields = {d["field"] for d in resp.json()["error"]["details"]}
    assert any(f and f.startswith("work_authorisation") for f in fields)

    # Bad language level.
    resp = await client.post(API, json=_payload(languages={"English": "okay"}))
    assert resp.status_code == 422

    # Skills list must be non-empty.
    resp = await client.post(API, json=_payload(skills=[]))
    assert resp.status_code == 422

    # Experience years bounds.
    resp = await client.post(API, json=_payload(experience_years=75))
    assert resp.status_code == 422


async def test_create_missing_fields_unprocessable(client):
    resp = await client.post(API, json={})
    assert resp.status_code == 422
    fields = {detail["field"] for detail in resp.json()["error"]["details"]}
    assert {
        "name",
        "email",
        "education_level",
        "skills",
        "languages",
        "preferred_locations",
        "experience_years",
    } <= fields


# --- List --------------------------------------------------------------------


async def test_list_empty(client):
    resp = await client.get(API)
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert body["data"] == []
    assert body["meta"]["total_items"] == 0


async def test_list_pagination(client):
    for i in range(3):
        await _create(client, email=f"user{i}@example.com", name=f"User {i}")
    resp = await client.get(API, params={"page": 1, "page_size": 2})
    assert resp.status_code == 200
    body = resp.json()
    assert [profile["id"] for profile in body["data"]] == [1, 2]
    assert body["meta"] == {
        "page": 1,
        "page_size": 2,
        "total_items": 3,
        "total_pages": 2,
        "has_next": True,
        "has_previous": False,
    }


async def test_list_invalid_pagination_unprocessable(client):
    resp = await client.get(API, params={"page": 0})
    assert resp.status_code == 422
    assert resp.json()["error"]["code"] == "VALIDATION_ERROR"


# --- Read one ----------------------------------------------------------------


async def test_get_profile(client):
    created = await _create(client)
    resp = await client.get(f"{API}/{created['id']}")
    assert resp.status_code == 200
    assert resp.json()["data"] == created


async def test_get_missing_profile_not_found(client):
    resp = await client.get(f"{API}/999")
    assert resp.status_code == 404
    body = resp.json()
    assert body["success"] is False
    assert body["error"]["code"] == "PROFILE_NOT_FOUND"


async def test_get_non_integer_id_unprocessable(client):
    resp = await client.get(f"{API}/abc")
    assert resp.status_code == 422
    assert resp.json()["error"]["code"] == "VALIDATION_ERROR"


# --- Update ------------------------------------------------------------------


async def test_patch_partial_update(client):
    created = await _create(client)
    resp = await client.patch(f"{API}/{created['id']}", json={"name": "Ada King"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["message"] == "Profile updated."
    data = body["data"]
    assert data["name"] == "Ada King"
    assert data["email"] == created["email"]  # untouched field
    assert data["skills"] == created["skills"]  # untouched career field


async def test_patch_career_fields_and_clearing(client):
    created = await _create(client)
    resp = await client.patch(
        f"{API}/{created['id']}",
        json={"experience_years": 3, "citizenship": None, "education_field": None},
    )
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["experience_years"] == 3.0
    assert data["citizenship"] is None
    assert data["education_field"] is None


async def test_patch_email_to_taken_email_conflict(client):
    created = await _create(client)
    await _create(client, email="bob@example.com", name="Bob")
    resp = await client.patch(f"{API}/{created['id']}", json={"email": "bob@example.com"})
    assert resp.status_code == 409
    assert resp.json()["error"]["code"] == "EMAIL_ALREADY_REGISTERED"


async def test_patch_keep_own_email_is_no_conflict(client):
    # Re-sending the profile's own email must not trip the uniqueness check.
    created = await _create(client)
    resp = await client.patch(f"{API}/{created['id']}", json={"email": created["email"]})
    assert resp.status_code == 200


async def test_patch_empty_body_changes_nothing(client):
    created = await _create(client)
    resp = await client.patch(f"{API}/{created['id']}", json={})
    assert resp.status_code == 200
    assert resp.json()["data"] == created


async def test_patch_missing_profile_not_found(client):
    resp = await client.patch(f"{API}/999", json={"name": "Nobody"})
    assert resp.status_code == 404
    assert resp.json()["error"]["code"] == "PROFILE_NOT_FOUND"


# --- Delete ------------------------------------------------------------------


async def test_delete_profile(client):
    created = await _create(client)
    # Shortlist something so cascade deletion is exercised.
    await client.post(
        "/api/v1/shortlist",
        json={"profile_id": created["id"], "opportunity_id": "J001"},
    )
    resp = await client.delete(f"{API}/{created['id']}")
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert body["data"] is None
    assert body["message"] == "Profile deleted."
    # Gone afterwards.
    resp = await client.get(f"{API}/{created['id']}")
    assert resp.status_code == 404


async def test_delete_missing_profile_not_found(client):
    resp = await client.delete(f"{API}/999")
    assert resp.status_code == 404
