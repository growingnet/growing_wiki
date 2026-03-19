from growing_wiki_council.providers.arxiv import ArxivLatexProvider


class FakeArxivClient:
    """Minimal fake MCP-shaped client for adapter testing."""

    def get_paper(self, arxiv_id: str) -> dict:
        return {
            "arxiv_id": arxiv_id,
            "title": "Sample",
            "content": "content",
            "source_type": "latex",
            "fallback_used": False,
            "fallback_reason": None,
            "warnings": [],
        }


def test_arxiv_provider_maps_mcp_response() -> None:
    """The adapter maps MCP-shaped paper payloads into provider results."""
    provider = ArxivLatexProvider(client=FakeArxivClient())

    result = provider.load("1234.56789")

    assert result.success is True
    assert result.source_kind == "arxiv_latex"
