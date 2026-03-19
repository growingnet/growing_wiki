"""CLI entrypoints for the Growing Wiki council."""

from __future__ import annotations

import json
from pathlib import Path


def write_review_artifacts(
    output_dir: Path,
    *,
    review_json: dict,
    review_markdown: str,
) -> None:
    """Persist council review artifacts to disk."""
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "review.json").write_text(
        json.dumps(review_json, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (output_dir / "review.md").write_text(review_markdown, encoding="utf-8")


def main() -> None:
    """Placeholder CLI entrypoint until provider wiring is added."""
    raise SystemExit("CLI execution is not implemented yet.")
