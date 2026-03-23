"""Client contracts for arXiv-backed evidence retrieval."""

from typing import Any, Protocol


class ArxivClientError(RuntimeError):
    """Raised when the injected arXiv client cannot complete a request."""


class ArxivPaperClientProtocol(Protocol):
    """Protocol consumed by the council arXiv adapter."""

    def get_paper(self, arxiv_id: str) -> dict[str, Any]:
        """Return the core paper payload for an arXiv identifier."""

    def extract_equations(self, arxiv_id: str) -> list[dict[str, Any]]:
        """Return extracted equations for an arXiv identifier."""

    def get_bibliography(self, arxiv_id: str) -> list[dict[str, Any]] | dict[str, Any]:
        """Return bibliography data for an arXiv identifier."""
