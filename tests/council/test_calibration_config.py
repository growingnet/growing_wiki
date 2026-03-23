from growing_wiki_council.config import CouncilConfig


def test_council_config_supports_schema_calibration_settings() -> None:
    """Council config includes the first live schema-calibration settings."""
    config = CouncilConfig(
        openrouter_api_key="test-key",
        openrouter_base_url="https://openrouter.ai/api/v1",
        claim_extractor_model="openrouter/openai/gpt-4.1-mini",
        calibration_run_label="schema-calibration",
        calibration_output_dir="artifacts/calibration",
    )

    assert config.calibration_run_label == "schema-calibration"
