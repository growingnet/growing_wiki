# Figure Sources

This directory contains source files for reproducible documentation figures.

- `tikz/`: Math-heavy pedagogical diagrams compiled to SVG. Light-theme figures use
  base names (e.g. `example.tex` → `example.svg`); optional dark-theme companions
  use a `-dark` suffix for `only-dark` / `only-light` pairs in Sphinx.
- `dot/`: Graphviz source for process/topology diagrams (`.dot -> .svg`).
- `drawio/`: diagrams.net exports (e.g.\ `grow-and-prune-pipeline.drawio.svg`,
  `partial-area-convolution.drawio.svg` → paired light/dark SVGs in
  `docs/_static/` by resolving `light-dark()` in the export).
- `py/`: Python scripts that generate static figures into `docs/_static/`.

Generated outputs belong in `docs/_static/` and should be built via:

```bash
scripts/build_figures.sh
```

See per-modality readmes for input/output contracts.
