"""Reviewer agent protocols for deterministic council orchestration."""

from typing import Any, Protocol

from growing_wiki_council.config import CouncilConfig
from growing_wiki_council.models.evidence import EvidenceBundle
from growing_wiki_council.models.review import ReviewerReport


class ReviewerAgent(Protocol):
    """Protocol for reviewer-like agents used by the council."""

    def run(self, bundle: EvidenceBundle) -> Any:
        """Return a structured reviewer payload for the given evidence."""


class ClaimExtractorAgent:
    """Claim extraction wrapper for the first real council reviewer."""

    def __init__(
        self,
        *,
        config: CouncilConfig,
        model_backend: Any | None = None,
    ) -> None:
        """Store runtime config and an optionally injected model backend."""
        self.config = config
        self.model_backend = model_backend or self._build_default_backend()

    def run(self, bundle: EvidenceBundle) -> ReviewerReport:
        """Run claim extraction against the provided evidence bundle."""
        prompt = self._build_prompt(bundle)
        response_payload = self.model_backend.run_prompt(prompt)
        return ReviewerReport.model_validate(response_payload)

    def _build_default_backend(self) -> Any:
        """Create the default backend placeholder for the real runtime path."""
        return _UnconfiguredClaimBackend()

    def _build_prompt(self, bundle: EvidenceBundle) -> str:
        """Build the first simple claim extraction prompt from evidence."""
        section_blocks = "\n\n".join(
            f"[{section.name}]\n{section.content}" for section in bundle.sections
        )
        return (
            f"paper_id: {bundle.paper_id}\n"
            f"title: {bundle.title}\n"
            f"source_kind: {bundle.source_kind}\n"
            f"extraction_confidence: {bundle.extraction_confidence}\n\n"
            f"{section_blocks}"
        )


class _UnconfiguredClaimBackend:
    """Placeholder backend until the OpenRouter client is wired in."""

    def run_prompt(self, prompt: str) -> dict[str, Any]:
        """Fail fast when the real backend has not been configured."""
        raise RuntimeError(
            "No claim extraction backend is configured yet."
        )
