# OpenRouter Schema Calibration Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use executing-plans skill to implement this plan task-by-task.

**Goal:** Add a schema-reliability calibration path that runs a real OpenRouter-backed `ClaimExtractorAgent` against fake evidence input and records whether the output validates into the council `ReviewerReport` schema.

**Architecture:** Reuse the current council vertical slice, but isolate the experimental arXiv client by introducing a calibration runner built on fixed fake evidence. The calibration path should exercise the real OpenRouter call path, preserve the raw model response for debugging, validate into the existing review schema, and emit artifacts that make schema failures easy to inspect.

**Tech Stack:** Python 3.11+, Pydantic, httpx, existing `growing_wiki_council` package, OpenRouter, pytest

---

### Task 1: Add calibration config fields for live schema tests

**Files:**
- Modify: `growing_wiki_council/config.py`
- Test: `tests/council/test_calibration_config.py`

**Step 1: Write the failing test**

```python
from growing_wiki_council.config import CouncilConfig


def test_council_config_supports_schema_calibration_settings() -> None:
    config = CouncilConfig(
        openrouter_api_key="test-key",
        openrouter_base_url="https://openrouter.ai/api/v1",
        claim_extractor_model="openrouter/openai/gpt-4.1-mini",
        calibration_run_label="schema-calibration",
        calibration_output_dir="artifacts/calibration",
    )
    assert config.calibration_run_label == "schema-calibration"
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/council/test_calibration_config.py -v`

Expected: FAIL with missing calibration fields on `CouncilConfig`

**Step 3: Write minimal implementation**

Add only the fields needed for the first live calibration run:

- `calibration_run_label: str = "schema-calibration"`
- `calibration_output_dir: str = "artifacts/calibration"`

Keep config as pure data. Do not add env-loading logic.

**Step 4: Run test to verify it passes**

Run: `pytest tests/council/test_calibration_config.py -v`

Expected: PASS

**Step 5: Commit**

```bash
git add growing_wiki_council/config.py tests/council/test_calibration_config.py
git commit -m "feat(council): add schema calibration config"
```

### Task 2: Add a fixed fake-evidence builder for calibration runs

**Files:**
- Create: `growing_wiki_council/services/calibration_inputs.py`
- Modify: `growing_wiki_council/services/__init__.py`
- Test: `tests/council/test_calibration_inputs.py`

**Step 1: Write the failing test**

```python
from growing_wiki_council.services.calibration_inputs import build_schema_calibration_bundle


def test_schema_calibration_bundle_is_deterministic() -> None:
    bundle = build_schema_calibration_bundle()
    assert bundle.paper_id == "schema-calibration-paper"
    assert bundle.source_kind == "generic_pdf"
    assert len(bundle.sections) >= 1
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/council/test_calibration_inputs.py -v`

Expected: FAIL with missing calibration input builder

**Step 3: Write minimal implementation**

Create one deterministic fake evidence builder that returns an `EvidenceBundle` with:

- `paper_id="schema-calibration-paper"`
- `source_kind="generic_pdf"`
- a short title
- one or two sections with clear, simple scientific-style prose
- no equations or bibliography required
- `extraction_confidence="medium"`

This bundle is not meant to be realistic enough for scientific judgment. It is only meant to test schema compliance.

**Step 4: Run test to verify it passes**

Run: `pytest tests/council/test_calibration_inputs.py -v`

Expected: PASS

**Step 5: Commit**

```bash
git add growing_wiki_council/services/__init__.py growing_wiki_council/services/calibration_inputs.py tests/council/test_calibration_inputs.py
git commit -m "feat(council): add schema calibration inputs"
```

### Task 3: Preserve raw OpenRouter responses for debugging

**Files:**
- Modify: `growing_wiki_council/clients/openrouter_client.py`
- Test: `tests/council/test_openrouter_raw_response.py`

**Step 1: Write the failing test**

```python
from growing_wiki_council.clients.openrouter_client import OpenRouterClaimExtractorClient


class FakeBackend:
    def extract_claims(self, prompt: str) -> dict:
        return {"raw_response": {"content": "bad json"}}


def test_openrouter_client_exposes_raw_backend_payload() -> None:
    client = OpenRouterClaimExtractorClient(backend=FakeBackend())
    payload = client.run_prompt("prompt")
    assert "raw_response" in payload
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/council/test_openrouter_raw_response.py -v`

Expected: FAIL if the client strips or reshapes raw payloads in a way that hides backend output

**Step 3: Write minimal implementation**

Adjust the client so that:

- injected fake backends can return arbitrary JSON-like payloads unchanged
- the live OpenRouter path returns a dict that includes:
  - the parsed structured content when successful
  - the raw provider response content in a stable debug field, for example `raw_response`

Do not redesign the whole client. Keep the change minimal and backward-compatible with the existing tests.

**Step 4: Run test to verify it passes**

Run: `pytest tests/council/test_openrouter_raw_response.py -v`

Expected: PASS

**Step 5: Run regression checks**

Run: `pytest tests/council/test_openrouter_client.py tests/council/test_openrouter_raw_response.py -v`

Expected: PASS

**Step 6: Commit**

```bash
git add growing_wiki_council/clients/openrouter_client.py tests/council/test_openrouter_raw_response.py
git commit -m "feat(council): preserve raw openrouter responses"
```

### Task 4: Add a schema-validation result model for calibration artifacts

**Files:**
- Create: `growing_wiki_council/models/calibration.py`
- Modify: `growing_wiki_council/models/__init__.py`
- Test: `tests/council/test_calibration_models.py`

**Step 1: Write the failing test**

```python
from growing_wiki_council.models.calibration import SchemaCalibrationResult


def test_schema_calibration_result_tracks_validation_state() -> None:
    result = SchemaCalibrationResult(
        success=True,
        run_label="schema-calibration",
        validation_error=None,
        raw_response={"role": "claim_extractor"},
    )
    assert result.success is True
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/council/test_calibration_models.py -v`

Expected: FAIL with missing calibration model

**Step 3: Write minimal implementation**

Create a small model for the calibration artifact:

- `success: bool`
- `run_label: str`
- `validation_error: str | None`
- `raw_response: dict | list | str | None`
- `validated_report: ReviewerReport | None`

Keep it JSON-friendly. No timestamps or metrics yet.

**Step 4: Run test to verify it passes**

Run: `pytest tests/council/test_calibration_models.py -v`

Expected: PASS

**Step 5: Commit**

```bash
git add growing_wiki_council/models/__init__.py growing_wiki_council/models/calibration.py tests/council/test_calibration_models.py
git commit -m "feat(council): add schema calibration result model"
```

### Task 5: Add a calibration runner that validates one real OpenRouter response

**Files:**
- Create: `growing_wiki_council/services/schema_calibration.py`
- Modify: `growing_wiki_council/services/__init__.py`
- Test: `tests/council/test_schema_calibration_runner.py`

**Step 1: Write the failing test**

```python
from growing_wiki_council.services.schema_calibration import run_schema_calibration


class FakeAgent:
    def run(self, bundle):
        return {
            "role": "claim_extractor",
            "summary": "Claims extracted.",
            "findings": [],
            "claims": [{"claim": "A", "evidence_refs": ["section:full_text"]}],
        }


def test_schema_calibration_runner_returns_success_for_valid_payload() -> None:
    result = run_schema_calibration(
        claim_extractor=FakeAgent(),
        run_label="schema-calibration",
    )
    assert result.success is True
    assert result.validated_report is not None
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/council/test_schema_calibration_runner.py -v`

Expected: FAIL with missing runner

**Step 3: Write minimal implementation**

Implement `run_schema_calibration(...)` that:

1. builds the deterministic fake evidence bundle
2. calls the supplied `claim_extractor`
3. validates the result into `ReviewerReport`
4. returns `SchemaCalibrationResult`

Failure behavior:

- catch schema validation exceptions
- store the exception text in `validation_error`
- preserve the raw response payload when possible
- do not raise on schema failure in this runner

**Step 4: Run test to verify it passes**

Run: `pytest tests/council/test_schema_calibration_runner.py -v`

Expected: PASS

**Step 5: Commit**

```bash
git add growing_wiki_council/services/__init__.py growing_wiki_council/services/schema_calibration.py tests/council/test_schema_calibration_runner.py
git commit -m "feat(council): add schema calibration runner"
```

### Task 6: Add calibration artifact writing

**Files:**
- Modify: `growing_wiki_council/artifacts.py`
- Test: `tests/council/test_calibration_artifacts.py`

**Step 1: Write the failing test**

```python
from pathlib import Path

from growing_wiki_council.artifacts import write_schema_calibration_artifacts
from growing_wiki_council.models.calibration import SchemaCalibrationResult


def test_write_schema_calibration_artifacts_creates_debug_output(tmp_path: Path) -> None:
    result = SchemaCalibrationResult(
        success=True,
        run_label="schema-calibration",
        validation_error=None,
        raw_response={"role": "claim_extractor"},
        validated_report=None,
    )
    output_dir = tmp_path / "calibration"
    write_schema_calibration_artifacts(output_dir, result)
    assert (output_dir / "calibration.json").exists()
    assert (output_dir / "raw-response.json").exists()
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/council/test_calibration_artifacts.py -v`

Expected: FAIL with missing calibration artifact writer

**Step 3: Write minimal implementation**

Add `write_schema_calibration_artifacts(...)` that writes:

- `calibration.json`
- `raw-response.json`
- optionally `validated-report.json` when validation succeeded

Keep file names explicit and deterministic.

**Step 4: Run test to verify it passes**

Run: `pytest tests/council/test_calibration_artifacts.py -v`

Expected: PASS

**Step 5: Commit**

```bash
git add growing_wiki_council/artifacts.py tests/council/test_calibration_artifacts.py
git commit -m "feat(council): add schema calibration artifacts"
```

### Task 7: Add a Python-callable live calibration entrypoint

**Files:**
- Modify: `growing_wiki_council/cli.py`
- Test: `tests/council/test_cli_schema_calibration.py`

**Step 1: Write the failing test**

```python
from pathlib import Path

from growing_wiki_council.cli import run_schema_calibration_once


class FakeAgent:
    def run(self, bundle):
        return {
            "role": "claim_extractor",
            "summary": "Claims extracted.",
            "findings": [],
            "claims": [{"claim": "A", "evidence_refs": ["section:full_text"]}],
        }


def test_run_schema_calibration_once_writes_outputs(tmp_path: Path) -> None:
    output_dir = tmp_path / "calibration"
    result = run_schema_calibration_once(
        claim_extractor=FakeAgent(),
        output_dir=output_dir,
        run_label="schema-calibration",
    )
    assert result.success is True
    assert (output_dir / "calibration.json").exists()
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/council/test_cli_schema_calibration.py -v`

Expected: FAIL with missing entrypoint

**Step 3: Write minimal implementation**

Add `run_schema_calibration_once(...)` that:

- delegates to `run_schema_calibration(...)`
- writes schema calibration artifacts
- returns the `SchemaCalibrationResult`

Do not add command-line argument parsing yet.

**Step 4: Run test to verify it passes**

Run: `pytest tests/council/test_cli_schema_calibration.py -v`

Expected: PASS

**Step 5: Commit**

```bash
git add growing_wiki_council/cli.py tests/council/test_cli_schema_calibration.py
git commit -m "feat(council): add schema calibration entrypoint"
```

### Task 8: Add a no-network smoke test and document the calibration flow

**Files:**
- Modify: `README.md`
- Create: `tests/council/test_schema_calibration_smoke.py`

**Step 1: Write the failing test**

```python
def test_schema_calibration_placeholder() -> None:
    assert False, "replace with a schema calibration smoke test"
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/council/test_schema_calibration_smoke.py -v`

Expected: FAIL

**Step 3: Write minimal implementation**

Replace the placeholder with a smoke test that uses:

- the deterministic calibration bundle
- a fake claim extractor
- the real calibration runner
- the real calibration artifact writer

Update `README.md` with:

- purpose of the schema calibration path
- required `OPENROUTER_API_KEY`
- how to run the calibration path from Python
- what success means
- what files to inspect on failure

Be explicit that this phase tests schema reliability, not claim quality.

**Step 4: Run test to verify it passes**

Run: `pytest tests/council/test_schema_calibration_smoke.py -v`

Expected: PASS

**Step 5: Run broader verification**

Run:

```bash
pytest tests/council -v
pytest -v
```

Expected:

- the expanded council suite PASS
- existing repo tests remain green

**Step 6: Commit**

```bash
git add README.md tests/council/test_schema_calibration_smoke.py
git commit -m "docs(council): add schema calibration usage and smoke test"
```

## Implementation Notes

- The success criterion for this phase is strict schema validity of the real OpenRouter response, not semantic quality of the claims.
- Keep the fake evidence input deterministic so repeated runs are comparable.
- Preserve raw responses whenever possible. Do not hide parsing or validation failures.
- Keep all live network usage isolated in the OpenRouter client wrapper.
- Do not involve the experimental arXiv client yet.

## Verification Notes

- Tests must stay no-network by using injected fake backends.
- The live calibration run should be Python-callable before any shell CLI UX is added.
- If `uv run ty check .` still fails because `ty` is unavailable, report that as an environment issue rather than a code failure.

Plan complete and saved to `docs/plans/2026-03-20-openrouter-schema-calibration.md`. Two execution options:

**1. Subagent-Driven (this session)** - I dispatch fresh subagent per task, review between tasks, fast iteration

**2. Parallel Session (separate)** - Open new session with executing-plans, batch execution with checkpoints

Which approach?
