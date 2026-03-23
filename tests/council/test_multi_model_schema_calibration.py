from pathlib import Path

from growing_wiki_council.config import CouncilConfig
from growing_wiki_council.services.multi_model_schema_calibration import (
    run_multi_model_schema_calibration,
)


class FakeAgent:
    """Return a schema-valid payload tagged by model ID."""

    def __init__(self, model_id: str) -> None:
        self.model_id = model_id

    def run(self, bundle):
        return {
            "role": "claim_extractor",
            "summary": self.model_id,
            "findings": [],
            "claims": [{"claim": "A", "evidence_refs": ["section:full_text"]}],
        }


def test_run_multi_model_schema_calibration_returns_one_result_per_model(
    tmp_path: Path,
) -> None:
    """The multi-model calibration service emits one result per model ID."""
    config = CouncilConfig(
        openrouter_api_key="test-key",
        claim_extractor_model="unused",
        calibration_model_ids=["model-a", "model-b"],
    )

    result = run_multi_model_schema_calibration(
        config=config,
        output_dir=tmp_path,
        run_label="schema-calibration",
        agent_factory=lambda model_id: FakeAgent(model_id),
    )

    assert len(result.model_runs) == 2
