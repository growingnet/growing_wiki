"""Artifact writing helpers for council outputs."""

from __future__ import annotations

import json
from pathlib import Path

from growing_wiki_council.models.calibration import SchemaCalibrationResult
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
