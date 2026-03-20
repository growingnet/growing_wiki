<p align="center">
  <img src="docs/_static/logo.png" alt="The Growing Wiki logo" width="260">
</p>
<p align="center"><strong>The Growing Wiki</strong></p>
<p align="center"><a href="https://growingnet.github.io/growing_wiki">https://growingnet.github.io/growing_wiki</a></p>

The Growing Wiki documents algorithms for growing neural networks during training.

## Repository Layout

- `docs/`: Sphinx source and build configuration
- `docs/overview/`: conceptual and survey-style pages
- `docs/algorithms/`: per-algorithm reference pages
- `docs/applications/`: application-focused pages
- `references.bib`: bibliography used by the docs

## Build Locally

### Prerequisites

- Python 3.10+ (3.11 used in CI)
- `pip`

### Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Build HTML documentation

```bash
make -C docs html
```

Built files will be in:

```text
docs/_build/html
```

## Council Prototype

The repository now includes an early council package under `growing_wiki_council/`.
At this stage it provides:

- provider contracts for arXiv and generic PDF ingestion
- normalized evidence schemas
- deterministic review orchestration
- artifact writing to `review.json` and `review.md`
- a Python-callable vertical slice for one real claim-extraction run

### Environment

For the real claim-extraction runtime, set:

```bash
export OPENROUTER_API_KEY=your-key
```

The current codebase now includes an OpenRouter-backed client wrapper for claim
extraction, but tests still run entirely with injected fake backends.
Keep the key out of tracked files and source code. For live runs, inject it
through the environment and build config with `CouncilConfig.from_env(...)`.
For a portable local setup, you can also create an untracked `.env` file with:

```text
OPENROUTER_API_KEY=your-key
```

The repo includes `.env.example` as a template. `.env` must stay local and must
not be committed.

### Library Entry Examples

For an arXiv-backed run, inject an MCP-compatible client into the adapter:

```python
from growing_wiki_council.providers.arxiv import ArxivLatexProvider
from growing_wiki_council.services.vertical_slice import run_claim_extraction_slice
from growing_wiki_council.agents import ClaimExtractorAgent
from growing_wiki_council.config import CouncilConfig

provider = ArxivLatexProvider(client=my_arxiv_client)
claim_extractor = ClaimExtractorAgent(
    config=CouncilConfig.from_env(
        openrouter_base_url="https://openrouter.ai/api/v1",
        claim_extractor_model="openrouter/openai/gpt-4.1-mini",
    )
)
artifact = run_claim_extraction_slice(
    source="1511.05641",
    provider=provider,
    claim_extractor=claim_extractor,
    output_dir=Path("artifacts"),
)
```

For a PDF-backed run:

```python
from pathlib import Path

from growing_wiki_council.providers.pdf import GenericPdfProvider
from growing_wiki_council.services.vertical_slice import run_claim_extraction_slice
from growing_wiki_council.agents import ClaimExtractorAgent
from growing_wiki_council.config import CouncilConfig

provider = GenericPdfProvider()
claim_extractor = ClaimExtractorAgent(
    config=CouncilConfig.from_env(
        openrouter_base_url="https://openrouter.ai/api/v1",
        claim_extractor_model="openrouter/openai/gpt-4.1-mini",
    )
)
artifact = run_claim_extraction_slice(
    source=str(Path("paper.pdf")),
    provider=provider,
    claim_extractor=claim_extractor,
    output_dir=Path("artifacts"),
)
```

### Artifact Output

```python
from pathlib import Path

from growing_wiki_council.cli import write_review_artifacts

write_review_artifacts(
    Path("artifacts"),
    review_json={"status": "ok"},
    review_markdown="# Review",
)
```

This writes:

```text
artifacts/review.json
artifacts/review.md
```

### Schema Calibration

The schema calibration path is a narrower live-integration check for the
OpenRouter-backed claim extractor. Its purpose is to test schema reliability:
can the model return a payload that validates into `ReviewerReport`? It is not
intended to evaluate claim quality yet.

For a live calibration run, set:

```bash
export OPENROUTER_API_KEY=your-key
```

The current supported entrypoint is the Python API:

```python
from pathlib import Path

from growing_wiki_council.agents import ClaimExtractorAgent
from growing_wiki_council.cli import run_schema_calibration_once
from growing_wiki_council.config import CouncilConfig

claim_extractor = ClaimExtractorAgent(
    config=CouncilConfig.from_env(
        openrouter_base_url="https://openrouter.ai/api/v1",
        claim_extractor_model="openrouter/openai/gpt-4.1-mini",
        calibration_run_label="schema-calibration",
        calibration_output_dir="artifacts/calibration",
    )
)
result = run_schema_calibration_once(
    claim_extractor=claim_extractor,
    output_dir=Path("artifacts/calibration"),
    run_label="schema-calibration",
)
```

Success means:

- `result.success` is `True`
- `artifacts/calibration/calibration.json` exists
- `artifacts/calibration/raw-response.json` exists

On failure, inspect:

- `artifacts/calibration/calibration.json` for `validation_error`
- `artifacts/calibration/raw-response.json` for the provider payload
- `artifacts/calibration/validated-report.json` when validation succeeds

### Current Limitations

- The CLI entrypoint is still a placeholder; the current supported integration
  surface is the Python package API.
- `GenericPdfProvider` validates inputs but does not yet parse PDFs.
- `ArxivLatexProvider` is an adapter around an injected client and does not
  implement MCP communication itself.
- Only claim extraction is wired to a real model-client path in this slice.
- The chair verdict in the vertical slice is synthetic and always marks the run
  as `needs_human_review`.
- Extraction confidence in v1 is heuristic:
  - warnings or fallback paths -> `low`
  - raw-text-only clean inputs -> `medium`
  - structured sections without warnings -> `high`

## Writing Docs

This wiki uses custom prose preprocessing in [`docs/conf.py`](docs/conf.py), so
contributors should not treat the `.rst` files as plain reStructuredText.

- Use `[[Page]]` to link to another page when the page title or docname resolves
  uniquely.
- Use `[[Label|path/to/docname]]` when the target would otherwise be ambiguous or
  when you want explicit control over the destination page.
- Use standard citation roles such as:

  ```rst
  :cite:p:`key`
  ```
- Pages with citations receive a local `References` section automatically during
  the Sphinx build, so you should not add a manual `.. bibliography::` block
  unless you intend to override that behavior.

If a prose change introduces broken or ambiguous wiki links, the Sphinx build
will emit warnings from the custom link resolver in `docs/conf.py`.
