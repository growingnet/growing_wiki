# Figure Sources

Editable diagram sources for documentation figures.

## draw.io (`drawio/`)

diagrams.net exports named `<name>.drawio.svg`. Each export uses CSS
`light-dark(light, dark)` for theme-aware colors. The build resolves those
pairs into committed light/dark SVGs in `docs/_static/`:

| Source | Light output | Dark output |
|--------|--------------|-------------|
| `grow-and-prune-pipeline.drawio.svg` | `grow-and-prune-pipeline.svg` | `grow-and-prune-pipeline-dark.svg` |
| `partial-area-convolution.drawio.svg` | `partial-area-convolution.svg` | `partial-area-convolution-dark.svg` |

Regenerate after editing a source:

```bash
scripts/build_figures.sh
# or: make -C docs figures
```

Sphinx embeds the `_static/` outputs (not the `.drawio.svg` files directly).
