"""Response schema for the reference taxonomy (drives the frontend form
dropdowns and the score-weight legend)."""

from pydantic import BaseModel, Field


class RankedLevel(BaseModel):
    """A ranked enum entry (degree or language level)."""

    value: str
    label: str
    rank: int


class CountryInfo(BaseModel):
    """A country with its region."""

    name: str
    region: str


class TaxonomyRead(BaseModel):
    """Everything the profile form and scoring legend need."""

    degree_levels: list[RankedLevel]
    language_levels: list[RankedLevel]
    languages: list[str]
    skills: list[str]
    fields: list[str]
    countries: list[CountryInfo]
    career_tracks: list[str]
    work_auth_values: list[str]
    weights: dict[str, int] = Field(description="Six-part weighted score, totalling 100 points.")
    disclaimer: str
