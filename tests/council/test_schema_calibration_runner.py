from growing_wiki_council.services.schema_calibration import (
    run_schema_calibration,
)
from growing_wiki_council.agents import ClaimExtractorAgent
from growing_wiki_council.config import CouncilConfig


class FakeAgent:
    """Return a schema-valid reviewer payload."""

    def run(self, bundle):
        return {
            "role": "claim_extractor",
            "summary": "Claims extracted.",
            "findings": [],
            "claims": [{"claim": "A", "evidence_refs": ["section:full_text"]}],
        }


def test_schema_calibration_runner_returns_success_for_valid_payload() -> None:
    """Calibration succeeds when the reviewer payload validates."""
    result = run_schema_calibration(
        claim_extractor=FakeAgent(),
        run_label="schema-calibration",
    )

    assert result.success is True
    assert result.validated_report is not None


class InvalidGateway:
    """Return a payload that fails reviewer-schema validation."""

    def run_prompt(self, prompt: str) -> dict:
        return {"paper_id": "schema-calibration-paper"}


def test_schema_calibration_runner_captures_agent_validation_failures() -> None:
    """Calibration records schema failures instead of raising from the agent."""
    agent = ClaimExtractorAgent(
        config=CouncilConfig(
            openrouter_api_key="test-key",
            claim_extractor_model="openrouter/openai/gpt-4.1-mini",
        ),
        model_backend=InvalidGateway(),
    )

    result = run_schema_calibration(
        claim_extractor=agent,
        run_label="schema-calibration",
    )

    assert result.success is False
    assert result.validation_error is not None
