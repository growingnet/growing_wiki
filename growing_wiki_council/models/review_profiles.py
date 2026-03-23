"""Additive review schemas for benchmark steerability experiments."""

from __future__ import annotations

from pydantic import Field

from growing_wiki_council.models.review import ReviewerReport


class WebsiteAlignedReviewerReport(ReviewerReport):
    """Reviewer report variant with website-aligned mechanistic fields."""

    schema_variant: str = "website_aligned"
    method_family: str | None = None
    growth_operator: str | None = None
    initialization_strategy: str | None = None
    selection_criterion: str | None = None
    mechanistic_notes: list[str] = Field(default_factory=list)
    website_alignment_notes: str | None = None
