from growing_wiki_council.providers.arxiv import ArxivLatexProvider


class FakeRealClient:
    """A fake client that returns richer payloads than the first adapter test."""

    def get_paper(self, arxiv_id: str) -> dict:
        return {
            "arxiv_id": arxiv_id,
            "title": "Sample",
            "content": "Sectioned text",
            "source_type": "pdf",
            "fallback_used": True,
            "fallback_reason": "201: No source available",
            "warnings": ["Used PDF fallback"],
        }

    def extract_equations(self, arxiv_id: str) -> list[dict]:
        return [{"equation_id": "eq_1", "latex": "x+y", "section_context": "Results"}]

    def get_bibliography(self, arxiv_id: str) -> dict:
        return {"entries": [{"key": "smith2024", "citation": "Smith et al. (2024)."}]}


def test_arxiv_provider_maps_real_client_payloads() -> None:
    """The adapter coerces real client payloads into schema models."""
    provider = ArxivLatexProvider(client=FakeRealClient())

    result = provider.load("1234.56789")

    assert result.source_kind == "arxiv_pdf"
    assert result.fallback_used is True
    assert result.equations[0].latex == "x+y"
    assert result.bibliography[0].key == "smith2024"
