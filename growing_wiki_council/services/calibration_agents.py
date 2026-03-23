"""Helpers for building model-specific agents during calibration."""

from typing import Any

from growing_wiki_council.agents import ClaimExtractorAgent
from growing_wiki_council.config import CouncilConfig


def build_calibration_claim_extractor(
    *,
    config: CouncilConfig,
    model_id: str,
    model_backend: Any | None = None,
) -> ClaimExtractorAgent:
    """Build a claim extractor with a calibration-specific model override."""
    calibration_config = config.model_copy(update={"claim_extractor_model": model_id})
    return ClaimExtractorAgent(
        config=calibration_config,
        model_backend=model_backend,
    )
