# The Growing Wiki

![The Growing Wiki logo](docs/_static/logo.png)

The Growing Wiki is documents methods for growing neural networks during training.

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
