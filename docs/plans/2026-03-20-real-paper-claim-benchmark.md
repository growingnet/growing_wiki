# Real-Paper Claim Benchmark Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use executing-plans skill to implement this plan task-by-task.

**Goal:** Build a real-paper claim-extraction benchmark that runs the existing provider-to-evidence-to-agent path on a small committed paper set and emits deterministic machine and human evaluation artifacts.

**Architecture:** Add a benchmark-specific layer beside the current vertical slice. The benchmark will load a manifest, resolve a provider per paper source type, normalize provider output into `EvidenceBundle`, run the claim extractor, and persist per-paper machine artifacts plus a structured human scoring template. `nvidia/nemotron-3-super-120b-a12b:free` remains the default benchmark baseline, while the runner interface still permits explicit model overrides later.

**Tech Stack:** Python, pytest, pydantic, python-dotenv, OpenRouter client wrapper, local PDF text extraction via `pypdf`

---

### Task 1: Add benchmark models and manifest loader

**Files:**
- Create: `growing_wiki_council/models/benchmark.py`
- Modify: `growing_wiki_council/models/__init__.py`
- Create: `growing_wiki_council/benchmarks/real_paper_benchmark.json`
- Test: `tests/council/test_benchmark_models.py`

**Step 1: Write the failing test**

```python
from pathlib import Path

from growing_wiki_council.models.benchmark import BenchmarkDataset


def test_benchmark_dataset_loads_supported_source_types(tmp_path: Path) -> None:
    manifest_path = tmp_path / "benchmark.json"
    manifest_path.write_text(
        """
        {
          "dataset_name": "real-paper-benchmark",
          "entries": [
            {"paper_id": "paper-a", "source_type": "pdf_path", "source": "fixtures/a.pdf"},
            {"paper_id": "paper-b", "source_type": "arxiv_id", "source": "1511.05641"}
          ]
        }
        """.strip(),
        encoding="utf-8",
    )

    dataset = BenchmarkDataset.load(manifest_path)

    assert dataset.dataset_name == "real-paper-benchmark"
    assert dataset.entries[0].source_type == "pdf_path"
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/council/test_benchmark_models.py::test_benchmark_dataset_loads_supported_source_types -v`
Expected: FAIL with import or attribute errors because benchmark dataset models do not exist yet.

**Step 3: Write minimal implementation**

```python
class BenchmarkEntry(BaseModel):
    paper_id: str
    source_type: Literal["arxiv_id", "arxiv_pdf_path", "pdf_path"]
    source: str
    title: str | None = None
    notes: str | None = None
    tags: list[str] = Field(default_factory=list)


class BenchmarkDataset(BaseModel):
    dataset_name: str
    entries: list[BenchmarkEntry] = Field(default_factory=list)

    @classmethod
    def load(cls, manifest_path: Path) -> "BenchmarkDataset":
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
        return cls.model_validate(payload)
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/council/test_benchmark_models.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add tests/council/test_benchmark_models.py growing_wiki_council/models/benchmark.py growing_wiki_council/models/__init__.py growing_wiki_council/benchmarks/real_paper_benchmark.json
git commit -m "feat(council): add benchmark dataset models"
```

### Task 2: Add human evaluation schema and template writer

**Files:**
- Create: `growing_wiki_council/models/human_eval.py`
- Modify: `growing_wiki_council/models/__init__.py`
- Modify: `growing_wiki_council/artifacts.py`
- Test: `tests/council/test_human_eval_artifacts.py`

**Step 1: Write the failing test**

```python
from pathlib import Path

from growing_wiki_council.artifacts import write_human_eval_template
from growing_wiki_council.models.human_eval import HumanEvaluationTemplate


def test_write_human_eval_template_persists_json(tmp_path: Path) -> None:
    output_path = tmp_path / "human-eval.template.json"
    template = HumanEvaluationTemplate(
        paper_id="paper-1",
        model_id="nvidia/nemotron-3-super-120b-a12b:free",
        run_label="benchmark-run",
    )

    write_human_eval_template(output_path, template)

    assert output_path.exists()
    assert '"claim_faithfulness": null' in output_path.read_text(encoding="utf-8")
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/council/test_human_eval_artifacts.py::test_write_human_eval_template_persists_json -v`
Expected: FAIL because the human evaluation model and writer do not exist.

**Step 3: Write minimal implementation**

```python
class HumanEvaluationTemplate(BaseModel):
    paper_id: str
    model_id: str
    run_label: str
    review_status: Literal["not_started", "in_progress", "completed"] = "not_started"
    scored_at: str | None = None
    claim_faithfulness: int | None = None
    evidence_grounding: int | None = None
    omission_rate: int | None = None
    hallucination_flags: list[str] = Field(default_factory=list)
    reviewer_notes: str | None = None


def write_human_eval_template(output_path: Path, template: HumanEvaluationTemplate) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(template.model_dump(mode="json"), indent=2, sort_keys=True) + "\n", encoding="utf-8")
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/council/test_human_eval_artifacts.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add tests/council/test_human_eval_artifacts.py growing_wiki_council/models/human_eval.py growing_wiki_council/models/__init__.py growing_wiki_council/artifacts.py
git commit -m "feat(council): add human evaluation artifacts"
```

### Task 3: Implement local PDF text extraction in the generic PDF provider

**Files:**
- Modify: `requirements.txt`
- Modify: `growing_wiki_council/providers/pdf.py`
- Test: `tests/council/test_pdf_provider.py`

**Step 1: Write the failing test**

```python
from pathlib import Path

from growing_wiki_council.providers.pdf import GenericPdfProvider


def test_pdf_provider_extracts_raw_text_from_pdf_fixture() -> None:
    provider = GenericPdfProvider()

    result = provider.load(Path("tests/fixtures/pdfs/minimal-paper.pdf"))

    assert result.success is True
    assert "growing networks" in result.raw_text.lower()
    assert result.warnings == []
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/council/test_pdf_provider.py::test_pdf_provider_extracts_raw_text_from_pdf_fixture -v`
Expected: FAIL because the provider currently returns only a placeholder warning and no extracted text.

**Step 3: Write minimal implementation**

```python
from pypdf import PdfReader


class GenericPdfProvider:
    def load(self, source: Path | str) -> ProviderResult:
        pdf_path = Path(source)
        ...
        reader = PdfReader(str(pdf_path))
        pages = [page.extract_text() or "" for page in reader.pages]
        raw_text = "\n\n".join(page for page in pages if page.strip())
        warnings = [] if raw_text else ["PDF text extraction returned no text."]
        return ProviderResult(
            success=bool(raw_text),
            source_kind="generic_pdf",
            title=pdf_path.stem,
            raw_text=raw_text or None,
            warnings=warnings,
        )
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/council/test_pdf_provider.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add requirements.txt tests/council/test_pdf_provider.py growing_wiki_council/providers/pdf.py
git commit -m "feat(council): extract text from local pdf fixtures"
```

### Task 4: Add benchmark provider resolution and source handling

**Files:**
- Create: `growing_wiki_council/services/benchmark_sources.py`
- Test: `tests/council/test_benchmark_sources.py`

**Step 1: Write the failing test**

```python
from growing_wiki_council.models.benchmark import BenchmarkEntry
from growing_wiki_council.services.benchmark_sources import resolve_benchmark_source


def test_resolve_benchmark_source_uses_pdf_provider_for_pdf_path() -> None:
    entry = BenchmarkEntry(
        paper_id="paper-1",
        source_type="pdf_path",
        source="tests/fixtures/pdfs/minimal-paper.pdf",
    )

    resolution = resolve_benchmark_source(entry=entry, arxiv_provider=object(), pdf_provider=object())

    assert resolution.source == "tests/fixtures/pdfs/minimal-paper.pdf"
    assert resolution.provider_kind == "generic_pdf"
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/council/test_benchmark_sources.py::test_resolve_benchmark_source_uses_pdf_provider_for_pdf_path -v`
Expected: FAIL because the source resolver does not exist.

**Step 3: Write minimal implementation**

```python
class ResolvedBenchmarkSource(BaseModel):
    provider_kind: Literal["arxiv", "generic_pdf"]
    source: str


def resolve_benchmark_source(*, entry: BenchmarkEntry, arxiv_provider: Any, pdf_provider: Any) -> ResolvedBenchmarkSource:
    if entry.source_type == "arxiv_id":
        return ResolvedBenchmarkSource(provider_kind="arxiv", source=entry.source)
    if entry.source_type in {"arxiv_pdf_path", "pdf_path"}:
        return ResolvedBenchmarkSource(provider_kind="generic_pdf", source=entry.source)
    raise ValueError(f"Unsupported benchmark source type: {entry.source_type}")
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/council/test_benchmark_sources.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add tests/council/test_benchmark_sources.py growing_wiki_council/services/benchmark_sources.py
git commit -m "feat(council): resolve benchmark sources through providers"
```

### Task 5: Add benchmark artifact writers and run summary models

**Files:**
- Modify: `growing_wiki_council/artifacts.py`
- Create: `growing_wiki_council/models/benchmark_run.py`
- Modify: `growing_wiki_council/models/__init__.py`
- Create: `growing_wiki_council/services/benchmark_paths.py`
- Test: `tests/council/test_benchmark_artifacts.py`

**Step 1: Write the failing test**

```python
from pathlib import Path

from growing_wiki_council.artifacts import write_benchmark_run_artifacts


def test_write_benchmark_run_artifacts_uses_deterministic_paths(tmp_path: Path) -> None:
    paper_output_dir = tmp_path / "claim-extraction-benchmark" / "run-1" / "nvidia-nemotron-3-super-120b-a12b-free" / "paper-1"

    write_benchmark_run_artifacts(
        output_dir=paper_output_dir,
        benchmark_entry={"paper_id": "paper-1"},
        provider_result={"success": True},
        evidence_bundle={"paper_id": "paper-1"},
        raw_output={"role": "claim_extractor"},
        validated_report={"role": "claim_extractor", "summary": "ok", "findings": [], "claims": [], "open_questions": []},
        summary_markdown="# Summary",
    )

    assert (paper_output_dir / "benchmark-entry.json").exists()
    assert (paper_output_dir / "validated-reviewer-report.json").exists()
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/council/test_benchmark_artifacts.py::test_write_benchmark_run_artifacts_uses_deterministic_paths -v`
Expected: FAIL because the benchmark artifact writer does not exist.

**Step 3: Write minimal implementation**

```python
def write_benchmark_run_artifacts(...):
    output_dir.mkdir(parents=True, exist_ok=True)
    ...
    (output_dir / "benchmark-entry.json").write_text(...)
    (output_dir / "provider-result.json").write_text(...)
    (output_dir / "evidence-bundle.json").write_text(...)
    (output_dir / "raw-reviewer-output.json").write_text(...)
    (output_dir / "validated-reviewer-report.json").write_text(...)
    (output_dir / "summary.md").write_text(summary_markdown, encoding="utf-8")
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/council/test_benchmark_artifacts.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add tests/council/test_benchmark_artifacts.py growing_wiki_council/artifacts.py growing_wiki_council/models/benchmark_run.py growing_wiki_council/models/__init__.py growing_wiki_council/services/benchmark_paths.py
git commit -m "feat(council): add benchmark artifact writers"
```

### Task 6: Implement the benchmark runner with frozen default baseline

**Files:**
- Modify: `growing_wiki_council/config.py`
- Create: `growing_wiki_council/services/claim_extraction_benchmark.py`
- Modify: `growing_wiki_council/cli.py`
- Test: `tests/council/test_claim_extraction_benchmark.py`
- Test: `tests/council/test_cli_claim_extraction_benchmark.py`

**Step 1: Write the failing test**

```python
from pathlib import Path

from growing_wiki_council.config import CouncilConfig
from growing_wiki_council.services.claim_extraction_benchmark import run_claim_extraction_benchmark


def test_claim_extraction_benchmark_defaults_to_frozen_baseline(tmp_path: Path) -> None:
    config = CouncilConfig(
        openrouter_api_key="test-key",
        claim_extractor_model="some-other-model",
    )

    result = run_claim_extraction_benchmark(
        config=config,
        dataset_path=tmp_path / "benchmark.json",
        output_dir=tmp_path / "artifacts",
        provider_factory=None,
        claim_extractor_factory=None,
        model_ids=None,
    )

    assert result.model_runs[0].model_id == "nvidia/nemotron-3-super-120b-a12b:free"
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/council/test_claim_extraction_benchmark.py::test_claim_extraction_benchmark_defaults_to_frozen_baseline -v`
Expected: FAIL because the benchmark service and baseline-default policy do not exist.

**Step 3: Write minimal implementation**

```python
DEFAULT_BENCHMARK_MODEL_ID = "nvidia/nemotron-3-super-120b-a12b:free"


def run_claim_extraction_benchmark(..., model_ids: list[str] | None = None):
    selected_model_ids = model_ids or [DEFAULT_BENCHMARK_MODEL_ID]
    ...
    for model_id in selected_model_ids:
        ...
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/council/test_claim_extraction_benchmark.py tests/council/test_cli_claim_extraction_benchmark.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add tests/council/test_claim_extraction_benchmark.py tests/council/test_cli_claim_extraction_benchmark.py growing_wiki_council/config.py growing_wiki_council/services/claim_extraction_benchmark.py growing_wiki_council/cli.py
git commit -m "feat(council): add real-paper claim benchmark runner"
```

### Task 7: Add committed benchmark fixtures and end-to-end smoke coverage

**Files:**
- Create: `tests/fixtures/pdfs/minimal-paper.pdf`
- Create: `tests/fixtures/pdfs/minimal-paper-2.pdf`
- Modify: `growing_wiki_council/benchmarks/real_paper_benchmark.json`
- Test: `tests/council/test_claim_extraction_benchmark_smoke.py`

**Step 1: Write the failing test**

```python
from pathlib import Path

from growing_wiki_council.services.claim_extraction_benchmark import run_claim_extraction_benchmark


def test_claim_extraction_benchmark_smoke_writes_per_paper_outputs(tmp_path: Path) -> None:
    result = run_claim_extraction_benchmark(
        ...,
        dataset_path=Path("growing_wiki_council/benchmarks/real_paper_benchmark.json"),
        output_dir=tmp_path / "artifacts",
    )

    assert result.paper_runs
    assert (tmp_path / "artifacts" / "claim-extraction-benchmark").exists()
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/council/test_claim_extraction_benchmark_smoke.py -v`
Expected: FAIL until the committed fixture dataset and smoke wiring are in place.

**Step 3: Write minimal implementation**

```python
# Add 5 to 10 manifest entries that point at committed local fixture PDFs.
# Keep files small and deterministic.
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/council/test_claim_extraction_benchmark_smoke.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add tests/fixtures/pdfs growing_wiki_council/benchmarks/real_paper_benchmark.json tests/council/test_claim_extraction_benchmark_smoke.py
git commit -m "test(council): add real-paper benchmark fixtures"
```

### Task 8: Update README with benchmark usage and artifact paths

**Files:**
- Modify: `README.md`
- Test: `tests/test_contributor_docs.py`

**Step 1: Write the failing test**

```python
def test_readme_mentions_claim_extraction_benchmark() -> None:
    readme_text = Path("README.md").read_text(encoding="utf-8")
    assert "Claim Extraction Benchmark" in readme_text
    assert "human-eval.template.json" in readme_text
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_contributor_docs.py -v`
Expected: FAIL until README coverage includes the benchmark section.

**Step 3: Write minimal implementation**

```markdown
## Claim Extraction Benchmark

Describe the benchmark dataset, the default Nemotron Super baseline, and the
artifact layout under `artifacts/claim-extraction-benchmark/...`.
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_contributor_docs.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add README.md tests/test_contributor_docs.py
git commit -m "docs(council): document claim extraction benchmark"
```

### Task 9: Run full verification and prepare handoff

**Files:**
- Modify: `docs/plans/2026-03-20-real-paper-claim-benchmark.md` if commands or outcomes need correction after execution

**Step 1: Run formatting**

Run: `uv run ruff format .`
Expected: PASS

**Step 2: Run linting**

Run: `uv run ruff check --fix .`
Expected: PASS

**Step 3: Run type checks**

Run: `uv run ty check .`
Expected: PASS

**Step 4: Run full test suite**

Run: `PYTHONPATH=. uv run pytest tests/`
Expected: PASS

**Step 5: Commit final cleanups if needed**

```bash
git add relevant/files
git commit -m "chore(council): finalize claim benchmark verification"
```
