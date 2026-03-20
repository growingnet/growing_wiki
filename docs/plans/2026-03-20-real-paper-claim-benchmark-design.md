# Real-Paper Claim Benchmark Design

## Goal

Build the next stage toward council deployment by adding a small real-paper
claim-extraction benchmark that runs the existing provider-to-evidence-to-agent
pipeline on committed paper fixtures and emits structured machine and human
evaluation artifacts.

The benchmark should freeze
`nvidia/nemotron-3-super-120b-a12b:free` as the default baseline while keeping
the runner extensible enough to accept optional comparison models later through
the same interface.

## Scope

This design covers:

- a small benchmark dataset format for 5 to 10 papers
- committed local PDF fixtures in the repo
- support for `arxiv_id`, arXiv PDF path, and non-arXiv PDF path inputs
- a benchmark runner that reuses the existing provider boundary
- deterministic benchmark artifact output
- a structured human evaluation template per paper run

This design does not cover:

- the full multi-agent council
- automated wiki patching
- model voting or consensus
- remote dataset downloading

## Recommended Approach

Add a dedicated benchmark layer beside the current vertical slice instead of
expanding the vertical slice into a generic experiment framework.

The new path should:

1. load a benchmark manifest
2. resolve a provider from the entry source type
3. load and normalize evidence through the existing adapter boundary
4. run the claim extractor on the `EvidenceBundle`
5. write deterministic machine artifacts and a human scoring template

This keeps the current council prototype stable while adding a narrow,
benchmark-specific surface for real-paper evaluation.

## Alternatives Considered

### 1. Dedicated benchmark layer beside the vertical slice

Recommended.

Pros:

- preserves the current vertical-slice intent
- reuses the provider and evidence seams already in the package
- keeps benchmark artifacts separate from council-review artifacts
- avoids overbuilding the full council too early

Cons:

- introduces a second orchestration path

### 2. Extend the vertical slice directly

Not recommended.

Pros:

- fewer files initially

Cons:

- mixes single-run demo concerns with dataset iteration and scoring
- makes future council responsibilities less clear

### 3. Build a general experiment framework now

Not recommended for this phase.

Pros:

- maximum future flexibility

Cons:

- unnecessary abstraction for the current target
- slower path to a usable benchmark

## Dataset Design

Add a benchmark manifest under `growing_wiki_council/benchmarks/` plus a small
fixture set of committed PDFs in the repo.

Each manifest row should contain:

- `paper_id`
- `source_type`
- `source`
- `title` optional
- `notes` optional
- `tags` optional

Supported `source_type` values:

- `arxiv_id`
- `arxiv_pdf_path`
- `pdf_path`

This format is intentionally small. It is enough to drive the benchmark while
keeping the source-selection rules explicit and testable.

## Architecture

Add a benchmark-specific orchestration service above the current provider and
claim-extractor components.

Components:

- benchmark dataset models
  - validate and load the manifest
- provider resolver
  - choose the correct provider for each manifest entry
- benchmark runner
  - iterate over entries
  - build evidence bundles
  - run the claim extractor
  - persist benchmark artifacts
- human evaluation models
  - define the scoring schema and template writer

The current `run_claim_extraction_slice(...)` path should remain callable and
unchanged in purpose.

## Provider Boundary

The benchmark must use the existing provider boundary instead of assembling
`EvidenceBundle` objects directly.

Planned provider routing:

- `arxiv_id` -> `ArxivLatexProvider`
- `arxiv_pdf_path` -> arXiv PDF handling through the same adapter boundary
- `pdf_path` -> `GenericPdfProvider`

For this stage, provider resolution belongs in a small benchmark service or
factory rather than inside the dataset model.

## PDF Extraction

`GenericPdfProvider` should move from path validation only to simple local PDF
text extraction.

Requirements:

- validate the input path clearly
- extract page text into `raw_text`
- preserve warnings when extraction is weak or empty
- avoid OCR or layout-heavy logic in this phase

The benchmark needs a real non-arXiv PDF path, not just a stub provider.

## Baseline Model Policy

Freeze `nvidia/nemotron-3-super-120b-a12b:free` as the benchmark default in the
benchmark runner configuration.

The runner should still allow optional model overrides or comparison lists, but
the default single-model run must always target the frozen baseline unless the
caller explicitly overrides it.

This keeps the benchmark reproducible while preserving a clean upgrade path to
later model comparisons.

## Artifact Layout

Write deterministic artifacts under a benchmark-specific root.

Example:

```text
artifacts/claim-extraction-benchmark/<run_label>/<model_slug>/<paper_id>/
  benchmark-entry.json
  provider-result.json
  evidence-bundle.json
  raw-reviewer-output.json
  validated-reviewer-report.json
  summary.md
  human-eval.template.json
```

Run-level files should include:

- `manifest.snapshot.json`
- `run-summary.json`

These artifacts separate benchmark inspection from the existing council
`review.json` and `review.md` outputs.

## Human Evaluation Schema

Add a structured human scoring model with at least:

- `claim_faithfulness`
- `evidence_grounding`
- `omission_rate`
- `hallucination_flags`
- `reviewer_notes`

Recommended metadata fields:

- `paper_id`
- `model_id`
- `run_label`
- `review_status`
- `scored_at`

The template should be emitted as JSON so it stays aligned with the package’s
other structured artifacts and is easy to validate later.

## Error Handling

Benchmark runs should isolate failures per paper.

Rules:

- if one paper fails provider loading, record the provider result and continue
- if one paper fails schema validation, preserve the raw model output and
  continue
- if one paper succeeds, still emit the human evaluation template
- do not abort the full benchmark because one entry fails

## Testing

Tests should remain deterministic and offline by default.

Coverage should include:

- benchmark manifest validation
- provider resolution by source type
- local PDF extraction success and failure paths
- deterministic artifact paths
- human evaluation template writing
- baseline-default model selection
- an end-to-end benchmark run with fake providers or fake model backends

The live OpenRouter path should stay injectable so tests do not require network
access.

## Security

- keep `OPENROUTER_API_KEY` in environment variables or untracked `.env`
- do not write secrets into committed files or generated artifacts
- do not modify the external arXiv MCP repo
- if a blocker depends on that repo, stop and report a ticket-ready issue

## Rollout

Phase 1:

- add the benchmark dataset, runner, artifacts, and tests
- implement simple local PDF extraction
- freeze the Nemotron Super baseline as default

Phase 2, later:

- add optional side-by-side model comparison reports
- integrate benchmark signals into future council orchestration
- consider richer review tooling for scored benchmark analysis
