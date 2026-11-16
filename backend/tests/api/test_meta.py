"""Meta taxonomy endpoint tests — the contract the profile form relies on
(dropdown options must match exactly what profile validation accepts)."""

API = "/api/v1/meta/taxonomy"


async def test_taxonomy_countries_with_regions_and_aliases(client):
    resp = await client.get(API)
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    countries = {c["name"]: c for c in body["data"]["countries"]}

    # Bangladesh is selectable as a preferred/work-auth country.
    assert countries["Bangladesh"]["region"] == "Asia-Pacific"

    # Aliases mirror the backend's accepted input spellings.
    assert sorted(countries["United States"]["aliases"]) == sorted(
        ["usa", "us", "u.s.", "u.s.a.", "united states of america", "america"]
    )
    assert countries["Bangladesh"]["aliases"] == []
    assert countries["United Kingdom"]["region"] == "Europe"


async def test_taxonomy_countries_match_profile_validation(client):
    """Every taxonomy country round-trips through profile validation
    (chunked — profiles accept at most 10 preferred locations)."""
    from tests.api.test_profiles import _payload

    names = [c["name"] for c in (await client.get(API)).json()["data"]["countries"]]
    for index in range(0, len(names), 10):
        chunk = names[index : index + 10]
        resp = await client.post(
            "/api/v1/profiles",
            json=_payload(preferred_locations=chunk, email=f"roundtrip{index}@example.com"),
        )
        assert resp.status_code == 201
        assert resp.json()["data"]["preferred_locations"] == chunk
