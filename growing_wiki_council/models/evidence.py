"""Evidence models for normalized paper review inputs."""

from pydantic import BaseModel, Field
from typing import Literal

EvidenceProvenance = Literal["latex", "pdf", "metadata", "manual", "unknown"]
EvidenceSourceKind = Literal["arxiv_latex", "arxiv_pdf", "generic_pdf"]
ExtractionConfidence = Literal["high", "medium", "low"]


class EvidenceMetadata(BaseModel):
    """Canonical identifiers and metadata for a reviewed paper."""

    title: str
    paper_id: str | None = None
    doi: str | None = None
    arxiv_id: str | None = None
    authors: list[str] = Field(default_factory=list)
    venue: str | None = None
    published_at: str | None = None


class EvidenceSection(BaseModel):
    """A normalized section with explicit provenance."""

    name: str
    content: str
    provenance: EvidenceProvenance


class EvidenceEquation(BaseModel):
    """A normalized equation extracted from a paper."""

    equation_id: str
    latex: str
    provenance: EvidenceProvenance
    section_name: str | None = None


class EvidenceBibliographyEntry(BaseModel):
    """A bibliography entry with provenance."""

    key: str
    citation: str
    provenance: EvidenceProvenance


class EvidenceBundle(BaseModel):
    """Shared evidence object consumed by reviewer agents."""

    paper_id: str
    source_kind: EvidenceSourceKind
    title: str
    metadata: EvidenceMetadata | None = None
    sections: list[EvidenceSection] = Field(default_factory=list)
    equations: list[EvidenceEquation] = Field(default_factory=list)
    bibliography: list[EvidenceBibliographyEntry] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    extraction_confidence: ExtractionConfidence
