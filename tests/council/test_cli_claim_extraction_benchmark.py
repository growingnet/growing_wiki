from pathlib import Path

from growing_wiki_council.cli import run_claim_extraction_benchmark_once
from growing_wiki_council.config import CouncilConfig
from growing_wiki_council.models.benchmark import BenchmarkEntry
from growing_wiki_council.providers.base import ProviderResult
from growing_wiki_council.services.benchmark_sources import ResolvedBenchmarkSource


class FakeProvider:
    """Provide deterministic provider output for CLI benchmark tests."""

    def load(self, source: str) -> ProviderResult:
        """Return a provider result for the requested source."""
        return ProviderResult(
            success=True,
            source_kind="generic_pdf",
            paper_id="paper-1",
            title="Paper 1",
            raw_text=f"Growing networks benchmark text from {source}.",
            warnings=[],
        )


class FakeClaimExtractor:
    """Return a schema-valid raw reviewer payload."""

    def __init__(self, model_id: str) -> None:
        """Store the model identifier used for this extractor."""
        self.model_id = model_id

    def run_raw(self, bundle) -> dict:
        """Return a deterministic raw reviewer output."""
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
    """Create a minimal benchmark manifest for CLI tests."""
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
    """Resolve test benchmark entries to the fake provider."""
    return ResolvedBenchmarkSource(
        provider_kind="generic_pdf",
        provider=FakeProvider(),
        source=entry.source,
    )


def test_run_claim_extraction_benchmark_once_writes_outputs(tmp_path: Path) -> None:
    """The CLI helper delegates to the benchmark service and writes outputs."""
    manifest_path = tmp_path / "benchmark.json"
    output_dir = tmp_path / "artifacts"
    write_manifest(manifest_path)
    config = CouncilConfig(
        openrouter_api_key="test-key",
        claim_extractor_model="some-other-model",
    )

    result = run_claim_extraction_benchmark_once(
        config=config,
        dataset_path=manifest_path,
        output_dir=output_dir,
        run_label="benchmark-run",
        provider_factory=build_provider_resolution,
        claim_extractor_factory=lambda model_id: FakeClaimExtractor(model_id),
        model_ids=None,
    )

    assert result.model_runs[0].model_id == "nvidia/nemotron-3-super-120b-a12b:free"
    assert (
        output_dir
        / "claim-extraction-benchmark"
        / "benchmark-run"
        / "nvidia-nemotron-3-super-120b-a12b-free"
        / "run-summary.json"
    ).exists()
