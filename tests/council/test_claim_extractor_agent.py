from growing_wiki_council.agents import ClaimExtractorAgent
from growing_wiki_council.config import CouncilConfig


def test_claim_extractor_agent_exposes_run_method() -> None:
    """The real claim extractor wrapper exposes the council agent contract."""
    agent = ClaimExtractorAgent(
        config=CouncilConfig(
            openrouter_api_key="test-key",
            openrouter_base_url="https://openrouter.ai/api/v1",
            claim_extractor_model="openrouter/openai/gpt-4.1-mini",
        ),
        model_backend=object(),
    )

    assert callable(agent.run)
