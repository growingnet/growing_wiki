"""Structured models for schema calibration artifacts."""

from typing import Any

from pydantic import BaseModel

from growing_wiki_council.models.review import ReviewerReport


class SchemaCalibrationResult(BaseModel):
    """Track schema-validation state for a live calibration run."""

    success: bool
    run_label: str
    validation_error: str | None = None
    raw_response: dict[str, Any] | list[Any] | str | None = None
    validated_report: ReviewerReport | None = None
