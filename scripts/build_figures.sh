#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TIKZ_SRC_DIR="${ROOT_DIR}/docs/_figures_src/tikz"
DOT_SRC_DIR="${ROOT_DIR}/docs/_figures_src/dot"
PY_SRC_DIR="${ROOT_DIR}/docs/_figures_src/py"
OUT_DIR="${ROOT_DIR}/docs/_static"
BUILD_DIR="${ROOT_DIR}/docs/_build/figures"

mkdir -p "${BUILD_DIR}" "${OUT_DIR}"
shopt -s nullglob

had_work=0

# ----------------------------
# TikZ (.tex) -> PDF -> SVG
# ----------------------------
tex_files=("${TIKZ_SRC_DIR}"/*.tex)
if [ ${#tex_files[@]} -gt 0 ]; then
  had_work=1
  if ! command -v pdflatex >/dev/null 2>&1; then
    echo "Missing dependency for TikZ build: pdflatex" >&2
    exit 1
  fi
  if ! command -v pdftocairo >/dev/null 2>&1; then
    echo "Missing dependency for TikZ build: pdftocairo" >&2
    exit 1
  fi

  for tex_file in "${tex_files[@]}"; do
    base_name="$(basename "${tex_file}" .tex)"
    pdf_file="${BUILD_DIR}/${base_name}.pdf"
    svg_file="${OUT_DIR}/${base_name}.svg"

    echo "Building TikZ: ${base_name}.tex -> ${base_name}.svg"
    pdflatex -interaction=nonstopmode -halt-on-error -output-directory "${BUILD_DIR}" "${tex_file}" >/dev/null
    pdftocairo -svg "${pdf_file}" "${svg_file}"
  done
fi

# ----------------------------
# Graphviz (.dot) -> SVG
# ----------------------------
dot_files=("${DOT_SRC_DIR}"/*.dot)
if [ ${#dot_files[@]} -gt 0 ]; then
  had_work=1
  if ! command -v dot >/dev/null 2>&1; then
    echo "Missing dependency for Graphviz build: dot" >&2
    exit 1
  fi

  for dot_file in "${dot_files[@]}"; do
    base_name="$(basename "${dot_file}" .dot)"
    svg_file="${OUT_DIR}/${base_name}.svg"
    echo "Building Graphviz: ${base_name}.dot -> ${base_name}.svg"
    dot -Tsvg "${dot_file}" -o "${svg_file}"
  done
fi

# ----------------------------
# Python generators (.py)
# Contract:
#   python script.py --out-dir <OUT_DIR>
# or use FIGURE_OUT_DIR environment variable.
# ----------------------------
py_files=("${PY_SRC_DIR}"/*.py)
if [ ${#py_files[@]} -gt 0 ]; then
  had_work=1
  if ! command -v python >/dev/null 2>&1; then
    echo "Missing dependency for Python figure build: python" >&2
    exit 1
  fi

  for py_file in "${py_files[@]}"; do
    base_name="$(basename "${py_file}")"
    echo "Building Python figure(s): ${base_name}"
    FIGURE_OUT_DIR="${OUT_DIR}" python "${py_file}" --out-dir "${OUT_DIR}"
  done
fi

if [ "${had_work}" -eq 0 ]; then
  echo "No figure sources found in ${ROOT_DIR}/docs/_figures_src/{tikz,dot,py}"
  exit 0
fi

echo "Figure build completed successfully."
