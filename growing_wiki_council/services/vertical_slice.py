"""Vertical-slice service for a single real claim-extraction run."""

from pathlib import Path
from typing import Any

from growing_wiki_council.cli import write_review_artifacts
from growing_wiki_council.models.review import (
    ChairVerdict,
    CouncilReviewArtifact,
    ReviewerReport,
)
from growing_wiki_council.services.evidence_builder import EvidenceBuilder


def run_claim_extraction_slice(
    *,
    source: str,
    provider: Any,
    claim_extractor: Any,
    output_dir: Path,
) -> CouncilReviewArtifact:
    """Run the first real council slice with one provider and one reviewer."""
    provider_result = provider.load(source)
    bundle = EvidenceBuilder().build(provider_result)
    reviewer_report = ReviewerReport.model_validate(claim_extractor.run(bundle))
    artifact = CouncilReviewArtifact(
        paper_id=bundle.paper_id,
        source_kind=bundle.source_kind,
        reviewer_reports=[reviewer_report],
        chair_verdict=ChairVerdict(
            verdict="needs_human_review",
            summary="Single-reviewer vertical slice completed.",
            blocking_issues=[],
            confidence=bundle.extraction_confidence,
            recommended_actions=["Run the remaining council roles."],
        ),
    )
    write_review_artifacts(
        output_dir,
        review_json=artifact.model_dump(mode="json"),
        review_markdown=f"# Review\n\n{artifact.chair_verdict.summary}",
    )
    return artifact
