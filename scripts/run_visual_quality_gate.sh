#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FIGURE_NAME="${1:-nest_growth_overview}"
SOURCE_PATH="${ROOT_DIR}/docs/_figures_src/tikz/${FIGURE_NAME}.tex"
SPEC_PATH="${ROOT_DIR}/docs/_figures_src/quality/${FIGURE_NAME}.constraints.json"
REPORT_DIR="${ROOT_DIR}/docs/_build/figure_eval"
REPORT_PATH="${REPORT_DIR}/${FIGURE_NAME}.json"

echo "== Visual quality gate: ${FIGURE_NAME} =="
echo "-- Build figure assets"
"${ROOT_DIR}/scripts/build_figures.sh"

if [[ -f "${SPEC_PATH}" ]]; then
  echo "-- Evaluate TikZ constraints"
  python "${ROOT_DIR}/scripts/eval_tikz_constraints.py" \
    --source "${SOURCE_PATH}" \
    --spec "${SPEC_PATH}" \
    --output "${REPORT_PATH}"
else
  echo "-- No constraints spec found at ${SPEC_PATH}; skipping constraint checks"
fi

echo "-- Strict docs build"
make -C "${ROOT_DIR}/docs" stricthtml

echo "Quality gate passed."
if [[ -f "${REPORT_PATH}" ]]; then
  echo "Layout report: ${REPORT_PATH}"
fi

