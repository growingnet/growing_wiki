"""OpenRouter-backed client wrappers for council model calls."""

from __future__ import annotations

from typing import Any

import httpx


class OpenRouterClaimExtractorClient:
    """Run claim extraction prompts through an injected or real backend."""

    def __init__(
        self,
        *,
        backend: Any | None = None,
        api_key: str | None = None,
        base_url: str = "https://openrouter.ai/api/v1",
        model: str | None = None,
        timeout_seconds: float = 60.0,
    ) -> None:
        """Store backend configuration for claim extraction requests."""
        self.backend = backend
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout_seconds = timeout_seconds

    def run_prompt(self, prompt: str) -> dict[str, Any]:
        """Execute a claim extraction prompt and return a JSON-like payload."""
        if self.backend is not None:
            return self.backend.extract_claims(prompt)
        return self._run_openrouter_request(prompt)

    def _run_openrouter_request(self, prompt: str) -> dict[str, Any]:
        """Execute the real OpenRouter-compatible request path."""
        if not self.api_key:
            raise RuntimeError("OpenRouter API key is required for live requests.")
        if not self.model:
            raise RuntimeError("OpenRouter model is required for live requests.")

        response = httpx.post(
            f"{self.base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "response_format": {"type": "json_object"},
            },
            timeout=self.timeout_seconds,
        )
        response.raise_for_status()
        payload = response.json()
        content = payload["choices"][0]["message"]["content"]
        if isinstance(content, dict):
            return content
        return httpx.Response(200, text=content).json()
