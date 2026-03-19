from growing_wiki_council.config import CouncilConfig


def test_council_config_exposes_openrouter_model_defaults() -> None:
    """Council runtime config exposes the first real OpenRouter settings."""
    config = CouncilConfig(
        openrouter_api_key="test-key",
        openrouter_base_url="https://openrouter.ai/api/v1",
        claim_extractor_model="openrouter/openai/gpt-4.1-mini",
    )

    assert config.claim_extractor_model == "openrouter/openai/gpt-4.1-mini"
