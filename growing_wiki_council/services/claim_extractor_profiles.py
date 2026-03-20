"""Prompt builders for benchmark steerability profiles."""

from __future__ import annotations

from growing_wiki_council.models.evidence import EvidenceBundle


def build_prompt_for_profile(*, profile_id: str, bundle: EvidenceBundle) -> str:
    """Build a claim-extraction prompt for the selected benchmark profile."""
    section_blocks = "\n\n".join(
        f"[{section.name}]\n{section.content}" for section in bundle.sections
    )
    paper_context = (
        "Paper evidence follows.\n"
        f"paper_id: {bundle.paper_id}\n"
        f"title: {bundle.title}\n"
        f"source_kind: {bundle.source_kind}\n"
        f"extraction_confidence: {bundle.extraction_confidence}\n\n"
        f"{section_blocks}"
    )

    if profile_id == "baseline":
        return _build_baseline_prompt(paper_context)
    if profile_id == "baseline_prompt_variant":
        return _build_prompt_variant(paper_context)
    if profile_id == "website_aligned":
        return _build_website_aligned_prompt(paper_context)
    raise ValueError(f"Unsupported benchmark profile: {profile_id}")


def _build_baseline_prompt(paper_context: str) -> str:
    """Build the current baseline prompt."""
    return (
        "You are the claim_extractor reviewer in a scientific review council.\n"
        "Return JSON only.\n"
        "Do not return markdown.\n"
        "Do not return prose outside the JSON object.\n"
        "Do not return any top-level fields other than role, summary, findings, claims, and open_questions.\n"
        "The JSON object must follow this schema exactly:\n"
        "{\n"
        '  "role": "claim_extractor",\n'
        '  "summary": "Short summary here.",\n'
        '  "findings": [\n'
        "    {\n"
        '      "severity": "low",\n'
        '      "claim": "Finding tied to evidence.",\n'
        '      "evidence_refs": ["section:full_text"],\n'
        '      "rationale": "Why this matters.",\n'
        '      "recommendation": "Optional recommendation."\n'
        "    }\n"
        "  ],\n"
        '  "claims": [\n'
        "    {\n"
        '      "claim": "Atomic claim from the paper.",\n'
        '      "evidence_refs": ["section:full_text"],\n'
        '      "confidence": "medium",\n'
        '      "notes": "Optional note."\n'
        "    }\n"
        "  ],\n"
        '  "open_questions": ["Optional open question."]\n'
        "}\n"
        "If the evidence is weak, still return the same schema. Use empty lists when needed.\n"
        "The summary field is mandatory.\n\n"
        f"{paper_context}"
    )


def _build_prompt_variant(paper_context: str) -> str:
    """Build the prompt-only steerability variant on the same schema."""
    return (
        "You are the claim_extractor reviewer in a scientific review council.\n"
        "Return JSON only.\n"
        "Prioritize strict evidence anchoring and avoid unsupported specificity.\n"
        "Maximize evidence anchoring while still extracting the main paper contributions.\n"
        "Do not return markdown.\n"
        "Do not return prose outside the JSON object.\n"
        "Do not return any top-level fields other than role, summary, findings, claims, and open_questions.\n"
        "The JSON object must follow this schema exactly:\n"
        "{\n"
        '  "role": "claim_extractor",\n'
        '  "summary": "Short summary here.",\n'
        '  "findings": [],\n'
        '  "claims": [\n'
        "    {\n"
        '      "claim": "Atomic claim from the paper.",\n'
        '      "evidence_refs": ["section:full_text"],\n'
        '      "confidence": "medium",\n'
        '      "notes": "Optional note."\n'
        "    }\n"
        "  ],\n"
        '  "open_questions": []\n'
        "}\n"
        "Prefer omission over overclaiming when the evidence is ambiguous.\n\n"
        f"{paper_context}"
    )


def _build_website_aligned_prompt(paper_context: str) -> str:
    """Build the additive-schema prompt aligned to the website analysis style."""
    return (
        "You are the claim_extractor reviewer in a scientific review council.\n"
        "Return JSON only.\n"
        "Use a website-aligned, mechanistic analysis style rather than an abstract-only summary style.\n"
        "Do not return markdown.\n"
        "Do not return prose outside the JSON object.\n"
        "The JSON object must follow this schema exactly:\n"
        "{\n"
        '  "role": "claim_extractor",\n'
        '  "summary": "Short summary here.",\n'
        '  "findings": [],\n'
        '  "claims": [],\n'
        '  "open_questions": [],\n'
        '  "schema_variant": "website_aligned",\n'
        '  "method_family": "Optional method family.",\n'
        '  "growth_operator": "Optional growth operator.",\n'
        '  "initialization_strategy": "Optional initialization strategy.",\n'
        '  "selection_criterion": "Optional selection criterion.",\n'
        '  "mechanistic_notes": ["Optional mechanistic note."],\n'
        '  "website_alignment_notes": "Optional alignment note."\n'
        "}\n"
        "Prefer mechanistic decomposition over marketing language.\n"
        "When possible, identify method_family, growth_operator, initialization_strategy, and selection_criterion from the provided evidence.\n\n"
        f"{paper_context}"
    )
