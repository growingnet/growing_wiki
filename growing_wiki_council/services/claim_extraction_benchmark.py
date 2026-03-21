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
from growing_wiki_council.models.review_profiles import WebsiteAlignedReviewerReport
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
    claim_extractor_factory: Callable[[str, str], Any] | None = None,
    model_ids: list[str] | None = None,
    profile_ids: list[str] | None = None,
) -> ClaimExtractionBenchmarkResult:
    """Run the claim-extraction benchmark for the selected models."""
    dataset = BenchmarkDataset.load(dataset_path)
    selected_model_ids = model_ids or [config.benchmark_default_model_id]
    selected_profile_ids = profile_ids or ["baseline"]
    build_provider = provider_factory or _build_default_provider_factory()
    build_claim_extractor = claim_extractor_factory or (
        lambda model_id, profile_id: _build_default_claim_extractor(
            config=config,
            model_id=model_id,
            profile_id=profile_id,
        )
    )
    model_runs: list[BenchmarkRunSummary] = []

    for model_id in selected_model_ids:
        for profile_id in selected_profile_ids:
            paper_runs: list[BenchmarkPaperRun] = []
            claim_extractor = build_claim_extractor(model_id, profile_id)

            for entry in dataset.entries:
                paper_run = _run_benchmark_entry(
                    entry=entry,
                    model_id=model_id,
                    profile_id=profile_id,
                    run_label=run_label,
                    build_provider=build_provider,
                    claim_extractor=claim_extractor,
                )
                write_benchmark_run_artifacts(
                    output_dir=benchmark_paper_output_dir(
                        output_root=output_dir,
                        run_label=run_label,
                        profile_label=profile_id,
                        model_id=model_id,
                        paper_id=entry.paper_id,
                    ),
                    paper_run=paper_run,
                )
                paper_runs.append(paper_run)

            run_summary = BenchmarkRunSummary(
                run_label=run_label,
                profile_label=profile_id,
                model_id=model_id,
                dataset_name=dataset.dataset_name,
                paper_runs=paper_runs,
                manifest_snapshot=dataset.model_dump(mode="json"),
                completed_paper_count=sum(
                    paper_run.status == "completed" for paper_run in paper_runs
                ),
                failed_paper_count=sum(
                    paper_run.status == "failed" for paper_run in paper_runs
                ),
            )
            write_benchmark_run_summary(
                output_dir=benchmark_run_output_dir(
                    output_root=output_dir,
                    run_label=run_label,
                    profile_label=profile_id,
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
    profile_id: str,
) -> ClaimExtractorAgent:
    """Build the default claim extractor for one benchmark model."""
    return ClaimExtractorAgent(
        config=config.model_copy(update={"claim_extractor_model": model_id}),
        benchmark_profile_id=profile_id,
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


def _run_benchmark_entry(
    *,
    entry: BenchmarkEntry,
    model_id: str,
    profile_id: str,
    run_label: str,
    build_provider: Callable[[BenchmarkEntry], ResolvedBenchmarkSource],
    claim_extractor: Any,
) -> BenchmarkPaperRun:
    """Run one benchmark entry and capture either success or failure artifacts."""
    benchmark_entry = entry.model_dump(mode="json")
    provider_result: dict[str, Any] = {}
    evidence_bundle: dict[str, Any] = {}
    raw_review_output: dict[str, Any] = {}

    try:
        resolved_source = build_provider(entry)
        loaded_provider_result = resolved_source.provider.load(resolved_source.source)
        provider_result = loaded_provider_result.model_dump(mode="json")
        if not provider_result.get("paper_id"):
            provider_result["paper_id"] = entry.paper_id
        if not loaded_provider_result.success:
            return BenchmarkPaperRun(
                paper_id=entry.paper_id,
                run_label=run_label,
                profile_label=profile_id,
                model_id=model_id,
                status="failed",
                benchmark_entry=benchmark_entry,
                provider_result=provider_result,
                evidence_bundle=evidence_bundle,
                raw_review_output=raw_review_output,
                validated_reviewer_report={},
                summary_markdown=_build_failure_summary_markdown(
                    paper_id=entry.paper_id,
                    model_id=model_id,
                    error_kind="ProviderWarning",
                    error_message=f"Provider failed to load source: {loaded_provider_result.warnings}",
                ),
                error_type="ProviderWarning",
                error_message=f"Provider failed to load source: {loaded_provider_result.warnings}",
            )
        loaded_evidence_bundle = (
            EvidenceBuilder()
            .build(loaded_provider_result)
            .model_copy(update={"paper_id": entry.paper_id})
        )
        evidence_bundle = loaded_evidence_bundle.model_dump(mode="json")
        raw_review_output = claim_extractor.run_raw(loaded_evidence_bundle)
        validated_report = _reviewer_report_model_for_profile(
            profile_id
        ).model_validate(raw_review_output)
        return BenchmarkPaperRun(
            paper_id=entry.paper_id,
            run_label=run_label,
            profile_label=profile_id,
            model_id=model_id,
            status="completed",
            benchmark_entry=benchmark_entry,
            provider_result=provider_result,
            evidence_bundle=evidence_bundle,
            raw_review_output=raw_review_output,
            validated_reviewer_report=validated_report.model_dump(mode="json"),
            summary_markdown=_build_summary_markdown(
                paper_id=entry.paper_id,
                model_id=model_id,
                validated_report=validated_report,
            ),
        )
    except Exception as exc:
        error_kind, error_message = _normalize_error(exc)
        if provider_result:
            provider_result["success"] = False
            provider_result["warnings"] = provider_result.get("warnings", []) + [error_message]
        return BenchmarkPaperRun(
            paper_id=entry.paper_id,
            run_label=run_label,
            profile_label=profile_id,
            model_id=model_id,
            status="failed",
            benchmark_entry=benchmark_entry,
            provider_result=provider_result,
            evidence_bundle=evidence_bundle,
            raw_review_output=raw_review_output,
            validated_reviewer_report={},
            summary_markdown=_build_failure_summary_markdown(
                paper_id=entry.paper_id,
                model_id=model_id,
                error_kind=error_kind,
                error_message=error_message,
            ),
            error_type=error_kind,
            error_message=error_message,
        )


def _build_failure_summary_markdown(
    *,
    paper_id: str,
    model_id: str,
    error_kind: str,
    error_message: str,
) -> str:
    """Build a short markdown summary for one failed paper benchmark run."""
    return (
        f"# Claim Extraction Benchmark\n\n"
        f"- paper_id: {paper_id}\n"
        f"- model_id: {model_id}\n"
        f"- status: failed\n"
        f"- error_kind: {error_kind}\n"
        f"- error_message: {error_message}\n"
    )

def _normalize_error(exc: Exception) -> tuple[str, str]:
    """Map raw exceptions to deterministic error_kind and error_message strings."""
    msg = str(exc)
    error_kind = type(exc).__name__
    
    if "nodename nor servname" in msg or "Name or service not known" in msg or "getaddrinfo" in msg:
        return "dns_resolution_failure", "DNS resolution failed (normalized)"
    if "timeout" in msg.lower():
        return "network_timeout", "Network timeout (normalized)"
    if "Connection refused" in msg or "connect_tcp" in msg:
        return "connection_refused", "Connection refused (normalized)"
        
    return error_kind, msg


def _reviewer_report_model_for_profile(profile_id: str) -> type[ReviewerReport]:
    """Return the validation schema for one benchmark profile."""
    if profile_id == "website_aligned":
        return WebsiteAlignedReviewerReport
    return ReviewerReport
