"""Human evaluation models for benchmark scoring."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


ReviewStatus = Literal["not_started", "in_progress", "completed"]


class HumanEvaluationTemplate(BaseModel):
    """Structured template for manual review of a benchmark run."""

    paper_id: str
    model_id: str
    run_label: str
    review_status: ReviewStatus = "not_started"
    scored_at: str | None = None
    claim_faithfulness: int | None = None
    evidence_grounding: int | None = None
    omission_rate: int | None = None
    hallucination_flags: list[str] = Field(default_factory=list)
    reviewer_notes: str | None = None
