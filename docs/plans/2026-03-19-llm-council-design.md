# LLM Council for Scientific Review Design

**Date:** 2026-03-19
**Status:** Approved direction

## Decision Summary

Build the council as a source-agnostic scientific review pipeline.

The core decision is to separate:

- evidence acquisition
- evidence normalization
- structured review
- editorial synthesis

The council should not be implemented as a free-form multi-agent chat. It should be implemented as a deterministic workflow where specialized reviewer agents operate on a shared evidence object and return schema-validated outputs.

## Goals

- Review papers for scientific accuracy, internal consistency, and editorial fit for the wiki.
- Support three evidence situations:
  - arXiv papers with LaTeX source
  - arXiv papers with PDF-only access
  - non-arXiv papers with PDF access
- Preserve provenance and extraction quality so weak evidence is visible to downstream reviewers.
- Produce artifacts that are useful for the wiki:
  - machine-readable review JSON
  - human-readable markdown review
  - optional proposed `.rst` patch

## Non-Goals

- Fully autonomous publication or merge decisions.
- Open-ended research chat without evidence grounding.
- Building a general-purpose multi-agent framework.

## Considered Approaches

### 1. Direct inspiration from Karpathy-style council orchestration

Useful as inspiration, but not as the implementation model. The project needs explicit evidence handling, structured outputs, and deterministic review stages more than conversational emergence.

### 2. arXiv-first pipeline with PDF fallback

Strong for the current corpus, but insufficient because the council must also handle non-arXiv venue PDFs as first-class inputs.

### 3. Source-agnostic council with provider-specific ingestion

Recommended. All inputs are converted into the same normalized `EvidenceBundle`, and the council operates only on that bundle. This keeps review behavior stable while allowing different ingestion backends.

## Recommended Stack

- Agent runtime: PydanticAI
- Model gateway: OpenRouter
- Primary arXiv ingestion: `arxiv-latex-mcp`
- Generic PDF ingestion: a dedicated PDF provider
- External scholarly metadata: OpenAlex first, optional secondary enrichment later
- Tests: `pytest`

## Why This Stack

### PydanticAI

The council needs strict output schemas for claims, objections, confidence scores, evidence citations, and editorial recommendations. PydanticAI is a better fit for this than a chat-first orchestration runtime because the output contract is central to correctness.

### OpenRouter

OpenRouter is the right provider for v1 because it allows practical testing with the credits already available. It also keeps the council provider-agnostic at the model layer so additional providers can be added later without redesigning the review pipeline.

### arxiv-latex-mcp

This is the highest-quality evidence source for arXiv papers because it can preserve formulas, bibliography structure, and source provenance more faithfully than PDF parsing alone.

### Generic PDF Provider

This is required because the council must handle both arXiv PDF-only cases and non-arXiv venue PDFs. PDF ingestion is therefore a first-class backend, not just a fallback afterthought.

## Architecture

### 1. Evidence Providers

Each provider implements a common interface and returns raw extracted artifacts plus provenance:

- `ArxivLatexProvider`
- `GenericPdfProvider`

Both providers should expose:

- resolved metadata
- extracted text or sections
- equations if available
- bibliography if available
- extraction warnings
- provenance and confidence flags

### 2. Evidence Normalization

All provider outputs are converted into a shared `EvidenceBundle`.

The bundle should include at least:

- canonical paper identifier
- source kind
- title, authors, venue, dates, DOI/arXiv ID when available
- normalized sections
- extracted equations
- bibliography entries
- extraction warnings
- provenance per field
- overall extraction confidence

The council only reads the normalized bundle. Reviewer agents should never consume raw provider responses directly.

### 3. Reviewer Roles

The council should start with fixed roles:

- `claim_extractor`
  - extracts atomic claims from the paper with section-level evidence references
- `skeptical_reviewer`
  - attacks unsupported claims, missing baselines, weak experimental design, statistical gaps, and overstatements
- `supportive_reviewer`
  - identifies what is actually supported, useful methodological contributions, and where the paper is stronger than the skeptic allows
- `citation_auditor`
  - checks metadata, references, venue facts, and obvious related-work omissions when available
- `chair_editor`
  - synthesizes disagreements, identifies unresolved uncertainties, and produces the editorial artifact

These roles debate over the same evidence object, not over each other's ungrounded summaries.

### 4. Output Artifacts

Each paper review should produce:

- `review.json`
  - full structured agent outputs and provenance
- `review.md`
  - concise editorial review for a human maintainer
- optional `proposed_patch.rst`
  - candidate wiki content changes when confidence is sufficient

## Confidence Model

Confidence should be attached to both extraction and review.

Examples:

- `extraction_confidence`
  - high for well-formed LaTeX source
  - medium for clean PDF extraction
  - low for messy PDF extraction or missing bibliography
- `review_confidence`
  - reduced when evidence is incomplete, contradictory, or missing key sections

The chair editor should be required to explain any downgrade in confidence.

## Human-in-the-Loop Policy

No review should directly update the wiki without human approval.

Human review is mandatory when:

- extraction confidence is low
- the skeptic and supporter remain materially inconsistent
- bibliography or metadata are incomplete
- the council proposes substantive scientific claims not already present in the paper

## Model Strategy

Use OpenRouter for all council agents in v1, but keep the role-to-model mapping configurable.

The first release should prefer a small set of reliable role assignments over premature model diversity. Heterogeneous councils can be introduced later once the evidence schema and evaluation harness are stable.

## Evaluation Strategy

The system should be evaluated before wide use on the wiki.

Suggested evaluation set:

- 5 arXiv papers with LaTeX source
- 5 arXiv papers with PDF-only extraction
- 5 non-arXiv venue PDFs

For each paper, measure:

- metadata correctness
- equation preservation
- bibliography coverage
- quality of critical objections
- rate of unsupported reviewer claims
- usefulness of the final editorial artifact

## Recommended Rollout

### Phase 1

Build the normalized evidence layer and one end-to-end council run for a single paper.

### Phase 2

Add better PDF extraction quality controls, external metadata enrichment, and proposed wiki patch generation.

### Phase 3

Add model comparisons, confidence calibration, and batch review workflows.

## Final Recommendation

Adopt a source-agnostic council built around:

- PydanticAI for typed reviewer agents
- OpenRouter as the initial model provider
- `arxiv-latex-mcp` as the highest-quality arXiv evidence backend
- a first-class generic PDF provider for PDF-only papers
- a shared `EvidenceBundle` as the only input to reviewer agents

This gives the project the strongest balance of scientific rigor, practical testability, and future extensibility.
