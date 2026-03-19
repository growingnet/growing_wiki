"""Evidence normalization services."""

from growing_wiki_council.models.evidence import EvidenceBundle, EvidenceSection
from growing_wiki_council.providers.base import ProviderResult


class EvidenceBuilder:
    """Convert provider outputs into normalized evidence bundles."""

    def build(self, provider_result: ProviderResult) -> EvidenceBundle:
        """Normalize a provider result into the shared evidence schema."""
        normalized_sections = list(provider_result.sections)

        if not normalized_sections and provider_result.raw_text:
            normalized_sections.append(
                EvidenceSection(
                    name="full_text",
                    content=provider_result.raw_text,
                    provenance=self._default_provenance(provider_result.source_kind),
                )
            )

        return EvidenceBundle(
            paper_id=provider_result.paper_id or provider_result.title or "unknown-paper",
            source_kind=provider_result.source_kind or "generic_pdf",
            title=provider_result.title or "Untitled paper",
            sections=normalized_sections,
            equations=provider_result.equations,
            bibliography=provider_result.bibliography,
            warnings=provider_result.warnings,
            extraction_confidence=self._score_extraction_confidence(provider_result),
        )

    def _default_provenance(self, source_kind: str | None) -> str:
        """Map a source kind to default section provenance."""
        if source_kind == "arxiv_latex":
            return "latex"
        if source_kind in {"arxiv_pdf", "generic_pdf"}:
            return "pdf"
        return "unknown"

    def _score_extraction_confidence(self, provider_result: ProviderResult) -> str:
        """Assign a simple extraction confidence score for v1.

        Warnings or fallback paths indicate degraded extraction and are low
        confidence. Structured extracted sections without warnings are high
        confidence. Raw-text-only cases without warnings are medium confidence.
        """
        if (
            not provider_result.success
            or provider_result.warnings
            or provider_result.fallback_used
        ):
            return "low"
        if provider_result.sections:
            return "high"
        return "medium"
