from pathlib import Path

from growing_wiki_council.artifacts import write_schema_calibration_artifacts
from growing_wiki_council.services.schema_calibration import run_schema_calibration


class FakeClaimExtractor:
    """Return a schema-valid reviewer payload for smoke coverage."""

    def run(self, bundle):
        return {
            "role": "claim_extractor",
            "summary": "Claims extracted from the calibration bundle.",
            "findings": [],
            "claims": [{"claim": "A", "evidence_refs": ["section:full_text"]}],
        }


def test_schema_calibration_smoke(tmp_path: Path) -> None:
    """The calibration flow runs without network access and writes artifacts."""
    output_dir = tmp_path / "calibration"

    result = run_schema_calibration(
        claim_extractor=FakeClaimExtractor(),
        run_label="schema-calibration",
    )
    write_schema_calibration_artifacts(output_dir, result)

    assert result.success is True
    assert (output_dir / "calibration.json").exists()
    assert (output_dir / "raw-response.json").exists()
