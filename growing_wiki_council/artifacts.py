"""Artifact writing helpers for council outputs."""

from __future__ import annotations

import json
from pathlib import Path

from growing_wiki_council.models.calibration import SchemaCalibrationResult
from growing_wiki_council.models.benchmark_run import (
    BenchmarkPaperRun,
    BenchmarkRunSummary,
)
from growing_wiki_council.models.human_eval import HumanEvaluationTemplate


def write_review_artifacts(
    output_dir: Path,
    *,
    review_json: dict,
    review_markdown: str,
) -> None:
    """Persist council review artifacts to disk."""
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "review.json").write_text(
        json.dumps(review_json, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (output_dir / "review.md").write_text(review_markdown, encoding="utf-8")


def write_schema_calibration_artifacts(
    output_dir: Path,
    result: SchemaCalibrationResult,
) -> None:
    """Persist schema-calibration outputs to disk."""
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "calibration.json").write_text(
        json.dumps(result.model_dump(mode="json"), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (output_dir / "raw-response.json").write_text(
        json.dumps(result.raw_response, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    if result.validated_report is not None:
        (output_dir / "validated-report.json").write_text(
            json.dumps(
                result.validated_report.model_dump(mode="json"),
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )


def write_human_eval_template(
    output_path: Path,
    template: HumanEvaluationTemplate,
) -> None:
    """Persist a human-evaluation template as deterministic JSON."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(template.model_dump(mode="json"), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def write_benchmark_run_artifacts(
    *,
    output_dir: Path,
    paper_run: BenchmarkPaperRun,
) -> None:
    """Persist the per-paper benchmark artifacts to disk."""
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "benchmark-entry.json").write_text(
        json.dumps(paper_run.benchmark_entry, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (output_dir / "provider-result.json").write_text(
        json.dumps(paper_run.provider_result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (output_dir / "evidence-bundle.json").write_text(
        json.dumps(paper_run.evidence_bundle, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (output_dir / "raw-reviewer-output.json").write_text(
        json.dumps(paper_run.raw_review_output, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (output_dir / "validated-reviewer-report.json").write_text(
        json.dumps(
            paper_run.validated_reviewer_report,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    (output_dir / "summary.md").write_text(
        paper_run.summary_markdown,
        encoding="utf-8",
    )
    write_human_eval_template(
        output_dir / "human-eval.template.json",
        HumanEvaluationTemplate(
            paper_id=paper_run.paper_id,
            run_label=paper_run.run_label,
            model_id=paper_run.model_id,
        ),
    )


def write_benchmark_run_summary(
    *,
    output_dir: Path,
    run_summary: BenchmarkRunSummary,
) -> None:
    """Persist benchmark run-level summary artifacts to disk."""
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "manifest.snapshot.json").write_text(
        json.dumps(run_summary.manifest_snapshot, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (output_dir / "run-summary.json").write_text(
        json.dumps(run_summary.model_dump(mode="json"), indent=2, sort_keys=True)
        + "\n",
        encoding="utf-8",
    )
