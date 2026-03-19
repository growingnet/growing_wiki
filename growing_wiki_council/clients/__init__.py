"""Client contracts for external council integrations."""

from growing_wiki_council.clients.arxiv_client import (
    ArxivClientError,
    ArxivPaperClientProtocol,
)
from growing_wiki_council.clients.openrouter_client import OpenRouterClaimExtractorClient

__all__ = [
    "ArxivClientError",
    "ArxivPaperClientProtocol",
    "OpenRouterClaimExtractorClient",
]
