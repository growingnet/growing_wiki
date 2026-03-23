from pathlib import Path

from growing_wiki_council.cli import run_schema_calibration_once


class FakeAgent:
    """Return a schema-valid reviewer payload."""

    def run(self, bundle):
        return {
            "role": "claim_extractor",
            "summary": "Claims extracted.",
            "findings": [],
            "claims": [{"claim": "A", "evidence_refs": ["section:full_text"]}],
        }


def test_run_schema_calibration_once_writes_outputs(tmp_path: Path) -> None:
    """The calibration entrypoint writes its output files."""
    output_dir = tmp_path / "calibration"

    result = run_schema_calibration_once(
        claim_extractor=FakeAgent(),
        output_dir=output_dir,
        run_label="schema-calibration",
    )

    assert result.success is True
    assert (output_dir / "calibration.json").exists()
