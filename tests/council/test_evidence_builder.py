from growing_wiki_council.providers.base import ProviderResult
from growing_wiki_council.services.evidence_builder import EvidenceBuilder


def test_evidence_builder_assigns_low_confidence_on_warnings() -> None:
    """Warnings downgrade extraction confidence in the normalized bundle."""
    builder = EvidenceBuilder()
    provider_result = ProviderResult(
        success=True,
        source_kind="generic_pdf",
        title="Paper",
        raw_text="text",
        sections=[],
        equations=[],
        bibliography=[],
        warnings=["missing bibliography"],
    )

    bundle = builder.build(provider_result)

    assert bundle.extraction_confidence == "low"
