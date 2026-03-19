"""Provider contracts for council evidence ingestion."""

from growing_wiki_council.providers.base import EvidenceProvider, ProviderResult
from growing_wiki_council.providers.pdf import GenericPdfProvider

__all__ = ["EvidenceProvider", "GenericPdfProvider", "ProviderResult"]
