from growing_wiki_council.config import CouncilConfig
from growing_wiki_council.services.calibration_agents import (
    build_calibration_claim_extractor,
)


def test_build_calibration_claim_extractor_overrides_model_id() -> None:
    """Calibration agent factory swaps only the model ID."""
    config = CouncilConfig(
        openrouter_api_key="test-key",
        claim_extractor_model="model-a",
    )

    agent = build_calibration_claim_extractor(
        config=config,
        model_id="model-b",
        model_backend=object(),
    )

    assert agent.config.claim_extractor_model == "model-b"
