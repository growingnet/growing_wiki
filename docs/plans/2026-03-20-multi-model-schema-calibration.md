# Multi-Model Schema Calibration Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use executing-plans skill to implement this plan task-by-task.

**Goal:** Add a calibration-only multi-model runner that executes the same schema-calibration flow against two pinned OpenRouter models and writes artifacts into separate per-model directories.

**Architecture:** Reuse the existing single-model calibration path as the inner loop. Add a small multi-model orchestration layer above it, plus minimal config and artifact support, while keeping the main council claim-extraction path single-model.

**Tech Stack:** Python 3.11+, Pydantic, pytest, existing `growing_wiki_council` package, OpenRouter

---

### Task 1: Add calibration model list config

**Files:**
- Modify: `growing_wiki_council/config.py`
- Test: `tests/council/test_config.py`

**Step 1: Write the failing test**

```python
def test_council_config_exposes_multi_model_calibration_defaults() -> None:
    config = CouncilConfig(
        openrouter_api_key="test-key",
        claim_extractor_model="openrouter/openai/gpt-4.1-mini",
    )
    assert config.calibration_model_ids == [
        "nvidia/nemotron-3-super-120b-a12b:free",
        "stepfun/step-3.5-flash:free",
    ]
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/council/test_config.py::test_council_config_exposes_multi_model_calibration_defaults -v`

Expected: FAIL with missing `calibration_model_ids`

**Step 3: Write minimal implementation**

Add to `CouncilConfig`:

```python
calibration_model_ids: list[str] = Field(
    default_factory=lambda: [
        "nvidia/nemotron-3-super-120b-a12b:free",
        "stepfun/step-3.5-flash:free",
    ]
)
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/council/test_config.py::test_council_config_exposes_multi_model_calibration_defaults -v`

Expected: PASS

**Step 5: Commit**

```bash
git add growing_wiki_council/config.py tests/council/test_config.py
git commit -m "feat(council): add multi-model calibration defaults"
```

### Task 2: Add a model slug helper for artifact directories

**Files:**
- Create: `growing_wiki_council/services/model_slug.py`
- Modify: `growing_wiki_council/services/__init__.py`
- Test: `tests/council/test_model_slug.py`

**Step 1: Write the failing test**

```python
from growing_wiki_council.services.model_slug import model_id_to_slug


def test_model_id_to_slug_normalizes_openrouter_model_ids() -> None:
    assert (
        model_id_to_slug("nvidia/nemotron-3-super-120b-a12b:free")
        == "nvidia-nemotron-3-super-120b-a12b-free"
    )
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/council/test_model_slug.py -v`

Expected: FAIL with missing helper

**Step 3: Write minimal implementation**

Create a helper that:

- lowercases the model ID
- replaces `/`, `:`, and `.` with `-`
- collapses repeated separators

**Step 4: Run test to verify it passes**

Run: `pytest tests/council/test_model_slug.py -v`

Expected: PASS

**Step 5: Commit**

```bash
git add growing_wiki_council/services/model_slug.py growing_wiki_council/services/__init__.py tests/council/test_model_slug.py
git commit -m "feat(council): add model slug helper"
```

### Task 3: Add multi-model calibration result models

**Files:**
- Modify: `growing_wiki_council/models/calibration.py`
- Modify: `growing_wiki_council/models/__init__.py`
- Test: `tests/council/test_calibration_models.py`

**Step 1: Write the failing test**

```python
from growing_wiki_council.models.calibration import MultiModelCalibrationResult


def test_multi_model_calibration_result_tracks_per_model_runs() -> None:
    result = MultiModelCalibrationResult(
        run_label="schema-calibration",
        model_runs={"model-a": {"success": True, "run_label": "schema-calibration"}},
    )
    assert "model-a" in result.model_runs
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/council/test_calibration_models.py -v`

Expected: FAIL with missing model

**Step 3: Write minimal implementation**

Add:

- `ModelCalibrationRun` with:
  - `model_id: str`
  - `output_dir: str`
  - `result: SchemaCalibrationResult`
- `MultiModelCalibrationResult` with:
  - `run_label: str`
  - `model_runs: list[ModelCalibrationRun]`

Keep fields JSON-friendly.

**Step 4: Run test to verify it passes**

Run: `pytest tests/council/test_calibration_models.py -v`

Expected: PASS

**Step 5: Commit**

```bash
git add growing_wiki_council/models/calibration.py growing_wiki_council/models/__init__.py tests/council/test_calibration_models.py
git commit -m "feat(council): add multi-model calibration models"
```

### Task 4: Add a factory for per-model claim extractors

**Files:**
- Create: `growing_wiki_council/services/calibration_agents.py`
- Modify: `growing_wiki_council/services/__init__.py`
- Test: `tests/council/test_calibration_agents.py`

**Step 1: Write the failing test**

```python
from growing_wiki_council.config import CouncilConfig
from growing_wiki_council.services.calibration_agents import build_calibration_claim_extractor


def test_build_calibration_claim_extractor_overrides_model_id() -> None:
    config = CouncilConfig(
        openrouter_api_key="test-key",
        claim_extractor_model="model-a",
    )
    agent = build_calibration_claim_extractor(
        config=config,
        model_id="model-b",
        model_backend=object(),
    )
    assert agent.config.claim_extractor_model == "model-b"
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/council/test_calibration_agents.py -v`

Expected: FAIL with missing factory

**Step 3: Write minimal implementation**

Create a helper that:

- clones the existing `CouncilConfig`
- overrides `claim_extractor_model`
- returns a `ClaimExtractorAgent`

Allow backend injection for tests.

**Step 4: Run test to verify it passes**

Run: `pytest tests/council/test_calibration_agents.py -v`

Expected: PASS

**Step 5: Commit**

```bash
git add growing_wiki_council/services/calibration_agents.py growing_wiki_council/services/__init__.py tests/council/test_calibration_agents.py
git commit -m "feat(council): add calibration agent factory"
```

### Task 5: Add the multi-model calibration service

**Files:**
- Create: `growing_wiki_council/services/multi_model_schema_calibration.py`
- Modify: `growing_wiki_council/services/__init__.py`
- Test: `tests/council/test_multi_model_schema_calibration.py`

**Step 1: Write the failing test**

```python
from pathlib import Path

from growing_wiki_council.config import CouncilConfig
from growing_wiki_council.services.multi_model_schema_calibration import (
    run_multi_model_schema_calibration,
)


class FakeAgent:
    def __init__(self, model_id: str) -> None:
        self.model_id = model_id

    def run(self, bundle):
        return {
            "role": "claim_extractor",
            "summary": self.model_id,
            "findings": [],
            "claims": [{"claim": "A", "evidence_refs": ["section:full_text"]}],
        }


def test_run_multi_model_schema_calibration_returns_one_result_per_model(
    tmp_path: Path,
) -> None:
    config = CouncilConfig(
        openrouter_api_key="test-key",
        claim_extractor_model="unused",
        calibration_model_ids=["model-a", "model-b"],
    )
    result = run_multi_model_schema_calibration(
        config=config,
        output_dir=tmp_path,
        run_label="schema-calibration",
        agent_factory=lambda model_id: FakeAgent(model_id),
    )
    assert len(result.model_runs) == 2
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/council/test_multi_model_schema_calibration.py -v`

Expected: FAIL with missing service

**Step 3: Write minimal implementation**

Implement a service that:

- loops over `config.calibration_model_ids`
- builds a model-specific agent
- calls the existing `run_schema_calibration(...)`
- computes a slugged subdirectory
- writes calibration artifacts into that subdirectory
- returns `MultiModelCalibrationResult`

Keep execution sequential in this phase.

**Step 4: Run test to verify it passes**

Run: `pytest tests/council/test_multi_model_schema_calibration.py -v`

Expected: PASS

**Step 5: Commit**

```bash
git add growing_wiki_council/services/multi_model_schema_calibration.py growing_wiki_council/services/__init__.py tests/council/test_multi_model_schema_calibration.py
git commit -m "feat(council): add multi-model schema calibration service"
```

### Task 6: Add a Python entrypoint for the multi-model run

**Files:**
- Modify: `growing_wiki_council/cli.py`
- Test: `tests/council/test_cli_multi_model_schema_calibration.py`

**Step 1: Write the failing test**

```python
from pathlib import Path

from growing_wiki_council.config import CouncilConfig
from growing_wiki_council.cli import run_multi_model_schema_calibration_once


class FakeAgent:
    def __init__(self, model_id: str) -> None:
        self.model_id = model_id

    def run(self, bundle):
        return {
            "role": "claim_extractor",
            "summary": self.model_id,
            "findings": [],
            "claims": [{"claim": "A", "evidence_refs": ["section:full_text"]}],
        }


def test_run_multi_model_schema_calibration_once_writes_model_directories(
    tmp_path: Path,
) -> None:
    config = CouncilConfig(
        openrouter_api_key="test-key",
        claim_extractor_model="unused",
        calibration_model_ids=["model-a", "model-b"],
    )
    result = run_multi_model_schema_calibration_once(
        config=config,
        output_dir=tmp_path,
        run_label="schema-calibration",
        agent_factory=lambda model_id: FakeAgent(model_id),
    )
    assert len(result.model_runs) == 2
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/council/test_cli_multi_model_schema_calibration.py -v`

Expected: FAIL with missing entrypoint

**Step 3: Write minimal implementation**

Add a CLI helper that delegates to the multi-model service and returns
`MultiModelCalibrationResult`.

Do not add shell argument parsing.

**Step 4: Run test to verify it passes**

Run: `pytest tests/council/test_cli_multi_model_schema_calibration.py -v`

Expected: PASS

**Step 5: Commit**

```bash
git add growing_wiki_council/cli.py tests/council/test_cli_multi_model_schema_calibration.py
git commit -m "feat(council): add multi-model calibration entrypoint"
```

### Task 7: Add smoke coverage and docs

**Files:**
- Modify: `README.md`
- Test: `tests/council/test_multi_model_schema_calibration_smoke.py`

**Step 1: Write the failing test**

```python
from pathlib import Path

from growing_wiki_council.config import CouncilConfig
from growing_wiki_council.cli import run_multi_model_schema_calibration_once


class FakeAgent:
    def __init__(self, model_id: str) -> None:
        self.model_id = model_id

    def run(self, bundle):
        return {
            "role": "claim_extractor",
            "summary": self.model_id,
            "findings": [],
            "claims": [{"claim": "A", "evidence_refs": ["section:full_text"]}],
        }


def test_multi_model_schema_calibration_smoke(tmp_path: Path) -> None:
    config = CouncilConfig(
        openrouter_api_key="test-key",
        claim_extractor_model="unused",
        calibration_model_ids=["model-a", "model-b"],
    )
    result = run_multi_model_schema_calibration_once(
        config=config,
        output_dir=tmp_path,
        run_label="schema-calibration",
        agent_factory=lambda model_id: FakeAgent(model_id),
    )
    assert len(result.model_runs) == 2
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/council/test_multi_model_schema_calibration_smoke.py -v`

Expected: FAIL until the helper is documented and wired

**Step 3: Write minimal implementation**

Update README with:

- the two default calibration models
- the purpose of multi-model schema calibration
- the per-model artifact layout
- a Python usage example using `CouncilConfig.from_env(...)`

**Step 4: Run test to verify it passes**

Run: `pytest tests/council/test_multi_model_schema_calibration_smoke.py -v`

Expected: PASS

**Step 5: Run broader verification**

Run:

```bash
pytest tests/council -v
pytest -v
uv run ruff format .
uv run ruff check --fix .
```

Expected:

- council tests PASS
- repo tests PASS
- formatting and lint PASS

**Step 6: Commit**

```bash
git add README.md tests/council/test_multi_model_schema_calibration_smoke.py
git commit -m "docs(council): add multi-model calibration usage and smoke test"
```
