"""Services for calibration runs across multiple pinned models."""

from pathlib import Path
from typing import Any, Callable

from growing_wiki_council.artifacts import write_schema_calibration_artifacts
from growing_wiki_council.config import CouncilConfig
from growing_wiki_council.models.calibration import (
    ModelCalibrationRun,
    MultiModelCalibrationResult,
)
from growing_wiki_council.services.calibration_agents import (
    build_calibration_claim_extractor,
)
from growing_wiki_council.services.model_slug import model_id_to_slug
from growing_wiki_council.services.schema_calibration import run_schema_calibration


def run_multi_model_schema_calibration(
    *,
    config: CouncilConfig,
    output_dir: Path,
    run_label: str,
    agent_factory: Callable[[str], Any] | None = None,
) -> MultiModelCalibrationResult:
    """Run schema calibration once per configured model ID."""
    model_runs: list[ModelCalibrationRun] = []

    for model_id in config.calibration_model_ids:
        claim_extractor = (
            agent_factory(model_id)
            if agent_factory is not None
            else build_calibration_claim_extractor(
                config=config,
                model_id=model_id,
            )
        )
        calibration_result = run_schema_calibration(
            claim_extractor=claim_extractor,
            run_label=run_label,
        )
        model_output_dir = output_dir / model_id_to_slug(model_id)
        write_schema_calibration_artifacts(model_output_dir, calibration_result)
        model_runs.append(
            ModelCalibrationRun(
                model_id=model_id,
                output_dir=str(model_output_dir),
                result=calibration_result,
            )
        )

    return MultiModelCalibrationResult(
        run_label=run_label,
        model_runs=model_runs,
    )
