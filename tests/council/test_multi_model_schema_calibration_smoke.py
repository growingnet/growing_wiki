from pathlib import Path

from growing_wiki_council.cli import run_multi_model_schema_calibration_once
from growing_wiki_council.config import CouncilConfig


class FakeAgent:
    """Return a schema-valid reviewer payload tagged by model ID."""

    def __init__(self, model_id: str) -> None:
        self.model_id = model_id

    def run(self, bundle):
        return {
            "role": "claim_extractor",
            "summary": self.model_id,
            "findings": [],
            "claims": [{"claim": "A", "evidence_refs": ["section:full_text"]}],
        }


def test_multi_model_schema_calibration_smoke(tmp_path: Path) -> None:
    """The multi-model calibration flow emits one artifact directory per model."""
    config = CouncilConfig(
        openrouter_api_key="test-key",
        claim_extractor_model="unused",
        calibration_model_ids=["model-a", "model-b"],
    )

    result = run_multi_model_schema_calibration_once(
        config=config,
        output_dir=tmp_path,
        run_label="schema-calibration",
        agent_factory=lambda model_id: FakeAgent(model_id),
    )

    assert len(result.model_runs) == 2
    assert (tmp_path / "model-a" / "calibration.json").exists()
    assert (tmp_path / "model-b" / "calibration.json").exists()
