from growing_wiki_council.models.evidence import EvidenceBundle
from growing_wiki_council.services.review_runner import ReviewRunner


class FakeReviewer:
    """Minimal fake reviewer used to validate orchestration order."""

    def __init__(self, payload: dict) -> None:
        self.payload = payload

    def run(self, bundle: EvidenceBundle):
        return self.payload


def test_review_runner_returns_all_expected_roles() -> None:
    """The runner returns a review artifact for the complete council flow."""
    sample_bundle = EvidenceBundle(
        paper_id="paper-1",
        source_kind="generic_pdf",
        title="Sample Paper",
        sections=[],
        equations=[],
        bibliography=[],
        warnings=[],
        extraction_confidence="medium",
    )
    runner = ReviewRunner(
        claim_extractor=FakeReviewer(
            {
                "role": "claim_extractor",
                "summary": "Claims extracted.",
                "findings": [],
                "claims": [
                    {
                        "claim": "The paper improves performance.",
                        "evidence_refs": ["section:full_text"],
                    }
                ],
            }
        ),
        skeptical_reviewer=FakeReviewer(
            {
                "role": "skeptical_reviewer",
                "summary": "One concern found.",
                "findings": [
                    {
                        "severity": "medium",
                        "claim": "The baseline set is incomplete.",
                        "evidence_refs": ["section:full_text"],
                        "rationale": "Only one baseline is reported.",
                    }
                ],
                "claims": [],
            }
        ),
        supportive_reviewer=FakeReviewer(
            {
                "role": "supportive_reviewer",
                "summary": "One strength found.",
                "findings": [],
                "claims": [],
            }
        ),
        citation_auditor=FakeReviewer(
            {
                "role": "citation_auditor",
                "summary": "No citation issues found.",
                "findings": [],
                "claims": [],
            }
        ),
        chair_editor=FakeReviewer(
            {
                "verdict": "revise",
                "summary": "Needs follow-up before wiki integration.",
                "blocking_issues": ["Clarify baseline coverage."],
                "confidence": "medium",
                "recommended_actions": ["Check related-work coverage."],
            }
        ),
    )

    artifact = runner.run(sample_bundle)

    assert artifact is not None
    assert artifact.paper_id == "paper-1"
    assert len(artifact.reviewer_reports) == 4
