import httpx
import pytest
from growing_wiki_council.clients.openrouter_client import (
    OpenRouterClaimExtractorClient,
)


class FakeBackend:
    """Return a raw payload for schema calibration debugging."""

    def extract_claims(self, prompt: str) -> dict:
        return {"raw_response": {"content": "bad json"}}


def test_openrouter_client_exposes_raw_backend_payload() -> None:
    """Injected backends can surface raw payloads unchanged."""
    client = OpenRouterClaimExtractorClient(backend=FakeBackend())

    payload = client.run_prompt("prompt")

    assert "raw_response" in payload


def test_openrouter_client_preserves_raw_live_response(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Live responses expose parsed content and the raw provider payload."""

    def fake_post(*args: object, **kwargs: object) -> httpx.Response:
        response_payload = {
            "choices": [
                {
                    "message": {
                        "content": '{"summary":"Claims extracted.","findings":[],"claims":[]}'
                    }
                }
            ]
        }
        return httpx.Response(
            200,
            json=response_payload,
            request=httpx.Request("POST", "https://openrouter.ai/api/v1/chat/completions"),
        )

    monkeypatch.setattr(httpx, "post", fake_post)
    client = OpenRouterClaimExtractorClient(
        api_key="test-key",
        model="openrouter/openai/gpt-4.1-mini",
    )

    payload = client.run_prompt("prompt")

    assert payload["summary"] == "Claims extracted."
    assert payload["raw_response"]["choices"][0]["message"]["content"]
