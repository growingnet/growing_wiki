# Claim Benchmark Steerability Design

## Goal

Extend the real-paper claim-extraction benchmark so it can probe prompt
steerability explicitly before any workflow-heavy changes.

The benchmark should support two new comparison modes on the same model and
dataset:

1. a prompt-only variant that keeps the current schema and artifact shape
2. a prompt-plus-schema variant that adds website-aligned mechanistic fields on
   top of the current schema

This lets us measure whether prompt engineering alone is enough to improve
alignment with the research team's website analysis.

## Scope

This design covers:

- benchmark prompt profiles
- a prompt-only comparison mode on the current schema
- an additive website-aligned schema variant
- deterministic profile-separated artifacts
- repeated-run comparison on the same committed benchmark dataset

This design does not cover:

- workflow changes outside prompt and schema steering
- multi-agent council changes
- automated wiki patching
- replacing the current benchmark dataset

## Recommended Approach

Keep one benchmark runner and add named benchmark profiles above it.

Each profile should define:

- the prompt instructions used by the claim extractor
- the output schema to validate against
- the artifact subdirectory label used for deterministic comparison

Profiles:

- `baseline`
  - current prompt
  - current `ReviewerReport` schema
- `baseline_prompt_variant`
  - alternate prompt
  - same `ReviewerReport` schema
- `website_aligned`
  - website-oriented prompt
  - additive extension of `ReviewerReport`

This preserves the runner, provider path, and dataset while isolating
steerability as the main experimental variable.

## Alternatives Considered

### 1. One runner with prompt profiles and additive schema variants

Recommended.

Pros:

- direct comparability
- low code churn
- one shared artifact and execution path
- easy repeated-run analysis

Cons:

- benchmark configuration becomes more explicit and slightly larger

### 2. Separate runners per prompt family

Not recommended.

Pros:

- very explicit separation

Cons:

- duplicated logic
- more room for accidental divergence
- harder to compare profile results cleanly

### 3. Workflow adaptation before prompt probing

Not recommended for this phase.

Pros:

- potentially larger quality gains

Cons:

- confounds steerability with workflow changes
- heavier implementation before we know prompt steering is enough

## Profile Design

Add a benchmark profile concept with a stable identifier and an explicit
artifact label.

Suggested initial profiles:

- `baseline`
- `baseline_prompt_variant`
- `website_aligned`

Each profile should specify:

- `profile_id`
- `prompt_style`
- `schema_variant`
- `artifact_label`

The current benchmark behavior should become the `baseline` profile so existing
runs remain interpretable.

## Prompt Strategy

### `baseline`

Keep the current claim-extractor prompt unchanged as the control condition.

### `baseline_prompt_variant`

Keep the same output schema and artifact shape, but adapt the prompt to push
for:

- stricter evidence anchoring
- less unsupported specificity
- more complete extraction of the main paper contributions

This profile is intended to answer:

- can prompt changes alone reduce omission and mild overreach?

### `website_aligned`

Use a different prompt that explicitly asks for a more mechanistic,
algorithm-oriented analysis aligned with the website.

The prompt should bias toward:

- growth mechanism description
- initialization or extension strategy
- optimization or selection criterion
- algorithm-family or method-family framing

This profile is intended to answer:

- can the same model be steered from abstract-like summarization toward the
  research team's website framing?

## Schema Strategy

Keep the current `ReviewerReport` fields as the shared base contract:

- `summary`
- `findings`
- `claims`
- `open_questions`

For the `website_aligned` profile, add optional fields rather than replacing
the schema.

Suggested additive fields:

- `method_family`
- `growth_operator`
- `initialization_strategy`
- `selection_criterion`
- `mechanistic_notes`
- `website_alignment_notes`

This preserves overlap with the current benchmark while making the second mode
explicitly evaluable.

## Artifact Layout

Separate artifacts by profile under the run root.

Example:

```text
artifacts/claim-extraction-benchmark/<run_label>/<profile>/<model_slug>/<paper_id>/
```

Per-paper files should remain stable:

- `benchmark-entry.json`
- `provider-result.json`
- `evidence-bundle.json`
- `raw-reviewer-output.json`
- `validated-reviewer-report.json`
- `summary.md`
- `human-eval.template.json`

Run-level files should remain:

- `manifest.snapshot.json`
- `run-summary.json`

This gives profile-specific comparability without introducing a new artifact
system.

## Evaluation Plan

The benchmark should support the following controlled comparisons:

1. `baseline` vs `baseline_prompt_variant`
   - same schema
   - prompt-only change
2. `baseline` vs `website_aligned`
   - prompt change plus additive schema change
3. repeated runs inside each profile
   - measure structural and quality variance

Key outputs to compare:

- completion rate
- claim count variance
- findings and open-question variance
- manual scores from the benchmark grading rubric
- website-alignment quality for the additive fields

## Testing

Tests should remain offline and deterministic.

Coverage should include:

- profile model validation
- prompt selection by profile
- same-schema validation for the prompt-only profile
- additive-schema validation for the website-aligned profile
- deterministic profile-specific artifact paths
- a smoke test that runs multiple profiles with fake backends

## Rollout

Phase 1:

- add profile models and prompt builders
- add additive schema for `website_aligned`
- add profile-separated artifacts
- test the new benchmark modes offline

Phase 2:

- run live repeated benchmarks across the three profiles
- compare quality and standard deviation
- decide whether prompt steering is sufficient or whether workflow changes are
  justified
