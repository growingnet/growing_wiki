# Python Figure Generators

Put Python scripts that generate static figure assets in this directory.

Build contract for each script:

- The script must accept `--out-dir <path>`.
- The script may also read `FIGURE_OUT_DIR`.
- The script writes one or more assets into `docs/_static/`.

The shared builder invokes scripts through:

```bash
FIGURE_OUT_DIR=docs/_static python docs/_figures_src/py/<script>.py --out-dir docs/_static
```

Prefer deterministic outputs and stable filenames.
