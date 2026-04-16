# Figure Sources

This directory contains source files for reproducible documentation figures.

- `tikz/`: Math-heavy pedagogical diagrams compiled to SVG.
- `dot/`: Graphviz source for process/topology diagrams (`.dot -> .svg`).
- `py/`: Python scripts that generate static figures into `docs/_static/`.

Generated outputs belong in `docs/_static/` and should be built via:

```bash
scripts/build_figures.sh
```

See per-modality readmes for input/output contracts.
