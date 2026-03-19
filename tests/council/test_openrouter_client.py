from growing_wiki_council.clients.openrouter_client import OpenRouterClaimExtractorClient


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
