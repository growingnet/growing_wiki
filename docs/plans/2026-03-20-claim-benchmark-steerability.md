# Claim Benchmark Steerability Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use executing-plans skill to implement this plan task-by-task.

**Goal:** Add prompt-steerability benchmark profiles so the same model and dataset can be compared under baseline, prompt-only, and website-aligned review modes.

**Architecture:** Extend the existing benchmark runner with explicit profile selection. The baseline profile keeps the current prompt and schema, the prompt-only profile swaps only the prompt while preserving `ReviewerReport`, and the website-aligned profile uses a website-oriented prompt with an additive schema layered on top of `ReviewerReport`. Artifacts stay deterministic and are separated by profile within the same benchmark root.

**Tech Stack:** Python, pytest, pydantic, existing benchmark runner, OpenRouter client wrapper

---

### Task 1: Add benchmark profile models

**Files:**
- Create: `growing_wiki_council/models/benchmark_profiles.py`
- Modify: `growing_wiki_council/models/__init__.py`
- Test: `tests/council/test_benchmark_profiles.py`

**Step 1: Write the failing test**

```python
from growing_wiki_council.models.benchmark_profiles import BenchmarkProfileConfig


def test_benchmark_profile_config_supports_expected_profiles() -> None:
    profile = BenchmarkProfileConfig(profile_id="website_aligned")

    assert profile.profile_id == "website_aligned"
    assert profile.schema_variant == "website_aligned"
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/council/test_benchmark_profiles.py -v`
Expected: FAIL with missing module or missing profile model.

**Step 3: Write minimal implementation**

```python
class BenchmarkProfileId = Literal[
    "baseline",
    "baseline_prompt_variant",
    "website_aligned",
]


class BenchmarkProfileConfig(BaseModel):
    profile_id: BenchmarkProfileId
    schema_variant: str | None = None
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/council/test_benchmark_profiles.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add tests/council/test_benchmark_profiles.py growing_wiki_council/models/benchmark_profiles.py growing_wiki_council/models/__init__.py
git commit -m "feat(council): add benchmark profile models"
```

### Task 2: Add website-aligned review schema

**Files:**
- Create: `growing_wiki_council/models/review_profiles.py`
- Modify: `growing_wiki_council/models/__init__.py`
- Test: `tests/council/test_review_profile_models.py`

**Step 1: Write the failing test**

```python
from growing_wiki_council.models.review_profiles import WebsiteAlignedReviewerReport


def test_website_aligned_report_extends_reviewer_report() -> None:
    report = WebsiteAlignedReviewerReport(
        role="claim_extractor",
        summary="Summary",
        findings=[],
        claims=[],
        open_questions=[],
        method_family="layer_growth",
    )

    assert report.method_family == "layer_growth"
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/council/test_review_profile_models.py -v`
Expected: FAIL with missing schema module.

**Step 3: Write minimal implementation**

```python
class WebsiteAlignedReviewerReport(ReviewerReport):
    method_family: str | None = None
    growth_operator: str | None = None
    initialization_strategy: str | None = None
    selection_criterion: str | None = None
    mechanistic_notes: list[str] = Field(default_factory=list)
    website_alignment_notes: str | None = None
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/council/test_review_profile_models.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add tests/council/test_review_profile_models.py growing_wiki_council/models/review_profiles.py growing_wiki_council/models/__init__.py
git commit -m "feat(council): add website aligned review schema"
```

### Task 3: Add profile-specific prompt builders

**Files:**
- Create: `growing_wiki_council/services/claim_extractor_profiles.py`
- Test: `tests/council/test_claim_extractor_profiles.py`

**Step 1: Write the failing test**

```python
from growing_wiki_council.models.evidence import EvidenceBundle
from growing_wiki_council.services.claim_extractor_profiles import build_prompt_for_profile


def test_build_prompt_for_profile_uses_website_alignment_language() -> None:
    bundle = EvidenceBundle(
        paper_id="paper-1",
        source_kind="generic_pdf",
        title="Paper",
        extraction_confidence="medium",
    )

    prompt = build_prompt_for_profile(profile_id="website_aligned", bundle=bundle)

    assert "growth_operator" in prompt
    assert "method_family" in prompt
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/council/test_claim_extractor_profiles.py -v`
Expected: FAIL because the profile prompt builder does not exist.

**Step 3: Write minimal implementation**

```python
def build_prompt_for_profile(*, profile_id: str, bundle: EvidenceBundle) -> str:
    ...
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/council/test_claim_extractor_profiles.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add tests/council/test_claim_extractor_profiles.py growing_wiki_council/services/claim_extractor_profiles.py
git commit -m "feat(council): add profile specific prompts"
```

### Task 4: Make claim extractor support prompt profiles

**Files:**
- Modify: `growing_wiki_council/agents.py`
- Test: `tests/council/test_claim_extractor_agent.py`

**Step 1: Write the failing test**

```python
def test_claim_extractor_agent_builds_prompt_for_selected_profile() -> None:
    ...
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/council/test_claim_extractor_agent.py -v`
Expected: FAIL because the agent does not accept a benchmark profile.

**Step 3: Write minimal implementation**

```python
class ClaimExtractorAgent:
    def __init__(..., benchmark_profile_id: str = "baseline") -> None:
        self.benchmark_profile_id = benchmark_profile_id
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/council/test_claim_extractor_agent.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add tests/council/test_claim_extractor_agent.py growing_wiki_council/agents.py
git commit -m "feat(council): add claim extractor benchmark profiles"
```

### Task 5: Add profile-aware benchmark artifact paths

**Files:**
- Modify: `growing_wiki_council/services/benchmark_paths.py`
- Test: `tests/council/test_benchmark_artifacts.py`

**Step 1: Write the failing test**

```python
def test_benchmark_paths_include_profile_label() -> None:
    ...
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/council/test_benchmark_artifacts.py -v`
Expected: FAIL because paths do not include the profile segment.

**Step 3: Write minimal implementation**

```python
def benchmark_run_output_dir(..., profile_label: str) -> Path:
    return output_root / "claim-extraction-benchmark" / run_label / profile_label / model_slug
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/council/test_benchmark_artifacts.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add tests/council/test_benchmark_artifacts.py growing_wiki_council/services/benchmark_paths.py
git commit -m "feat(council): separate benchmark artifacts by profile"
```

### Task 6: Extend benchmark runner for multiple profiles

**Files:**
- Modify: `growing_wiki_council/models/benchmark_run.py`
- Modify: `growing_wiki_council/services/claim_extraction_benchmark.py`
- Modify: `growing_wiki_council/cli.py`
- Test: `tests/council/test_claim_extraction_benchmark.py`
- Test: `tests/council/test_cli_claim_extraction_benchmark.py`

**Step 1: Write the failing test**

```python
def test_claim_extraction_benchmark_runs_multiple_profiles() -> None:
    ...
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/council/test_claim_extraction_benchmark.py tests/council/test_cli_claim_extraction_benchmark.py -v`
Expected: FAIL because the runner cannot select profiles or write profile-separated artifacts.

**Step 3: Write minimal implementation**

```python
def run_claim_extraction_benchmark(..., profile_ids: list[str] | None = None):
    selected_profile_ids = profile_ids or ["baseline"]
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/council/test_claim_extraction_benchmark.py tests/council/test_cli_claim_extraction_benchmark.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add tests/council/test_claim_extraction_benchmark.py tests/council/test_cli_claim_extraction_benchmark.py growing_wiki_council/models/benchmark_run.py growing_wiki_council/services/claim_extraction_benchmark.py growing_wiki_council/cli.py
git commit -m "feat(council): add benchmark steerability profiles"
```

### Task 7: Add smoke coverage for prompt-only and website-aligned profiles

**Files:**
- Modify: `tests/council/test_claim_extraction_benchmark_smoke.py`

**Step 1: Write the failing test**

```python
def test_claim_extraction_benchmark_smoke_writes_profile_outputs() -> None:
    ...
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/council/test_claim_extraction_benchmark_smoke.py -v`
Expected: FAIL until the smoke test includes multiple profiles.

**Step 3: Write minimal implementation**

```python
# Update the smoke test to run baseline and website_aligned and assert both output roots exist.
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/council/test_claim_extraction_benchmark_smoke.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add tests/council/test_claim_extraction_benchmark_smoke.py
git commit -m "test(council): cover benchmark steerability profiles"
```

### Task 8: Document profile usage in README

**Files:**
- Modify: `README.md`
- Test: `tests/test_contributor_docs.py`

**Step 1: Write the failing test**

```python
def test_readme_documents_benchmark_profiles() -> None:
    ...
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_contributor_docs.py -v`
Expected: FAIL until README mentions the prompt-only and website-aligned profiles.

**Step 3: Write minimal implementation**

```markdown
Add a short section describing `baseline`, `baseline_prompt_variant`, and `website_aligned`.
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_contributor_docs.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add README.md tests/test_contributor_docs.py
git commit -m "docs(council): document benchmark profiles"
```

### Task 9: Run verification

**Files:**
- Modify: `docs/plans/2026-03-20-claim-benchmark-steerability.md` if commands need correction

**Step 1: Run formatting**

Run: `uv run ruff format .`
Expected: PASS

**Step 2: Run linting**

Run: `uv run ruff check --fix .`
Expected: PASS

**Step 3: Run type checks**

Run: `uv run ty check .`
Expected: PASS or environment-specific missing-tool note

**Step 4: Run full test suite**

Run: `PYTHONPATH=. uv run pytest tests/`
Expected: PASS

**Step 5: Commit final cleanups if needed**

```bash
git add relevant/files
git commit -m "chore(council): verify benchmark steerability profiles"
```
