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

### Install dependencies

With python 3.11, install

```bash
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

To rebuild automatically while editing locally after installing the
requirements, run `make -C docs livehtml`. Rendered html is served locally at
`http://127.0.0.1:8000`.

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

The CI requires that Sphinx build results in no errors or warnings. To run this check manually run

```bash
pre-commit run --all-files
```

To enforce the check automatically on every local commit, run `pre-commit install`.
