"""Services for live schema calibration runs."""

from typing import Any

from pydantic import ValidationError

from growing_wiki_council.models.calibration import SchemaCalibrationResult
from growing_wiki_council.models.review import ReviewerReport
from growing_wiki_council.services.calibration_inputs import (
    build_schema_calibration_bundle,
)


def run_schema_calibration(
    *,
    claim_extractor: Any,
    run_label: str,
) -> SchemaCalibrationResult:
    """Run one schema-calibration pass against deterministic evidence."""
    evidence_bundle = build_schema_calibration_bundle()
    try:
        raw_response = _run_claim_extractor_raw(claim_extractor, evidence_bundle)
    except ValidationError as validation_error:
        return SchemaCalibrationResult(
            success=False,
            run_label=run_label,
            validation_error=str(validation_error),
            raw_response=None,
            validated_report=None,
        )

    try:
        validated_report = ReviewerReport.model_validate(raw_response)
    except ValidationError as validation_error:
        return SchemaCalibrationResult(
            success=False,
            run_label=run_label,
            validation_error=str(validation_error),
            raw_response=_extract_raw_response(raw_response),
            validated_report=None,
        )

    return SchemaCalibrationResult(
        success=True,
        run_label=run_label,
        validation_error=None,
        raw_response=_extract_raw_response(raw_response),
        validated_report=validated_report,
    )


def _extract_raw_response(raw_response: Any) -> dict[str, Any] | list[Any] | str | None:
    """Normalize raw calibration output into a JSON-friendly debug payload."""
    if isinstance(raw_response, dict):
        return raw_response.get("raw_response", raw_response)
    if isinstance(raw_response, (list, str)):
        return raw_response
    return None


def _run_claim_extractor_raw(claim_extractor: Any, evidence_bundle: Any) -> Any:
    """Use the raw extractor path when available, otherwise fall back to `run`."""
    if hasattr(claim_extractor, "run_raw"):
        return claim_extractor.run_raw(evidence_bundle)
    return claim_extractor.run(evidence_bundle)
