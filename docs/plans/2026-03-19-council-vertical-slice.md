# Council Vertical Slice Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use executing-plans skill to implement this plan task-by-task.

**Goal:** Build and verify the first real end-to-end council slice: one real arXiv-backed paper retrieval path, one real OpenRouter-backed reviewer, and persisted review artifacts.

**Architecture:** Keep the scope intentionally narrow. Extend the existing council package with a real arXiv client interface, a real OpenRouter-backed `claim_extractor`, and a small orchestrated path that runs provider -> evidence builder -> one real reviewer -> artifact writer. Reuse the current provider, evidence, and review schemas so the first real integration validates architecture rather than broadening it.

**Tech Stack:** Python 3.11+, Pydantic, PydanticAI, httpx, pytest, OpenRouter, existing `growing_wiki_council` package

---

### Task 1: Expand configuration for the first real runtime

**Files:**
- Modify: `growing_wiki_council/config.py`
- Test: `tests/council/test_config.py`

**Step 1: Write the failing test**

```python
from growing_wiki_council.config import CouncilConfig


def test_council_config_exposes_openrouter_model_defaults() -> None:
    config = CouncilConfig(
        openrouter_api_key="test-key",
        openrouter_base_url="https://openrouter.ai/api/v1",
        claim_extractor_model="openrouter/openai/gpt-4.1-mini",
    )
    assert config.claim_extractor_model == "openrouter/openai/gpt-4.1-mini"
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/council/test_config.py -v`

Expected: FAIL with a validation error or missing field on `CouncilConfig`

**Step 3: Write minimal implementation**

Add fields to `CouncilConfig`:

- `openrouter_api_key: str`
- `openrouter_base_url: str = "https://openrouter.ai/api/v1"`
- `claim_extractor_model: str`
- `request_timeout_seconds: float = 60.0`

Keep the config model small and runtime-focused. Do not add council-wide model routing yet.

**Step 4: Run test to verify it passes**

Run: `pytest tests/council/test_config.py -v`

Expected: PASS

**Step 5: Commit**

```bash
git add growing_wiki_council/config.py tests/council/test_config.py
git commit -m "feat(council): expand runtime config for vertical slice"
```

### Task 2: Define the real arXiv client contract and failure surface

**Files:**
- Create: `growing_wiki_council/clients/arxiv_client.py`
- Create: `growing_wiki_council/clients/__init__.py`
- Test: `tests/council/test_arxiv_client_contract.py`

**Step 1: Write the failing test**

```python
from growing_wiki_council.clients.arxiv_client import ArxivPaperClientProtocol


def test_arxiv_client_protocol_exposes_required_methods() -> None:
    required_methods = ["get_paper", "extract_equations", "get_bibliography"]
    for method_name in required_methods:
        assert hasattr(ArxivPaperClientProtocol, method_name)
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/council/test_arxiv_client_contract.py -v`

Expected: FAIL with missing client contract module

**Step 3: Write minimal implementation**

Create a client-side protocol that the adapter will consume:

- `get_paper(arxiv_id: str) -> dict`
- `extract_equations(arxiv_id: str) -> list[dict]`
- `get_bibliography(arxiv_id: str) -> list[dict] | dict`

Also create one explicit exception class for client-level retrieval failures:

- `ArxivClientError`

Do not wire the MCP transport yet. This task only freezes the interface.

**Step 4: Run test to verify it passes**

Run: `pytest tests/council/test_arxiv_client_contract.py -v`

Expected: PASS

**Step 5: Commit**

```bash
git add growing_wiki_council/clients/__init__.py growing_wiki_council/clients/arxiv_client.py tests/council/test_arxiv_client_contract.py
git commit -m "feat(council): add arxiv client contract"
```

### Task 3: Harden the arXiv adapter for real client responses

**Files:**
- Modify: `growing_wiki_council/providers/arxiv.py`
- Test: `tests/council/test_arxiv_provider_real_mapping.py`

**Step 1: Write the failing test**

```python
from growing_wiki_council.providers.arxiv import ArxivLatexProvider


class FakeRealClient:
    def get_paper(self, arxiv_id: str) -> dict:
        return {
            "arxiv_id": arxiv_id,
            "title": "Sample",
            "content": "Sectioned text",
            "source_type": "pdf",
            "fallback_used": True,
            "fallback_reason": "201: No source available",
            "warnings": ["Used PDF fallback"],
        }

    def extract_equations(self, arxiv_id: str) -> list[dict]:
        return [{"equation_id": "eq_1", "latex": "x+y", "section_context": "Results"}]

    def get_bibliography(self, arxiv_id: str) -> dict:
        return {"entries": [{"key": "smith2024", "citation": "Smith et al. (2024)."}]}


def test_arxiv_provider_maps_real_client_payloads() -> None:
    provider = ArxivLatexProvider(client=FakeRealClient())
    result = provider.load("1234.56789")
    assert result.source_kind == "arxiv_pdf"
    assert result.fallback_used is True
    assert result.equations[0].latex == "x+y"
    assert result.bibliography[0].key == "smith2024"
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/council/test_arxiv_provider_real_mapping.py -v`

Expected: FAIL because the adapter does not yet coerce real equation and bibliography payloads into schema models

**Step 3: Write minimal implementation**

Update `ArxivLatexProvider` so it:

- accepts the new client protocol
- keeps core retrieval required
- treats equation and bibliography enrichment as best-effort
- converts equation dicts into `EvidenceEquation`
- converts bibliography dict payloads into `EvidenceBibliographyEntry`
- supports bibliography responses shaped as either:
  - `{"entries": [...]}`
  - `[...]`

Do not add MCP transport code here.

**Step 4: Run test to verify it passes**

Run: `pytest tests/council/test_arxiv_provider_real_mapping.py -v`

Expected: PASS

**Step 5: Run regression checks**

Run: `pytest tests/council/test_arxiv_provider.py tests/council/test_arxiv_provider_real_mapping.py -v`

Expected: PASS

**Step 6: Commit**

```bash
git add growing_wiki_council/providers/arxiv.py tests/council/test_arxiv_provider_real_mapping.py
git commit -m "feat(council): harden arxiv adapter for real payloads"
```

### Task 4: Add a real claim extractor agent wrapper

**Files:**
- Modify: `growing_wiki_council/agents.py`
- Test: `tests/council/test_claim_extractor_agent.py`

**Step 1: Write the failing test**

```python
from growing_wiki_council.agents import ClaimExtractorAgent
from growing_wiki_council.config import CouncilConfig


def test_claim_extractor_agent_exposes_run_method() -> None:
    agent = ClaimExtractorAgent(
        config=CouncilConfig(
            openrouter_api_key="test-key",
            openrouter_base_url="https://openrouter.ai/api/v1",
            claim_extractor_model="openrouter/openai/gpt-4.1-mini",
        ),
        model_backend=object(),
    )
    assert callable(agent.run)
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/council/test_claim_extractor_agent.py -v`

Expected: FAIL with missing agent implementation

**Step 3: Write minimal implementation**

Add a real wrapper class:

- `ClaimExtractorAgent`

Constructor inputs:

- `config: CouncilConfig`
- `model_backend: Any | None = None`

Implementation rules:

- expose `run(bundle: EvidenceBundle) -> ReviewerReport`
- keep prompt construction local to this class
- allow dependency injection of the underlying model backend for tests
- if no backend is injected, create one from config

Do not add the rest of the council roles yet.

**Step 4: Run test to verify it passes**

Run: `pytest tests/council/test_claim_extractor_agent.py -v`

Expected: PASS

**Step 5: Commit**

```bash
git add growing_wiki_council/agents.py tests/council/test_claim_extractor_agent.py
git commit -m "feat(council): add claim extractor agent wrapper"
```

### Task 5: Add a fakeable OpenRouter-backed model gateway

**Files:**
- Create: `growing_wiki_council/clients/openrouter_client.py`
- Modify: `growing_wiki_council/clients/__init__.py`
- Test: `tests/council/test_openrouter_client.py`

**Step 1: Write the failing test**

```python
from growing_wiki_council.clients.openrouter_client import OpenRouterClaimExtractorClient


class FakeBackend:
    def extract_claims(self, prompt: str) -> dict:
        return {
            "role": "claim_extractor",
            "summary": "Claims extracted.",
            "findings": [],
            "claims": [{"claim": "A", "evidence_refs": ["section:full_text"]}],
        }


def test_openrouter_claim_client_uses_injected_backend() -> None:
    client = OpenRouterClaimExtractorClient(backend=FakeBackend())
    report = client.run_prompt("prompt")
    assert report["role"] == "claim_extractor"
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/council/test_openrouter_client.py -v`

Expected: FAIL with missing client module

**Step 3: Write minimal implementation**

Create:

- `OpenRouterClaimExtractorClient`

Behavior:

- if a backend is injected, delegate to it
- otherwise initialize a real OpenRouter-compatible model call path
- expose a single method:
  - `run_prompt(prompt: str) -> dict`

The real path should be isolated behind this client so tests never depend on the network.

**Step 4: Run test to verify it passes**

Run: `pytest tests/council/test_openrouter_client.py -v`

Expected: PASS

**Step 5: Commit**

```bash
git add growing_wiki_council/clients/__init__.py growing_wiki_council/clients/openrouter_client.py tests/council/test_openrouter_client.py
git commit -m "feat(council): add openrouter claim client"
```

### Task 6: Connect the claim extractor agent to the model gateway

**Files:**
- Modify: `growing_wiki_council/agents.py`
- Test: `tests/council/test_claim_extractor_integration.py`

**Step 1: Write the failing test**

```python
from growing_wiki_council.agents import ClaimExtractorAgent
from growing_wiki_council.config import CouncilConfig
from growing_wiki_council.models.evidence import EvidenceBundle


class FakeGateway:
    def run_prompt(self, prompt: str) -> dict:
        return {
            "role": "claim_extractor",
            "summary": "Claims extracted.",
            "findings": [],
            "claims": [{"claim": "A", "evidence_refs": ["section:full_text"]}],
        }


def test_claim_extractor_agent_returns_reviewer_report() -> None:
    bundle = EvidenceBundle(
        paper_id="paper-1",
        source_kind="generic_pdf",
        title="Paper",
        sections=[],
        equations=[],
        bibliography=[],
        warnings=[],
        extraction_confidence="medium",
    )
    agent = ClaimExtractorAgent(
        config=CouncilConfig(
            openrouter_api_key="test-key",
            openrouter_base_url="https://openrouter.ai/api/v1",
            claim_extractor_model="openrouter/openai/gpt-4.1-mini",
        ),
        model_backend=FakeGateway(),
    )
    report = agent.run(bundle)
    assert report.role == "claim_extractor"
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/council/test_claim_extractor_integration.py -v`

Expected: FAIL because the agent is not yet wired to the OpenRouter client path

**Step 3: Write minimal implementation**

Update `ClaimExtractorAgent` so it:

- builds a prompt from the evidence bundle
- calls the OpenRouter client wrapper
- validates the returned dict into `ReviewerReport`

Keep the prompt simple:

- paper identifier
- title
- source kind
- extraction confidence
- section names and content

Do not optimize prompt wording yet.

**Step 4: Run test to verify it passes**

Run: `pytest tests/council/test_claim_extractor_integration.py -v`

Expected: PASS

**Step 5: Run regression checks**

Run: `pytest tests/council/test_claim_extractor_agent.py tests/council/test_claim_extractor_integration.py tests/council/test_review_runner.py -v`

Expected: PASS

**Step 6: Commit**

```bash
git add growing_wiki_council/agents.py tests/council/test_claim_extractor_integration.py
git commit -m "feat(council): wire claim extractor to model gateway"
```

### Task 7: Add a vertical-slice service that runs one real reviewer

**Files:**
- Create: `growing_wiki_council/services/vertical_slice.py`
- Modify: `growing_wiki_council/services/__init__.py`
- Test: `tests/council/test_vertical_slice.py`

**Step 1: Write the failing test**

```python
from pathlib import Path

from growing_wiki_council.services.vertical_slice import run_claim_extraction_slice


class FakeProvider:
    def load(self, source: str):
        ...


class FakeAgent:
    def run(self, bundle):
        ...


def test_vertical_slice_writes_artifacts(tmp_path: Path) -> None:
    output_dir = tmp_path / "artifacts"
    run_claim_extraction_slice(
        source="paper-1",
        provider=FakeProvider(),
        claim_extractor=FakeAgent(),
        output_dir=output_dir,
    )
    assert (output_dir / "review.json").exists()
    assert (output_dir / "review.md").exists()
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/council/test_vertical_slice.py -v`

Expected: FAIL with missing service

**Step 3: Write minimal implementation**

Implement `run_claim_extraction_slice(...)` with these steps:

1. `provider.load(source)`
2. `EvidenceBuilder().build(provider_result)`
3. `claim_extractor.run(bundle)`
4. wrap that report into a minimal `CouncilReviewArtifact`
5. call `write_review_artifacts(...)`

The minimal artifact should:

- include one reviewer report
- include a chair verdict with:
  - `verdict="needs_human_review"`
  - summary indicating this is a single-reviewer slice
  - confidence derived from bundle extraction confidence

**Step 4: Run test to verify it passes**

Run: `pytest tests/council/test_vertical_slice.py -v`

Expected: PASS

**Step 5: Commit**

```bash
git add growing_wiki_council/services/__init__.py growing_wiki_council/services/vertical_slice.py tests/council/test_vertical_slice.py
git commit -m "feat(council): add claim extraction vertical slice"
```

### Task 8: Add a real-run CLI path for one paper

**Files:**
- Modify: `growing_wiki_council/cli.py`
- Test: `tests/council/test_cli_vertical_slice.py`

**Step 1: Write the failing test**

```python
from pathlib import Path

from growing_wiki_council.cli import run_vertical_slice


class FakeProvider:
    def load(self, source: str):
        ...


class FakeAgent:
    def run(self, bundle):
        ...


def test_run_vertical_slice_creates_artifacts(tmp_path: Path) -> None:
    output_dir = tmp_path / "artifacts"
    run_vertical_slice(
        source="paper-1",
        provider=FakeProvider(),
        claim_extractor=FakeAgent(),
        output_dir=output_dir,
    )
    assert (output_dir / "review.json").exists()
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/council/test_cli_vertical_slice.py -v`

Expected: FAIL with missing function

**Step 3: Write minimal implementation**

Add:

- `run_vertical_slice(...)`

Inputs:

- `source: str`
- `provider`
- `claim_extractor`
- `output_dir: Path`

This function should delegate to `run_claim_extraction_slice(...)`.

Do not add `argparse` or shell parsing yet unless it is trivial once this function exists.

**Step 4: Run test to verify it passes**

Run: `pytest tests/council/test_cli_vertical_slice.py -v`

Expected: PASS

**Step 5: Commit**

```bash
git add growing_wiki_council/cli.py tests/council/test_cli_vertical_slice.py
git commit -m "feat(council): add vertical slice cli entry"
```

### Task 9: Add a non-network smoke test for the real slice and document it

**Files:**
- Modify: `README.md`
- Create: `tests/council/test_vertical_slice_smoke.py`

**Step 1: Write the failing test**

```python
def test_vertical_slice_placeholder() -> None:
    assert False, "replace with a vertical-slice smoke test"
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/council/test_vertical_slice_smoke.py -v`

Expected: FAIL

**Step 3: Write minimal implementation**

Replace the placeholder with a smoke test that uses:

- a fake arXiv provider result
- a fake claim extractor
- the real vertical-slice service
- the real artifact writer

Update `README.md` with:

- required environment variables for the future real OpenRouter run
- how to inject an MCP-compatible arXiv client
- how to invoke the vertical-slice function from Python
- a reminder that only claim extraction is real in this slice and the chair verdict is synthetic

**Step 4: Run test to verify it passes**

Run: `pytest tests/council/test_vertical_slice_smoke.py -v`

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
git add README.md tests/council/test_vertical_slice_smoke.py
git commit -m "docs(council): add vertical slice usage and smoke test"
```

## Implementation Notes

- Keep the MCP server out of scope. The council code should depend only on an injected client contract. If the real MCP integration is blocked, stop and emit a ticket-ready message instead of patching the MCP repo.
- Keep all network-dependent code behind fakeable clients.
- Only the claim extractor should be real in this slice. Other reviewer roles should remain unimplemented.
- Prefer a Python-callable vertical slice before building a full CLI UX.
- Keep prompts simple and explicit; optimize later with evaluation data.

## Blocking Conditions for MCP Integration

If any of these are missing from the injected arXiv client in a way that prevents the vertical slice from running, stop and open a ticket for the MCP maintainer:

- retrieval of paper content
- stable source provenance (`latex` or `pdf`)
- fallback flags (`fallback_used`, `fallback_reason`)
- predictable bibliography/equation response shape, or at least safe empty results

## Verification Notes

- Do not require live network calls in tests.
- Treat OpenRouter integration as dependency-injected so tests remain deterministic.
- If `uv run ty check .` still fails because `ty` is unavailable, report that as an environment issue rather than a code failure.

Plan complete and saved to `docs/plans/2026-03-19-council-vertical-slice.md`. Two execution options:

**1. Subagent-Driven (this session)** - I dispatch fresh subagent per task, review between tasks, fast iteration

**2. Parallel Session (separate)** - Open new session with executing-plans, batch execution with checkpoints

Which approach?
