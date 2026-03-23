"""CLI entrypoints for the Growing Wiki council."""

from __future__ import annotations

from pathlib import Path

from growing_wiki_council.artifacts import (
    write_review_artifacts,
    write_schema_calibration_artifacts,
)
from growing_wiki_council.services.multi_model_schema_calibration import (
    run_multi_model_schema_calibration,
)
from growing_wiki_council.services.claim_extraction_benchmark import (
    run_claim_extraction_benchmark,
)
from growing_wiki_council.services.schema_calibration import run_schema_calibration
from growing_wiki_council.services.vertical_slice import run_claim_extraction_slice

__all__ = [
    "main",
    "run_claim_extraction_benchmark_once",
    "run_multi_model_schema_calibration_once",
    "run_schema_calibration_once",
    "run_vertical_slice",
    "write_review_artifacts",
]


def run_vertical_slice(
    *,
    source: str,
    provider,
    claim_extractor,
    output_dir: Path,
):
    """Delegate a single-paper claim-extraction run to the slice service."""
    return run_claim_extraction_slice(
        source=source,
        provider=provider,
        claim_extractor=claim_extractor,
        output_dir=output_dir,
    )


def run_schema_calibration_once(
    *,
    claim_extractor,
    output_dir: Path,
    run_label: str,
):
    """Execute one schema-calibration run and persist its artifacts."""
    result = run_schema_calibration(
        claim_extractor=claim_extractor,
        run_label=run_label,
    )
    write_schema_calibration_artifacts(output_dir, result)
    return result


def run_multi_model_schema_calibration_once(
    *,
    config,
    output_dir: Path,
    run_label: str,
    agent_factory=None,
):
    """Execute schema calibration once per configured model ID."""
    return run_multi_model_schema_calibration(
        config=config,
        output_dir=output_dir,
        run_label=run_label,
        agent_factory=agent_factory,
    )


def run_claim_extraction_benchmark_once(
    *,
    config,
    dataset_path: Path,
    output_dir: Path,
    run_label: str,
    provider_factory=None,
    claim_extractor_factory=None,
    model_ids=None,
    profile_ids=None,
):
    """Execute the real-paper claim benchmark and persist its artifacts."""
    return run_claim_extraction_benchmark(
        config=config,
        dataset_path=dataset_path,
        output_dir=output_dir,
        run_label=run_label,
        provider_factory=provider_factory,
        claim_extractor_factory=claim_extractor_factory,
        model_ids=model_ids,
        profile_ids=profile_ids,
    )


def main() -> None:
    """Placeholder CLI entrypoint until provider wiring is added."""
    raise SystemExit("CLI execution is not implemented yet.")
