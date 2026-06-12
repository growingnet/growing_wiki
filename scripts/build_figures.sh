#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
python_cmd=""
if command -v python3 >/dev/null 2>&1; then
  python_cmd="python3"
elif command -v python >/dev/null 2>&1; then
  python_cmd="python"
else
  echo "Missing dependency for figure build: python3 or python" >&2
  exit 1
fi

"${python_cmd}" "${ROOT_DIR}/scripts/build_drawio_figures.py"
