from pathlib import Path

from growing_wiki_council.config import CouncilConfig
from growing_wiki_council.models.benchmark import BenchmarkEntry
from growing_wiki_council.providers.base import ProviderResult
from growing_wiki_council.services.benchmark_sources import ResolvedBenchmarkSource
from growing_wiki_council.services.claim_extraction_benchmark import (
    run_claim_extraction_benchmark,
)


class FakeProvider:
    """Provide deterministic benchmark input for offline tests."""

    def load(self, source: str) -> ProviderResult:
        """Return a provider result with stable raw text."""
        return ProviderResult(
            success=True,
            source_kind="generic_pdf",
            paper_id="paper-1",
            title="Paper 1",
            raw_text=f"Growing networks benchmark text from {source}.",
            warnings=[],
        )


class FakeClaimExtractor:
    """Return a schema-valid reviewer payload for benchmark tests."""

    def __init__(self, model_id: str) -> None:
        """Store the model identifier used to build this extractor."""
        self.model_id = model_id

    def run_raw(self, bundle) -> dict:
        """Return a raw claim-extraction payload for the evidence bundle."""
        return {
            "role": "claim_extractor",
            "summary": f"Claims extracted with {self.model_id}.",
            "findings": [],
            "claims": [
                {
                    "claim": "Networks can grow during training.",
                    "evidence_refs": ["section:full_text"],
                    "confidence": "medium",
                }
            ],
            "open_questions": [],
        }


def write_manifest(manifest_path: Path) -> None:
    """Create a minimal benchmark manifest for service tests."""
    manifest_path.write_text(
        (
            "{\n"
            '  "dataset_name": "real-paper-benchmark",\n'
            '  "entries": [\n'
            '    {\n'
            '      "paper_id": "paper-1",\n'
            '      "source_type": "pdf_path",\n'
            '      "source": "tests/fixtures/pdfs/minimal-paper.pdf"\n'
            "    }\n"
            "  ]\n"
            "}\n"
        ),
        encoding="utf-8",
    )


def build_provider_resolution(entry: BenchmarkEntry) -> ResolvedBenchmarkSource:
    """Resolve every test entry to the fake PDF provider."""
    return ResolvedBenchmarkSource(
        provider_kind="generic_pdf",
        provider=FakeProvider(),
        source=entry.source,
    )


def test_claim_extraction_benchmark_defaults_to_frozen_baseline(
    tmp_path: Path,
) -> None:
    """The benchmark defaults to the frozen Nemotron baseline."""
    manifest_path = tmp_path / "benchmark.json"
    output_dir = tmp_path / "artifacts"
    selected_model_ids: list[str] = []
    write_manifest(manifest_path)
    config = CouncilConfig(
        openrouter_api_key="test-key",
        claim_extractor_model="some-other-model",
    )

    def build_claim_extractor(model_id: str) -> FakeClaimExtractor:
        selected_model_ids.append(model_id)
        return FakeClaimExtractor(model_id=model_id)

    result = run_claim_extraction_benchmark(
        config=config,
        dataset_path=manifest_path,
        output_dir=output_dir,
        run_label="benchmark-run",
        provider_factory=build_provider_resolution,
        claim_extractor_factory=build_claim_extractor,
        model_ids=None,
    )

    assert selected_model_ids == ["nvidia/nemotron-3-super-120b-a12b:free"]
    assert result.model_runs[0].model_id == "nvidia/nemotron-3-super-120b-a12b:free"
    assert (
        output_dir
        / "claim-extraction-benchmark"
        / "benchmark-run"
        / "nvidia-nemotron-3-super-120b-a12b-free"
        / "paper-1"
        / "validated-reviewer-report.json"
    ).exists()


def test_claim_extraction_benchmark_respects_explicit_model_override(
    tmp_path: Path,
) -> None:
    """The benchmark uses caller-supplied model overrides when provided."""
    manifest_path = tmp_path / "benchmark.json"
    output_dir = tmp_path / "artifacts"
    selected_model_ids: list[str] = []
    write_manifest(manifest_path)
    config = CouncilConfig(
        openrouter_api_key="test-key",
        claim_extractor_model="some-other-model",
    )

    def build_claim_extractor(model_id: str) -> FakeClaimExtractor:
        selected_model_ids.append(model_id)
        return FakeClaimExtractor(model_id=model_id)

    result = run_claim_extraction_benchmark(
        config=config,
        dataset_path=manifest_path,
        output_dir=output_dir,
        run_label="benchmark-run",
        provider_factory=build_provider_resolution,
        claim_extractor_factory=build_claim_extractor,
        model_ids=["example/model"],
    )

    assert selected_model_ids == ["example/model"]
    assert result.model_runs[0].model_id == "example/model"
