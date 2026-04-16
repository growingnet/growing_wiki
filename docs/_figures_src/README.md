# Figure Sources

This directory contains source files for reproducible documentation figures.

- `tikz/`: Math-heavy pedagogical diagrams compiled to SVG. Light-theme figures use
  base names (e.g. `nest_connection_growth.tex` → `nest_connection_growth.svg`);
  optional dark-theme companions use a `-dark` suffix (e.g.
  `nest_connection_growth-dark.tex` → `nest_connection_growth-dark.svg`) for
  `only-dark` / `only-light` pairs in Sphinx.
- `dot/`: Graphviz source for process/topology diagrams (`.dot -> .svg`).
- `py/`: Python scripts that generate static figures into `docs/_static/`.

Generated outputs belong in `docs/_static/` and should be built via:

```bash
scripts/build_figures.sh
```

See per-modality readmes for input/output contracts.
