from growing_wiki_council.agents import ClaimExtractorAgent
from growing_wiki_council.config import CouncilConfig
from growing_wiki_council.models.evidence import EvidenceBundle


class FakeGateway:
    """Fake OpenRouter-compatible gateway for the claim extractor."""

    def run_prompt(self, prompt: str) -> dict:
        return {
            "role": "claim_extractor",
            "summary": "Claims extracted.",
            "findings": [],
            "claims": [{"claim": "A", "evidence_refs": ["section:full_text"]}],
        }


def test_claim_extractor_agent_returns_reviewer_report() -> None:
    """The claim extractor returns a validated reviewer report."""
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
            openrouter_base_url="https://openrouter.ai/api/v1",
            claim_extractor_model="openrouter/openai/gpt-4.1-mini",
        ),
        model_backend=FakeGateway(),
    )

    report = agent.run(bundle)

    assert report.role == "claim_extractor"
