from growing_wiki_council.config import CouncilConfig


def test_council_package_imports() -> None:
    """The council package exposes a minimal configuration model."""
    config = CouncilConfig(openrouter_api_key="test-key")

    assert config.openrouter_api_key == "test-key"
