"""Services for running the real-paper claim-extraction benchmark."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from pydantic import BaseModel, Field

from growing_wiki_council.agents import ClaimExtractorAgent
from growing_wiki_council.artifacts import (
    write_benchmark_run_artifacts,
    write_benchmark_run_summary,
)
from growing_wiki_council.config import CouncilConfig
from growing_wiki_council.models.benchmark import BenchmarkDataset, BenchmarkEntry
from growing_wiki_council.models.benchmark_run import (
    BenchmarkPaperRun,
    BenchmarkRunSummary,
)
from growing_wiki_council.models.review import ReviewerReport
from growing_wiki_council.providers.pdf import GenericPdfProvider
from growing_wiki_council.services.benchmark_paths import (
    benchmark_paper_output_dir,
    benchmark_run_output_dir,
)
from growing_wiki_council.services.benchmark_sources import (
    ResolvedBenchmarkSource,
    resolve_benchmark_source,
)
from growing_wiki_council.services.evidence_builder import EvidenceBuilder


class ClaimExtractionBenchmarkResult(BaseModel):
    """Top-level result for a benchmark run across one or more models."""

    run_label: str
    model_runs: list[BenchmarkRunSummary] = Field(default_factory=list)


class UnsupportedArxivBenchmarkProvider:
    """Raise a clear error when no arXiv benchmark provider is injected."""

    def load(self, source: str) -> Any:
        """Explain how to enable arXiv-backed benchmark entries."""
        raise RuntimeError(
            "ArXiv benchmark sources require an injected provider_factory."
        )


def run_claim_extraction_benchmark(
    *,
    config: CouncilConfig,
    dataset_path: Path,
    output_dir: Path,
    run_label: str,
    provider_factory: Callable[[BenchmarkEntry], ResolvedBenchmarkSource] | None = None,
    claim_extractor_factory: Callable[[str], Any] | None = None,
    model_ids: list[str] | None = None,
) -> ClaimExtractionBenchmarkResult:
    """Run the claim-extraction benchmark for the selected models."""
    dataset = BenchmarkDataset.load(dataset_path)
    selected_model_ids = model_ids or [config.benchmark_default_model_id]
    build_provider = provider_factory or _build_default_provider_factory()
    build_claim_extractor = claim_extractor_factory or (
        lambda model_id: _build_default_claim_extractor(
            config=config,
            model_id=model_id,
        )
    )
    model_runs: list[BenchmarkRunSummary] = []

    for model_id in selected_model_ids:
        paper_runs: list[BenchmarkPaperRun] = []
        claim_extractor = build_claim_extractor(model_id)

        for entry in dataset.entries:
            resolved_source = build_provider(entry)
            provider_result = resolved_source.provider.load(resolved_source.source)
            evidence_bundle = EvidenceBuilder().build(provider_result)
            raw_review_output = claim_extractor.run_raw(evidence_bundle)
            validated_report = ReviewerReport.model_validate(raw_review_output)
            paper_run = BenchmarkPaperRun(
                paper_id=entry.paper_id,
                run_label=run_label,
                model_id=model_id,
                benchmark_entry=entry.model_dump(mode="json"),
                provider_result=provider_result.model_dump(mode="json"),
                evidence_bundle=evidence_bundle.model_dump(mode="json"),
                raw_review_output=raw_review_output,
                validated_reviewer_report=validated_report.model_dump(mode="json"),
                summary_markdown=_build_summary_markdown(
                    paper_id=entry.paper_id,
                    model_id=model_id,
                    validated_report=validated_report,
                ),
            )
            write_benchmark_run_artifacts(
                output_dir=benchmark_paper_output_dir(
                    output_root=output_dir,
                    run_label=run_label,
                    model_id=model_id,
                    paper_id=entry.paper_id,
                ),
                paper_run=paper_run,
            )
            paper_runs.append(paper_run)

        run_summary = BenchmarkRunSummary(
            run_label=run_label,
            model_id=model_id,
            dataset_name=dataset.dataset_name,
            paper_runs=paper_runs,
            manifest_snapshot=dataset.model_dump(mode="json"),
        )
        write_benchmark_run_summary(
            output_dir=benchmark_run_output_dir(
                output_root=output_dir,
                run_label=run_label,
                model_id=model_id,
            ),
            run_summary=run_summary,
        )
        model_runs.append(run_summary)

    return ClaimExtractionBenchmarkResult(
        run_label=run_label,
        model_runs=model_runs,
    )


def _build_default_provider_factory() -> Callable[
    [BenchmarkEntry], ResolvedBenchmarkSource
]:
    """Build the default provider resolver for local benchmark runs."""
    pdf_provider = GenericPdfProvider()
    arxiv_provider = UnsupportedArxivBenchmarkProvider()

    def resolve_entry(entry: BenchmarkEntry) -> ResolvedBenchmarkSource:
        """Resolve one benchmark entry to its provider and source."""
        return resolve_benchmark_source(
            entry=entry,
            arxiv_provider=arxiv_provider,
            pdf_provider=pdf_provider,
        )

    return resolve_entry


def _build_default_claim_extractor(
    *,
    config: CouncilConfig,
    model_id: str,
) -> ClaimExtractorAgent:
    """Build the default claim extractor for one benchmark model."""
    return ClaimExtractorAgent(
        config=config.model_copy(update={"claim_extractor_model": model_id}),
    )


def _build_summary_markdown(
    *,
    paper_id: str,
    model_id: str,
    validated_report: ReviewerReport,
) -> str:
    """Build a short markdown summary for one paper benchmark run."""
    return (
        f"# Claim Extraction Benchmark\n\n"
        f"- paper_id: {paper_id}\n"
        f"- model_id: {model_id}\n"
        f"- summary: {validated_report.summary}\n"
    )
