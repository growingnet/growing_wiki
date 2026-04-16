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
stale_count=0

# Helper: check whether a committed SVG is older than its source.
# Prints a warning per stale file; increments stale_count.
check_freshness() {
  local src_file="$1" svg_file="$2"
  if [ -f "${svg_file}" ] && [ "${src_file}" -nt "${svg_file}" ]; then
    echo "WARNING: ${src_file##"${ROOT_DIR}"/} is newer than ${svg_file##"${ROOT_DIR}"/} — SVG may be stale" >&2
    stale_count=$((stale_count + 1))
  fi
}

# Helper: true if every source in a list has a corresponding SVG already.
all_outputs_exist() {
  local ext="$1"; shift
  for src in "$@"; do
    local base
    base="$(basename "${src}" ".${ext}")"
    [ -f "${OUT_DIR}/${base}.svg" ] || return 1
  done
  return 0
}

# ----------------------------
# TikZ (.tex) -> PDF -> SVG
# ----------------------------
tex_files=("${TIKZ_SRC_DIR}"/*.tex)
if [ ${#tex_files[@]} -gt 0 ]; then
  had_work=1
  has_pdflatex=true
  has_pdftocairo=true
  command -v pdflatex  >/dev/null 2>&1 || has_pdflatex=false
  command -v pdftocairo >/dev/null 2>&1 || has_pdftocairo=false

  if $has_pdflatex && $has_pdftocairo; then
    for tex_file in "${tex_files[@]}"; do
      base_name="$(basename "${tex_file}" .tex)"
      pdf_file="${BUILD_DIR}/${base_name}.pdf"
      svg_file="${OUT_DIR}/${base_name}.svg"
      echo "Building TikZ: ${base_name}.tex -> ${base_name}.svg"
      pdflatex -interaction=nonstopmode -halt-on-error -output-directory "${BUILD_DIR}" "${tex_file}" >/dev/null
      pdftocairo -svg "${pdf_file}" "${svg_file}"
    done
  elif all_outputs_exist tex "${tex_files[@]}"; then
    echo "TikZ tools not found (pdflatex/pdftocairo) — using committed SVGs." >&2
    for tex_file in "${tex_files[@]}"; do
      base_name="$(basename "${tex_file}" .tex)"
      check_freshness "${tex_file}" "${OUT_DIR}/${base_name}.svg"
    done
  else
    echo "ERROR: TikZ tools not found and some SVGs are missing:" >&2
    for tex_file in "${tex_files[@]}"; do
      base_name="$(basename "${tex_file}" .tex)"
      [ -f "${OUT_DIR}/${base_name}.svg" ] || echo "  missing: ${OUT_DIR}/${base_name}.svg" >&2
    done
    echo "Install pdflatex and pdftocairo, or commit the SVGs." >&2
    exit 1
  fi
fi

# ----------------------------
# Graphviz (.dot) -> SVG
# ----------------------------
dot_files=("${DOT_SRC_DIR}"/*.dot)
if [ ${#dot_files[@]} -gt 0 ]; then
  had_work=1
  if command -v dot >/dev/null 2>&1; then
    for dot_file in "${dot_files[@]}"; do
      base_name="$(basename "${dot_file}" .dot)"
      svg_file="${OUT_DIR}/${base_name}.svg"
      echo "Building Graphviz: ${base_name}.dot -> ${base_name}.svg"
      dot -Tsvg "${dot_file}" -o "${svg_file}"
    done
  elif all_outputs_exist dot "${dot_files[@]}"; then
    echo "Graphviz not found — using committed SVGs." >&2
    for dot_file in "${dot_files[@]}"; do
      base_name="$(basename "${dot_file}" .dot)"
      check_freshness "${dot_file}" "${OUT_DIR}/${base_name}.svg"
    done
  else
    echo "ERROR: Graphviz not found and some SVGs are missing:" >&2
    for dot_file in "${dot_files[@]}"; do
      base_name="$(basename "${dot_file}" .dot)"
      [ -f "${OUT_DIR}/${base_name}.svg" ] || echo "  missing: ${OUT_DIR}/${base_name}.svg" >&2
    done
    echo "Install graphviz, or commit the SVGs." >&2
    exit 1
  fi
fi

# ----------------------------
# Python generators (.py)
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

if [ "${stale_count}" -gt 0 ]; then
  echo "WARNING: ${stale_count} SVG(s) may be stale — regenerate with TeX tools and commit." >&2
fi

echo "Figure build completed successfully."
