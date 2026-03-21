import httpx
import pytest
import growing_wiki_council.clients.openrouter_client as openrouter_client_module
from growing_wiki_council.clients.openrouter_client import (
    OpenRouterClaimExtractorClient,
)


class FakeBackend:
    """Simple fake backend for the OpenRouter claim client test."""

    def extract_claims(self, prompt: str) -> dict:
        return {
            "role": "claim_extractor",
            "summary": "Claims extracted.",
            "findings": [],
            "claims": [{"claim": "A", "evidence_refs": ["section:full_text"]}],
        }


def test_openrouter_claim_client_uses_injected_backend() -> None:
    """The claim client delegates to an injected backend in tests."""
    client = OpenRouterClaimExtractorClient(backend=FakeBackend())

    report = client.run_prompt("prompt")

    assert report["role"] == "claim_extractor"


def test_openrouter_client_retries_on_rate_limit(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Live client retries transient 429 failures before succeeding."""
    calls: list[int] = []

    def fake_post(*args: object, **kwargs: object) -> httpx.Response:
        calls.append(1)
        if len(calls) == 1:
            return httpx.Response(
                429,
                json={"error": {"message": "rate limited"}},
                request=httpx.Request(
                    "POST", "https://openrouter.ai/api/v1/chat/completions"
                ),
            )
        return httpx.Response(
            200,
            json={
                "choices": [
                    {
                        "message": {
                            "content": '{"summary":"Claims extracted.","findings":[],"claims":[]}'
                        }
                    }
                ]
            },
            request=httpx.Request(
                "POST", "https://openrouter.ai/api/v1/chat/completions"
            ),
        )

    sleep_calls: list[float] = []

    monkeypatch.setattr(httpx, "post", fake_post)
    monkeypatch.setattr(
        openrouter_client_module.time,
        "sleep",
        lambda seconds: sleep_calls.append(seconds),
    )
    client = OpenRouterClaimExtractorClient(
        api_key="test-key",
        model="openrouter/openai/gpt-4.1-mini",
        max_retries=1,
        retry_backoff_seconds=0.25,
    )

    payload = client.run_prompt("prompt")

    assert payload["summary"] == "Claims extracted."
    assert len(calls) == 2
    assert sleep_calls == [0.25]


def test_openrouter_client_uses_retry_after_header_when_rate_limited(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Live client respects Retry-After when a 429 response provides it."""
    calls: list[int] = []

    def fake_post(*args: object, **kwargs: object) -> httpx.Response:
        calls.append(1)
        if len(calls) == 1:
            return httpx.Response(
                429,
                headers={"Retry-After": "2"},
                json={"error": {"message": "rate limited"}},
                request=httpx.Request(
                    "POST", "https://openrouter.ai/api/v1/chat/completions"
                ),
            )
        return httpx.Response(
            200,
            json={
                "choices": [
                    {
                        "message": {
                            "content": '{"summary":"Claims extracted.","findings":[],"claims":[]}'
                        }
                    }
                ]
            },
            request=httpx.Request(
                "POST", "https://openrouter.ai/api/v1/chat/completions"
            ),
        )

    sleep_calls: list[float] = []

    monkeypatch.setattr(httpx, "post", fake_post)
    monkeypatch.setattr(
        openrouter_client_module.time,
        "sleep",
        lambda seconds: sleep_calls.append(seconds),
    )
    client = OpenRouterClaimExtractorClient(
        api_key="test-key",
        model="openrouter/openai/gpt-4.1-mini",
        max_retries=1,
        retry_backoff_seconds=0.25,
    )

    payload = client.run_prompt("prompt")

    assert payload["summary"] == "Claims extracted."
    assert len(calls) == 2
    assert sleep_calls == [2.0]


def test_openrouter_client_does_not_retry_not_found(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Live client surfaces hard 404 errors without retrying."""
    calls: list[int] = []

    def fake_post(*args: object, **kwargs: object) -> httpx.Response:
        calls.append(1)
        return httpx.Response(
            404,
            json={"error": {"message": "model not found"}},
            request=httpx.Request(
                "POST", "https://openrouter.ai/api/v1/chat/completions"
            ),
        )

    monkeypatch.setattr(httpx, "post", fake_post)
    client = OpenRouterClaimExtractorClient(
        api_key="test-key",
        model="openrouter/openai/gpt-4.1-mini",
        max_retries=3,
        retry_backoff_seconds=0.25,
    )

    with pytest.raises(httpx.HTTPStatusError):
        client.run_prompt("prompt")

    assert len(calls) == 1
