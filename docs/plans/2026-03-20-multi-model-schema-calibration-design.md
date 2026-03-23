# Multi-Model Schema Calibration Design

## Goal

Extend the existing schema-calibration path so it can run the same deterministic
fake evidence input through two pinned OpenRouter models and preserve their
outputs separately for comparison.

The change must stay isolated to schema calibration. The main council
claim-extraction path should remain single-model for now.

## Scope

This design covers:

- selecting two pinned OpenRouter model IDs for calibration
- running one calibration pass per model
- writing artifacts into per-model output directories
- capturing per-model schema success or validation failure

This design does not cover:

- consensus or voting across models
- merging reports into one combined reviewer output
- changing the main claim-extractor runtime to multi-model
- provider changes outside OpenRouter

## Recommended Approach

Use a calibration-only multi-model runner that wraps the existing
`run_schema_calibration(...)` flow.

Each calibration model should:

1. build a `CouncilConfig` with the shared runtime settings and a model override
2. instantiate a `ClaimExtractorAgent`
3. run against the same deterministic calibration bundle
4. write artifacts into a model-specific directory
5. return a structured per-model result for later comparison

This keeps the current single-model paths stable and reuses the code that
already exists for raw-response preservation and schema validation.

## Alternatives Considered

### 1. Multi-model only in schema calibration

Recommended.

Pros:

- smallest change surface
- easiest to compare outputs
- no impact on the main council flow
- low risk for regressions

Cons:

- no immediate benefit to the real vertical slice

### 2. Multi-model in the main claim-extraction path

Not recommended yet.

Pros:

- richer live outputs immediately

Cons:

- pushes model-routing complexity into the production path too early
- makes debugging schema reliability harder
- complicates artifact and prompt ownership

### 3. Use `openrouter/free` instead of pinned model IDs

Not recommended for this phase.

Pros:

- simplest config

Cons:

- underlying model can change between runs
- weak reproducibility for scientific review experiments

## Selected Models

The starting pair is:

- `nvidia/nemotron-3-super-120b-a12b:free`
- `stepfun/step-3.5-flash:free`

These should be treated as explicit calibration inputs, not hidden defaults in
the main runtime path.

## Architecture

Add a calibration-only orchestration layer above the existing single-model
runner.

Components:

- `CouncilConfig`
  - add a calibration model list field for multi-model runs
- multi-model calibration service
  - loops over pinned model IDs
  - creates one agent per model
  - calls the existing schema-calibration runner
- artifact writer
  - writes one subdirectory per model slug
- summary model
  - stores per-model success state and artifact location

The existing single-model calibration path should stay callable as-is.

## Artifact Layout

Use deterministic model-specific directories under the calibration root.

Example:

```text
artifacts/calibration/
  nvidia-nemotron-3-super-120b-a12b-free/
    calibration.json
    raw-response.json
    validated-report.json
  stepfun-step-3-5-flash-free/
    calibration.json
    raw-response.json
    validated-report.json
```

Optional later:

- a top-level summary JSON listing all model outcomes

## Error Handling

Per-model failures should be isolated.

Rules:

- if one model fails schema validation, keep the other model results
- if one model returns HTTP or runtime failure, record that failure without
  aborting the entire batch
- preserve raw responses whenever available
- do not hide validation errors behind retries in this phase

## Testing

Tests should stay no-network.

Coverage should include:

- config support for a calibration model list
- a multi-model service that runs two fake agents
- artifact output in per-model directories
- one smoke test for the full multi-model calibration flow

## Security

- API keys remain external to the repo
- `.env` or environment variables provide the OpenRouter key
- no model run should print the key
- raw responses should be preserved, but secret-bearing headers must not be
  written

## Rollout

Phase 1:

- add the multi-model calibration path only
- verify both pinned free models can be targeted
- compare schema reliability and raw outputs manually

Phase 2, if useful:

- add a comparison summary artifact
- consider prompt diagnostics
- decide whether either model should graduate into the main review flow
