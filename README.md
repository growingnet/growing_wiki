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

### Environment

For the eventual real model runtime, set:

```bash
export OPENROUTER_API_KEY=your-key
```

The current checked-in scaffolding does not yet call OpenRouter directly; it
defines the contract that later agent integrations will use.

### Library Entry Examples

For an arXiv-backed run, inject an MCP-compatible client into the adapter:

```python
from growing_wiki_council.providers.arxiv import ArxivLatexProvider
from growing_wiki_council.services.evidence_builder import EvidenceBuilder

provider = ArxivLatexProvider(client=my_arxiv_client)
provider_result = provider.load("1511.05641")
bundle = EvidenceBuilder().build(provider_result)
```

For a PDF-backed run:

```python
from pathlib import Path

from growing_wiki_council.providers.pdf import GenericPdfProvider
from growing_wiki_council.services.evidence_builder import EvidenceBuilder

provider_result = GenericPdfProvider().load(Path("paper.pdf"))
bundle = EvidenceBuilder().build(provider_result)
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

### Current Limitations

- The CLI entrypoint is still a placeholder; the current integration surface is
  the Python package API.
- `GenericPdfProvider` validates inputs but does not yet parse PDFs.
- `ArxivLatexProvider` is an adapter around an injected client and does not
  implement MCP communication itself.
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
