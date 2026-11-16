"""Response schemas for recommendations and match analyses.

Every score point is explainable by contract: each dimension carries its
points, maximum, matched/missing items and notes; each eligibility check
carries its status and evidence. The disclaimer travels with every payload
so no consumer can present eligibility output as a legal determination.
"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.opportunity import OpportunitySummary

EligibilityStatus = Literal["eligible", "needs_verification", "ineligible"]
CheckStatus = Literal["pass", "fail", "needs_verification", "not_applicable"]


class DimensionScoreRead(BaseModel):
    """Points awarded for one scoring dimension, with evidence."""

    key: str = Field(examples=["skills"])
    label: str = Field(examples=["Skills"])
    score: float = Field(examples=[30.1])
    max_points: float = Field(examples=[35])
    percentage: float = Field(examples=[86.0])
    matched: list[str] = Field(default_factory=list)
    missing: list[str] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)


class EligibilityCheckRead(BaseModel):
    """One hard-constraint evaluation with its evidence."""

    code: str = Field(examples=["WORK_AUTHORIZATION"])
    label: str = Field(examples=["Work authorisation — Germany"])
    status: CheckStatus
    evidence: str
    requires_verification: bool = False


class EligibilityRead(BaseModel):
    """Aggregate eligibility outcome (guidance, not a legal determination)."""

    status: EligibilityStatus
    status_label: str
    eligible: bool
    summary: str
    checks: list[EligibilityCheckRead]


class RecommendationItem(BaseModel):
    """One ranked recommendation."""

    rank: int
    opportunity: OpportunitySummary
    total_score: float = Field(examples=[78.5])
    max_score: float = Field(examples=[100])
    cosine_similarity: float = Field(examples=[0.83])
    score_breakdown: list[DimensionScoreRead]
    eligibility: EligibilityRead
    strengths: list[str]
    gaps: list[str]
    shortlisted: bool = False


class RecommendationList(BaseModel):
    """Full ranked recommendation set for one profile."""

    profile_id: int
    profile_name: str
    generated_at: datetime
    top_k: int
    total_opportunities: int
    retrieved_count: int
    disclaimer: str
    items: list[RecommendationItem]


class MatchDetail(BaseModel):
    """Single-opportunity match analysis (job detail page)."""

    opportunity_id: str
    profile_id: int
    total_score: float
    max_score: float
    cosine_similarity: float
    score_breakdown: list[DimensionScoreRead]
    eligibility: EligibilityRead
    strengths: list[str]
    gaps: list[str]
    shortlisted: bool = False
    disclaimer: str
