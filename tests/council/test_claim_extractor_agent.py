from growing_wiki_council.agents import ClaimExtractorAgent
from growing_wiki_council.config import CouncilConfig
from growing_wiki_council.models.evidence import EvidenceBundle


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


def test_claim_extractor_prompt_requires_reviewer_report_json_shape() -> None:
    """The prompt spells out the required reviewer-report JSON contract."""
    bundle = EvidenceBundle(
        paper_id="paper-1",
        source_kind="generic_pdf",
        title="Paper",
        sections=[],
        equations=[],
        bibliography=[],
        warnings=[],
        extraction_confidence="medium",
    )
    agent = ClaimExtractorAgent(
        config=CouncilConfig(
            openrouter_api_key="test-key",
            claim_extractor_model="openrouter/openai/gpt-4.1-mini",
        ),
        model_backend=object(),
    )

    prompt = agent._build_prompt(bundle)

    assert '"summary": "Short summary here."' in prompt
    assert '"role": "claim_extractor"' in prompt
    assert "Return JSON only." in prompt
