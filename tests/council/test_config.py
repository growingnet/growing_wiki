from growing_wiki_council.config import CouncilConfig


def test_council_config_exposes_openrouter_model_defaults() -> None:
    """Council runtime config exposes the first real OpenRouter settings."""
    config = CouncilConfig(
        openrouter_api_key="test-key",
        openrouter_base_url="https://openrouter.ai/api/v1",
        claim_extractor_model="openrouter/openai/gpt-4.1-mini",
    )

    assert config.claim_extractor_model == "openrouter/openai/gpt-4.1-mini"


def test_council_config_can_load_openrouter_key_from_environment(
    monkeypatch,
) -> None:
    """Live config construction can read the OpenRouter key from the environment."""
    monkeypatch.setenv("OPENROUTER_API_KEY", "env-test-key")

    config = CouncilConfig.from_env(
        claim_extractor_model="openrouter/openai/gpt-4.1-mini",
    )

    assert config.openrouter_api_key.get_secret_value() == "env-test-key"


def test_council_config_can_load_openrouter_key_from_dotenv(
    monkeypatch,
    tmp_path,
) -> None:
    """Live config construction can load the OpenRouter key from `.env`."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    (tmp_path / ".env").write_text("OPENROUTER_API_KEY=dotenv-test-key\n")

    config = CouncilConfig.from_env(
        claim_extractor_model="openrouter/openai/gpt-4.1-mini",
    )

    assert config.openrouter_api_key.get_secret_value() == "dotenv-test-key"


def test_council_config_exposes_multi_model_calibration_defaults() -> None:
    """Calibration defaults pin the first two comparison models."""
    config = CouncilConfig(
        openrouter_api_key="test-key",
        claim_extractor_model="openrouter/openai/gpt-4.1-mini",
    )

    assert config.calibration_model_ids == [
        "nvidia/nemotron-3-super-120b-a12b:free",
        "stepfun/step-3.5-flash:free",
    ]
