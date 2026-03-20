from pathlib import Path

from growing_wiki_council.artifacts import write_schema_calibration_artifacts
from growing_wiki_council.models.calibration import SchemaCalibrationResult


def test_write_schema_calibration_artifacts_creates_debug_output(
    tmp_path: Path,
) -> None:
    """Calibration artifacts include the validation summary and raw response."""
    result = SchemaCalibrationResult(
        success=True,
        run_label="schema-calibration",
        validation_error=None,
        raw_response={"role": "claim_extractor"},
        validated_report=None,
    )
    output_dir = tmp_path / "calibration"

    write_schema_calibration_artifacts(output_dir, result)

    assert (output_dir / "calibration.json").exists()
    assert (output_dir / "raw-response.json").exists()
