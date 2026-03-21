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

    def __init__(self, model_id: str, profile_id: str) -> None:
        """Store the model identifier and profile used to build this extractor."""
        self.model_id = model_id
        self.profile_id = profile_id

    def run_raw(self, bundle) -> dict:
        """Return a raw claim-extraction payload for the evidence bundle."""
        reviewer_payload = {
            "role": "claim_extractor",
            "summary": (
                f"Claims extracted with {self.model_id} for {self.profile_id}."
            ),
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
        if self.profile_id == "website_aligned":
            reviewer_payload.update(
                {
                    "schema_variant": "website_aligned",
                    "method_family": "layer_growth",
                    "growth_operator": "add_neurons",
                    "initialization_strategy": "svd",
                    "selection_criterion": "gradient_alignment",
                    "mechanistic_notes": ["Adds units where gradients bottleneck."],
                    "website_alignment_notes": "Aligned to website taxonomy.",
                }
            )
        return reviewer_payload


class CapturingClaimExtractor:
    """Capture the paper_id seen by the benchmark claim extractor."""

    def __init__(self, model_id: str, profile_id: str) -> None:
        """Store constructor inputs and benchmark bundle observations."""
        self.model_id = model_id
        self.profile_id = profile_id
        self.seen_paper_ids: list[str] = []

    def run_raw(self, bundle) -> dict:
        """Record the bundle paper_id and return a valid reviewer payload."""
        self.seen_paper_ids.append(bundle.paper_id)
        return {
            "role": "claim_extractor",
            "summary": "Captured bundle paper_id.",
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


class DivergingPaperIdProvider:
    """Return a provider result whose paper_id differs from the manifest entry."""

    def load(self, source: str) -> ProviderResult:
        """Return a stable provider result with a canonical-but-different paper id."""
        return ProviderResult(
            success=True,
            source_kind="generic_pdf",
            paper_id="provider-paper-id",
            title="Paper 1",
            raw_text=f"Growing networks benchmark text from {source}.",
            warnings=[],
        )


class FailingProvider:
    """Raise a deterministic provider failure for benchmark tests."""

    def load(self, source: str) -> ProviderResult:
        """Raise a runtime error for the requested source."""
        raise RuntimeError(f"provider failed for {source}")


class InvalidClaimExtractor:
    """Return a schema-invalid reviewer payload for benchmark tests."""

    def __init__(self, model_id: str, profile_id: str) -> None:
        """Store the model identifier and profile used to build this extractor."""
        self.model_id = model_id
        self.profile_id = profile_id

    def run_raw(self, bundle) -> dict:
        """Return a payload that fails `ReviewerReport` validation."""
        return {
            "role": "claim_extractor",
            "summary": (
                f"Claims extracted with {self.model_id} for {self.profile_id}."
            ),
            "findings": [],
            "claims": [{"claim": "Missing evidence refs"}],
            "open_questions": [],
        }


def write_manifest(manifest_path: Path) -> None:
    """Create a minimal benchmark manifest for service tests."""
    manifest_path.write_text(
        (
            "{\n"
            '  "dataset_name": "real-paper-benchmark",\n'
            '  "entries": [\n'
            "    {\n"
            '      "paper_id": "paper-1",\n'
            '      "source_type": "pdf_path",\n'
            '      "source": "tests/fixtures/pdfs/minimal-paper.pdf"\n'
            "    }\n"
            "  ]\n"
            "}\n"
        ),
        encoding="utf-8",
    )


def write_two_entry_manifest(manifest_path: Path) -> None:
    """Create a two-paper benchmark manifest for failure-isolation tests."""
    manifest_path.write_text(
        (
            "{\n"
            '  "dataset_name": "real-paper-benchmark",\n'
            '  "entries": [\n'
            "    {\n"
            '      "paper_id": "paper-1",\n'
            '      "source_type": "pdf_path",\n'
            '      "source": "tests/fixtures/pdfs/minimal-paper.pdf"\n'
            "    },\n"
            "    {\n"
            '      "paper_id": "paper-2",\n'
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


def build_diverging_provider_resolution(
    entry: BenchmarkEntry,
) -> ResolvedBenchmarkSource:
    """Resolve test entries to a provider whose canonical id differs from the manifest."""
    return ResolvedBenchmarkSource(
        provider_kind="generic_pdf",
        provider=DivergingPaperIdProvider(),
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

    def build_claim_extractor(model_id: str, profile_id: str) -> FakeClaimExtractor:
        selected_model_ids.append(f"{model_id}|{profile_id}")
        return FakeClaimExtractor(model_id=model_id, profile_id=profile_id)

    result = run_claim_extraction_benchmark(
        config=config,
        dataset_path=manifest_path,
        output_dir=output_dir,
        run_label="benchmark-run",
        provider_factory=build_provider_resolution,
        claim_extractor_factory=build_claim_extractor,
        model_ids=None,
    )

    assert selected_model_ids == ["nvidia/nemotron-3-super-120b-a12b:free|baseline"]
    assert result.model_runs[0].profile_label == "baseline"
    assert result.model_runs[0].paper_runs[0].profile_label == "baseline"
    assert result.model_runs[0].model_id == "nvidia/nemotron-3-super-120b-a12b:free"
    assert (
        output_dir
        / "claim-extraction-benchmark"
        / "benchmark-run"
        / "baseline"
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

    def build_claim_extractor(model_id: str, profile_id: str) -> FakeClaimExtractor:
        selected_model_ids.append(f"{model_id}|{profile_id}")
        return FakeClaimExtractor(model_id=model_id, profile_id=profile_id)

    result = run_claim_extraction_benchmark(
        config=config,
        dataset_path=manifest_path,
        output_dir=output_dir,
        run_label="benchmark-run",
        provider_factory=build_provider_resolution,
        claim_extractor_factory=build_claim_extractor,
        model_ids=["example/model"],
    )

    assert selected_model_ids == ["example/model|baseline"]
    assert result.model_runs[0].profile_label == "baseline"
    assert result.model_runs[0].model_id == "example/model"


def test_claim_extraction_benchmark_uses_manifest_paper_id_in_evidence_bundle(
    tmp_path: Path,
) -> None:
    """Benchmark prompts should use the manifest paper_id for stable correlation."""
    manifest_path = tmp_path / "benchmark.json"
    output_dir = tmp_path / "artifacts"
    write_manifest(manifest_path)
    config = CouncilConfig(
        openrouter_api_key="test-key",
        claim_extractor_model="some-other-model",
    )
    claim_extractor = CapturingClaimExtractor(
        model_id="nvidia/nemotron-3-super-120b-a12b:free",
        profile_id="baseline",
    )

    result = run_claim_extraction_benchmark(
        config=config,
        dataset_path=manifest_path,
        output_dir=output_dir,
        run_label="benchmark-run",
        provider_factory=build_diverging_provider_resolution,
        claim_extractor_factory=lambda model_id, profile_id: claim_extractor,
    )

    assert claim_extractor.seen_paper_ids == ["paper-1"]
    assert result.model_runs[0].paper_runs[0].paper_id == "paper-1"


def test_claim_extraction_benchmark_supports_multiple_profiles(
    tmp_path: Path,
) -> None:
    """The benchmark runs profile-specific variants and keeps their schemas separate."""
    manifest_path = tmp_path / "benchmark.json"
    output_dir = tmp_path / "artifacts"
    selected_profiles: list[str] = []
    write_manifest(manifest_path)
    config = CouncilConfig(
        openrouter_api_key="test-key",
        claim_extractor_model="some-other-model",
    )

    def build_claim_extractor(model_id: str, profile_id: str) -> FakeClaimExtractor:
        selected_profiles.append(profile_id)
        return FakeClaimExtractor(model_id=model_id, profile_id=profile_id)

    result = run_claim_extraction_benchmark(
        config=config,
        dataset_path=manifest_path,
        output_dir=output_dir,
        run_label="benchmark-run",
        provider_factory=build_provider_resolution,
        claim_extractor_factory=build_claim_extractor,
        profile_ids=["baseline_prompt_variant", "website_aligned"],
    )

    assert selected_profiles == ["baseline_prompt_variant", "website_aligned"]
    assert [model_run.profile_label for model_run in result.model_runs] == [
        "baseline_prompt_variant",
        "website_aligned",
    ]
    assert result.model_runs[0].paper_runs[0].validated_reviewer_report == {
        "role": "claim_extractor",
        "summary": (
            "Claims extracted with nvidia/nemotron-3-super-120b-a12b:free "
            "for baseline_prompt_variant."
        ),
        "findings": [],
        "claims": [
            {
                "claim": "Networks can grow during training.",
                "evidence_refs": ["section:full_text"],
                "confidence": "medium",
                "notes": None,
            }
        ],
        "open_questions": [],
    }
    assert (
        result.model_runs[1].paper_runs[0].validated_reviewer_report["method_family"]
        == "layer_growth"
    )
    assert (
        result.model_runs[1].paper_runs[0].validated_reviewer_report["schema_variant"]
        == "website_aligned"
    )
    assert (
        output_dir
        / "claim-extraction-benchmark"
        / "benchmark-run"
        / "website_aligned"
        / "nvidia-nemotron-3-super-120b-a12b-free"
        / "paper-1"
        / "validated-reviewer-report.json"
    ).exists()


def test_claim_extraction_benchmark_records_provider_failures_and_continues(
    tmp_path: Path,
) -> None:
    """The benchmark records one provider failure and continues."""
    manifest_path = tmp_path / "benchmark.json"
    output_dir = tmp_path / "artifacts"
    write_two_entry_manifest(manifest_path)
    config = CouncilConfig(
        openrouter_api_key="test-key",
        claim_extractor_model="some-other-model",
    )

    def build_provider(entry: BenchmarkEntry) -> ResolvedBenchmarkSource:
        provider = FailingProvider() if entry.paper_id == "paper-1" else FakeProvider()
        return ResolvedBenchmarkSource(
            provider_kind="generic_pdf",
            provider=provider,
            source=entry.source,
        )

    result = run_claim_extraction_benchmark(
        config=config,
        dataset_path=manifest_path,
        output_dir=output_dir,
        run_label="benchmark-run",
        provider_factory=build_provider,
        claim_extractor_factory=lambda model_id, profile_id: FakeClaimExtractor(
            model_id,
            profile_id,
        ),
    )

    assert len(result.model_runs[0].paper_runs) == 2
    assert result.model_runs[0].paper_runs[0].status == "failed"
    assert result.model_runs[0].paper_runs[0].error_type == "RuntimeError"
    assert result.model_runs[0].paper_runs[1].status == "completed"
    assert (
        output_dir
        / "claim-extraction-benchmark"
        / "benchmark-run"
        / "baseline"
        / "nvidia-nemotron-3-super-120b-a12b-free"
        / "paper-1"
        / "validated-reviewer-report.json"
    ).exists()
    assert (
        output_dir
        / "claim-extraction-benchmark"
        / "benchmark-run"
        / "baseline"
        / "nvidia-nemotron-3-super-120b-a12b-free"
        / "paper-2"
        / "validated-reviewer-report.json"
    ).exists()


def test_claim_extraction_benchmark_records_validation_failures_and_continues(
    tmp_path: Path,
) -> None:
    """The benchmark records schema failures without aborting the full run."""
    manifest_path = tmp_path / "benchmark.json"
    output_dir = tmp_path / "artifacts"
    write_two_entry_manifest(manifest_path)
    config = CouncilConfig(
        openrouter_api_key="test-key",
        claim_extractor_model="some-other-model",
    )
    extractor_calls = {"count": 0}

    def build_claim_extractor(model_id: str, profile_id: str):
        class MixedClaimExtractor:
            """Return one invalid payload before returning valid ones."""

            def run_raw(self, bundle) -> dict:
                extractor_calls["count"] += 1
                if extractor_calls["count"] == 1:
                    return InvalidClaimExtractor(model_id, profile_id).run_raw(bundle)
                return FakeClaimExtractor(model_id, profile_id).run_raw(bundle)

        return MixedClaimExtractor()

    result = run_claim_extraction_benchmark(
        config=config,
        dataset_path=manifest_path,
        output_dir=output_dir,
        run_label="benchmark-run",
        provider_factory=build_provider_resolution,
        claim_extractor_factory=build_claim_extractor,
    )

    assert len(result.model_runs[0].paper_runs) == 2
    assert result.model_runs[0].paper_runs[0].status == "failed"
    assert result.model_runs[0].paper_runs[0].error_type == "ValidationError"
    assert result.model_runs[0].paper_runs[1].status == "completed"
