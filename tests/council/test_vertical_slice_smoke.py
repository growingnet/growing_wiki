from pathlib import Path

from growing_wiki_council.models.evidence import EvidenceBundle
from growing_wiki_council.providers.base import ProviderResult
from growing_wiki_council.services.vertical_slice import run_claim_extraction_slice


class FakeArxivProvider:
    """Fake arXiv-backed provider for the vertical-slice smoke test."""

    def load(self, source: str) -> ProviderResult:
        return ProviderResult(
            success=True,
            source_kind="arxiv_pdf",
            paper_id=source,
            title="Smoke Paper",
            raw_text="A smoke-test paper body.",
            warnings=["Used PDF fallback"],
            fallback_used=True,
            fallback_reason="201: No source available",
        )


class FakeClaimExtractor:
    """Fake real-reviewer stand-in for the vertical slice."""

    def run(self, bundle: EvidenceBundle):
        return {
            "role": "claim_extractor",
            "summary": "Claims extracted from the smoke paper.",
            "findings": [],
            "claims": [{"claim": "A", "evidence_refs": ["section:full_text"]}],
        }


def test_vertical_slice_smoke(tmp_path: Path) -> None:
    """The real vertical slice can emit artifacts without network access."""
    output_dir = tmp_path / "artifacts"

    artifact = run_claim_extraction_slice(
        source="arxiv:paper-1",
        provider=FakeArxivProvider(),
        claim_extractor=FakeClaimExtractor(),
        output_dir=output_dir,
    )

    assert artifact.source_kind == "arxiv_pdf"
    assert artifact.chair_verdict.verdict == "needs_human_review"
    assert (output_dir / "review.json").exists()
    assert (output_dir / "review.md").exists()
