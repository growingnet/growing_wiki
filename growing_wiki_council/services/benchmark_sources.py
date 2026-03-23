"""Source resolution helpers for the real-paper benchmark."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

from growing_wiki_council.models.benchmark import BenchmarkEntry

BenchmarkProviderKind = Literal["arxiv", "generic_pdf"]


@dataclass(frozen=True, slots=True)
class ResolvedBenchmarkSource:
    """A benchmark source paired with its selected provider."""

    provider_kind: BenchmarkProviderKind
    provider: Any
    source: str


def resolve_benchmark_source(
    *,
    entry: BenchmarkEntry,
    arxiv_provider: Any,
    pdf_provider: Any,
) -> ResolvedBenchmarkSource:
    """Select the provider for a benchmark entry and preserve its source."""
    if entry.source_type in {"arxiv_id", "arxiv_pdf_path"}:
        return ResolvedBenchmarkSource(
            provider_kind="arxiv",
            provider=arxiv_provider,
            source=entry.source,
        )

    if entry.source_type == "pdf_path":
        return ResolvedBenchmarkSource(
            provider_kind="generic_pdf",
            provider=pdf_provider,
            source=entry.source,
        )

    raise ValueError(f"Unsupported benchmark source type: {entry.source_type}")
