from pathlib import Path

from growing_wiki_council.cli import run_vertical_slice
from growing_wiki_council.models.evidence import EvidenceBundle
from growing_wiki_council.providers.base import ProviderResult


class FakeProvider:
    """Fake provider for the CLI vertical-slice test."""

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
    """Fake claim extractor for the CLI vertical-slice test."""

    def run(self, bundle: EvidenceBundle):
        return {
            "role": "claim_extractor",
            "summary": "Claims extracted.",
            "findings": [],
            "claims": [{"claim": "A", "evidence_refs": ["section:full_text"]}],
        }


def test_run_vertical_slice_creates_artifacts(tmp_path: Path) -> None:
    """The CLI helper delegates to the vertical-slice service."""
    output_dir = tmp_path / "artifacts"

    run_vertical_slice(
        source="paper-1",
        provider=FakeProvider(),
        claim_extractor=FakeAgent(),
        output_dir=output_dir,
    )

    assert (output_dir / "review.json").exists()
