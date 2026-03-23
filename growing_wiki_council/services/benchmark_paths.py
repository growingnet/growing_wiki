"""Deterministic filesystem helpers for benchmark artifacts."""

from __future__ import annotations

from pathlib import Path

from growing_wiki_council.services.model_slug import model_id_to_slug


def benchmark_run_output_dir(
    *,
    output_root: Path,
    run_label: str,
    profile_label: str,
    model_id: str,
) -> Path:
    """Return the directory for a benchmark run and model combination."""
    return (
        output_root
        / "claim-extraction-benchmark"
        / run_label
        / profile_label
        / model_id_to_slug(model_id)
    )


def benchmark_paper_output_dir(
    *,
    output_root: Path,
    run_label: str,
    profile_label: str,
    model_id: str,
    paper_id: str,
) -> Path:
    """Return the directory for one paper inside a benchmark run."""
    return (
        benchmark_run_output_dir(
            output_root=output_root,
            run_label=run_label,
            profile_label=profile_label,
            model_id=model_id,
        )
        / paper_id
    )
