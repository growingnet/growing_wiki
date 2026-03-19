"""Deterministic orchestration for council reviewer execution."""

from typing import Any

from growing_wiki_council.agents import ReviewerAgent
from growing_wiki_council.models.evidence import EvidenceBundle
from growing_wiki_council.models.review import (
    ChairVerdict,
    CouncilReviewArtifact,
    ReviewerReport,
)


class ReviewRunner:
    """Run the council reviewers in a fixed deterministic order."""

    def __init__(
        self,
        *,
        claim_extractor: ReviewerAgent,
        skeptical_reviewer: ReviewerAgent,
        supportive_reviewer: ReviewerAgent,
        citation_auditor: ReviewerAgent,
        chair_editor: ReviewerAgent,
    ) -> None:
        """Store the reviewer agents used by the council."""
        self.claim_extractor = claim_extractor
        self.skeptical_reviewer = skeptical_reviewer
        self.supportive_reviewer = supportive_reviewer
        self.citation_auditor = citation_auditor
        self.chair_editor = chair_editor

    def run(self, bundle: EvidenceBundle) -> CouncilReviewArtifact:
        """Execute reviewers in order and build the final review artifact."""
        reviewer_reports = [
            self._coerce_report(self.claim_extractor.run(bundle)),
            self._coerce_report(self.skeptical_reviewer.run(bundle)),
            self._coerce_report(self.supportive_reviewer.run(bundle)),
            self._coerce_report(self.citation_auditor.run(bundle)),
        ]
        chair_verdict = self._coerce_verdict(self.chair_editor.run(bundle))

        return CouncilReviewArtifact(
            paper_id=bundle.paper_id,
            source_kind=bundle.source_kind,
            reviewer_reports=reviewer_reports,
            chair_verdict=chair_verdict,
        )

    def _coerce_report(self, payload: ReviewerReport | dict[str, Any]) -> ReviewerReport:
        """Normalize reviewer outputs into a reviewer report model."""
        if isinstance(payload, ReviewerReport):
            return payload
        return ReviewerReport.model_validate(payload)

    def _coerce_verdict(
        self, payload: ChairVerdict | dict[str, Any]
    ) -> ChairVerdict:
        """Normalize the chair output into a verdict model."""
        if isinstance(payload, ChairVerdict):
            return payload
        return ChairVerdict.model_validate(payload)
