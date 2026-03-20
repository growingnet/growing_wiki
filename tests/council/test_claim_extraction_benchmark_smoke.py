from pathlib import Path

from growing_wiki_council.config import CouncilConfig
from growing_wiki_council.services.claim_extraction_benchmark import (
    run_claim_extraction_benchmark,
)


class FakeClaimExtractor:
    """Return a schema-valid reviewer payload for the smoke benchmark."""

    def __init__(self, model_id: str) -> None:
        """Store the model identifier used for the smoke run."""
        self.model_id = model_id

    def run_raw(self, bundle) -> dict:
        """Return a deterministic claim-extraction payload."""
        return {
            "role": "claim_extractor",
            "summary": f"Claims extracted with {self.model_id}.",
            "findings": [],
            "claims": [
                {
                    "claim": "The paper studies growing neural networks.",
                    "evidence_refs": ["section:full_text"],
                    "confidence": "medium",
                }
            ],
            "open_questions": [],
        }


def test_claim_extraction_benchmark_smoke_writes_profile_outputs(
    tmp_path: Path,
) -> None:
    """The benchmark runner writes per-paper outputs for the committed dataset."""
    config = CouncilConfig(
        openrouter_api_key="test-key",
        claim_extractor_model="placeholder-model",
    )

    result = run_claim_extraction_benchmark(
        config=config,
        dataset_path=Path("growing_wiki_council/benchmarks/real_paper_benchmark.json"),
        output_dir=tmp_path / "artifacts",
        run_label="benchmark-smoke",
        profile_ids=["baseline", "website_aligned"],
        claim_extractor_factory=lambda model_id, profile_id: FakeClaimExtractor(
            model_id
        ),
    )

    assert len(result.model_runs) == 2
    assert {model_run.profile_label for model_run in result.model_runs} == {
        "baseline",
        "website_aligned",
    }
    assert all(len(model_run.paper_runs) == 5 for model_run in result.model_runs)
    assert (
        tmp_path
        / "artifacts"
        / "claim-extraction-benchmark"
        / "benchmark-smoke"
        / "baseline"
        / "nvidia-nemotron-3-super-120b-a12b-free"
        / "gradmax-2022"
        / "validated-reviewer-report.json"
    ).exists()
    assert (
        tmp_path
        / "artifacts"
        / "claim-extraction-benchmark"
        / "benchmark-smoke"
        / "website_aligned"
        / "nvidia-nemotron-3-super-120b-a12b-free"
        / "gradmax-2022"
        / "validated-reviewer-report.json"
    ).exists()
