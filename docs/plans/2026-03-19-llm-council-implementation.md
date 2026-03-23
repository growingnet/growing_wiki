# LLM Council Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use executing-plans skill to implement this plan task-by-task.

**Goal:** Build a source-agnostic scientific paper review pipeline for the wiki that uses OpenRouter-backed reviewer agents over a normalized evidence bundle generated from arXiv LaTeX, arXiv PDF, and generic PDF inputs.

**Architecture:** Add a small Python package inside this repository that separates provider ingestion, evidence normalization, and reviewer orchestration. All reviewers consume the same `EvidenceBundle`, return schema-validated outputs, and are orchestrated by a deterministic runner that emits JSON and markdown review artifacts.

**Tech Stack:** Python 3.11+, PydanticAI, Pydantic, httpx, pytest, existing `requirements.txt`

---

### Task 1: Create the council package skeleton and dependency baseline

**Files:**
- Create: `growing_wiki_council/__init__.py`
- Create: `growing_wiki_council/config.py`
- Create: `growing_wiki_council/cli.py`
- Modify: `requirements.txt`
- Test: `tests/council/test_imports.py`

**Step 1: Write the failing test**

```python
from growing_wiki_council.config import CouncilConfig


def test_council_package_imports() -> None:
    config = CouncilConfig(openrouter_api_key="test-key")
    assert config.openrouter_api_key == "test-key"
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/council/test_imports.py -v`

Expected: FAIL with `ModuleNotFoundError` for `growing_wiki_council`

**Step 3: Write minimal implementation**

Create the package and a minimal config model:

```python
from pydantic import BaseModel


class CouncilConfig(BaseModel):
    openrouter_api_key: str
```

Add dependencies to `requirements.txt`:

- `pydantic>=2`
- `pydantic-ai`
- `httpx`

**Step 4: Run test to verify it passes**

Run: `pytest tests/council/test_imports.py -v`

Expected: PASS

**Step 5: Commit**

```bash
git add requirements.txt growing_wiki_council/__init__.py growing_wiki_council/config.py growing_wiki_council/cli.py tests/council/test_imports.py
git commit -m "feat(council): add package scaffold and config"
```

### Task 2: Define normalized evidence schemas

**Files:**
- Create: `growing_wiki_council/models/evidence.py`
- Create: `growing_wiki_council/models/__init__.py`
- Test: `tests/council/test_evidence_models.py`

**Step 1: Write the failing test**

```python
from growing_wiki_council.models.evidence import EvidenceBundle, EvidenceSection


def test_evidence_bundle_tracks_provenance() -> None:
    bundle = EvidenceBundle(
        paper_id="arxiv:1511.05641",
        source_kind="arxiv_latex",
        title="Net2Net",
        sections=[EvidenceSection(name="abstract", content="text", provenance="latex")],
        equations=[],
        bibliography=[],
        warnings=[],
        extraction_confidence="high",
    )
    assert bundle.sections[0].provenance == "latex"
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/council/test_evidence_models.py -v`

Expected: FAIL with missing models

**Step 3: Write minimal implementation**

Implement explicit Pydantic models for:

- `EvidenceMetadata`
- `EvidenceSection`
- `EvidenceEquation`
- `EvidenceBibliographyEntry`
- `EvidenceBundle`

Include fields for:

- identifiers
- provenance
- warnings
- extraction confidence

**Step 4: Run test to verify it passes**

Run: `pytest tests/council/test_evidence_models.py -v`

Expected: PASS

**Step 5: Commit**

```bash
git add growing_wiki_council/models/__init__.py growing_wiki_council/models/evidence.py tests/council/test_evidence_models.py
git commit -m "feat(council): add evidence models"
```

### Task 3: Add provider interfaces and a generic PDF provider contract

**Files:**
- Create: `growing_wiki_council/providers/base.py`
- Create: `growing_wiki_council/providers/pdf.py`
- Create: `growing_wiki_council/providers/__init__.py`
- Test: `tests/council/test_pdf_provider.py`

**Step 1: Write the failing test**

```python
from pathlib import Path

from growing_wiki_council.providers.pdf import GenericPdfProvider


def test_pdf_provider_rejects_missing_file(tmp_path: Path) -> None:
    provider = GenericPdfProvider()
    result = provider.load(tmp_path / "missing.pdf")
    assert result.success is False
    assert "missing" in result.warnings[0].lower()
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/council/test_pdf_provider.py -v`

Expected: FAIL with missing provider module

**Step 3: Write minimal implementation**

Add:

- an `EvidenceProvider` protocol or abstract base class
- a `ProviderResult` model
- a `GenericPdfProvider` with file validation and a stub extraction path

Do not integrate the final PDF parser yet. First make the contract explicit and testable.

**Step 4: Run test to verify it passes**

Run: `pytest tests/council/test_pdf_provider.py -v`

Expected: PASS

**Step 5: Commit**

```bash
git add growing_wiki_council/providers/__init__.py growing_wiki_council/providers/base.py growing_wiki_council/providers/pdf.py tests/council/test_pdf_provider.py
git commit -m "feat(council): add provider contracts and pdf provider stub"
```

### Task 4: Add the arXiv MCP adapter

**Files:**
- Create: `growing_wiki_council/providers/arxiv.py`
- Test: `tests/council/test_arxiv_provider.py`

**Step 1: Write the failing test**

```python
from growing_wiki_council.providers.arxiv import ArxivLatexProvider


class FakeArxivClient:
    def get_paper(self, arxiv_id: str) -> dict:
        return {
            "arxiv_id": arxiv_id,
            "title": "Sample",
            "content": "content",
            "source_type": "latex",
            "fallback_used": False,
            "fallback_reason": None,
            "warnings": [],
        }


def test_arxiv_provider_maps_mcp_response() -> None:
    provider = ArxivLatexProvider(client=FakeArxivClient())
    result = provider.load("1234.56789")
    assert result.success is True
    assert result.source_kind == "arxiv_latex"
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/council/test_arxiv_provider.py -v`

Expected: FAIL with missing adapter

**Step 3: Write minimal implementation**

Implement an adapter that:

- wraps the MCP client
- maps `source_type`, `fallback_used`, and `fallback_reason`
- retrieves equations and bibliography when available
- returns a provider result without leaking raw MCP response shape

**Step 4: Run test to verify it passes**

Run: `pytest tests/council/test_arxiv_provider.py -v`

Expected: PASS

**Step 5: Commit**

```bash
git add growing_wiki_council/providers/arxiv.py tests/council/test_arxiv_provider.py
git commit -m "feat(council): add arxiv mcp provider adapter"
```

### Task 5: Build the evidence normalization service

**Files:**
- Create: `growing_wiki_council/services/evidence_builder.py`
- Create: `growing_wiki_council/services/__init__.py`
- Test: `tests/council/test_evidence_builder.py`

**Step 1: Write the failing test**

```python
from growing_wiki_council.services.evidence_builder import EvidenceBuilder
from growing_wiki_council.providers.base import ProviderResult


def test_evidence_builder_assigns_low_confidence_on_warnings() -> None:
    builder = EvidenceBuilder()
    provider_result = ProviderResult(
        success=True,
        source_kind="pdf",
        title="Paper",
        raw_text="text",
        sections=[],
        equations=[],
        bibliography=[],
        warnings=["missing bibliography"],
    )
    bundle = builder.build(provider_result)
    assert bundle.extraction_confidence == "low"
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/council/test_evidence_builder.py -v`

Expected: FAIL with missing service

**Step 3: Write minimal implementation**

Implement the normalizer that converts provider results into `EvidenceBundle` and assigns:

- canonical source kind
- normalized sections
- provenance fields
- extraction confidence

Keep the scoring heuristic simple in v1 and make it explicit in code comments.

**Step 4: Run test to verify it passes**

Run: `pytest tests/council/test_evidence_builder.py -v`

Expected: PASS

**Step 5: Commit**

```bash
git add growing_wiki_council/services/__init__.py growing_wiki_council/services/evidence_builder.py tests/council/test_evidence_builder.py
git commit -m "feat(council): add evidence normalization service"
```

### Task 6: Define structured reviewer output schemas

**Files:**
- Create: `growing_wiki_council/models/review.py`
- Test: `tests/council/test_review_models.py`

**Step 1: Write the failing test**

```python
from growing_wiki_council.models.review import ReviewFinding


def test_review_finding_requires_evidence_reference() -> None:
    finding = ReviewFinding(
        severity="medium",
        claim="The paper overstates efficiency gains.",
        evidence_refs=["section:results"],
        rationale="The reported baseline set is incomplete.",
    )
    assert finding.evidence_refs == ["section:results"]
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/council/test_review_models.py -v`

Expected: FAIL with missing review schema

**Step 3: Write minimal implementation**

Implement explicit models for:

- `ClaimRecord`
- `ReviewFinding`
- `ReviewerReport`
- `ChairVerdict`
- `CouncilReviewArtifact`

Require evidence references everywhere a reviewer makes a substantive claim.

**Step 4: Run test to verify it passes**

Run: `pytest tests/council/test_review_models.py -v`

Expected: PASS

**Step 5: Commit**

```bash
git add growing_wiki_council/models/review.py tests/council/test_review_models.py
git commit -m "feat(council): add structured review schemas"
```

### Task 7: Implement reviewer agents and deterministic orchestration

**Files:**
- Create: `growing_wiki_council/agents.py`
- Create: `growing_wiki_council/services/review_runner.py`
- Test: `tests/council/test_review_runner.py`

**Step 1: Write the failing test**

```python
from growing_wiki_council.models.evidence import EvidenceBundle
from growing_wiki_council.services.review_runner import ReviewRunner


class FakeReviewer:
    def run(self, bundle: EvidenceBundle):
        return {"role": "skeptic", "findings": []}


def test_review_runner_returns_all_expected_roles(sample_bundle: EvidenceBundle) -> None:
    runner = ReviewRunner(
        claim_extractor=FakeReviewer(),
        skeptical_reviewer=FakeReviewer(),
        supportive_reviewer=FakeReviewer(),
        citation_auditor=FakeReviewer(),
        chair_editor=FakeReviewer(),
    )
    artifact = runner.run(sample_bundle)
    assert artifact is not None
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/council/test_review_runner.py -v`

Expected: FAIL with missing runner

**Step 3: Write minimal implementation**

Implement:

- PydanticAI-backed reviewer wrappers
- role-specific prompts
- deterministic orchestration order
- transformation from reviewer outputs into `CouncilReviewArtifact`

Do not add adaptive self-routing in v1. Keep the flow explicit:

1. claim extraction
2. skeptical review
3. supportive review
4. citation audit
5. chair synthesis

**Step 4: Run test to verify it passes**

Run: `pytest tests/council/test_review_runner.py -v`

Expected: PASS

**Step 5: Commit**

```bash
git add growing_wiki_council/agents.py growing_wiki_council/services/review_runner.py tests/council/test_review_runner.py
git commit -m "feat(council): add reviewer orchestration"
```

### Task 8: Add CLI entrypoint and artifact emission

**Files:**
- Modify: `growing_wiki_council/cli.py`
- Create: `tests/council/test_cli.py`

**Step 1: Write the failing test**

```python
from pathlib import Path

from growing_wiki_council.cli import write_review_artifacts


def test_write_review_artifacts_creates_json_and_markdown(tmp_path: Path) -> None:
    output_dir = tmp_path / "artifacts"
    write_review_artifacts(output_dir, review_json={"status": "ok"}, review_markdown="# Review")
    assert (output_dir / "review.json").exists()
    assert (output_dir / "review.md").exists()
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/council/test_cli.py -v`

Expected: FAIL with missing artifact writer

**Step 3: Write minimal implementation**

Add:

- a CLI entrypoint that accepts either:
  - `--arxiv-id`
  - `--pdf-path`
- provider selection logic
- evidence normalization
- review runner execution
- artifact emission to a chosen output directory

Start with JSON and markdown outputs only. Defer `.rst` patch generation to a later task unless it is trivial once the review artifact exists.

**Step 4: Run test to verify it passes**

Run: `pytest tests/council/test_cli.py -v`

Expected: PASS

**Step 5: Commit**

```bash
git add growing_wiki_council/cli.py tests/council/test_cli.py
git commit -m "feat(council): add cli and review artifact output"
```

### Task 9: Document council usage and validate the end-to-end path

**Files:**
- Modify: `README.md`
- Create: `tests/council/test_end_to_end_smoke.py`

**Step 1: Write the failing test**

```python
def test_smoke_placeholder() -> None:
    assert False, "replace with a council smoke test after wiring fakes"
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/council/test_end_to_end_smoke.py -v`

Expected: FAIL

**Step 3: Write minimal implementation**

Replace the placeholder with a smoke test using fake providers and fake reviewer agents. Update `README.md` with:

- required environment variables
- arXiv and PDF entry examples
- artifact output examples
- limitations of extraction confidence in v1

**Step 4: Run test to verify it passes**

Run: `pytest tests/council/test_end_to_end_smoke.py -v`

Expected: PASS

**Step 5: Run broader verification**

Run:

```bash
pytest tests/council -v
pytest -v
```

Expected:

- new council tests PASS
- existing repo tests remain green

**Step 6: Commit**

```bash
git add README.md tests/council/test_end_to_end_smoke.py
git commit -m "docs(council): document usage and add smoke coverage"
```

## Implementation Notes

- Prefer explicit types and small modules.
- Keep business logic in service modules, not the CLI.
- Treat `arxiv-latex-mcp` as an adapter dependency, not a direct dependency of reviewer logic.
- Require evidence references for reviewer findings from day one.
- Keep model selection configurable in `CouncilConfig`.
- Do not auto-apply wiki patches in v1.

## Risks to Watch

- PDF extraction quality may be too weak for automatic confidence scoring.
- arXiv MCP outputs may need additional normalization if raw LaTeX is returned in some cases.
- Reviewer prompts may start making unsupported claims if evidence references are not strictly validated.
- OpenRouter model variability may require a small evaluation harness before choosing default role mappings.

## Suggested Verification Dataset

- 3 arXiv papers with LaTeX source
- 3 arXiv papers that fall back to PDF
- 3 non-arXiv venue PDFs

Use those cases to compare:

- extraction completeness
- equation preservation
- bibliography coverage
- reviewer hallucination rate
- usefulness of the chair summary

Plan complete and saved to `docs/plans/2026-03-19-llm-council-implementation.md`. Two execution options:

**1. Subagent-Driven (this session)** - I dispatch fresh subagent per task, review between tasks, fast iteration

**2. Parallel Session (separate)** - Open new session with executing-plans, batch execution with checkpoints

Which approach?
