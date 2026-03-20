from growing_wiki_council.services.schema_calibration import (
    run_schema_calibration,
)


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
