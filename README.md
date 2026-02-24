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
