from growing_wiki_council.clients.arxiv_client import ArxivPaperClientProtocol


def test_arxiv_client_protocol_exposes_required_methods() -> None:
    """The arXiv client protocol exposes the adapter-facing methods."""
    required_methods = ["get_paper", "extract_equations", "get_bibliography"]

    for method_name in required_methods:
        assert hasattr(ArxivPaperClientProtocol, method_name)
