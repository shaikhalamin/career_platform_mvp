"""Integrity checks for the country taxonomy — the invariants the 422
validation and the location scoring silently rely on."""

from app.services import taxonomy


def test_country_data_has_unique_names_and_iso_codes():
    names = [row[0] for row in taxonomy.COUNTRY_DATA]
    iso2 = [row[2] for row in taxonomy.COUNTRY_DATA]
    iso3 = [row[3] for row in taxonomy.COUNTRY_DATA]
    # Dict-building would silently drop duplicates — fail loudly instead.
    assert len(names) == len(set(names))
    assert len(iso2) == len(set(iso2))
    assert len(iso3) == len(set(iso3))
    assert len(taxonomy.COUNTRY_REGIONS) == len(taxonomy.COUNTRY_DATA)


def test_every_alias_resolves_to_a_known_country():
    for alias, canonical in taxonomy.COUNTRY_ALIASES.items():
        assert canonical in taxonomy.COUNTRY_REGIONS
        assert taxonomy.normalize_country_key(alias) == canonical


def test_normalize_country_key_accepts_names_cases_and_iso_codes():
    assert taxonomy.normalize_country_key("bangladesh") == "Bangladesh"
    assert taxonomy.normalize_country_key("  Türkiye  ") == "Türkiye"
    assert taxonomy.normalize_country_key("BGD") == "Bangladesh"
    assert taxonomy.normalize_country_key("usa") == "United States"
    assert taxonomy.normalize_country_key("UK") == "United Kingdom"
    assert taxonomy.normalize_country_key("ivory coast") == "Côte d'Ivoire"
    assert taxonomy.normalize_country_key("") is None
    assert taxonomy.normalize_country_key(None) is None
    assert taxonomy.normalize_country_key("Narnia") is None
