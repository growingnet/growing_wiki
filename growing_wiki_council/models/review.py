"""Structured review models for council outputs."""

from typing import Literal

from pydantic import BaseModel, Field

from growing_wiki_council.models.evidence import EvidenceSourceKind


FindingSeverity = Literal["low", "medium", "high", "critical"]
ReviewerRole = Literal[
    "claim_extractor",
    "skeptical_reviewer",
    "supportive_reviewer",
    "citation_auditor",
    "chair_editor",
]
VerdictStatus = Literal["accept", "revise", "reject", "needs_human_review"]
ReviewConfidence = Literal["low", "medium", "high"]


class ClaimRecord(BaseModel):
    """An extracted claim with explicit evidence references."""

    claim: str
    evidence_refs: list[str] = Field(min_length=1)
    confidence: ReviewConfidence | None = None
    notes: str | None = None


class ReviewFinding(BaseModel):
    """A structured reviewer finding tied to evidence references."""

    severity: FindingSeverity
    claim: str
    evidence_refs: list[str] = Field(min_length=1)
    rationale: str
    recommendation: str | None = None


class ReviewerReport(BaseModel):
    """A role-specific reviewer report."""

    role: ReviewerRole
    summary: str
    findings: list[ReviewFinding] = Field(default_factory=list)
    claims: list[ClaimRecord] = Field(default_factory=list)
    open_questions: list[str] = Field(default_factory=list)


class ChairVerdict(BaseModel):
    """Final council verdict for a reviewed paper."""

    verdict: VerdictStatus
    summary: str
    blocking_issues: list[str] = Field(default_factory=list)
    confidence: ReviewConfidence
    recommended_actions: list[str] = Field(default_factory=list)


class CouncilReviewArtifact(BaseModel):
    """Top-level review artifact emitted by the council."""

    paper_id: str
    source_kind: EvidenceSourceKind
    reviewer_reports: list[ReviewerReport] = Field(default_factory=list)
    chair_verdict: ChairVerdict
