from growing_wiki_council.models.calibration import SchemaCalibrationResult


def test_schema_calibration_result_tracks_validation_state() -> None:
    """Calibration results preserve validation and raw-response state."""
    result = SchemaCalibrationResult(
        success=True,
        run_label="schema-calibration",
        validation_error=None,
        raw_response={"role": "claim_extractor"},
    )

    assert result.success is True
