"""CLI entrypoints for the Growing Wiki council."""

from __future__ import annotations

from pathlib import Path

from growing_wiki_council.artifacts import write_review_artifacts
from growing_wiki_council.services.vertical_slice import run_claim_extraction_slice


def run_vertical_slice(
    *,
    source: str,
    provider,
    claim_extractor,
    output_dir: Path,
):
    """Delegate a single-paper claim-extraction run to the slice service."""
    return run_claim_extraction_slice(
        source=source,
        provider=provider,
        claim_extractor=claim_extractor,
        output_dir=output_dir,
    )


def main() -> None:
    """Placeholder CLI entrypoint until provider wiring is added."""
    raise SystemExit("CLI execution is not implemented yet.")
