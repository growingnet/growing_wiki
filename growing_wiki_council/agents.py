"""Reviewer agent protocols for deterministic council orchestration."""

from typing import Any, Protocol

from growing_wiki_council.clients.openrouter_client import (
    OpenRouterClaimExtractorClient,
)
from growing_wiki_council.config import CouncilConfig
from growing_wiki_council.models.evidence import EvidenceBundle
from growing_wiki_council.models.review import ReviewerReport
from growing_wiki_council.models.review_profiles import WebsiteAlignedReviewerReport


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
        benchmark_profile_id: str = "baseline",
    ) -> None:
        """Store runtime config and an optionally injected model backend."""
        self.config = config
        self.model_backend = model_backend or self._build_default_backend()
        self.benchmark_profile_id = benchmark_profile_id

    def run(self, bundle: EvidenceBundle) -> ReviewerReport:
        """Run claim extraction against the provided evidence bundle."""
        response_payload = self.run_raw(bundle)
        return self._reviewer_report_model().model_validate(response_payload)

    def run_raw(self, bundle: EvidenceBundle) -> dict[str, Any]:
        """Run claim extraction and return the raw structured payload."""
        prompt = self._build_prompt(bundle)
        response_payload = dict(self.model_backend.run_prompt(prompt))
        response_payload["role"] = "claim_extractor"
        return response_payload

    def _build_default_backend(self) -> Any:
        """Create the default backend placeholder for the real runtime path."""
        return OpenRouterClaimExtractorClient(
            api_key=self.config.openrouter_api_key.get_secret_value(),
            base_url=self.config.openrouter_base_url,
            model=self.config.claim_extractor_model,
            timeout_seconds=self.config.request_timeout_seconds,
            max_retries=self.config.openrouter_max_retries,
            retry_backoff_seconds=self.config.openrouter_retry_backoff_seconds,
        )

    def _build_prompt(self, bundle: EvidenceBundle) -> str:
        """Build the first simple claim extraction prompt from evidence."""
        from growing_wiki_council.services.claim_extractor_profiles import (
            build_prompt_for_profile,
        )

        return build_prompt_for_profile(
            profile_id=self.benchmark_profile_id,
            bundle=bundle,
        )

    def _reviewer_report_model(self) -> type[ReviewerReport]:
        """Return the validation model for the selected benchmark profile."""
        if self.benchmark_profile_id == "website_aligned":
            return WebsiteAlignedReviewerReport
        return ReviewerReport
