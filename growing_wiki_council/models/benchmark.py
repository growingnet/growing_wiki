"""Benchmark dataset models for real-paper claim extraction."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field

BenchmarkSourceType = Literal["arxiv_id", "arxiv_pdf_path", "pdf_path"]


class BenchmarkEntry(BaseModel):
    """One paper entry in the real-paper benchmark manifest."""

    paper_id: str
    source_type: BenchmarkSourceType
    source: str
    title: str | None = None
    notes: str | None = None
    tags: list[str] = Field(default_factory=list)


class BenchmarkDataset(BaseModel):
    """Validated benchmark manifest for a small set of papers."""

    dataset_name: str
    entries: list[BenchmarkEntry] = Field(default_factory=list)

    @classmethod
    def load(cls, manifest_path: Path) -> "BenchmarkDataset":
        """Load and validate a benchmark manifest from JSON."""
        manifest_payload = json.loads(manifest_path.read_text(encoding="utf-8"))
        return cls.model_validate(manifest_payload)
