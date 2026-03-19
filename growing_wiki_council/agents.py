"""Reviewer agent protocols for deterministic council orchestration."""

from typing import Any, Protocol

from growing_wiki_council.models.evidence import EvidenceBundle


class ReviewerAgent(Protocol):
    """Protocol for reviewer-like agents used by the council."""

    def run(self, bundle: EvidenceBundle) -> Any:
        """Return a structured reviewer payload for the given evidence."""
