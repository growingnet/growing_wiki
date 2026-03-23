"""Helpers for normalizing model IDs into artifact-safe slugs."""

import re


def model_id_to_slug(model_id: str) -> str:
    """Convert a model ID into a stable filesystem-friendly slug."""
    normalized_model_id = re.sub(r"[/:.]+", "-", model_id.lower())
    return re.sub(r"-{2,}", "-", normalized_model_id).strip("-")
