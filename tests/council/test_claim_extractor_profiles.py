from growing_wiki_council.models.evidence import EvidenceBundle
from growing_wiki_council.services.claim_extractor_profiles import (
    build_prompt_for_profile,
)


def test_build_prompt_for_profile_supports_expected_profiles() -> None:
    """Profile prompt builders should tailor instructions by profile."""
    bundle = EvidenceBundle(
        paper_id="paper-1",
        source_kind="generic_pdf",
        title="Paper",
        sections=[],
        equations=[],
        bibliography=[],
        warnings=[],
        extraction_confidence="medium",
    )

    baseline_prompt = build_prompt_for_profile(
        profile_id="baseline",
        bundle=bundle,
    )
    prompt_variant = build_prompt_for_profile(
        profile_id="baseline_prompt_variant",
        bundle=bundle,
    )
    website_aligned_prompt = build_prompt_for_profile(
        profile_id="website_aligned",
        bundle=bundle,
    )

    assert "Return JSON only." in baseline_prompt
    assert "evidence anchoring" in prompt_variant
    assert "method_family" in website_aligned_prompt
    assert "growth_operator" in website_aligned_prompt
    assert "initialization_strategy" in website_aligned_prompt
    assert "selection_criterion" in website_aligned_prompt


def test_website_aligned_prompt_requires_structured_claim_objects() -> None:
    """Website-aligned prompts should preserve the base claim object schema."""
    bundle = EvidenceBundle(
        paper_id="paper-1",
        source_kind="generic_pdf",
        title="Paper",
        sections=[],
        equations=[],
        bibliography=[],
        warnings=[],
        extraction_confidence="medium",
    )

    website_aligned_prompt = build_prompt_for_profile(
        profile_id="website_aligned",
        bundle=bundle,
    )

    assert '"claims": [' in website_aligned_prompt
    assert '"claim": "Atomic claim from the paper."' in website_aligned_prompt
    assert '"evidence_refs": ["section:full_text"]' in website_aligned_prompt
    assert '"confidence": "medium"' in website_aligned_prompt
    assert "claims must remain structured objects" in website_aligned_prompt
