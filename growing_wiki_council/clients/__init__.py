"""Client contracts for external council integrations."""

from growing_wiki_council.clients.arxiv_client import (
    ArxivClientError,
    ArxivPaperClientProtocol,
)

__all__ = ["ArxivClientError", "ArxivPaperClientProtocol"]
