from pathlib import Path

from growing_wiki_council.cli import write_review_artifacts
from growing_wiki_council.models.evidence import EvidenceBundle
from growing_wiki_council.providers.base import ProviderResult
from growing_wiki_council.services.evidence_builder import EvidenceBuilder
from growing_wiki_council.services.review_runner import ReviewRunner


class FakeProvider:
    """Provider double for the council smoke test."""

    def load(self, source: str) -> ProviderResult:
        return ProviderResult(
            success=True,
            source_kind="generic_pdf",
            paper_id=source,
            title="Smoke Test Paper",
            raw_text="A short paper body.",
            warnings=[],
        )


class FakeReviewer:
    """Reviewer double for the council smoke test."""

    def __init__(self, payload: dict) -> None:
        self.payload = payload

    def run(self, bundle: EvidenceBundle):
        return self.payload


def test_end_to_end_council_smoke(tmp_path: Path) -> None:
    """The council pipeline can produce review artifacts from fake inputs."""
    provider = FakeProvider()
    builder = EvidenceBuilder()
    bundle = builder.build(provider.load("paper-1"))

    runner = ReviewRunner(
        claim_extractor=FakeReviewer(
            {
                "role": "claim_extractor",
                "summary": "Claims extracted.",
                "findings": [],
                "claims": [
                    {
                        "claim": "The paper reports a gain.",
                        "evidence_refs": ["section:full_text"],
                    }
                ],
            }
        ),
        skeptical_reviewer=FakeReviewer(
            {
                "role": "skeptical_reviewer",
                "summary": "One gap remains.",
                "findings": [
                    {
                        "severity": "medium",
                        "claim": "The evaluation is underspecified.",
                        "evidence_refs": ["section:full_text"],
                        "rationale": "There is no dataset description.",
                    }
                ],
                "claims": [],
            }
        ),
        supportive_reviewer=FakeReviewer(
            {
                "role": "supportive_reviewer",
                "summary": "The contribution is clearly stated.",
                "findings": [],
                "claims": [],
            }
        ),
        citation_auditor=FakeReviewer(
            {
                "role": "citation_auditor",
                "summary": "No citation checks were run in smoke mode.",
                "findings": [],
                "claims": [],
            }
        ),
        chair_editor=FakeReviewer(
            {
                "verdict": "needs_human_review",
                "summary": "The artifact is structurally valid but still synthetic.",
                "blocking_issues": ["Use real provider and reviewer integrations."],
                "confidence": "medium",
                "recommended_actions": ["Run against a real paper next."],
            }
        ),
    )

    artifact = runner.run(bundle)
    output_dir = tmp_path / "artifacts"
    write_review_artifacts(
        output_dir,
        review_json=artifact.model_dump(mode="json"),
        review_markdown=f"# Review\n\n{artifact.chair_verdict.summary}",
    )

    assert (output_dir / "review.json").exists()
    assert (output_dir / "review.md").exists()
