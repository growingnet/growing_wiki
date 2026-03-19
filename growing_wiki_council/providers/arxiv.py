"""Thin adapter for arXiv MCP-style clients."""

from typing import Any

from growing_wiki_council.clients.arxiv_client import ArxivPaperClientProtocol
from growing_wiki_council.models.evidence import (
    EvidenceBibliographyEntry,
    EvidenceEquation,
)
from growing_wiki_council.providers.base import ProviderResult


class ArxivLatexProvider:
    """Adapt MCP-style paper retrieval into the provider contract."""

    def __init__(self, client: ArxivPaperClientProtocol) -> None:
        """Store the injected MCP-style client."""
        self.client = client

    def load(self, source: str) -> ProviderResult:
        """Load a paper by arXiv identifier through the client."""
        paper_payload = self.client.get_paper(source)
        source_type = paper_payload.get("source_type")
        warnings = list(paper_payload.get("warnings", []))

        source_kind = None
        if source_type == "latex":
            source_kind = "arxiv_latex"
        elif source_type == "pdf":
            source_kind = "arxiv_pdf"
        else:
            warnings.append(f"Unsupported arXiv source type: {source_type}")
            return ProviderResult(
                success=False,
                title=paper_payload.get("title"),
                paper_id=paper_payload.get("arxiv_id"),
                raw_text=paper_payload.get("content"),
                warnings=warnings,
                fallback_used=paper_payload.get("fallback_used", False),
                fallback_reason=paper_payload.get("fallback_reason"),
            )

        equations: list[EvidenceEquation] = []
        bibliography: list[EvidenceBibliographyEntry] = []
        default_provenance = "latex" if source_kind == "arxiv_latex" else "pdf"

        if hasattr(self.client, "extract_equations"):
            try:
                equations = [
                    EvidenceEquation(
                        equation_id=equation_payload["equation_id"],
                        latex=equation_payload["latex"],
                        provenance=default_provenance,
                        section_name=equation_payload.get("section_context"),
                    )
                    for equation_payload in self.client.extract_equations(source)
                ]
            except Exception as exc:  # pragma: no cover - defensive adapter path
                warnings.append(f"Equation extraction failed: {exc}")

        if hasattr(self.client, "get_bibliography"):
            try:
                bibliography_payload = self.client.get_bibliography(source)
                bibliography_entries = (
                    bibliography_payload.get("entries", [])
                    if isinstance(bibliography_payload, dict)
                    else bibliography_payload
                )
                bibliography = [
                    EvidenceBibliographyEntry(
                        key=entry["key"],
                        citation=entry["citation"],
                        provenance=default_provenance,
                    )
                    for entry in bibliography_entries
                ]
            except Exception as exc:  # pragma: no cover - defensive adapter path
                warnings.append(f"Bibliography extraction failed: {exc}")

        return ProviderResult(
            success=bool(paper_payload.get("content")),
            source_kind=source_kind,
            title=paper_payload.get("title"),
            paper_id=paper_payload.get("arxiv_id"),
            raw_text=paper_payload.get("content"),
            equations=equations,
            bibliography=bibliography,
            warnings=warnings,
            fallback_used=paper_payload.get("fallback_used", False),
            fallback_reason=paper_payload.get("fallback_reason"),
        )
