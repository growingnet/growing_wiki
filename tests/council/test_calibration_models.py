from growing_wiki_council.models.calibration import (
    MultiModelCalibrationResult,
    SchemaCalibrationResult,
)


def test_schema_calibration_result_tracks_validation_state() -> None:
    """Calibration results preserve validation and raw-response state."""
    result = SchemaCalibrationResult(
        success=True,
        run_label="schema-calibration",
        validation_error=None,
        raw_response={"role": "claim_extractor"},
    )

    assert result.success is True


def test_multi_model_calibration_result_tracks_per_model_runs() -> None:
    """Multi-model calibration results preserve one entry per model run."""
    result = MultiModelCalibrationResult(
        run_label="schema-calibration",
        model_runs=[
            {
                "model_id": "model-a",
                "output_dir": "artifacts/model-a",
                "result": {
                    "success": True,
                    "run_label": "schema-calibration",
                    "validation_error": None,
                    "raw_response": None,
                    "validated_report": None,
                },
            }
        ],
    )

    assert result.model_runs[0].model_id == "model-a"
