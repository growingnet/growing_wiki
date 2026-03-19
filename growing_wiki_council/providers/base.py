"""Base contracts for evidence providers."""

from pathlib import Path
from typing import Protocol

from pydantic import BaseModel, Field

from growing_wiki_council.models.evidence import (
    EvidenceBibliographyEntry,
    EvidenceEquation,
    EvidenceSection,
    EvidenceSourceKind,
)


class ProviderResult(BaseModel):
    """Provider output before evidence normalization."""

    success: bool
    source_kind: EvidenceSourceKind | None = None
    title: str | None = None
    paper_id: str | None = None
    raw_text: str | None = None
    sections: list[EvidenceSection] = Field(default_factory=list)
    equations: list[EvidenceEquation] = Field(default_factory=list)
    bibliography: list[EvidenceBibliographyEntry] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    fallback_used: bool = False
    fallback_reason: str | None = None


class EvidenceProvider(Protocol):
    """Contract for provider adapters that load raw paper evidence."""

    def load(self, source: Path | str) -> ProviderResult:
        """Load provider-specific input into a provider result."""
