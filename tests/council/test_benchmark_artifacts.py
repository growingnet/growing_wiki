from pathlib import Path

from growing_wiki_council.artifacts import (
    write_benchmark_run_artifacts,
    write_benchmark_run_summary,
)
from growing_wiki_council.models.benchmark_run import (
    BenchmarkPaperRun,
    BenchmarkRunSummary,
)
from growing_wiki_council.services.benchmark_paths import (
    benchmark_paper_output_dir,
    benchmark_run_output_dir,
)


def test_benchmark_paths_are_deterministic() -> None:
    """Benchmark artifact paths should be stable and model-slug based."""
    run_output_dir = benchmark_run_output_dir(
        output_root=Path("artifacts"),
        run_label="benchmark-run",
        profile_label="baseline",
        model_id="nvidia/nemotron-3-super-120b-a12b:free",
    )

    paper_output_dir = benchmark_paper_output_dir(
        output_root=Path("artifacts"),
        run_label="benchmark-run",
        profile_label="baseline",
        model_id="nvidia/nemotron-3-super-120b-a12b:free",
        paper_id="paper-1",
    )

    assert run_output_dir == Path(
        "artifacts/claim-extraction-benchmark/benchmark-run/baseline/nvidia-nemotron-3-super-120b-a12b-free"
    )
    assert paper_output_dir == run_output_dir / "paper-1"


def test_benchmark_artifact_writers_persist_expected_files(tmp_path: Path) -> None:
    """Benchmark artifact writers should emit the per-paper and run-level files."""
    paper_output_dir = tmp_path / "artifacts"
    paper_run = BenchmarkPaperRun(
        paper_id="paper-1",
        run_label="benchmark-run",
        profile_label="baseline",
        model_id="nvidia/nemotron-3-super-120b-a12b:free",
        status="completed",
        benchmark_entry={"paper_id": "paper-1"},
        provider_result={"success": True},
        evidence_bundle={"paper_id": "paper-1"},
        raw_review_output={"role": "claim_extractor"},
        validated_reviewer_report={
            "role": "claim_extractor",
            "summary": "ok",
            "findings": [],
            "claims": [],
            "open_questions": [],
        },
        summary_markdown="# Summary",
    )
    run_summary = BenchmarkRunSummary(
        run_label="benchmark-run",
        profile_label="baseline",
        model_id="nvidia/nemotron-3-super-120b-a12b:free",
        dataset_name="real-paper-benchmark",
        paper_runs=[paper_run],
        completed_paper_count=1,
    )

    write_benchmark_run_artifacts(output_dir=paper_output_dir, paper_run=paper_run)
    write_benchmark_run_summary(output_dir=paper_output_dir, run_summary=run_summary)

    assert (paper_output_dir / "benchmark-entry.json").exists()
    assert (paper_output_dir / "provider-result.json").exists()
    assert (paper_output_dir / "evidence-bundle.json").exists()
    assert (paper_output_dir / "raw-reviewer-output.json").exists()
    assert (paper_output_dir / "validated-reviewer-report.json").exists()
    assert (paper_output_dir / "summary.md").exists()
    assert (paper_output_dir / "human-eval.template.json").exists()
    assert (paper_output_dir / "manifest.snapshot.json").exists()
    assert (paper_output_dir / "run-summary.json").exists()
