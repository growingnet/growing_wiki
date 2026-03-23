from pathlib import Path

from growing_wiki_council.models.evidence import EvidenceBundle
from growing_wiki_council.providers.base import ProviderResult
from growing_wiki_council.services.vertical_slice import run_claim_extraction_slice


class FakeProvider:
    """Fake provider for the vertical-slice service test."""

    def load(self, source: str) -> ProviderResult:
        return ProviderResult(
            success=True,
            source_kind="generic_pdf",
            paper_id=source,
            title="Paper",
            raw_text="A short paper body.",
            warnings=[],
        )


class FakeAgent:
    """Fake claim extractor for the vertical-slice service test."""

    def run(self, bundle: EvidenceBundle):
        return {
            "role": "claim_extractor",
            "summary": "Claims extracted.",
            "findings": [],
            "claims": [{"claim": "A", "evidence_refs": ["section:full_text"]}],
        }


def test_vertical_slice_writes_artifacts(tmp_path: Path) -> None:
    """The vertical slice writes both JSON and markdown artifacts."""
    output_dir = tmp_path / "artifacts"

    run_claim_extraction_slice(
        source="paper-1",
        provider=FakeProvider(),
        claim_extractor=FakeAgent(),
        output_dir=output_dir,
    )

    assert (output_dir / "review.json").exists()
    assert (output_dir / "review.md").exists()
